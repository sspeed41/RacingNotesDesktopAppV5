"""
Storage service for the Racing Notes Desktop App V5.
Handles media compression, upload, and download with retry logic.
"""

import asyncio
import io
import os
import tempfile
import uuid
from typing import Optional, Tuple, List, Dict, Any, BinaryIO
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps, ExifTags
from loguru import logger

# Optional imports
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

try:
    import pillow_heif
    PILLOW_HEIF_AVAILABLE = True
except ImportError:
    PILLOW_HEIF_AVAILABLE = False

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

# Optional moviepy import for video processing
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    VideoFileClip = None
    MOVIEPY_AVAILABLE = False

from supabase_client import get_supabase_client
from models import MediaTypeEnum, MediaUpload


class StorageService:
    """Media storage service with compression and retry logic."""

    def __init__(self, max_retries: int = 5):
        """Initialize the storage service."""
        self.max_retries = max_retries
        self.logger = logger
        
        # Image compression settings
        self.image_max_width = 1920
        self.image_max_height = 1080
        self.image_quality = 85
        self.image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.heic', '.heif'}
        
        # Video compression settings
        self.video_max_width = 1280
        self.video_max_height = 720
        self.video_bitrate = "1M"
        self.video_formats = {'.mp4', '.mov', '.avi', '.m4v'}
        
        # File size limits
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_compressed_image_size = 10 * 1024 * 1024  # 10MB
        self.max_compressed_video_size = 50 * 1024 * 1024  # 50MB
        
        # Retry configuration
        self.retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
        
        # Enable HEIF support
        if PILLOW_HEIF_AVAILABLE:
            pillow_heif.register_heif_opener()

    async def compress_image(self, image_data: bytes, filename: str) -> Tuple[bytes, str]:
        """Compress an image with optimization."""
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Auto-rotate based on EXIF data
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                
                if hasattr(image, '_getexif'):
                    exif = image._getexif()
                    if exif is not None:
                        orientation_value = exif.get(orientation)
                        if orientation_value:
                            image = ImageOps.exif_transpose(image)
            except Exception as e:
                self.logger.warning(f"Failed to process EXIF data: {e}")
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if needed
            if image.width > self.image_max_width or image.height > self.image_max_height:
                image.thumbnail((self.image_max_width, self.image_max_height), Image.Resampling.LANCZOS)
            
            # Compress and save
            output = io.BytesIO()
            
            # Determine format
            original_format = image.format
            if original_format in ('HEIC', 'HEIF') or filename.lower().endswith(('.heic', '.heif')):
                # Convert HEIC/HEIF to JPEG
                image.save(output, format='JPEG', quality=self.image_quality, optimize=True)
                new_filename = Path(filename).with_suffix('.jpg').name
            elif original_format == 'PNG' and len(image_data) > 2 * 1024 * 1024:  # Convert large PNGs to JPEG
                image.save(output, format='JPEG', quality=self.image_quality, optimize=True)
                new_filename = Path(filename).with_suffix('.jpg').name
            else:
                # Keep original format
                format_name = 'JPEG' if original_format == 'JPEG' else original_format
                if format_name == 'JPEG':
                    image.save(output, format=format_name, quality=self.image_quality, optimize=True)
                else:
                    image.save(output, format=format_name, optimize=True)
                new_filename = filename
            
            compressed_data = output.getvalue()
            
            # Check if compression was effective
            if len(compressed_data) > self.max_compressed_image_size:
                # Try more aggressive compression
                output = io.BytesIO()
                quality = max(50, self.image_quality - 20)
                image.save(output, format='JPEG', quality=quality, optimize=True)
                compressed_data = output.getvalue()
                new_filename = Path(filename).with_suffix('.jpg').name
            
            self.logger.info(f"Image compressed: {len(image_data)} -> {len(compressed_data)} bytes")
            return compressed_data, new_filename
            
        except Exception as e:
            self.logger.error(f"Failed to compress image: {e}")
            raise

    async def compress_video(self, video_data: bytes, filename: str) -> Tuple[bytes, str]:
        """Compress a video with optimization."""
        if not MOVIEPY_AVAILABLE:
            # If moviepy is not available, return the original video data
            self.logger.warning("MoviePy not available, returning original video data")
            return video_data, filename
            
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as input_file:
                input_file.write(video_data)
                input_path = input_file.name
            
            output_path = tempfile.mktemp(suffix='.mp4')
            
            try:
                # Load video
                video = VideoFileClip(input_path)
                
                # Get video info
                duration = video.duration
                width, height = video.size
                fps = video.fps
                
                # Calculate compression settings
                target_width = min(width, self.video_max_width)
                target_height = min(height, self.video_max_height)
                
                # Maintain aspect ratio
                aspect_ratio = width / height
                if target_width / target_height > aspect_ratio:
                    target_width = int(target_height * aspect_ratio)
                else:
                    target_height = int(target_width / aspect_ratio)
                
                # Ensure dimensions are even (required for some codecs)
                target_width = target_width if target_width % 2 == 0 else target_width - 1
                target_height = target_height if target_height % 2 == 0 else target_height - 1
                
                # Resize video
                if width > self.video_max_width or height > self.video_max_height:
                    video = video.resize((target_width, target_height))
                
                # Reduce frame rate if too high
                if fps > 30:
                    video = video.set_fps(30)
                
                # Write compressed video
                video.write_videofile(
                    output_path,
                    codec='libx264',
                    bitrate=self.video_bitrate,
                    temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                    remove_temp=True,
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
                
                video.close()
                
                # Read compressed video
                with open(output_path, 'rb') as f:
                    compressed_data = f.read()
                
                # Check if compression was effective
                if len(compressed_data) > self.max_compressed_video_size:
                    # Try more aggressive compression
                    if not MOVIEPY_AVAILABLE:
                        self.logger.warning("MoviePy not available, cannot perform aggressive compression")
                        return compressed_data, Path(filename).with_suffix('.mp4').name
                    video = VideoFileClip(input_path)
                    
                    # Further reduce quality
                    if width > 854 or height > 480:  # Reduce to 480p
                        target_width = min(854, int(480 * aspect_ratio))
                        target_height = min(480, int(854 / aspect_ratio))
                        target_width = target_width if target_width % 2 == 0 else target_width - 1
                        target_height = target_height if target_height % 2 == 0 else target_height - 1
                        video = video.resize((target_width, target_height))
                    
                    video.write_videofile(
                        output_path,
                        codec='libx264',
                        bitrate="500k",  # More aggressive bitrate
                        temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                        remove_temp=True,
                        audio_codec='aac',
                        verbose=False,
                        logger=None
                    )
                    
                    video.close()
                    
                    with open(output_path, 'rb') as f:
                        compressed_data = f.read()
                
                new_filename = Path(filename).with_suffix('.mp4').name
                
                self.logger.info(f"Video compressed: {len(video_data)} -> {len(compressed_data)} bytes")
                return compressed_data, new_filename
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(input_path)
                    os.unlink(output_path)
                except Exception:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Failed to compress video: {e}")
            raise

    async def upload_media_with_retry(self, file_data: bytes, filename: str, 
                                    content_type: str) -> Tuple[str, float]:
        """Upload media to Supabase storage with retry logic."""
        for attempt in range(self.max_retries):
            try:
                return await self._upload_media(file_data, filename, content_type)
            except Exception as e:
                self.logger.error(f"Upload attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                else:
                    raise Exception(f"Failed to upload after {self.max_retries} attempts: {e}")

    async def _upload_media(self, file_data: bytes, filename: str, 
                          content_type: str) -> Tuple[str, float]:
        """Upload media to Supabase storage."""
        try:
            client = get_supabase_client()
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y/%m")
            unique_filename = f"{timestamp}/{uuid.uuid4()}_{filename}"
            
            # Upload to Supabase storage
            result = client.client.storage.from_("racing-notes-v5-media").upload(
                unique_filename, file_data, file_options={"content-type": content_type}
            )
            
            if result.get("error"):
                raise Exception(f"Storage upload failed: {result['error']}")
            
            # Get public URL
            public_url = client.client.storage.from_("racing-notes-v5-media").get_public_url(unique_filename)
            
            # Calculate file size in MB
            size_mb = len(file_data) / (1024 * 1024)
            
            self.logger.info(f"Media uploaded successfully: {unique_filename}")
            return public_url, size_mb
            
        except Exception as e:
            self.logger.error(f"Failed to upload media: {e}")
            raise

    async def process_and_upload_media(self, media_upload: MediaUpload, 
                                     progress_callback: Optional[callable] = None) -> Tuple[str, float, str]:
        """Process (compress) and upload media."""
        try:
            if progress_callback:
                progress_callback(0, "Starting compression...")
            
            # Determine media type
            file_ext = Path(media_upload.filename).suffix.lower()
            
            if file_ext in self.image_formats:
                media_type = MediaTypeEnum.IMAGE
                if progress_callback:
                    progress_callback(25, "Compressing image...")
                try:
                    compressed_data, new_filename = await self.compress_image(
                        media_upload.data, media_upload.filename
                    )
                except Exception as e:
                    # Fallback: upload original image if compression fails (e.g., unsupported format)
                    self.logger.warning(
                        f"Image compression failed for {media_upload.filename}: {e}. Uploading original file without compression."
                    )
                    compressed_data = media_upload.data
                    new_filename = media_upload.filename
            elif file_ext in self.video_formats:
                media_type = MediaTypeEnum.VIDEO
                if progress_callback:
                    progress_callback(25, "Compressing video...")
                compressed_data, new_filename = await self.compress_video(
                    media_upload.data, media_upload.filename
                )
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            if progress_callback:
                progress_callback(75, "Uploading to storage...")
            
            # Upload compressed media
            public_url, size_mb = await self.upload_media_with_retry(
                compressed_data, new_filename, media_upload.content_type
            )
            
            if progress_callback:
                progress_callback(100, "Upload complete!")
            
            return public_url, size_mb, new_filename
            
        except Exception as e:
            self.logger.error(f"Failed to process and upload media: {e}")
            raise

    async def delete_media(self, file_url: str) -> bool:
        """Delete media from storage."""
        try:
            client = get_supabase_client()
            
            # Extract filename from URL
            # Assuming URL format: .../storage/v1/object/public/racing-notes-v5-media/filename
            parts = file_url.split('/')
            if 'racing-notes-v5-media' in parts:
                filename_parts = parts[parts.index('racing-notes-v5-media') + 1:]
                filename = '/'.join(filename_parts)
            else:
                raise ValueError("Invalid file URL format")
            
            # Delete from storage
            result = client.client.storage.from_("racing-notes-v5-media").remove([filename])
            
            if result.get("error"):
                raise Exception(f"Storage delete failed: {result['error']}")
            
            self.logger.info(f"Media deleted successfully: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete media: {e}")
            return False

    async def generate_thumbnail(self, image_data: bytes, size: Tuple[int, int] = (200, 200)) -> bytes:
        """Generate a thumbnail from image data."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Auto-rotate based on EXIF data
            try:
                image = ImageOps.exif_transpose(image)
            except Exception:
                pass
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create thumbnail
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save as JPEG
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=80, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to generate thumbnail: {e}")
            raise

    async def get_media_info(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Get information about media file."""
        try:
            file_ext = Path(filename).suffix.lower()
            info = {
                "filename": filename,
                "size_bytes": len(file_data),
                "size_mb": len(file_data) / (1024 * 1024),
                "extension": file_ext
            }
            
            if file_ext in self.image_formats:
                try:
                    image = Image.open(io.BytesIO(file_data))
                    info.update({
                        "type": "image",
                        "width": image.width,
                        "height": image.height,
                        "format": image.format,
                        "mode": image.mode
                    })
                except Exception:
                    info["type"] = "image"
                    
            elif file_ext in self.video_formats:
                if not MOVIEPY_AVAILABLE:
                    info["type"] = "video"
                else:
                    try:
                        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
                            temp_file.write(file_data)
                            temp_path = temp_file.name
                        
                        try:
                            video = VideoFileClip(temp_path)
                            info.update({
                                "type": "video",
                                "width": video.w,
                                "height": video.h,
                                "duration": video.duration,
                                "fps": video.fps
                            })
                            video.close()
                        finally:
                            os.unlink(temp_path)
                            
                    except Exception:
                        info["type"] = "video"
            else:
                info["type"] = "unknown"
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get media info: {e}")
            raise

    def validate_media_file(self, filename: str, file_size: int) -> Tuple[bool, str]:
        """Validate media file before processing."""
        try:
            file_ext = Path(filename).suffix.lower()
            
            # Check file extension
            if file_ext not in (self.image_formats | self.video_formats):
                return False, f"Unsupported file type: {file_ext}"
            
            # Check file size
            if file_size > self.max_file_size:
                max_size_mb = self.max_file_size / (1024 * 1024)
                return False, f"File too large: {file_size / (1024 * 1024):.1f}MB > {max_size_mb:.0f}MB"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {e}"

    async def batch_process_media(self, media_uploads: List[MediaUpload], 
                                progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """Process multiple media files in batch."""
        results = []
        total_files = len(media_uploads)
        
        for i, media_upload in enumerate(media_uploads):
            try:
                if progress_callback:
                    progress_callback(i, total_files, f"Processing {media_upload.filename}...")
                
                # Validate file
                is_valid, message = self.validate_media_file(media_upload.filename, len(media_upload.data))
                if not is_valid:
                    results.append({
                        "filename": media_upload.filename,
                        "success": False,
                        "error": message
                    })
                    continue
                
                # Process and upload
                public_url, size_mb, new_filename = await self.process_and_upload_media(media_upload)
                
                results.append({
                    "filename": media_upload.filename,
                    "new_filename": new_filename,
                    "success": True,
                    "public_url": public_url,
                    "size_mb": size_mb
                })
                
            except Exception as e:
                results.append({
                    "filename": media_upload.filename,
                    "success": False,
                    "error": str(e)
                })
        
        if progress_callback:
            progress_callback(total_files, total_files, "Batch processing complete!")
        
        return results


# Global storage service instance
storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get the global storage service instance."""
    global storage_service
    if storage_service is None:
        storage_service = StorageService()
    return storage_service 