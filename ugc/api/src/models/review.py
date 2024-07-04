from main import db


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.String(128), nullable=False)
    review = db.Column(db.String(1024), nullable=False)

    def __repr__(self):
        return f"<Review movie_id={self.movie_id}, user_id={self.user_id}, review={self.review}>"
