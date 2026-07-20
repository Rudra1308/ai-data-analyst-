import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    row_count = Column(Integer, nullable=True)
    col_count = Column(Integer, nullable=True)
    schema_json = Column(JSON, nullable=True)  # Infers types & headers
    profile_json = Column(JSON, nullable=True)  # General descriptive stats, null counts, cardinalities
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project = relationship("Project", back_populates="datasets")
