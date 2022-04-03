import tweepy
from os import environ
from dotenv import load_dotenv

load_dotenv()

client = tweepy.Client(
   bearer_token=environ.get("BEARER"),
   access_token=environ.get("ACCESS_TOKEN"),
   access_token_secret=environ.get("ACCESS_TOKEN_SECRET"),
   consumer_key= environ.get("API_KEY"),
   consumer_secret=environ.get("API_KEY_SECRET"),
)

auth = tweepy.OAuth1UserHandler(
   access_token=environ.get("ACCESS_TOKEN"),
   access_token_secret=environ.get("ACCESS_TOKEN_SECRET"),
   consumer_key=environ.get("API_KEY"),
   consumer_secret=environ.get("API_KEY_SECRET"),
)
api = tweepy.API(auth=auth)

