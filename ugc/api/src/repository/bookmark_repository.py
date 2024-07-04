import sentry_sdk
from models.bookmark import Bookmark
from sqlalchemy.orm import Session


class BookmarkSQLAlchemyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self):
        try:
            return self.db.query(Bookmark).all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e

    def add_bookmark(self, title: str, url: str, user_id: str):
        try:
            new_bookmark = Bookmark(title=title, url=url, user_id=user_id)
            self.db.add(new_bookmark)
            self.db.commit()
            self.db.refresh(new_bookmark)
            return new_bookmark
        except Exception as e:
            self.db.rollback()
            sentry_sdk.capture_exception(e)
            raise e

    def create(self, data: dict):
        try:
            movie_id = data.get("movie_id")
            user_id = data.get("user_id")
            new_bookmark = Bookmark(movie_id=movie_id, user_id=user_id)
            self.db.add(new_bookmark)
            self.db.commit()
            self.db.refresh(new_bookmark)
            return new_bookmark
        except Exception as e:
            self.db.rollback()
            sentry_sdk.capture_exception(e)
            raise e

    def get_by_movie_id_and_user_id(self, movie_id: str, user_id: str):
        try:
            return self.db.query(Bookmark).filter_by(movie_id=movie_id, user_id=user_id).first()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e

    def delete(self, bookmark: Bookmark):
        try:
            self.db.delete(bookmark)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            sentry_sdk.capture_exception(e)
            raise e
