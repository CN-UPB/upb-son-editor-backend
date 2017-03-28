import json
from json import JSONEncoder
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from son_editor.app.database import Base


class Descriptor(Base):
    """
    The Base class for storing the function and the service descriptors.
    Both descriptors share the properties name, vendor and version 
    and are constrained to have a unique uid inside of a project
    """

    __tablename__ = 'descriptor'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    vendor = Column(String(50))
    version = Column(String(50))
    uid = Column(String(150))
    project_id = Column(Integer, ForeignKey('project.id'))
    descriptor = Column(Text())

    UniqueConstraint('project_id', 'uid', name='uix_1')

    def __init__(self, name=None, version=None, vendor=None, descriptor=None):
        self.name = name
        self.vendor = vendor
        self.version = version
        self.descriptor = descriptor
        if self.name and self.vendor and self.version:
            self.uid = "{}:{}:{}".format(self.vendor, self.name, self.version)

    def __repr__(self):
        return '<Descriptor {}>'.format(self.uid)

    def as_dict(self):
        return {'id': self.id, 'uid': self.uid,
                'descriptor': json.loads(self.descriptor)}


class Function(Descriptor):
    """The Model for the function Descriptor"""

    __tablename__ = 'function'
    id = Column(Integer, ForeignKey('descriptor.id'), primary_key=True)
    project = relationship("Project", back_populates="functions")

    def __init__(self, name=None, version=None, vendor=None, descriptor=None, project=None):
        super(Function, self).__init__(name, version, vendor, descriptor)
        if project:
            self.project = project

    __mapper_args__ = {
        'polymorphic_identity': 'function',
    }

    def __repr__(self):
        return '<Function {}>'.format(self.uid)


class Service(Descriptor):
    """ The Model for the service descriptor additionally contains 
    a meta property that can hold arbitrary meta-data about the service"""

    __tablename__ = 'service'
    id = Column(Integer, ForeignKey('descriptor.id'), primary_key=True)
    project = relationship("Project", back_populates="services")
    meta = Column(Text())

    def __init__(self, name=None, version=None, vendor=None, descriptor=None, project=None, meta="{}"):
        super(Service, self).__init__(name, version, vendor, descriptor)
        if project:
            self.project = project

        self.meta = meta

    __mapper_args__ = {
        'polymorphic_identity': 'service',
    }

    def __repr__(self):
        return '<Service {}>'.format(self.uid)

    def as_dict(self):
        result = super().as_dict()
        result["meta"] = json.loads(self.meta)
        return result
