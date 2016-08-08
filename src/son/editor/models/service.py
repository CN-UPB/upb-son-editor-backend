from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from son.editor.app.database import Base


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates="services")

    def __init__(self, name=None, project=None):
        self.name = name
        if project:
            self.project_id = project.id

    def __repr__(self):
        return '<Service %r:%r>' % (self.name, self.path)
