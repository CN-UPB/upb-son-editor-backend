from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from son_editor.app.database import Base


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    vendor = Column(String(50))
    version = Column(String(50))
    uid = Column(String(150), unique=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates="services")
    descriptor = Column(Text())

    def __init__(self, name=None, project=None, version=None, vendor=None, descriptor=None):
        self.name = name
        self.vendor = vendor
        self.version = version
        self.uid = "{}:{}:{}".format(vendor, name, version)
        self.descriptor = descriptor
        if project:
            self.project = project

    def __repr__(self):
        return '<Service {}>'.format(self.name)

    def as_dict(self):
        return {'id': self.id, 'name': self.name, 'vendor': self.vendor, 'version': self.version, 'uid': self.uid}
