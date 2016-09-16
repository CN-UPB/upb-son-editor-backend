from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from son_editor.app.database import Base


class Repository(Base):
    __tablename__ = 'repository'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    url = Column(String(50))
    workspace_id = Column(Integer, ForeignKey('workspace.id'))

    def __init__(self, name=None, url=None, workspace=None):
        self.name = name
        self.url = url
        if workspace:
            self.workspace_id = workspace.id

    def __repr__(self):
        return '<Repository {}>'.format(self.name)

    def as_dict(self):
        return {'id': self.id, 'name': self.name, 'url': self.url}


class Catalogue(Repository):
    __tablename__ = 'catalogue'
    id = Column(Integer, ForeignKey('repository.id'), primary_key=True)
    workspace = relationship("Workspace", back_populates="catalogues")

    __mapper_args__ = {
        'polymorphic_identity': 'catalogue',
    }

    def __repr__(self):
        return '<Catalogue {}>'.format(self.name)


class Platform(Repository):
    __tablename__ = 'platform'
    id = Column(Integer, ForeignKey('repository.id'), primary_key=True)
    workspace = relationship("Workspace", back_populates="platforms")

    __mapper_args__ = {
        'polymorphic_identity': 'platform',
    }

    def __repr__(self):
        return '<Platform {}>'.format(self.name)
