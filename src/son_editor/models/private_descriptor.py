import json
from json import JSONEncoder
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from son_editor.app.database import Base


class PrivateDescriptor(Base):
    """The private descriptor is the model for the 
    service and function descriptors in the private catalogue"""

    __tablename__ = 'private_descriptor'
    id = Column(Integer, ForeignKey('base_descriptor.id'), primary_key=True)
    ws_id = Column(Integer, ForeignKey('workspace.id'))
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    vendor = Column(String(50))
    version = Column(String(50))
    uid = Column(String(150))
    descriptor = Column(Text())

    UniqueConstraint('ws_id', 'uid', name='uix_1')

    def __init__(self, ws_id=None, name=None, version=None, vendor=None, descriptor=None):
        self.name = name
        self.vendor = vendor
        self.version = version
        self.descriptor = descriptor
        self.ws_id = ws_id
        if self.name and self.vendor and self.version:
            self.uid = "{}:{}:{}".format(self.vendor, self.name, self.version)

    def as_dict(self):
        return {'id': self.id, 'name': self.name, 'vendor': self.vendor, 'version': self.version, 'uid': self.uid,
                'descriptor': json.loads(self.descriptor)}


class PrivateFunction(PrivateDescriptor):
    """The Private function is the Model for the 
    Function descriptors in the private catalogue"""
    __tablename__ = 'private_function'
    id = Column(Integer, ForeignKey('private_descriptor.id'), primary_key=True)
    workspace = relationship("Workspace", back_populates="priv_functions")
    __mapper_args__ = {
        'polymorphic_identity': 'private_function',
    }


class PrivateService(PrivateDescriptor):
    """The Private service is the Model for the 
    Service descriptors in the private catalogue"""

    __tablename__ = 'private_service'
    id = Column(Integer, ForeignKey('private_descriptor.id'), primary_key=True)
    workspace = relationship("Workspace", back_populates="priv_services")
    __mapper_args__ = {
        'polymorphic_identity': 'private_service',
    }
