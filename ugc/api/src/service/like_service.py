from repository.like_repository import LikeSQLAlchemyRepository
from sqlalchemy.orm import Session


class LikeService(LikeSQLAlchemyRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)
