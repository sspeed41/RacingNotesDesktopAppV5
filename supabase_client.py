"""
Async Supabase client wrapper for the Racing Notes Desktop App V5.
Provides all database operations with error handling and retries.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
import os
from datetime import datetime, timedelta

from supabase import create_client, Client
from postgrest.exceptions import APIError
from loguru import logger

# Optional structlog import
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

from models import (
    Track, Series, Driver, Session, Note, Media, Tag, NoteTag,
    NoteWithDetails, NoteCreate, SearchFilters, PaginatedResponse,
    TrackTypeEnum, SessionTypeEnum, CategoryEnum, MediaTypeEnum
)


class SupabaseClient:
    """Async Supabase client with comprehensive error handling and retries."""

    def __init__(self, supabase_url: str, supabase_key: str, max_retries: int = 3):
        """Initialize the Supabase client."""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.max_retries = max_retries
        self.client: Optional[Client] = None
        self.logger = structlog.get_logger(__name__) if STRUCTLOG_AVAILABLE else logger
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Connection retry configuration
        self.retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
        
    async def initialize(self) -> None:
        """Initialize the Supabase client with retries."""
        for attempt in range(self.max_retries):
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                await self._test_connection()
                self.logger.info("Supabase client initialized successfully")
                return
            except Exception as e:
                self.logger.error(f"Failed to initialize Supabase client (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                else:
                    raise Exception(f"Failed to initialize Supabase client after {self.max_retries} attempts")

    async def _test_connection(self) -> None:
        """Test the database connection."""
        try:
            result = self.client.table("tracks").select("count").execute()
            self.logger.info("Database connection test successful")
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            raise

    async def _execute_with_retry(self, operation, *args, **kwargs) -> Any:
        """Execute a database operation with retry logic."""
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except APIError as e:
                self.logger.error(f"API error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                else:
                    raise

    # Track operations
    async def get_tracks(self) -> List[Track]:
        """Get all tracks."""
        try:
            result = self.client.table("tracks").select("*").order("name").execute()
            return [Track(**track) for track in result.data]
        except Exception as e:
            self.logger.error(f"Failed to get tracks: {e}")
            raise

    async def get_track_by_id(self, track_id: UUID) -> Optional[Track]:
        """Get a track by ID."""
        try:
            result = self.client.table("tracks").select("*").eq("id", str(track_id)).execute()
            if result.data:
                return Track(**result.data[0])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get track {track_id}: {e}")
            raise

    async def create_track(self, name: str, track_type: TrackTypeEnum) -> Track:
        """Create a new track."""
        try:
            result = self.client.table("tracks").insert({
                "name": name,
                "type": track_type.value
            }).execute()
            return Track(**result.data[0])
        except Exception as e:
            self.logger.error(f"Failed to create track: {e}")
            raise

    # Series operations
    async def get_series(self) -> List[Series]:
        """Get all series."""
        try:
            result = self.client.table("series").select("*").order("name").execute()
            return [Series(**series) for series in result.data]
        except Exception as e:
            self.logger.error(f"Failed to get series: {e}")
            raise

    async def get_series_by_id(self, series_id: UUID) -> Optional[Series]:
        """Get a series by ID."""
        try:
            result = self.client.table("series").select("*").eq("id", str(series_id)).execute()
            if result.data:
                return Series(**result.data[0])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get series {series_id}: {e}")
            raise

    async def create_series(self, name: str) -> Series:
        """Create a new series."""
        try:
            result = self.client.table("series").insert({
                "name": name
            }).execute()
            return Series(**result.data[0])
        except Exception as e:
            self.logger.error(f"Failed to create series: {e}")
            raise

    # Driver operations
    async def get_drivers(self, series_id: Optional[UUID] = None) -> List[Driver]:
        """Get drivers, optionally filtered by series."""
        try:
            query = self.client.table("drivers").select("*")
            if series_id:
                query = query.eq("series_id", str(series_id))
            result = query.order("name").execute()
            return [Driver(**driver) for driver in result.data]
        except Exception as e:
            self.logger.error(f"Failed to get drivers: {e}")
            raise

    async def get_driver_by_id(self, driver_id: UUID) -> Optional[Driver]:
        """Get a driver by ID."""
        try:
            result = self.client.table("drivers").select("*").eq("id", str(driver_id)).execute()
            if result.data:
                return Driver(**result.data[0])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get driver {driver_id}: {e}")
            raise

    async def create_driver(self, name: str, series_id: UUID) -> Driver:
        """Create a new driver."""
        try:
            result = self.client.table("drivers").insert({
                "name": name,
                "series_id": str(series_id)
            }).execute()
            return Driver(**result.data[0])
        except Exception as e:
            self.logger.error(f"Failed to create driver: {e}")
            raise

    # Session operations
    async def get_sessions(self, track_id: Optional[UUID] = None, 
                          series_id: Optional[UUID] = None,
                          session_type: Optional[SessionTypeEnum] = None,
                          date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None) -> List[Session]:
        """Get sessions with optional filters."""
        try:
            query = self.client.table("sessions").select("*")
            
            if track_id:
                query = query.eq("track_id", str(track_id))
            if series_id:
                query = query.eq("series_id", str(series_id))
            if session_type:
                query = query.eq("type", session_type.value)
            if date_from:
                query = query.gte("date", date_from.isoformat())
            if date_to:
                query = query.lte("date", date_to.isoformat())
                
            result = query.order("date", desc=True).execute()
            return [Session(**session) for session in result.data]
        except Exception as e:
            self.logger.error(f"Failed to get sessions: {e}")
            raise

    async def get_session_by_id(self, session_id: UUID) -> Optional[Session]:
        """Get a session by ID."""
        try:
            result = self.client.table("sessions").select("*").eq("id", str(session_id)).execute()
            if result.data:
                return Session(**result.data[0])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {e}")
            raise

    async def create_session(self, date: datetime, session_type: SessionTypeEnum, 
                           track_id: UUID, series_id: UUID) -> Session:
        """Create a new session."""
        try:
            result = self.client.table("sessions").insert({
                "date": date.isoformat(),
                "type": session_type.value,
                "track_id": str(track_id),
                "series_id": str(series_id)
            }).execute()
            return Session(**result.data[0])
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise

    # Tag operations
    async def get_tags(self, search_term: Optional[str] = None) -> List[Tag]:
        """Get tags with optional search."""
        try:
            query = self.client.table("tags").select("*")
            if search_term:
                query = query.ilike("label", f"%{search_term}%")
            result = query.order("label").execute()
            return [Tag(**tag) for tag in result.data]
        except Exception as e:
            self.logger.error(f"Failed to get tags: {e}")
            raise

    async def get_tag_by_id(self, tag_id: UUID) -> Optional[Tag]:
        """Get a tag by ID."""
        try:
            result = self.client.table("tags").select("*").eq("id", str(tag_id)).execute()
            if result.data:
                return Tag(**result.data[0])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get tag {tag_id}: {e}")
            raise

    async def create_tag(self, label: str) -> Tag:
        """Create a new tag."""
        try:
            result = self.client.table("tags").insert({
                "label": label.lower().strip()
            }).execute()
            return Tag(**result.data[0])
        except Exception as e:
            self.logger.error(f"Failed to create tag: {e}")
            raise

    async def get_or_create_tag(self, label: str) -> Tag:
        """Get existing tag or create new one."""
        try:
            # Try to find existing tag
            result = self.client.table("tags").select("*").eq("label", label.lower().strip()).execute()
            if result.data:
                return Tag(**result.data[0])
            
            # Create new tag if not found
            return await self.create_tag(label)
        except Exception as e:
            self.logger.error(f"Failed to get or create tag: {e}")
            raise

    # Note operations
    async def get_notes_feed(self, filters: Optional[SearchFilters] = None) -> PaginatedResponse:
        """Get notes feed with optional filters and pagination."""
        try:
            if not filters:
                filters = SearchFilters()

            query = self.client.table("notes_with_details").select("*")

            # Apply filters
            if filters.text_query:
                query = query.text_search("search_vector", filters.text_query)
            
            if filters.track_ids:
                query = query.in_("track_id", [str(tid) for tid in filters.track_ids])
            
            if filters.series_ids:
                query = query.in_("series_id", [str(sid) for sid in filters.series_ids])
            
            if filters.driver_ids:
                query = query.in_("driver_id", [str(did) for did in filters.driver_ids])
            
            if filters.categories:
                query = query.in_("category", [cat.value for cat in filters.categories])
            
            if filters.session_types:
                query = query.in_("session_type", [st.value for st in filters.session_types])
            
            if filters.date_from:
                query = query.gte("created_at", filters.date_from.isoformat())
            
            if filters.date_to:
                query = query.lte("created_at", filters.date_to.isoformat())
            
            if filters.shared_only:
                query = query.eq("shared", True)
            
            if filters.has_media is not None:
                if filters.has_media:
                    query = query.gt("media_count", 0)
                else:
                    query = query.eq("media_count", 0)

            # Get total count
            count_result = query.execute()
            total = len(count_result.data)

            # Apply pagination
            result = query.order("created_at", desc=True).range(
                filters.offset, filters.offset + filters.limit - 1
            ).execute()

            notes = [NoteWithDetails(**note) for note in result.data]
            
            return PaginatedResponse(
                items=notes,
                total=total,
                limit=filters.limit,
                offset=filters.offset,
                has_next=filters.offset + filters.limit < total,
                has_previous=filters.offset > 0
            )
        except Exception as e:
            self.logger.error(f"Failed to get notes feed: {e}")
            raise

    async def get_note_by_id(self, note_id: UUID) -> Optional[NoteWithDetails]:
        """Get a note by ID with all related data."""
        try:
            result = self.client.table("notes_with_details").select("*").eq("id", str(note_id)).execute()
            if result.data:
                return NoteWithDetails(**result.data[0])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get note {note_id}: {e}")
            raise

    async def create_note(self, note_data: NoteCreate) -> Note:
        """Create a new note with tags and media."""
        try:
            # Start transaction by creating the note first
            note_result = self.client.table("notes").insert({
                "body": note_data.body,
                "shared": note_data.shared,
                "driver_id": str(note_data.driver_id) if note_data.driver_id else None,
                "session_id": str(note_data.session_id) if note_data.session_id else None,
                "category": note_data.category.value
            }).execute()

            note = Note(**note_result.data[0])

            # Add tags if provided
            if note_data.tag_ids:
                for tag_id in note_data.tag_ids:
                    await self.create_note_tag(note.id, tag_id)

            # Refresh materialized view
            await self.refresh_materialized_view()

            return note
        except Exception as e:
            self.logger.error(f"Failed to create note: {e}")
            raise

    async def update_note(self, note_id: UUID, updates: Dict[str, Any]) -> Note:
        """Update a note."""
        try:
            result = self.client.table("notes").update(updates).eq("id", str(note_id)).execute()
            if result.data:
                await self.refresh_materialized_view()
                return Note(**result.data[0])
            raise Exception(f"Note {note_id} not found")
        except Exception as e:
            self.logger.error(f"Failed to update note {note_id}: {e}")
            raise

    async def delete_note(self, note_id: UUID) -> bool:
        """Delete a note."""
        try:
            result = self.client.table("notes").delete().eq("id", str(note_id)).execute()
            await self.refresh_materialized_view()
            return bool(result.data)
        except Exception as e:
            self.logger.error(f"Failed to delete note {note_id}: {e}")
            raise

    # Media operations
    async def create_media(self, note_id: UUID, file_url: str, media_type: MediaTypeEnum,
                          size_mb: float, filename: str) -> Media:
        """Create a new media record."""
        try:
            result = self.client.table("media").insert({
                "note_id": str(note_id),
                "file_url": file_url,
                "type": media_type.value,
                "size_mb": size_mb,
                "filename": filename
            }).execute()
            
            await self.refresh_materialized_view()
            return Media(**result.data[0])
        except Exception as e:
            self.logger.error(f"Failed to create media: {e}")
            raise

    async def get_media_by_note_id(self, note_id: UUID) -> List[Media]:
        """Get all media for a note."""
        try:
            result = self.client.table("media").select("*").eq("note_id", str(note_id)).execute()
            return [Media(**media) for media in result.data]
        except Exception as e:
            self.logger.error(f"Failed to get media for note {note_id}: {e}")
            raise

    async def delete_media(self, media_id: UUID) -> bool:
        """Delete a media record."""
        try:
            result = self.client.table("media").delete().eq("id", str(media_id)).execute()
            await self.refresh_materialized_view()
            return bool(result.data)
        except Exception as e:
            self.logger.error(f"Failed to delete media {media_id}: {e}")
            raise

    # Note-Tag operations
    async def create_note_tag(self, note_id: UUID, tag_id: UUID) -> NoteTag:
        """Create a note-tag relationship."""
        try:
            result = self.client.table("note_tags").insert({
                "note_id": str(note_id),
                "tag_id": str(tag_id)
            }).execute()
            return NoteTag(**result.data[0])
        except Exception as e:
            self.logger.error(f"Failed to create note-tag relationship: {e}")
            raise

    async def delete_note_tag(self, note_id: UUID, tag_id: UUID) -> bool:
        """Delete a note-tag relationship."""
        try:
            result = self.client.table("note_tags").delete().eq("note_id", str(note_id)).eq("tag_id", str(tag_id)).execute()
            return bool(result.data)
        except Exception as e:
            self.logger.error(f"Failed to delete note-tag relationship: {e}")
            raise

    # Utility operations
    async def refresh_materialized_view(self) -> None:
        """Refresh the materialized view for notes with details."""
        try:
            self.client.rpc("refresh_notes_with_details").execute()
        except Exception as e:
            self.logger.error(f"Failed to refresh materialized view: {e}")
            # Don't raise here as it's not critical for basic functionality

    async def get_popular_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular tags with usage count."""
        try:
            result = self.client.table("tags").select(
                "*, note_tags(count)"
            ).order("note_tags.count", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            self.logger.error(f"Failed to get popular tags: {e}")
            raise

    async def search_media(self, filters: Optional[SearchFilters] = None) -> List[Dict[str, Any]]:
        """Search media with filters."""
        try:
            if not filters:
                filters = SearchFilters()

            query = self.client.table("media_search").select("*")

            if filters.text_query:
                query = query.or_(
                    f"filename.ilike.%{filters.text_query}%,"
                    f"note_body.ilike.%{filters.text_query}%"
                )

            result = query.order("created_at", desc=True).limit(filters.limit).execute()
            return result.data
        except Exception as e:
            self.logger.error(f"Failed to search media: {e}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """Get application statistics."""
        try:
            stats = {}
            
            # Get counts
            notes_count = self.client.table("notes").select("count").execute()
            media_count = self.client.table("media").select("count").execute()
            tags_count = self.client.table("tags").select("count").execute()
            
            stats["notes_count"] = len(notes_count.data)
            stats["media_count"] = len(media_count.data)
            stats["tags_count"] = len(tags_count.data)
            
            # Get storage usage
            storage_result = self.client.table("media").select("sum(size_mb)").execute()
            stats["storage_usage_mb"] = storage_result.data[0].get("sum", 0) if storage_result.data else 0
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            raise


# Global client instance
supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get the global Supabase client instance and ensure it is initialized."""
    global supabase_client
    if supabase_client is None:
        try:
            # Try Streamlit secrets first
            import streamlit as st
            supabase_url = st.secrets["SUPABASE_URL"]
            supabase_key = st.secrets["SUPABASE_ANON_KEY"]
        except Exception:
            # Fall back to environment variables for local development
            supabase_url = os.getenv("SUPABASE_URL", "http://localhost:8000")
            supabase_key = os.getenv("SUPABASE_ANON_KEY", "demo-key")
        supabase_client = SupabaseClient(supabase_url, supabase_key)

    # Lazily initialize the underlying PostgREST client if it hasn't been done yet
    if supabase_client.client is None:
        try:
            import nest_asyncio, asyncio
            nest_asyncio.apply()
            asyncio.run(supabase_client.initialize())
        except RuntimeError:
            # Already inside an event loop (Streamlit runtime); use create_task workaround
            import asyncio
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                loop.run_until_complete(supabase_client.initialize())
            else:
                # Schedule initialization and wait briefly
                loop.create_task(supabase_client.initialize())

    return supabase_client


async def initialize_client() -> None:
    """Initialize the global Supabase client."""
    client = get_supabase_client()
    await client.initialize() 