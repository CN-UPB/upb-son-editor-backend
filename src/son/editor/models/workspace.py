from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from son.editor.app.database import Base
from . import project


class Workspace(Base):
    __tablename__ = 'workspace'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    path = Column(String(255), unique=True)
    project = relationship("Project", back_populates="workspace")

    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path

    def __repr__(self):
        return '<Workspace %r:%r>' % (self.name, self.path)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
