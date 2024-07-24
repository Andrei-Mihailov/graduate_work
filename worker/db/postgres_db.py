from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import  Column, String, Boolean, UUID
from core.settings import settings
 
postgres_database = settings.db_connection
engine = create_engine(postgres_database, echo=True)
 
class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "user"
    
    uuid = Column(UUID, primary_key=True)
    email = Column(String)
    is_active = Column(Boolean)
 
Base.metadata.create_all(bind=engine)

def check_user(uuid: str, email: str, is_active: bool):
    with Session(autoflush=False, bind=engine) as db:
        new_user = db.query(User).filter(User.uuid==uuid).first()
        if new_user is None:
            item = User(uuid=uuid, email=email, is_active=is_active)
            db.add(item)
        else:
            new_user.is_active = is_active
            new_user.email = email

        db.commit() 