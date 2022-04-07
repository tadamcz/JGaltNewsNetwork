import datetime
import json
import os.path
from time import sleep

import dateutil.parser
import imgkit
import peewee
import regex
import requests
import tweepy
from bs4 import BeautifulSoup

from db import Comment, Question
from twitter_api import client, api


class NewsNetwork:
	COMMENTS_URL = "https://www.metaculus.com/api2/comments/?author=101465"
	START_DATE = datetime.datetime(2022, 3, 1)
	JPEG_PATH = 'images_temp'

	def __init__(self, production):
		print(f"Production: {production}")
		self.production = production

	def get_comments(self):

		response = requests.get(self.COMMENTS_URL).json()

		comments = response['results']

		for comment_dict in comments:
			id = comment_dict['id']
			submit_type = comment_dict['submit_type']
			parent = comment_dict['parent']
			created_at = dateutil.parser.parse(comment_dict['created_time'])
			if Comment.get_or_none(id) is None:
				question_id = comment_dict['question']['id']
				try:
					question = Question.get(id=question_id)
				except peewee.DoesNotExist:
					question_title = comment_dict['question']['title']
					question_url = "https://www.metaculus.com" + comment_dict['question']['url']
					question = Question.create(id=question_id, title=question_title, url=question_url)

				Comment.create(id=id, json=json.dumps(comment_dict),
							   submit_type=submit_type,
							   created_at=created_at,
							   question=question,
							   parent=parent)

	def tweet_comments(self):
		comments_to_tweet = Comment.select().where((Comment.tweeted == False)
												   & (Comment.submit_type == 'I')
												   & (Comment.created_at > self.START_DATE)
												   & (Comment.parent.is_null())
												   )

		print(f"Total comments in database: {Comment.select().count()}")
		print(f"Comments to tweet: {len(comments_to_tweet)}")
		for comment_db in comments_to_tweet:
			comment = json.loads(comment_db.json)
			html = comment['comment_html']
			tweet_text = self.generate_tweet_text(comment_db)
			try:
				self.create_tweet(tweet_text=tweet_text, html=html, comment_id=comment_db.id)
			except tweepy.errors.BadRequest as e:
				print(tweepy.errors.BadRequest, e)
			finally:
				comment_db.tweeted = True
				comment_db.save()


	def create_tweet(self, tweet_text, html, comment_id):
		if self.production:
			sleep(30)
			quoted_tweet = self.comment_references_one_tweet(html)
			if quoted_tweet:
				link, id = quoted_tweet
				tweet_response = client.create_tweet(text=tweet_text, quote_tweet_id=id)
			else:
				file_name = os.path.join(self.JPEG_PATH, str(comment_id) + ".png")
				self.generate_image(html, file_name)
				image_id = api.media_upload(filename=file_name).media_id
				tweet_response = client.create_tweet(text=tweet_text, media_ids=[image_id])
			print(f"\n\n{tweet_response}")
			return tweet_response
		else:
			print(f"\n\n{tweet_text}")
			return tweet_text


	def generate_tweet_text(self, comment):
		html = json.loads(comment.json)['comment_html']
		soup = BeautifulSoup(html, 'html.parser')
		a_tags = soup.find_all('a')

		if self.comment_references_one_tweet(html):
			soup.a.decompose()
			soup.get_text()
			tweet_lines = [soup.get_text()+'⬇️']

		else:
			tweet_lines = []
			emoji_numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
			link_description_max_len = 100 // len(a_tags)
			for i, a_tag in enumerate(a_tags):
				a_text = a_tag.text
				a_href = a_tag['href']
				if len(a_text) > link_description_max_len:
					a_text = a_text[:link_description_max_len] + "..."

				if len(a_tags) == 1:
					tweet_lines.append(f"🔗{a_text}: {a_href}")
				elif 1 < len(a_tags) < 10:
					tweet_lines.append(f"🔗{emoji_numbers[i]} {a_text}: {a_href}")
				else:
					tweet_lines.append(f"{a_text}: {a_href}")

		question_mark_emoji = "❓"
		question_line = f"{question_mark_emoji}{comment.question.title} {comment.question.url}"
		tweet_lines.append(question_line)

		return "\n".join(tweet_lines)

	def comment_references_one_tweet(self, html):
		if self.count_links(html) == 1:
			a_tags = BeautifulSoup(html, 'html.parser').find_all('a')
			a_tag = a_tags[0]
			a_href = a_tag['href']
			filter = r"https?://twitter\.com/\w+/status/(\d+)"
			matches = regex.findall(filter, a_href)
			if len(matches) == 1:
				return a_href, matches[0]
		return False

	def count_links(self, html):
		a_tags = BeautifulSoup(html, 'html.parser').find_all('a')
		return len(a_tags)

	def generate_image(self, html, file_name):
		# IMAGE
		format = 'png'
		zoom = 2
		width = 500 * zoom

		imgkit.from_string(html, file_name, options={
			'format': format,
			'zoom': zoom,
			'width': width,
			'--disable-smart-width':1,
		})