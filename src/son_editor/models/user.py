from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from son_editor.app.database import Base


class User(Base):
    """ The user model stores the username and his email that was registered at github.
    It is the root object for all data belonging to a user"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)
