"""
Utility functions for the Racing Notes Desktop App V5.
Provides helper functions for timestamps, caching, validation, and more.
"""

import asyncio
import hashlib
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

import humanize
import pandas as pd
import streamlit as st
from dateutil import parser as date_parser
from loguru import logger

import io


class TimeUtils:
    """Utility functions for time and date operations."""
    
    @staticmethod
    def humanize_datetime(dt: datetime) -> str:
        """Convert datetime to human-readable format."""
        try:
            now = datetime.utcnow()
            diff = now - dt.replace(tzinfo=None)
            
            if diff.days > 7:
                return dt.strftime("%b %d, %Y")
            elif diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        except Exception as e:
            logger.error(f"Error humanizing datetime: {e}")
            return dt.strftime("%b %d, %Y")
    
    @staticmethod
    def parse_date_string(date_str: str) -> Optional[datetime]:
        """Parse a date string to datetime object."""
        try:
            return date_parser.parse(date_str)
        except Exception as e:
            logger.error(f"Error parsing date string '{date_str}': {e}")
            return None
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable format."""
        try:
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                minutes = seconds // 60
                seconds = seconds % 60
                return f"{int(minutes)}m {seconds:.0f}s"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                return f"{int(hours)}h {int(minutes)}m"
        except Exception as e:
            logger.error(f"Error formatting duration: {e}")
            return "Unknown"
    
    @staticmethod
    def get_race_weekend_dates(base_date: datetime) -> Dict[str, datetime]:
        """Get typical race weekend dates based on a base date."""
        try:
            # Assume base_date is race day (Sunday)
            # Friday: Practice 1 & 2
            # Saturday: Practice 3 & Qualifying
            # Sunday: Race
            
            friday = base_date - timedelta(days=2)
            saturday = base_date - timedelta(days=1)
            sunday = base_date
            
            return {
                "practice_1": friday.replace(hour=10, minute=0, second=0, microsecond=0),
                "practice_2": friday.replace(hour=14, minute=0, second=0, microsecond=0),
                "practice_3": saturday.replace(hour=10, minute=0, second=0, microsecond=0),
                "qualifying": saturday.replace(hour=14, minute=0, second=0, microsecond=0),
                "race": sunday.replace(hour=14, minute=0, second=0, microsecond=0)
            }
        except Exception as e:
            logger.error(f"Error getting race weekend dates: {e}")
            return {}


class CacheUtils:
    """Utility functions for caching operations."""
    
    @staticmethod
    def get_cache_key(prefix: str, *args: Any) -> str:
        """Generate a cache key from prefix and arguments."""
        try:
            # Convert all arguments to strings and join
            arg_str = "_".join(str(arg) for arg in args)
            
            # Create a hash for very long keys
            if len(arg_str) > 100:
                arg_str = hashlib.md5(arg_str.encode()).hexdigest()
            
            return f"{prefix}_{arg_str}"
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return f"{prefix}_default"
    
    @staticmethod
    def cache_data(key: str, data: Any, ttl: int = 3600) -> None:
        """Cache data in Streamlit session state with TTL."""
        try:
            cache_entry = {
                "data": data,
                "timestamp": datetime.utcnow(),
                "ttl": ttl
            }
            
            if "cache" not in st.session_state:
                st.session_state.cache = {}
            
            st.session_state.cache[key] = cache_entry
        except Exception as e:
            logger.error(f"Error caching data: {e}")
    
    @staticmethod
    def get_cached_data(key: str) -> Optional[Any]:
        """Get cached data from Streamlit session state."""
        try:
            if "cache" not in st.session_state:
                return None
            
            if key not in st.session_state.cache:
                return None
            
            cache_entry = st.session_state.cache[key]
            
            # Check if cache entry is expired
            if datetime.utcnow() - cache_entry["timestamp"] > timedelta(seconds=cache_entry["ttl"]):
                del st.session_state.cache[key]
                return None
            
            return cache_entry["data"]
        except Exception as e:
            logger.error(f"Error getting cached data: {e}")
            return None
    
    @staticmethod
    def clear_cache(pattern: Optional[str] = None) -> None:
        """Clear cached data, optionally by pattern."""
        try:
            if "cache" not in st.session_state:
                return
            
            if pattern is None:
                st.session_state.cache = {}
            else:
                keys_to_remove = [key for key in st.session_state.cache.keys() if pattern in key]
                for key in keys_to_remove:
                    del st.session_state.cache[key]
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


class ValidationUtils:
    """Utility functions for data validation."""
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate if a string is a valid UUID."""
        try:
            UUID(uuid_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: int = 100 * 1024 * 1024) -> Tuple[bool, str]:
        """Validate file size."""
        try:
            if file_size > max_size:
                max_mb = max_size / (1024 * 1024)
                current_mb = file_size / (1024 * 1024)
                return False, f"File too large: {current_mb:.1f}MB > {max_mb:.0f}MB"
            return True, "Valid"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def validate_media_type(filename: str) -> Tuple[bool, str]:
        """Validate media file type."""
        try:
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.heic', '.heif', '.mp4', '.mov', '.avi', '.m4v'}
            file_ext = filename.lower().split('.')[-1]
            
            if f'.{file_ext}' not in allowed_extensions:
                return False, f"Unsupported file type: {file_ext}"
            
            return True, "Valid"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        try:
            # Remove or replace invalid characters
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filename = re.sub(r'[^\w\s.-]', '', filename)
            filename = filename.strip()
            
            # Limit length
            if len(filename) > 255:
                name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
                max_name_len = 255 - len(ext) - 1
                filename = f"{name[:max_name_len]}.{ext}" if ext else name[:255]
            
            return filename or "unnamed_file"
        except Exception as e:
            logger.error(f"Error sanitizing filename: {e}")
            return "unnamed_file"


