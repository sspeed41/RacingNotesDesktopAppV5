"""
Unit tests for the Racing Notes Desktop App V5.
Tests all core functionality including database operations, media handling, and utilities.
"""

import asyncio
import io
import os
import tempfile
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

import pytest
import pandas as pd
from PIL import Image
from faker import Faker

from models import (
    Track, Series, Driver, Session, Note, Media, Tag, NoteTag,
    NoteWithDetails, NoteCreate, SearchFilters, MediaUpload,
    TrackTypeEnum, SessionTypeEnum, CategoryEnum, MediaTypeEnum
)
from supabase_client import SupabaseClient
from storage_service import StorageService
from utils import (
    TimeUtils, CacheUtils, ValidationUtils, TextUtils, FormatUtils,
    ExportUtils, UIUtils, AsyncUtils
)


# Test fixtures
@pytest.fixture
def faker():
    """Faker instance for generating test data."""
    return Faker()


@pytest.fixture
def sample_track():
    """Sample track for testing."""
    return Track(
        name="Test Speedway",
        type=TrackTypeEnum.INTERMEDIATE
    )


@pytest.fixture
def sample_series():
    """Sample series for testing."""
    return Series(name="Test Series")


@pytest.fixture
def sample_driver(sample_series):
    """Sample driver for testing."""
    return Driver(
        name="Test Driver",
        series_id=sample_series.id
    )


@pytest.fixture
def sample_session(sample_track, sample_series):
    """Sample session for testing."""
    return Session(
        date=datetime.now(),
        type=SessionTypeEnum.PRACTICE,
        track_id=sample_track.id,
        series_id=sample_series.id
    )


@pytest.fixture
def sample_note(sample_driver, sample_session):
    """Sample note for testing."""
    return Note(
        body="This is a test note about racing.",
        driver_id=sample_driver.id,
        session_id=sample_session.id,
        category=CategoryEnum.GENERAL
    )


@pytest.fixture
def sample_tag():
    """Sample tag for testing."""
    return Tag(label="test-tag")


@pytest.fixture
def sample_media_upload():
    """Sample media upload for testing."""
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return MediaUpload(
        filename="test_image.jpg",
        content_type="image/jpeg",
        size_bytes=len(img_bytes.getvalue()),
        data=img_bytes.getvalue()
    )


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    with patch('supabase_client.create_client') as mock_create:
        mock_client = Mock()
        mock_create.return_value = mock_client
        
        # Mock table operations
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        
        # Mock storage operations
        mock_storage = Mock()
        mock_client.storage = mock_storage
        
        yield mock_client


class TestModels:
    """Test Pydantic models."""
    
    def test_track_creation(self, sample_track):
        """Test track model creation and validation."""
        assert sample_track.name == "Test Speedway"
        assert sample_track.type == TrackTypeEnum.INTERMEDIATE
        assert isinstance(sample_track.id, uuid.UUID)
        assert isinstance(sample_track.created_at, datetime)
    
    def test_track_validation(self):
        """Test track model validation."""
        with pytest.raises(ValueError):
            Track(name="", type=TrackTypeEnum.INTERMEDIATE)
    
    def test_series_creation(self, sample_series):
        """Test series model creation."""
        assert sample_series.name == "Test Series"
        assert isinstance(sample_series.id, uuid.UUID)
    
    def test_driver_creation(self, sample_driver, sample_series):
        """Test driver model creation."""
        assert sample_driver.name == "Test Driver"
        assert sample_driver.series_id == sample_series.id
    
    def test_note_creation(self, sample_note):
        """Test note model creation."""
        assert sample_note.body == "This is a test note about racing."
        assert sample_note.category == CategoryEnum.GENERAL
        assert isinstance(sample_note.id, uuid.UUID)
    
    def test_note_validation(self):
        """Test note model validation."""
        with pytest.raises(ValueError):
            Note(body="", category=CategoryEnum.GENERAL)
    
    def test_media_upload_validation(self):
        """Test media upload validation."""
        # Test valid file
        media = MediaUpload(
            filename="test.jpg",
            content_type="image/jpeg",
            size_bytes=1024,
            data=b"fake image data"
        )
        assert media.filename == "test.jpg"
        
        # Test invalid file type
        with pytest.raises(ValueError):
            MediaUpload(
                filename="test.txt",
                content_type="text/plain",
                size_bytes=1024,
                data=b"fake data"
            )
        
        # Test file too large
        with pytest.raises(ValueError):
            MediaUpload(
                filename="test.jpg",
                content_type="image/jpeg",
                size_bytes=200 * 1024 * 1024,  # 200MB
                data=b"fake data"
            )
    
    def test_search_filters(self):
        """Test search filters model."""
        filters = SearchFilters(
            text_query="test",
            limit=10,
            offset=0
        )
        assert filters.text_query == "test"
        assert filters.limit == 10
        assert filters.offset == 0
    
    def test_note_create_model(self, faker):
        """Test note creation model."""
        note_data = NoteCreate(
            body=faker.text(),
            category=CategoryEnum.STRATEGY,
            shared=True
        )
        assert len(note_data.body) > 0
        assert note_data.category == CategoryEnum.STRATEGY
        assert note_data.shared is True


