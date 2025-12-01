from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()  # Reads from .env file

app = Flask(__name__)

# Using SQLite for student simplicity
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rockbands-mm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'SECRET'

db = SQLAlchemy(app)

# ==========================
# DATABASE MODELS
# ==========================

band_albums = db.Table('band_albums',
    db.Column('BandID', db.Integer, db.ForeignKey('bands.BandID'), primary_key=True),
    db.Column('AlbumID', db.Integer, db.ForeignKey('albums.AlbumID'), primary_key=True)
)

class Bands(db.Model):
    BandID = db.Column(db.Integer, primary_key=True)
    BandName = db.Column(db.String(80), nullable=False)
    FormedYear = db.Column(db.Integer)
    HomeLocation = db.Column(db.String(80))
    # Relationship: One band has many members + albums
    # members = db.relationship('Members', backref='band', lazy=True)
    memberships = db.relationship('Memberships', backref='band', lazy=True)
    songs = db.relationship('Songs', backref='band', lazy=True)
    albums = db.relationship('Albums', secondary=band_albums, back_populates='bands', lazy='subquery')


class Members(db.Model):
    MemberID = db.Column(db.Integer, primary_key=True)
    # BandID = db.Column(db.Integer, db.ForeignKey('bands.BandID'), nullable=False)
    MemberName = db.Column(db.String(80), nullable=False)
    MainPosition = db.Column(db.String(80))
    memberships = db.relationship('Memberships', backref='member', lazy=True)
    song_memberships = db.relationship('SongMembers', back_populates='member', lazy=True)


class Memberships(db.Model):
    MembershipID = db.Column(db.Integer, primary_key=True)
    BandID = db.Column(db.Integer, db.ForeignKey('bands.BandID'), nullable=False)
    MemberID = db.Column(db.Integer, db.ForeignKey('members.MemberID'), nullable=False)
    StartYear = db.Column(db.Integer)
    EndYear = db.Column(db.Integer)
    Role = db.Column(db.Text)


class Albums(db.Model):
    AlbumID = db.Column(db.Integer, primary_key=True)
    AlbumTitle = db.Column(db.String(80), nullable=False)
    ReleaseYear = db.Column(db.Integer)
    songs = db.relationship('Songs', backref='album', lazy=True)
    bands = db.relationship('Bands', secondary=band_albums, back_populates='albums', lazy='subquery')

class Songs(db.Model):
    SongID = db.Column(db.Integer, primary_key=True)
    BandID = db.Column(db.Integer, db.ForeignKey('bands.BandID'), nullable=False) 
    AlbumID = db.Column(db.Integer, db.ForeignKey('albums.AlbumID'), nullable=False)
    Song_title = db.Column(db.String(80), nullable=False)
    Release_Type = db.Column(db.String(5), nullable=False)
    MediaFormat = db.Column(db.String(12), nullable=False)
    SongReleaseYear = db.Column(db.Integer, nullable=False)
    song_members = db.relationship('SongMembers', back_populates='song', lazy=True)

class SongMembers(db.Model):
    SongMemberID = db.Column(db.Integer, primary_key=True)
    SongID = db.Column(db.Integer, db.ForeignKey('songs.SongID'), nullable=False)
    MemberID = db.Column(db.Integer, db.ForeignKey('members.MemberID'), nullable=False)
    Role = db.Column(db.String(80), nullable=False)
    song = db.relationship('Songs', back_populates='song_members')
    member = db.relationship('Members', back_populates='song_memberships')



# ==========================
# ROUTES
# ==========================


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bands/add', methods=['GET', 'POST'])
def add_band():
    if request.method == 'POST':
        new_band = Bands(
            BandName=request.form['bandname'],
            FormedYear=request.form['formedyear'],
            HomeLocation=request.form['homelocation']
        )
        db.session.add(new_band)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_band.html')


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    bands = Bands.query.all()  # Students see querying with relationships
    if request.method == 'POST':
        new_member = Members(
            MemberName=request.form['membername'],
            MainPosition=request.form['mainposition']
            # BandID=request.form['bandid']
        )
        db.session.add(new_member)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_member.html', bands=bands)


