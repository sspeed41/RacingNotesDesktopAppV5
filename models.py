"""
Pydantic models for the Racing Notes Desktop App V5.
Defines data structures with validation for all entities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, ConfigDict


class TrackTypeEnum(str, Enum):
    """Track types for NASCAR racing."""
    SUPERSPEEDWAY = "Superspeedway"
    INTERMEDIATE = "Intermediate"
    SHORT_TRACK = "Short Track"
    ROAD_COURSE = "Road Course"


class SessionTypeEnum(str, Enum):
    """Session types for racing events."""
    PRACTICE = "Practice"
    QUALIFYING = "Qualifying"
    RACE = "Race"


class CategoryEnum(str, Enum):
    """Note categories for organization."""
    GENERAL = "General"
    TRACK_SPECIFIC = "Track Specific"
    STRATEGY = "Strategy"
    OTHER = "Other"


class MediaTypeEnum(str, Enum):
    """Media file types."""
    IMAGE = "image"
    VIDEO = "video"


class Track(BaseModel):
    """Track model for racing venues."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=255)
    type: TrackTypeEnum
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('name')
    def validate_name(cls, v):
        """Validate track name."""
        if not v.strip():
            raise ValueError("Track name cannot be empty")
        return v.strip()


class Series(BaseModel):
    """Series model for racing series."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('name')
    def validate_name(cls, v):
        """Validate series name."""
        if not v.strip():
            raise ValueError("Series name cannot be empty")
        return v.strip()


class Driver(BaseModel):
    """Driver model for racing drivers."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=255)
    series_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('name')
    def validate_name(cls, v):
        """Validate driver name."""
        if not v.strip():
            raise ValueError("Driver name cannot be empty")
        return v.strip()


class Session(BaseModel):
    """Session model for racing sessions."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    date: datetime
    type: SessionTypeEnum
    track_id: UUID
    series_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Tag(BaseModel):
    """Tag model for note categorization."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    label: str = Field(..., min_length=1, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('label')
    def validate_label(cls, v):
        """Validate tag label."""
        if not v.strip():
            raise ValueError("Tag label cannot be empty")
        return v.strip().lower()


class Note(BaseModel):
    """Note model for racing notes."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    body: str = Field(..., min_length=1, max_length=5000)
    shared: bool = Field(default=False)
    driver_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    category: CategoryEnum = Field(default=CategoryEnum.GENERAL)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('body')
    def validate_body(cls, v):
        """Validate note body."""
        if not v.strip():
            raise ValueError("Note body cannot be empty")
        return v.strip()


class Media(BaseModel):
    """Media model for note attachments."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    note_id: UUID
    file_url: str = Field(..., min_length=1)
    type: MediaTypeEnum
    size_mb: float = Field(..., ge=0)
    filename: str = Field(..., min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('file_url')
    def validate_file_url(cls, v):
        """Validate file URL."""
        if not v.strip():
            raise ValueError("File URL cannot be empty")
        return v.strip()

    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename."""
        if not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()


class NoteTag(BaseModel):
    """Junction model for note-tag relationships."""
    model_config = ConfigDict(from_attributes=True)
    
    note_id: UUID
    tag_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Enhanced models with relationships for UI display
class NoteWithDetails(Note):
    """Note model with joined relationship data."""
    driver_name: Optional[str] = None
    session_type: Optional[SessionTypeEnum] = None
    session_date: Optional[datetime] = None
    track_name: Optional[str] = None
    track_type: Optional[TrackTypeEnum] = None
    series_name: Optional[str] = None
    tags: List[Tag] = Field(default_factory=list)
    media: List[Media] = Field(default_factory=list)
    likes_count: int = Field(default=0)
    replies_count: int = Field(default=0)


class MediaUpload(BaseModel):
    """Model for media upload requests."""
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1)
    size_bytes: int = Field(..., ge=0)
    data: bytes

    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename for upload."""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi'}
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"File type not supported. Allowed: {', '.join(allowed_extensions)}")
        return v.strip()

    @validator('size_bytes')
    def validate_size(cls, v):
        """Validate file size (max 100MB)."""
        max_size = 100 * 1024 * 1024  # 100MB in bytes
        if v > max_size:
            raise ValueError(f"File too large. Maximum size: {max_size / (1024*1024):.0f}MB")
        return v


class NoteCreate(BaseModel):
    """Model for creating new notes."""
    body: str = Field(..., min_length=1, max_length=5000)
    shared: bool = Field(default=False)
    driver_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    category: CategoryEnum = Field(default=CategoryEnum.GENERAL)
    tag_ids: List[UUID] = Field(default_factory=list)
    media_files: List[MediaUpload] = Field(default_factory=list)

    @validator('body')
    def validate_body(cls, v):
        """Validate note body."""
        if not v.strip():
            raise ValueError("Note body cannot be empty")
        return v.strip()


class SearchFilters(BaseModel):
    """Model for search and filter parameters."""
    text_query: Optional[str] = None
    track_ids: List[UUID] = Field(default_factory=list)
    series_ids: List[UUID] = Field(default_factory=list)
    driver_ids: List[UUID] = Field(default_factory=list)
    tag_ids: List[UUID] = Field(default_factory=list)
    categories: List[CategoryEnum] = Field(default_factory=list)
    session_types: List[SessionTypeEnum] = Field(default_factory=list)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    shared_only: bool = Field(default=False)
    has_media: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    items: List[BaseModel]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool 