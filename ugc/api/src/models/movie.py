from main import db


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    like_count = db.Column(db.Integer, default=0)
    dislike_count = db.Column(db.Integer, default=0)