class TestSupabaseClient:
    """Test Supabase client operations."""
    
    @pytest.fixture
    def client(self, mock_supabase_client):
        """Create SupabaseClient instance for testing."""
        return SupabaseClient("http://test", "test-key")
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, client, mock_supabase_client):
        """Test client initialization."""
        # Mock successful connection test
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = Mock(data=[])
        
        await client.initialize()
        assert client.client is not None
    
    @pytest.mark.asyncio
    async def test_get_tracks(self, client, mock_supabase_client):
        """Test getting tracks."""
        # Mock response
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "test-id",
                "name": "Test Track",
                "type": "Intermediate",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        client.client = mock_supabase_client
        tracks = await client.get_tracks()
        
        assert len(tracks) == 1
        assert tracks[0].name == "Test Track"
    
    @pytest.mark.asyncio
    async def test_create_note(self, client, mock_supabase_client):
        """Test creating a note."""
        note_data = NoteCreate(
            body="Test note",
            category=CategoryEnum.GENERAL
        )
        
        # Mock response
        mock_response = Mock()
        mock_response.data = [{
            "id": "test-id",
            "body": "Test note",
            "category": "General",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "shared": False,
            "driver_id": None,
            "session_id": None
        }]
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        client.client = mock_supabase_client
        note = await client.create_note(note_data)
        
        assert note.body == "Test note"
        assert note.category == CategoryEnum.GENERAL
    
    @pytest.mark.asyncio
    async def test_search_notes(self, client, mock_supabase_client):
        """Test searching notes."""
        filters = SearchFilters(text_query="test", limit=10)
        
        # Mock response
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "test-id",
                "body": "Test note with test keyword",
                "category": "General",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "shared": False,
                "driver_id": None,
                "session_id": None,
                "driver_name": None,
                "session_type": None,
                "session_date": None,
                "track_name": None,
                "track_type": None,
                "series_name": None,
                "tags": [],
                "media": [],
                "likes_count": 0,
                "replies_count": 0
            }
        ]
        
        # Mock the complex query chain
        mock_query = Mock()
        mock_query.text_search.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        mock_supabase_client.table.return_value.select.return_value = mock_query
        
        client.client = mock_supabase_client
        result = await client.get_notes_feed(filters)
        
        assert len(result.items) == 1
        assert "test" in result.items[0].body
    
    @pytest.mark.asyncio
    async def test_retry_logic(self, client, mock_supabase_client):
        """Test retry logic on failures."""
        # Mock initial failures followed by success
        mock_supabase_client.table.return_value.select.side_effect = [
            Exception("Connection failed"),
            Exception("Connection failed"),
            Mock(data=[])
        ]
        
        client.client = mock_supabase_client
        
        # Should succeed after retries
        await client._execute_with_retry(lambda: mock_supabase_client.table().select())


class TestStorageService:
    """Test storage service operations."""
    
    @pytest.fixture
    def storage_service(self):
        """Create StorageService instance for testing."""
        return StorageService()
    
    @pytest.mark.asyncio
    async def test_image_compression(self, storage_service, sample_media_upload):
        """Test image compression."""
        compressed_data, new_filename = await storage_service.compress_image(
            sample_media_upload.data,
            sample_media_upload.filename
        )
        
        assert len(compressed_data) > 0
        assert len(compressed_data) <= len(sample_media_upload.data)
        assert new_filename.endswith('.jpg')
    
    @pytest.mark.asyncio
    async def test_video_compression(self, storage_service):
        """Test video compression."""
        # Create a minimal video file for testing
        # This would require ffmpeg and more complex setup
        # For now, we'll skip this test
        pytest.skip("Video compression test requires ffmpeg setup")
    
    @pytest.mark.asyncio
    async def test_media_validation(self, storage_service):
        """Test media file validation."""
        # Valid image file
        is_valid, message = storage_service.validate_media_file("test.jpg", 1024)
        assert is_valid is True
        assert message == "Valid"
        
        # Invalid file type
        is_valid, message = storage_service.validate_media_file("test.txt", 1024)
        assert is_valid is False
        assert "Unsupported file type" in message
        
        # File too large
        is_valid, message = storage_service.validate_media_file("test.jpg", 200 * 1024 * 1024)
        assert is_valid is False
        assert "File too large" in message
    
    @pytest.mark.asyncio
    async def test_get_media_info(self, storage_service, sample_media_upload):
        """Test getting media information."""
        info = await storage_service.get_media_info(
            sample_media_upload.data,
            sample_media_upload.filename
        )
        
        assert info["filename"] == sample_media_upload.filename
        assert info["type"] == "image"
        assert info["size_bytes"] == len(sample_media_upload.data)
        assert "width" in info
        assert "height" in info
    
    @pytest.mark.asyncio
    async def test_thumbnail_generation(self, storage_service, sample_media_upload):
        """Test thumbnail generation."""
        thumbnail_data = await storage_service.generate_thumbnail(
            sample_media_upload.data,
            size=(50, 50)
        )
        
        assert len(thumbnail_data) > 0
        assert len(thumbnail_data) < len(sample_media_upload.data)
        
        # Verify it's a valid image
        thumbnail_img = Image.open(io.BytesIO(thumbnail_data))
        assert thumbnail_img.size[0] <= 50
        assert thumbnail_img.size[1] <= 50


