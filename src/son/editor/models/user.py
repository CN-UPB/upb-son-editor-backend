from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from son.editor.app.database import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    workspaces = relationship("Workspace", back_populates="owner")


    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)
