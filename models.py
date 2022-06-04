
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# configure the database to the app and return the database
def config_db(app):

    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    return db


class Artist(db.Model):
    """An artist model """
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.PickleType, default=[])
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))

    # add missing columns from the starter code with migration
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    upcoming_shows_count = db.Column(db.Integer, default = 0)
    past_shows_count = db.Column(db.Integer, default = 0)
    shows = db.relationship('Show', backref='artist', cascade="save-update, merge, delete")



class Venue(db.Model):
    """A venue model """
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))

    # add missing columns from the starter code with migration
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1000))
    genres = db.Column(db.PickleType, default=[])
    upcoming_shows_count = db.Column(db.Integer, default = 0)
    past_shows_count = db.Column(db.Integer, default = 0)
    shows = db.relationship('Show', backref='venue', cascade="save-update, merge, delete")

    # : implement any missing fields, as a database migration using Flask-Migrate


    #  implement any missing fields, as a database migration using Flask-Migrate


#  Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    upcoming = db.Column(db.Boolean, default=True)

