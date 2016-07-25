from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from son.editor.app.database import Base


class Workspace(Base):
    __tablename__ = 'workspaces'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    path = Column(String(255), unique=True)
    projects = relationship("Project", back_populates="workspaces")

    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path

    def __repr__(self):
        return '<Workspace %r:%r>' % (self.name, self.path)
