from models.review import Review
from sqlalchemy.orm import Session


class ReviewSQLAlchemyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self):
        return self.db.query(Review).all()

    def add_review(self, movie_id: str, user_id: str, review: str):
        new_review = Review(movie_id=movie_id, user_id=user_id, review=review)
        self.db.add(new_review)
        self.db.commit()
        self.db.refresh(new_review)
        return new_review
