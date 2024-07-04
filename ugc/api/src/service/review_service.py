from repository.review_repository import ReviewSQLAlchemyRepository
from sqlalchemy.orm import Session


class ReviewService(ReviewSQLAlchemyRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)
