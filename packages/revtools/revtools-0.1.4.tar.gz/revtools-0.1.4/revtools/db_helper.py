from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from . import Base, engine

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a Session
session = Session()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

def create_tables():
    try:
        Base.metadata.create_all(engine)
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")

def add_user(name, age):
    try:
        new_user = User(name=name, age=age)
        session.add(new_user)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error adding user: {e}")

def get_users():
    try:
        return session.query(User).all()
    except SQLAlchemyError as e:
        print(f"Error retrieving users: {e}")
        return []

def delete_user(user_id):
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error deleting user: {e}")
