from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import  Column, Integer, String, Boolean, UUID
from settings import settings
 
postgres_database = settings.db_connection
engine = create_engine(postgres_database, echo=True)
 
class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "user"
    
    uuid = Column(UUID, primary_key=True)
    email = Column(String)
    is_active = Column(Boolean)
 
Base.metadata.create_all(bind=engine)
 
with Session(autoflush=False, bind=engine) as db:
    new_user = db.query(User).filter(User.uuid=="dd3bf13d-35b2-4eb9-a0b0-5b1cde1b58ed").first()
    if new_user is None:
        item = User(uuid="dd3bf13d-35b2-4eb9-a0b0-5b1cde1b58ed", email="42", is_active=True)
        db.add(item)
    else:
        new_user.is_active = False
        new_user.email = "42"

    db.commit() 
    # получаем один объект, у которого id=1
    # tom = db.query(User).filter(Person.id==1).first()
    # if (tom != None):
    #     print(f"{tom.id}.{tom.name} ({tom.age})")   
    #     # 1.Tom (38)
 
    #     # изменениям значения
    #     tom.name = "Tomas"
    #     tom.age = 22
 
    #     db.commit() # сохраняем изменения
 
    #     # проверяем, что изменения применены в бд - получаем один объект, у которого имя - Tomas
    #     tomas = db.query(Person).filter(Person.id == 1).first()
    #     print(f"{tomas.id}.{tomas.name} ({tomas.age})")    
    #     # 1.Tomas (22)