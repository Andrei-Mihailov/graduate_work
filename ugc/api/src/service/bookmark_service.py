from repository.bookmark_repository import BookmarkSQLAlchemyRepository
from sqlalchemy.orm import Session


class BookmarkService(BookmarkSQLAlchemyRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)


def get_bookmark_service(db: Session) -> BookmarkService:
    return BookmarkService(db)
