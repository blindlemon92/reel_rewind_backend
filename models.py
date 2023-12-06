from app import db


class User(db.Model):
    id = db.Column(db.String(100), unique=True, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    img = db.Column(db.String(200), nullable=True)
    region = db.Column(db.Integer, nullable=True)
    collection = db.relationship("CollectionItem", backref="user", lazy=True)

    def __init__(self, id, username, email, img, region):
        self.id = id
        self.username = username
        self.email = email
        self.img = img
        self.region = region

    def __repr__(self):
        return f'<User"{self.username}">'


class CollectionItem(db.Model):
    movie_id = db.Column(db.String(100), unique=True, primary_key=True)
    movie_title = db.Column(db.String(100), unique=True)
    movie_year = db.Column(
        db.String(100),
    )
    actors = db.Column(
        db.ARRAY(db.String(100)),
    )
    img = db.Column(db.String(200), nullable=True)
    genre = db.Column(db.String(200), nullable=True)
    user_score = db.Column(db.String(3), nullable=True)
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"), nullable=False)

    def __init__(
        self, movie_id, movie_title, movie_year, actors, img, genre, user_score, user_id
    ):
        self.movie_id = movie_id
        self.movie_title = movie_title
        self.movie_year = movie_year
        self.actors = actors
        self.img = img
        self.genre = genre
        self.user_score = user_score
        self.user_id = user_id

    def __repr__(self):
        return f"Collection {self.id}"
