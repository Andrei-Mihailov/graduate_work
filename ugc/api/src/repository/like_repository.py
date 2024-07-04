from models.like import Like
from sqlalchemy.orm import Session


class LikeSQLAlchemyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self):
        return self.db.query(Like).all()

    def add_like(self, user_id: str, item_id: str):
        like = Like(user_id=user_id, item_id=item_id)
        self.db.add(like)
        self.db.commit()
        self.db.refresh(like)
        return like
