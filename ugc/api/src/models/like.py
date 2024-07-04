from main import db


class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.String(128), nullable=False)
    is_like = db.Column(db.Boolean, nullable=False)
    like = db.Column(db.Integer, default=0)
    dislike = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Like movie_id={self.movie_id}, user_id={self.user_id}, like={self.like}, dislike={self.dislike}>"
