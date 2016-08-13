from json import JSONEncoder
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from son.editor.app.database import Base


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    vendor = Column(String(50))
    version = Column(String(50))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates="services")

    def __init__(self, name=None, project=None, version=None, vendor=None):
        self.name = name
        self.vendor = vendor
        self.version = version
        if project:
            self.project_id = project.id

    def __repr__(self):
        return '<Service %r>' % (self.name)

class ServiceEncoder(JSONEncoder):
    def default(self,o):
        return {'id' : o.id, 'name' : o.name}