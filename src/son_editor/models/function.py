import json
from json import JSONEncoder
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from son_editor.app.database import Base


class Function(Base):
    __tablename__ = 'function'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    vendor = Column(String(50))
    version = Column(String(50))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates="functions")
    descriptor = Column(Text())

    UniqueConstraint('project_id', 'name', 'vendor', 'version', name='uix_1')

    def __init__(self, name=None, project=None, version=None, vendor=None, descriptor=None):
        self.name = name
        self.vendor = vendor
        self.version = version
        self.descriptor = descriptor
        if project:
            self.project = project

    def __repr__(self):
        return '<Function {}>'.format(self.name)

    def as_dict(self):
        return {'id': self.id, 'name': self.name, 'descriptor': json.loads(self.descriptor)}


class FunctionEncoder(JSONEncoder):
    def default(self, o):
        return {'id': o.id, 'descriptor': o.descriptor}
