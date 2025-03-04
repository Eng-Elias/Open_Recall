from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

# Junction table for Screenshots and Tags (many-to-many)
screenshot_tags = Table(
    'screenshot_tags',
    Base.metadata,
    Column('screenshot_id', Integer, ForeignKey('screenshots.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Column('tagged_at', DateTime, default=datetime.now(timezone.utc))
)

class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), index=True)
    app_name = Column(String, index=True)
    window_title = Column(String)
    extracted_text = Column(Text)
    confidence_score = Column(Float)
    is_favorite = Column(Boolean, default=False)
    notes = Column(Text)
    summary = Column(Text)

    # Relationship with Tags
    tags = relationship("Tag", 
                       secondary=screenshot_tags,
                       back_populates="screenshots",
                       cascade="save-update")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'timestamp': self.timestamp.isoformat(),
            'app_name': self.app_name,
            'window_title': self.window_title,
            'extracted_text': self.extracted_text,
            'confidence_score': self.confidence_score,
            'is_favorite': self.is_favorite,
            'notes': self.notes,
            'summary': self.summary,
            'tags': [tag.to_dict() for tag in self.tags]
        }

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    is_auto_generated = Column(Boolean, default=False)

    # Relationship with Screenshots
    screenshots = relationship("Screenshot",
                             secondary=screenshot_tags,
                             back_populates="tags",
                             cascade="all, delete")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'is_auto_generated': self.is_auto_generated
        }
