import peewee

db = peewee.SqliteDatabase('sqlite.db')

class BaseModel(peewee.Model):
    class Meta:
        database = db


class Question(BaseModel):
    title = peewee.TextField()
    url = peewee.TextField()

class Comment(BaseModel):
    json = peewee.TextField()
    tweeted = peewee.BooleanField(default=False)
    submit_type = peewee.TextField()
    created_at = peewee.DateTimeField()
    question = peewee.ForeignKeyField(Question)
    parent = peewee.TextField(null=True)



if not db.table_exists(Comment):
    db.create_tables([Comment])

if not db.table_exists(Question):
    db.create_tables([Question])