class TextUtils:
    """Utility functions for text processing."""
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text."""
        try:
            hashtag_pattern = r'#(\w+)'
            hashtags = re.findall(hashtag_pattern, text)
            return [tag.lower() for tag in hashtags]
        except Exception as e:
            logger.error(f"Error extracting hashtags: {e}")
            return []
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract @mentions from text."""
        try:
            mention_pattern = r'@(\w+)'
            mentions = re.findall(mention_pattern, text)
            return mentions
        except Exception as e:
            logger.error(f"Error extracting mentions: {e}")
            return []
    
    @staticmethod
    def suggest_tags(text: str) -> List[str]:
        """Suggest tags based on text content."""
        try:
            # Common racing terms that should become tags
            racing_terms = {
                'restart', 'aero', 'aerodynamics', 'pit', 'strategy', 'tire', 'tires',
                'fuel', 'setup', 'handling', 'speed', 'qualifying', 'pole', 'caution',
                'debris', 'crash', 'wreck', 'leader', 'lap', 'draft', 'drafting',
                'overtake', 'pass', 'position', 'finish', 'winner', 'checkered',
                'yellow', 'green', 'flag', 'race', 'practice', 'session'
            }
            
            # Convert text to lowercase and find matches
            text_lower = text.lower()
            suggestions = []
            
            for term in racing_terms:
                if term in text_lower:
                    suggestions.append(term)
            
            # Add hashtags found in text
            hashtags = TextUtils.extract_hashtags(text)
            suggestions.extend(hashtags)
            
            # Remove duplicates and return
            return list(set(suggestions))
        except Exception as e:
            logger.error(f"Error suggesting tags: {e}")
            return []
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length."""
        try:
            if len(text) <= max_length:
                return text
            
            truncated = text[:max_length - len(suffix)]
            # Try to break at word boundary
            if ' ' in truncated:
                truncated = truncated.rsplit(' ', 1)[0]
            
            return truncated + suffix
        except Exception as e:
            logger.error(f"Error truncating text: {e}")
            return text


class FormatUtils:
    """Utility functions for formatting data."""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        try:
            if size_bytes == 0:
                return "0 B"
            
            size_mb = size_bytes / (1024 * 1024)
            if size_mb < 1:
                size_kb = size_bytes / 1024
                return f"{size_kb:.1f} KB"
            elif size_mb < 1024:
                return f"{size_mb:.1f} MB"
            else:
                size_gb = size_mb / 1024
                return f"{size_gb:.1f} GB"
        except Exception as e:
            logger.error(f"Error formatting file size: {e}")
            return "Unknown"
    
    @staticmethod
    def format_number(number: Union[int, float]) -> str:
        """Format number with appropriate suffix (K, M, B)."""
        try:
            if number < 1000:
                return str(int(number))
            elif number < 1000000:
                return f"{number / 1000:.1f}K"
            elif number < 1000000000:
                return f"{number / 1000000:.1f}M"
            else:
                return f"{number / 1000000000:.1f}B"
        except Exception as e:
            logger.error(f"Error formatting number: {e}")
            return "Unknown"
    
    @staticmethod
    def format_percentage(value: float, total: float) -> str:
        """Format percentage with proper handling of edge cases."""
        try:
            if total == 0:
                return "0%"
            
            percentage = (value / total) * 100
            if percentage < 0.1:
                return "<0.1%"
            elif percentage > 99.9:
                return ">99.9%"
            else:
                return f"{percentage:.1f}%"
        except Exception as e:
            logger.error(f"Error formatting percentage: {e}")
            return "Unknown"


class ExportUtils:
    """Utility functions for data export."""
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> bytes:
        """Export data to CSV format."""
        try:
            df = pd.DataFrame(data)
            return df.to_csv(index=False).encode('utf-8')
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], filename: str) -> bytes:
        """Export data to JSON format."""
        try:
            df = pd.DataFrame(data)
            return df.to_json(orient='records', indent=2).encode('utf-8')
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
    
    @staticmethod
    def export_to_excel(data: List[Dict[str, Any]], filename: str) -> bytes:
        """Export data to Excel format."""
        try:
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Racing Notes', index=False)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise


class UIUtils:
    """Utility functions for UI components."""
    
    @staticmethod
    def show_success_toast(message: str) -> None:
        """Show success toast message."""
        try:
            st.toast(message, icon="✅")
        except Exception as e:
            logger.error(f"Error showing success toast: {e}")
    
    @staticmethod
    def show_error_toast(message: str) -> None:
        """Show error toast message."""
        try:
            st.toast(message, icon="❌")
        except Exception as e:
            logger.error(f"Error showing error toast: {e}")
    
    @staticmethod
    def show_info_toast(message: str) -> None:
        """Show info toast message."""
        try:
            st.toast(message, icon="ℹ️")
        except Exception as e:
            logger.error(f"Error showing info toast: {e}")
    
    @staticmethod
    def show_warning_toast(message: str) -> None:
        """Show warning toast message."""
        try:
            st.toast(message, icon="⚠️")
        except Exception as e:
            logger.error(f"Error showing warning toast: {e}")
    
    @staticmethod
    def create_tag_badge(tag: str, color: str = "blue") -> str:
        """Create HTML for a tag badge."""
        try:
            colors = {
                "blue": "#E3F2FD",
                "green": "#E8F5E8",
                "red": "#FFEBEE",
                "orange": "#FFF3E0",
                "purple": "#F3E5F5",
                "gray": "#F5F5F5"
            }
            
            bg_color = colors.get(color, colors["blue"])
            
            return f"""
            <span style="
                background-color: {bg_color};
                color: #333;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: 500;
                margin: 2px;
                display: inline-block;
            ">
                #{tag}
            </span>
            """
        except Exception as e:
            logger.error(f"Error creating tag badge: {e}")
            return f"#{tag}"
    
    @staticmethod
    def create_progress_bar(current: int, total: int, label: str = "") -> None:
        """Create a progress bar."""
        try:
            progress = current / total if total > 0 else 0
            st.progress(progress, text=f"{label} ({current}/{total})")
        except Exception as e:
            logger.error(f"Error creating progress bar: {e}")


class AsyncUtils:
    """Utility functions for async operations."""
    
    @staticmethod
    async def run_with_timeout(coroutine, timeout: float = 30.0):
        """Run a coroutine with timeout."""
        try:
            return await asyncio.wait_for(coroutine, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout} seconds")
            raise
        except Exception as e:
            logger.error(f"Error in async operation: {e}")
            raise
    
    @staticmethod
    async def batch_process(items: List[Any], batch_size: int = 10, 
                          process_func: callable = None) -> List[Any]:
        """Process items in batches to avoid overwhelming the system."""
        try:
            results = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_results = await asyncio.gather(*[process_func(item) for item in batch])
                results.extend(batch_results)
                
                # Small delay between batches to avoid rate limiting
                if i + batch_size < len(items):
                    await asyncio.sleep(0.1)
            
            return results
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise


# Convenience functions for common operations
def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string."""
    return TimeUtils.humanize_datetime(dt)


def cache_result(key: str, ttl: int = 3600):
    """Decorator for caching function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = CacheUtils.get_cache_key(key, *args, **kwargs)
            cached_result = CacheUtils.get_cached_data(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            CacheUtils.cache_data(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    return FormatUtils.format_file_size(size_bytes)


def truncate(text: str, length: int = 100) -> str:
    """Truncate text to specified length."""
    return TextUtils.truncate_text(text, length)


def success_toast(message: str) -> None:
    """Show success toast message."""
    UIUtils.show_success_toast(message)


def error_toast(message: str) -> None:
    """Show error toast message."""
    UIUtils.show_error_toast(message) 