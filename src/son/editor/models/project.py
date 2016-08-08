from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from son.editor.models.service import Service
from son.editor.models.workspace import Workspace

from son.editor.app.database import Base


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    rel_path = Column(String(255), unique=True)
    workspace_id = Column(Integer, ForeignKey('workspace.id'))
    workspace = relationship("Workspace", back_populates="project")
    service = relationship("Service", back_populates="project")

    def __init__(self, name=None, rel_path=None):
        self.name = name
        self.rel_path = rel_path

    def __repr__(self):
        return '<Project %r>' % (self.name)
