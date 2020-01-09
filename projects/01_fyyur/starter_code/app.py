# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
from sqlalchemy import types

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.PickleType, nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))
    show = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state} ' \
               f'{self.address} {self.phone} {self.image_link} ' \
               f'{self.facebook_link} {self.genres} ' \
               f'{self.seeking_talent} {self.seeking_description} ' \
               f'{self.website} {self.show}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.PickleType, nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))
    show = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} ' \
               f'{self.phone} {self.genres} {self.image_link} ' \
               f'{self.facebook_link}  ' \
               f'{self.seeking_venue} {self.seeking_description} ' \
               f'{self.website} {self.show}>'


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    start_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<{self.id} {self.venue_id} {self.artist_id} ' \
               f'{self.start_time}>'


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    venue_list = Venue.query.distinct('state', 'city').all()
    for venue in venue_list:
        venue_data = {
            "city": venue.city,
            "state": venue.state,
            "venues": Venue.query.filter_by(city=venue.city).all()
        }
        data.append(venue_data)

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():

    # Get the searched venue term
    search_venue_term = request.form.get('search_term', '')

    # Get all the venues from venue's table filtered by searched venue_term
    searched_venues_list = Venue.query.filter(Venue.name.ilike(f'%{search_venue_term}%')).all()

    # Get the found resorts count.
    venues_count = len(searched_venues_list)

    data = []
    for venue in searched_venues_list:
        data.append(venue)
        response = {
            "count": venues_count,
            "data": data
        }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.filter_by(id=venue_id).first()

    # Get the past show & artist details for the given venue.
    old_shows = Artist.query.with_entities(Artist.id, Artist.name, Artist.image_link, Show.start_time).\
        join(Show, Artist.id == Show.artist_id).\
        join(Venue, Venue.id == Show.venue_id).\
        filter(Venue.id == venue_id).\
        filter(Show.start_time < datetime.utcnow()).\
        all()

    p_shows = []
    for p_show in old_shows:
        prev_show = {
            "artist_id": p_show.id,
            "artist_name": p_show.name,
            "artist_image_link": p_show.image_link,
            "start_time": p_show.start_time.strftime("%d %b %Y %H:%M:%S.%f")
        }
        p_shows.append(prev_show)

    # Get the future show & artist details for the given venue.
    future_shows = Artist.query.with_entities(Artist.id, Artist.name, Artist.image_link, Show.start_time).\
        join(Show, Artist.id == Show.artist_id).\
        join(Venue, Venue.id == Show.venue_id).\
        filter(Venue.id == venue_id).\
        filter(Show.start_time >= datetime.utcnow()).\
        all()

    f_shows = []
    for f_show in future_shows:
        future_show = {
            "artist_id": f_show.id,
            "artist_name": f_show.name,
            "artist_image_link": f_show.image_link,
            "start_time": f_show.start_time.strftime("%d %b %Y %H:%M:%S.%f")
        }
        f_shows.append(future_show)

    # Get the upcoming shows count
    upcoming_shows_count = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.utcnow()).count()

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": p_shows,
        "upcoming_shows": f_shows,
        "past_shows_count": len(p_shows),
        "upcoming_shows_count": upcoming_shows_count
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        name = request.form.get('name', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        address = request.form.get('address', '')
        phone = request.form.get('phone', '')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link', '')
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                      facebook_link=facebook_link)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc.info)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if not error:
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue ' + venue_id + ' was successfully Deleted')
    except:
        error = True
        db.session.rollback()
        print(sys.exc.info)
        flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
    finally:
        db.session.close()
    if not error:
        return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_artist_term = request.form.get('search_term', '')
    searched_artist_list = Artist.query.filter(Artist.name.ilike(f'%{search_artist_term}%')).all()
    artist_count = len(searched_artist_list)
    data = []
    for artist in searched_artist_list:
        data.append(artist)
        response = {
            "count": artist_count,
            "data": data
        }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()

    old_shows = Venue.query.with_entities(Venue.id, Venue.name, Show.start_time).\
        join(Show,Venue.id == Show.venue_id).\
        join(Artist, Artist.id == Show.artist_id).\
        filter(Artist.id == artist_id).\
        filter(Show.start_time < datetime.utcnow()).all()

    p_shows = []

    for p_show in old_shows:
        prev_show = {
            "venue_id": p_show.id,
            "venue_name": p_show.name,
            "venue_image_link": p_show.image_link,
            "start_time": p_show.start_time.strftime("%d %b %Y %H:%M:%S.%f")
        }
        p_shows.append(prev_show)

    future_shows = Venue.query.with_entities(Venue.id, Venue.name, Venue.image_link, Show.start_time).\
        join(Show, Venue.id == Show.artist_id).\
        join(Artist, Artist.id == Show.venue_id).\
        filter(Artist.id == artist_id).\
        filter(Show.start_time > datetime.utcnow()).all()

    f_shows = []

    for f_show in future_shows:
        future_show = {
            "venue_id": f_show.id,
            "venue_name": f_show.name,
            "venue_image_link": f_show.image_link,
            "start_time": f_show.start_time.strftime("%d %b %Y %H:%M:%S.%f")
        }
        f_shows.append(future_show)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": p_shows,
        "upcoming_shows": f_shows,
        "past_shows_count": len(p_shows),
        "upcoming_shows_count": Show.query.filter(Show.artist_id == artist_id,Show.start_time > datetime.utcnow()).count()

    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        seeking_venue = request.form.get('seeking_venue')
        seeking_description = request.form.get('seeking_description')
        image_link = request.form.get('image_link')
        website = request.form.get('website')

        artist = Artist.query.get(artist_id)

        if name != artist.name:
            artist.name = name

        if city != artist.city:
            artist.city = city

        if state != artist.state:
            artist.state = state

        if genres != artist.genres:
            artist.genres = genres

        if phone != artist.phone:
            artist.phone = phone

        if facebook_link != artist.facebook_link:
            artist.facebook_link = facebook_link

        print(seeking_venue)

        if seeking_venue == 'Yes':
            artist.seeking_venue = True
            print('True')
        else:
            artist.seeking_venue = False
            print('False')

        if seeking_description != artist.seeking_description:
            artist.seeking_description = seeking_description

        if image_link != artist.image_link:
            artist.image_link = image_link

        if website != artist.website:
            artist.website = website

        db.session.commit()

        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc.info)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        seeking_talent = request.form.get('seeking_talent')
        seeking_description = request.form.get('seeking_description')
        image_link = request.form.get('image_link')
        website = request.form.get('website')

        venue = Venue.query.get(venue_id)

        if name != venue.name:
            venue.name = name

        if city != venue.city:
            venue.city = city

        if state != venue.state:
            venue.state = state

        if address != venue.address:
            venue.address = address

        if genres != venue.genres:
            venue.genres = genres

        if phone != venue.phone:
            venue.phone = phone

        if facebook_link != venue.facebook_link:
            venue.facebook_link = facebook_link

        if seeking_talent == "Yes":
            venue.seeking_talent = True
        else:
            venue.seeking_talent = False

        if seeking_description != venue.seeking_description:
            venue.seeking_description = seeking_description

        if image_link != venue.image_link:
            venue.image_link = image_link

        if website != venue.website:
            venue.website = website

        db.session.commit()

        flash('Venue ' + request.form['name'] + ' was successfully updated!')

    except:
        error = True
        db.session.rollback()
        # print(sys.exc.info)
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
    error = False
    try:
        name = request.form.get('name', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        phone = request.form.get('phone', '')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link', '')

        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                        facebook_link=facebook_link)

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc.info)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if not error:
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    shows = Show.query.all()
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        artist = Artist.query.filter_by(id=show.artist_id).first()
        data1 = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%d %b %Y %H:%M:%S.%f")
        }
        data.append(data1)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    try:
        artist_id = request.form.get('artist_id', '')
        venue_id = request.form.get('venue_id', '')
        start_time = request.form.get('start_time', '')
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    if not error:
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
