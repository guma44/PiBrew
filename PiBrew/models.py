import datetime
from flask import url_for
from PiBrew import db

class Step(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=255, required=True)
    span = db.IntField(required=True)

class Recipe(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    steps = db.ListField(db.EmbeddedDocumentField('Step'))

    def get_absolute_url(self):
        return url_for('post', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.name

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-name']
     }