@app.route('/albums/add', methods=['GET', 'POST'])
def add_album():
    bands = Bands.query.all()
    if request.method == 'POST':
        new_album = Albums(
            AlbumTitle=request.form['albumtitle'],
            ReleaseYear=request.form['releaseyear'],
            
        )

        selected_band_ids = request.form.getlist('bandid')
        if selected_band_ids:
            selected_bands = Bands.query.filter(Bands.BandID.in_(selected_band_ids)).all()
            new_album.bands.extend(selected_bands)
    
        db.session.add(new_album)
        db.session.commit()
        flash('Album added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('add_album.html', bands=bands)


@app.route('/song/add', methods= ['GET', 'POST'])
def add_song():
    bands = Bands.query.all()

    if request.method == 'POST':
        new_song = Songs(
            Song_title=request.form['songtitle'],
            BandID=request.form['bandid'],
            AlbumID=request.form['albumid'],
            Release_Type=request.form['releasetype'],
            MediaFormat=request.form['mediarelease'],
            SongReleaseYear=request.form['songreleaseyear']
        )
        db.session.add(new_song)
        db.session.commit()
        flash('Song added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('add_song.html', bands=bands)

@app.route('/get_albums/<int:band_id>')
def get_albums(band_id):
    albums = Albums.query.filter_by(BandID=band_id).all()
    return {'albums': [{'id':a.AlbumID, 'title':a.AlbumTitle} for a in albums]}

@app.route('/songmember/add', methods=['GET', 'POST'])
def add_songmember():
    songs = Songs.query.all()
    members = Members.query.all()

    if request.method == 'POST':
        new_songmember = SongMembers(
            SongID=request.form['songid'],
            MemberID=request.form['memberid'],
            Role=request.form['role']
        )
        db.session.add(new_songmember)
        db.session.commit()
        flash('Member added to song', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_songmember.html', songs=songs, members=members)


@app.route('/bands/view')
def view_by_band():
    bands = Bands.query.all()
    return render_template('display_by_band.html', bands=bands)


@app.route('/bands/view/<int:id>')
def view_band(id):
    # Shows real database relationship querying
    band = Bands.query.get_or_404(id)
    return render_template('display_by_band.html', bands=[band])


@app.route('/memberships/add', methods=['GET', 'POST'])
def add_membership():
    bands = Bands.query.all()
    members = Members.query.all()
    if request.method == 'POST':
        membership = Memberships(
            BandID=request.form.get('bandid'),
            MemberID=request.form.get('memberid'),
            Role=request.form.get('role'),
            StartYear=request.form.get('startyear') or None,
            EndYear=request.form.get('endyear') or None
        )
        db.session.add(membership)
        db.session.commit()
        flash('Membership assigned', 'success')
        return redirect(url_for('view_by_band'))
    return render_template('add_membership.html', bands=bands, members=members)



@app.route('/memberships/edit/<int:id>', methods=['GET', 'POST'])
def edit_membership(id):
    membership = Memberships.query.get_or_404(id)
    bands = Bands.query.all()
    members = Members.query.all()
    if request.method == 'POST':
        membership.BandID = request.form.get('bandid')
        membership.MemberID = request.form.get('memberid')
        membership.Role = request.form.get('role')
        membership.StartYear = request.form.get('startyear') or None
        membership.EndYear = request.form.get('endyear') or None
        db.session.commit()
        flash('Membership updates', 'success')
        return redirect(url_for('view_by_band'))

    return render_template('edit_membership.html', membership=membership, bands=bands, members=members)


@app.route('/memberships/delete/<int:id>')
def delete_membership(id):
    membership = Memberships.query.get_or_404(id)
    db.session.delete(membership)
    db.session.commit()
    flash('Membership removed', 'success')
    return redirect(url_for('view_by_band'))

@app.route('/album/<int:id>')
def view_album(id):
    album = Albums.query.get_or_404(id)
    all_albums = Albums.query.all()
    songs = album.songs
    member_ids = {sm.member.MemberID for song in songs for sm in song.song_members}
    members = Members.query.filter(Members.MemberID.in_(member_ids)).all()
    return render_template('display_by_album.html', album=album, songs=songs, members=members, all_albums=all_albums)


@app.route('/member/<int:id>')
def view_member(id):
    member = Members.query.get_or_404(id)
    all_members = Members.query.all()
    song_links = member.song_memberships
    songs = [sm.song for sm in song_links]
    album_ids = {s.AlbumID for s in songs}
    albums = Albums.query.filter(Albums.AlbumID.in_(album_ids)).all()

    return render_template('display_by_member.html', member=member, songs=songs, albums=albums, all_members=all_members)


@app.route('/song/<int:id>')
def view_song(id):
    song = Songs.query.get_or_404(id)
    all_songs = Songs.query.all()
    song_members = song.song_members
    members = [sm.member for sm in song_members]

    album = song.album
    bands = album.bands if album else []

    return render_template('view_song.html', song=song, members=members, album=album, bands=bands, all_songs=all_songs)


@app.route('/admin/data')
def manage_data():
    bands = Bands.query.all()
    members = Members.query.all()
    albums = Albums.query.all()
    songs = Songs.query.all()
    memberships = Memberships.query.all()
    song_members = SongMembers.query.all()
    return render_template('manage_data.html', bands=bands, members=members, albums=albums, songs=songs, memberships=memberships, song_members=song_members)

# Create DB if not exists
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
