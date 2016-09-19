from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from son_editor.app.database import Base


class Workspace(Base):
    __tablename__ = 'workspace'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    path = Column(String(255), unique=True)
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    catalogues = relationship("Catalogue", back_populates="workspace", cascade="all, delete-orphan")
    platforms = relationship("Platform", back_populates="workspace", cascade="all, delete-orphan")
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship("User", back_populates="workspaces")

    UniqueConstraint('owner_id', 'name', name='uix_1')

    def __init__(self, name=None, path=None, owner=None):
        self.name = name
        self.path = path
        self.owner = owner

    def __repr__(self):
        return '<Workspace %r:%r>' % (self.name, self.path)

    def as_dict(self):
        return {"id": self.id, "name": self.name, "path": self.path,
                "catalogues": list(map(lambda x: x.as_dict(), self.catalogues)),
                "platforms": list(map(lambda x: x.as_dict(), self.platforms))}