class TestUtils:
    """Test utility functions."""
    
    def test_time_utils(self):
        """Test time utility functions."""
        # Test humanize_datetime
        now = datetime.utcnow()
        assert TimeUtils.humanize_datetime(now) == "Just now"
        
        one_hour_ago = now - timedelta(hours=1)
        assert "1 hour ago" in TimeUtils.humanize_datetime(one_hour_ago)
        
        one_day_ago = now - timedelta(days=1)
        assert "1 day ago" in TimeUtils.humanize_datetime(one_day_ago)
        
        # Test format_duration
        assert TimeUtils.format_duration(30) == "30.0s"
        assert TimeUtils.format_duration(90) == "1m 30s"
        assert TimeUtils.format_duration(3660) == "1h 1m"
        
        # Test parse_date_string
        date_str = "2024-01-01T12:00:00Z"
        parsed = TimeUtils.parse_date_string(date_str)
        assert parsed is not None
        assert parsed.year == 2024
    
    def test_validation_utils(self):
        """Test validation utility functions."""
        # Test validate_uuid
        valid_uuid = str(uuid.uuid4())
        assert ValidationUtils.validate_uuid(valid_uuid) is True
        assert ValidationUtils.validate_uuid("invalid-uuid") is False
        
        # Test validate_file_size
        is_valid, message = ValidationUtils.validate_file_size(1024)
        assert is_valid is True
        assert message == "Valid"
        
        is_valid, message = ValidationUtils.validate_file_size(200 * 1024 * 1024)
        assert is_valid is False
        assert "File too large" in message
        
        # Test validate_media_type
        is_valid, message = ValidationUtils.validate_media_type("test.jpg")
        assert is_valid is True
        
        is_valid, message = ValidationUtils.validate_media_type("test.txt")
        assert is_valid is False
        
        # Test sanitize_filename
        filename = ValidationUtils.sanitize_filename("test<>file.jpg")
        assert "<" not in filename
        assert ">" not in filename
        assert filename.endswith(".jpg")
    
    def test_text_utils(self):
        """Test text utility functions."""
        # Test extract_hashtags
        text = "This is a #test note with #hashtags and #racing content"
        hashtags = TextUtils.extract_hashtags(text)
        assert "test" in hashtags
        assert "hashtags" in hashtags
        assert "racing" in hashtags
        
        # Test extract_mentions
        text = "Hey @driver1 and @driver2, great race!"
        mentions = TextUtils.extract_mentions(text)
        assert "driver1" in mentions
        assert "driver2" in mentions
        
        # Test suggest_tags
        text = "Great restart by the leader after the caution. Pit strategy was key."
        suggestions = TextUtils.suggest_tags(text)
        assert "restart" in suggestions
        assert "caution" in suggestions
        assert "pit" in suggestions
        assert "strategy" in suggestions
        
        # Test truncate_text
        long_text = "This is a very long text that needs to be truncated"
        truncated = TextUtils.truncate_text(long_text, 20)
        assert len(truncated) <= 23  # 20 + "..."
        assert truncated.endswith("...")
    
    def test_format_utils(self):
        """Test format utility functions."""
        # Test format_file_size
        assert FormatUtils.format_file_size(0) == "0 B"
        assert FormatUtils.format_file_size(1024) == "1.0 KB"
        assert FormatUtils.format_file_size(1024 * 1024) == "1.0 MB"
        assert FormatUtils.format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        
        # Test format_number
        assert FormatUtils.format_number(500) == "500"
        assert FormatUtils.format_number(1500) == "1.5K"
        assert FormatUtils.format_number(1500000) == "1.5M"
        assert FormatUtils.format_number(1500000000) == "1.5B"
        
        # Test format_percentage
        assert FormatUtils.format_percentage(25, 100) == "25.0%"
        assert FormatUtils.format_percentage(0, 100) == "0.0%"
        assert FormatUtils.format_percentage(100, 100) == "100.0%"
        assert FormatUtils.format_percentage(0, 0) == "0%"
    
    def test_export_utils(self):
        """Test export utility functions."""
        # Test data
        data = [
            {"id": 1, "name": "Test 1", "value": 100},
            {"id": 2, "name": "Test 2", "value": 200}
        ]
        
        # Test CSV export
        csv_data = ExportUtils.export_to_csv(data, "test.csv")
        assert b"id,name,value" in csv_data
        assert b"Test 1" in csv_data
        assert b"Test 2" in csv_data
        
        # Test JSON export
        json_data = ExportUtils.export_to_json(data, "test.json")
        assert b'"id": 1' in json_data
        assert b'"name": "Test 1"' in json_data
    
    @pytest.mark.asyncio
    async def test_async_utils(self):
        """Test async utility functions."""
        # Test run_with_timeout
        async def quick_task():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await AsyncUtils.run_with_timeout(quick_task(), timeout=1.0)
        assert result == "success"
        
        # Test timeout
        async def slow_task():
            await asyncio.sleep(2)
            return "too slow"
        
        with pytest.raises(asyncio.TimeoutError):
            await AsyncUtils.run_with_timeout(slow_task(), timeout=0.5)
        
        # Test batch_process
        items = [1, 2, 3, 4, 5]
        
        async def process_item(item):
            return item * 2
        
        results = await AsyncUtils.batch_process(items, batch_size=2, process_func=process_item)
        assert results == [2, 4, 6, 8, 10]


