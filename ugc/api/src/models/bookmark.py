from main import db


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    user_id = db.Column(
        db.String(128), nullable=False
    )  # Assuming bookmarks are user-specific

    def __repr__(self):
        return f"<Bookmark title={self.title}, url={self.url}, user_id={self.user_id}>"
