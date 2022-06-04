
#----------------------------------------------------------------------------#
# Imports
from pyrsistent import v
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from models import Artist, Show, Venue, config_db
import sys
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = config_db(app)

# connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# instatiate migration
migrate = Migrate(app, db)

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


@app.route('/venues')
def venues():

  # query all venues from Venue table grouped by city and state
  venue_areas = (db.session.query(Venue.city, Venue.state)
                .group_by(Venue.city, Venue.state).all())
  
  data = []
  # iterate through each venue from venue_areas and add the datas
  for area in venue_areas:
    
    data.append(
      {
        "city": area[0],
        "state": area[1],
        "venues": []
        }
    )
    # getting all the venues from the same city and state
    venues = db.session.query(Venue.id,Venue.name,
      Venue.upcoming_shows_count).filter(Venue.city==area[0],Venue.state==area[1]).all()

    # adding all the venues from the same city and state
    for venue in venues:
      data[-1]["venues"].append(
        {
              "id": venue[0],
              "name": venue[1],
              "num_upcoming_shows":venue[2]
              }
      )
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search_results = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response = {
    "count": len(search_results),
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": venue.upcoming_shows_count
      } for venue in search_results]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  #  replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)

  shows = venue.shows
  past_shows = []
  upcoming_shows = []
  for show in shows:
    show_info = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    if(show.upcoming):
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }


  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # : insert form data as a new Venue record in the db, instead
  # : modify data to be the data object returned from db insertion
  venue = VenueForm(request.form)
  name = venue.name.data
  city = venue.city.data
  state = venue.state.data
  address = venue.address.data
  phone = venue.phone.data
  facebook_link = venue.facebook_link.data
  image_link = venue.image_link.data
  website_link = venue.website_link.data
  genres = venue.genres.data
  seeking_talent = venue.seeking_talent.data
  seeking_description = venue.seeking_description.data
  
  new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link, image_link=image_link, website_link=website_link, genres=genres, seeking_talent=seeking_talent, seeking_description=seeking_description)
  
  try:
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  
  # on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    print("================== ERROR MSG ======================")
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  print("==================detele message =================")
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = []
  # query all artist table with id and name
  artists = db.session.query(Artist.id, Artist.name).all()
  # append each artist to the data list
  for artist in artists:
    data.append(
      {
        "id": artist.id,
        "name": artist.name,
      }
    )
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # : implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # query artist table with name filter by strings that include search terms
  search_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response = {
    "count": len(search_results),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(artist.shows),
    } for artist in search_results]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # replace with real artist data from the artist table, using artist_id

  # query artist table with id
  artist = Artist.query.get(artist_id)
  shows = artist.shows
  past_shows = []
  upcoming_shows = []
  for show in shows:
    show_info = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    if(show.upcoming):
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres, 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # artist = Artist.query.get(artist_id)

  artist = Artist.query.get(artist_id)
  artist = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }


  #  populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.facebook_link = form.facebook_link.data
  artist.image_link = form.image_link.data
  artist.website_link = form.website_link.data
  artist.genres = form.genres.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data
  try:
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  #  take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.phone = form.phone.data
  venue.facebook_link = form.facebook_link.data
  venue.image_link = form.image_link.data
  venue.website_link = form.website_link.data
  venue.genres = form.genres.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data
  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion

  artist = ArtistForm(request.form)
  name = artist.name.data
  city = artist.city.data
  state = artist.state.data
  phone = artist.phone.data
  facebook_link = artist.facebook_link.data
  image_link = artist.image_link.data
  website_link = artist.website_link.data
  genres = artist.genres.data
  seeking_venue = artist.seeking_venue.data
  seeking_description = artist.seeking_description.data

  new_artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link, image_link=image_link, website_link=website_link, genres=genres, seeking_venue=seeking_venue, seeking_description=seeking_description)
  
  try:
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    print("================== ArtistForm ERROR MSG ======================")
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  shows = (db.session.query(Show.venue_id, Show.artist_id, Show.start_time).all())
  # get Artist and Venue data of shows using foreign key
  
  
  for show in shows:
      # get artist and venue data using the relationship between
      # Show and Artist and Venue
      artist_name = db.session.query(Artist.name).filter(Artist.id == show.artist_id).first()[0]
      venue_name = db.session.query(Venue.name).filter(Venue.id == show.venue_id).first()[0]
      artist_image_link = db.session.query(Artist.image_link).filter(Artist.id == show.artist_id).first()[0]
      # change time format as in the sample data given.
      start_time = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
      data.append({
        "venue_id": show.venue_id,
        "venue_name": venue_name,
        "artist_id": show.artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": start_time
      })  
      
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  show = ShowForm(request.form)
  artist_id = show.artist_id.data
  venue_id = show.venue_id.data
  start_time = show.start_time.data

  new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
  try:
    db.session.add(new_show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print("================== ShowForm ERROR MSG ======================")
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