class TestCacheUtils:
    """Test cache utility functions."""
    
    def setup_method(self):
        """Set up test environment."""
        # Mock streamlit session state
        self.mock_session_state = {}
        
        with patch('streamlit.session_state', self.mock_session_state):
            pass
    
    def test_cache_operations(self):
        """Test cache operations."""
        with patch('streamlit.session_state', self.mock_session_state):
            # Test cache_data
            CacheUtils.cache_data("test_key", "test_value", ttl=3600)
            assert "cache" in self.mock_session_state
            assert "test_key" in self.mock_session_state["cache"]
            
            # Test get_cached_data
            cached_value = CacheUtils.get_cached_data("test_key")
            assert cached_value == "test_value"
            
            # Test cache miss
            missing_value = CacheUtils.get_cached_data("missing_key")
            assert missing_value is None
            
            # Test clear_cache
            CacheUtils.clear_cache()
            assert len(self.mock_session_state.get("cache", {})) == 0
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key = CacheUtils.get_cache_key("prefix", "arg1", "arg2")
        assert key.startswith("prefix_")
        assert "arg1" in key
        assert "arg2" in key
        
        # Test with long arguments
        long_arg = "a" * 200
        key = CacheUtils.get_cache_key("prefix", long_arg)
        assert len(key) <= 150  # Should be hashed


class TestIntegration:
    """Integration tests for the complete application."""
    
    @pytest.mark.asyncio
    async def test_note_creation_workflow(self, mock_supabase_client):
        """Test complete note creation workflow."""
        # This would test the entire flow from UI to database
        # For now, we'll create a simplified version
        
        # Mock dependencies
        client = SupabaseClient("http://test", "test-key")
        client.client = mock_supabase_client
        
        # Mock responses
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[{
                "id": "test-id",
                "body": "Test note",
                "category": "General",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "shared": False,
                "driver_id": None,
                "session_id": None
            }]
        )
        
        # Create note
        note_data = NoteCreate(
            body="Test note",
            category=CategoryEnum.GENERAL
        )
        
        note = await client.create_note(note_data)
        assert note.body == "Test note"
    
    @pytest.mark.asyncio
    async def test_media_upload_workflow(self, sample_media_upload):
        """Test complete media upload workflow."""
        storage_service = StorageService()
        
        # Mock the upload process
        with patch.object(storage_service, 'upload_media_with_retry') as mock_upload:
            mock_upload.return_value = ("http://test.com/image.jpg", 0.5)
            
            # Process media
            public_url, size_mb, filename = await storage_service.process_and_upload_media(
                sample_media_upload
            )
            
            assert public_url.startswith("http://")
            assert size_mb > 0
            assert filename.endswith('.jpg')
    
    def test_search_and_filter_integration(self):
        """Test search and filter integration."""
        # Test that search filters work correctly
        filters = SearchFilters(
            text_query="racing",
            categories=[CategoryEnum.STRATEGY],
            limit=10
        )
        
        assert filters.text_query == "racing"
        assert CategoryEnum.STRATEGY in filters.categories
        assert filters.limit == 10


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 