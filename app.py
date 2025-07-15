"""
Racing Notes Desktop App V5
Main Streamlit application entry point with navigation and core functionality.
"""

import asyncio
import io
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go

from models import (
    NoteCreate, SearchFilters, MediaUpload, NoteWithDetails,
    TrackTypeEnum, SessionTypeEnum, CategoryEnum, MediaTypeEnum, UploadedMedia
)
from supabase_client import get_supabase_client, initialize_client
from storage_service import get_storage_service
from utils import (
    TimeUtils, CacheUtils, ValidationUtils, TextUtils, FormatUtils,
    UIUtils, success_toast, error_toast, info_toast, warning_toast,
    get_time_ago, format_size, truncate
)
import nest_asyncio
nest_asyncio.apply()

# Configure page
st.set_page_config(
    page_title="Racing Notes Desktop App V5",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/racing-notes-v5',
        'Report a bug': 'https://github.com/your-repo/racing-notes-v5/issues',
        'About': """
        # Racing Notes Desktop App V5
        
        A premium racing notes application for NASCAR enthusiasts.
        Built with Streamlit, Supabase, and modern Python best practices.
        """
    }
)

# Custom CSS for racing theme
st.markdown("""
<style>
    /* Racing theme colors */
    :root {
        --primary-color: #1E3A8A;
        --secondary-color: #3B82F6;
        --accent-color: #EF4444;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --dark-bg: #1F2937;
        --light-bg: #F9FAFB;
    }
    
    /* Custom card styling */
    .note-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
    }
    
    .note-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* Tag styling */
    .tag {
        background: var(--secondary-color);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 2px 4px;
        display: inline-block;
    }
    
    /* Media preview styling */
    .media-preview {
        border-radius: 8px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    /* Progress bar styling */
    .upload-progress {
        background: var(--light-bg);
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
    
    /* Navigation styling */
    .nav-link {
        color: var(--primary-color);
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .nav-link:hover {
        background: var(--light-bg);
        color: var(--secondary-color);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .note-card {
            padding: 15px;
            margin: 12px 0;
        }
    }
    
    /* Hide Streamlit footer */
    footer {
        visibility: hidden;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: var(--secondary-color);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.current_page = "Home Feed"
    st.session_state.filters = SearchFilters()
    st.session_state.upload_progress = {}

# Initialize clients
@st.cache_resource
def init_clients():
    """Initialize database and storage clients."""
    try:
        asyncio.run(initialize_client())
        return True
    except Exception as e:
        st.error(f"Failed to initialize clients: {e}")
        return False

def load_cached_data():
    """Load frequently used data with caching."""
    try:
        client = get_supabase_client()
        
        # Cache tracks
        cache_key = "tracks_list"
        tracks = CacheUtils.get_cached_data(cache_key)
        if tracks is None:
            tracks = asyncio.run(client.get_tracks())
            CacheUtils.cache_data(cache_key, tracks, ttl=3600)
        
        # Cache series
        cache_key = "series_list"
        series = CacheUtils.get_cached_data(cache_key)
        if series is None:
            series = asyncio.run(client.get_series())
            CacheUtils.cache_data(cache_key, series, ttl=3600)
        
        # Cache tags
        cache_key = "tags_list"
        tags = CacheUtils.get_cached_data(cache_key)
        if tags is None:
            tags = asyncio.run(client.get_tags())
            CacheUtils.cache_data(cache_key, tags, ttl=1800)
        
        return tracks, series, tags
    except Exception as e:
        st.error(f"Failed to load cached data: {e}")
        return [], [], []

def create_note_card(note: NoteWithDetails) -> None:
    """Create a note card component."""
    try:
        with st.container():
            # Note header
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="note-card">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="width: 40px; height: 40px; background: var(--primary-color); 
                                    border-radius: 50%; display: flex; align-items: center; 
                                    justify-content: center; margin-right: 12px;">
                            <span style="color: white; font-weight: bold;">🏁</span>
                        </div>
                        <div>
                            <div style="font-weight: 600; color: var(--dark-bg);">
                                {note.driver_name or "General Note"}
                            </div>
                            <div style="font-size: 0.9em; color: #666;">
                                {get_time_ago(note.created_at)}
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px; line-height: 1.5;">
                        {note.body}
                    </div>
                    
                    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
                        {f'<span class="tag">📍 {note.track_name}</span>' if note.track_name else ''}
                        {f'<span class="tag">🏆 {note.series_name}</span>' if note.series_name else ''}
                        {f'<span class="tag">🚗 {note.session_type}</span>' if note.session_type else ''}
                        {f'<span class="tag">📂 {note.category}</span>'}
                    </div>
                    
                    <div style="display: flex; gap: 8px;">
                        {''.join([f'<span class="tag">#{tag.label}</span>' for tag in note.tags])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Action buttons
                col2a, col2b = st.columns(2)
                with col2a:
                    if st.button("👍", key=f"like_{note.id}"):
                        # TODO: Implement like functionality
                        info_toast("Like functionality coming soon!")
                
                with col2b:
                    if st.button("💬", key=f"reply_{note.id}"):
                        # TODO: Implement reply functionality
                        info_toast("Reply functionality coming soon!")
            
            # Display media
            if note.media:
                cols = st.columns(min(len(note.media), 3))
                for i, media in enumerate(note.media[:3]):
                    with cols[i % 3]:
                        if media.type.value == 'image':
                            st.image(media.file_url, use_column_width=True)
                        elif media.type.value == 'video':
                            st.video(media.file_url)
                        
                        st.caption(f"{media.filename} ({format_size(int(media.size_mb * 1024 * 1024))})")
                
                if len(note.media) > 3:
                    st.info(f"+ {len(note.media) - 3} more media files")
    
    except Exception as e:
        st.error(f"Error creating note card: {e}")

def create_note_form():
    """Create note creation form."""
    try:
        st.subheader("✍️ Create New Note")
        
        with st.form("note_form", clear_on_submit=True):
            # Load cached data
            tracks, series, tags = load_cached_data()
            
            # Note body
            note_body = st.text_area(
                "What's happening at the track?",
                height=120,
                placeholder="Share your thoughts, observations, or insights about the race..."
            )
            
            # Form columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Track selection
                track_options = ["None"] + [f"{track.name} ({track.type})" for track in tracks]
                selected_track = st.selectbox("Track", track_options)
                
                # Series selection
                series_options = ["None"] + [series.name for series in series]
                selected_series = st.selectbox("Series", series_options)
                
                # Category
                category = st.selectbox(
                    "Category",
                    [cat.value for cat in CategoryEnum],
                    index=0
                )
            
            with col2:
                # Driver selection (filtered by series)
                driver_options = ["None"]
                if selected_series != "None":
                    try:
                        series_id = next(s.id for s in series if s.name == selected_series)
                        client = get_supabase_client()
                        drivers = asyncio.run(client.get_drivers(series_id))
                        driver_options.extend([driver.name for driver in drivers])
                    except Exception:
                        pass
                
                selected_driver = st.selectbox("Driver", driver_options)
                
                # Session type
                session_type = st.selectbox(
                    "Session Type",
                    ["None"] + [session.value for session in SessionTypeEnum]
                )
                
                # Shared toggle
                shared = st.checkbox("Share publicly", value=False)
            
            # Tags
            tag_input = st.text_input(
                "Tags (comma-separated)",
                placeholder="restart, strategy, pit-stop, aero..."
            )
            
            # Auto-suggest tags
            if note_body:
                suggested_tags = TextUtils.suggest_tags(note_body)
                if suggested_tags:
                    st.info(f"💡 Suggested tags: {', '.join(suggested_tags)}")
            
            # Media upload
            st.subheader("📎 Media Upload")
            uploaded_files = st.file_uploader(
                "Choose files",
                accept_multiple_files=True,
                type=['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'],
                help="Upload images and videos. Max 100MB total."
            )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Post Note", type="primary")
            
            if submitted:
                if not note_body.strip():
                    error_toast("Please enter a note body")
                    return
                
                try:
                    # Create note data
                    note_data = NoteCreate(
                        body=note_body,
                        shared=shared,
                        category=CategoryEnum(category)
                    )
                    
                    # Set optional fields
                    if selected_track != "None":
                        track_id = next(t.id for t in tracks if f"{t.name} ({t.type})" == selected_track)
                        
                        # Create session if session type is selected
                        if session_type != "None":
                            client = get_supabase_client()
                            series_id = next(s.id for s in series if s.name == selected_series) if selected_series != "None" else None
                            
                            if series_id:
                                session = asyncio.run(client.create_session(
                                    date=datetime.now(),
                                    session_type=SessionTypeEnum(session_type),
                                    track_id=track_id,
                                    series_id=series_id
                                ))
                                note_data.session_id = session.id
                    
                    if selected_driver != "None":
                        driver_id = next(d.id for d in drivers if d.name == selected_driver)
                        note_data.driver_id = driver_id
                    
                    # Process tags
                    if tag_input.strip():
                        client = get_supabase_client()
                        tag_names = [tag.strip() for tag in tag_input.split(',')]
                        tag_ids = []
                        
                        for tag_name in tag_names:
                            if tag_name:
                                tag = asyncio.run(client.get_or_create_tag(tag_name))
                                tag_ids.append(tag.id)
                        
                        note_data.tag_ids = tag_ids
                    
                    # Process media files
                    if uploaded_files:
                        storage_service = get_storage_service()
                        media_uploads = []
                        
                        total_size = sum(file.size for file in uploaded_files)
                        if total_size > 100 * 1024 * 1024:  # 100MB
                            error_toast("Total file size exceeds 100MB limit")
                            return
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, file in enumerate(uploaded_files):
                            progress = (i + 1) / len(uploaded_files)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing {file.name}...")
                            
                            # Validate file
                            is_valid, message = ValidationUtils.validate_media_type(file.name)
                            if not is_valid:
                                error_toast(f"Invalid file {file.name}: {message}")
                                continue
                            
                            # Create media upload
                            media_upload = MediaUpload(
                                filename=file.name,
                                content_type=file.type,
                                size_bytes=file.size,
                                data=file.read()
                            )
                            
                            try:
                                # Process and upload
                                public_url, size_mb, new_filename = asyncio.run(
                                    storage_service.process_and_upload_media(media_upload)
                                )
                                
                                media_uploads.append(UploadedMedia(
                                    file_url=public_url,
                                    type=MediaTypeEnum.IMAGE if file.type.startswith('image/') else MediaTypeEnum.VIDEO,
                                    size_mb=size_mb,
                                    filename=new_filename
                                ))
                                
                            except Exception as e:
                                error_toast(f"Failed to process {file.name}: {e}")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        note_data.media_files = media_uploads
                    
                    # Create note
                    client = get_supabase_client()
                    note = asyncio.run(client.create_note(note_data))
                    
                    # Create media records
                    for media_info in note_data.media_files:
                        asyncio.run(client.create_media(
                            note_id=note.id,
                            file_url=media_info.file_url,
                            media_type=media_info.type,
                            size_mb=media_info.size_mb,
                            filename=media_info.filename
                        ))
                    
                    success_toast("Note created successfully!")
                    
                    # Clear cache
                    CacheUtils.clear_cache("notes_feed")
                    
                    # Rerun to show updated feed
                    st.rerun()
                    
                except Exception as e:
                    error_toast(f"Failed to create note: {e}")
    
    except Exception as e:
        st.error(f"Error creating note form: {e}")

def show_notes_feed():
    """Display the main notes feed."""
    try:
        st.title("🏁 Racing Notes Feed")
        
        # Filter sidebar
        with st.sidebar:
            st.subheader("🔍 Filters")
            
            # Text search
            search_query = st.text_input("Search notes...", placeholder="Enter keywords...")
            
            # Load cached data
            tracks, series, tags = load_cached_data()
            
            # Filter options
            with st.expander("📍 Track & Series"):
                selected_tracks = st.multiselect(
                    "Tracks",
                    options=[f"{track.name} ({track.type})" for track in tracks],
                    default=[]
                )
                
                selected_series = st.multiselect(
                    "Series",
                    options=[series.name for series in series],
                    default=[]
                )
            
            with st.expander("🏷️ Categories & Tags"):
                selected_categories = st.multiselect(
                    "Categories",
                    options=[cat.value for cat in CategoryEnum],
                    default=[]
                )
                
                selected_tags = st.multiselect(
                    "Tags",
                    options=[tag.label for tag in tags],
                    default=[]
                )
            
            with st.expander("📅 Date Range"):
                date_from = st.date_input("From", value=None)
                date_to = st.date_input("To", value=None)
            
            # Apply filters
            if st.button("Apply Filters"):
                # Build filters
                filters = SearchFilters(
                    text_query=search_query if search_query else None,
                    categories=[CategoryEnum(cat) for cat in selected_categories],
                    date_from=datetime.combine(date_from, datetime.min.time()) if date_from else None,
                    date_to=datetime.combine(date_to, datetime.max.time()) if date_to else None
                )
                
                # Convert selections to IDs
                if selected_tracks:
                    track_ids = [next(t.id for t in tracks if f"{t.name} ({t.type})" == track) for track in selected_tracks]
                    filters.track_ids = track_ids
                
                if selected_series:
                    series_ids = [next(s.id for s in series if s.name == ser) for ser in selected_series]
                    filters.series_ids = series_ids
                
                if selected_tags:
                    tag_ids = [next(t.id for t in tags if t.label == tag) for tag in selected_tags]
                    filters.tag_ids = tag_ids
                
                st.session_state.filters = filters
                CacheUtils.clear_cache("notes_feed")
        
        # Load notes
        try:
            client = get_supabase_client()
            
            # Check cache first
            cache_key = CacheUtils.get_cache_key("notes_feed", str(st.session_state.filters.dict()))
            cached_notes = CacheUtils.get_cached_data(cache_key)
            
            if cached_notes is None:
                notes_response = asyncio.run(client.get_notes_feed(st.session_state.filters))
                CacheUtils.cache_data(cache_key, notes_response, ttl=300)  # 5 minutes
            else:
                notes_response = cached_notes
            
            # Display notes
            if notes_response.items:
                st.write(f"📊 Showing {len(notes_response.items)} of {notes_response.total} notes")
                
                for note in notes_response.items:
                    create_note_card(note)
                
                # Pagination
                if notes_response.has_next or notes_response.has_previous:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if notes_response.has_previous and st.button("← Previous"):
                            st.session_state.filters.offset = max(0, st.session_state.filters.offset - st.session_state.filters.limit)
                            CacheUtils.clear_cache("notes_feed")
                            st.rerun()
                    
                    with col2:
                        current_page = (st.session_state.filters.offset // st.session_state.filters.limit) + 1
                        total_pages = (notes_response.total + st.session_state.filters.limit - 1) // st.session_state.filters.limit
                        st.write(f"Page {current_page} of {total_pages}")
                    
                    with col3:
                        if notes_response.has_next and st.button("Next →"):
                            st.session_state.filters.offset += st.session_state.filters.limit
                            CacheUtils.clear_cache("notes_feed")
                            st.rerun()
            else:
                st.info("🏁 No notes found. Create your first note to get started!")
                
        except Exception as e:
            st.error(f"Failed to load notes: {e}")
    
    except Exception as e:
        st.error(f"Error displaying notes feed: {e}")

def show_media_search():
    """Display media search interface."""
    try:
        st.title("📷 Media Search")
        
        # Search interface
        search_query = st.text_input("Search media...", placeholder="Search by filename or note content...")
        
        if st.button("Search") or search_query:
            try:
                client = get_supabase_client()
                filters = SearchFilters(text_query=search_query) if search_query else None
                
                media_results = asyncio.run(client.search_media(filters))
                
                if media_results:
                    st.write(f"Found {len(media_results)} media files")
                    
                    # Grid layout
                    cols = st.columns(3)
                    for i, media in enumerate(media_results):
                        with cols[i % 3]:
                            st.subheader(media.get("filename", "Unknown"))
                            
                            if media.get("type") == "image":
                                st.image(media.get("file_url"), use_column_width=True)
                            elif media.get("type") == "video":
                                st.video(media.get("file_url"))
                            
                            st.write(f"**Size:** {format_size(int(media.get('size_mb', 0) * 1024 * 1024))}")
                            st.write(f"**Date:** {get_time_ago(datetime.fromisoformat(media.get('created_at', '')))}")
                            
                            if media.get("note_body"):
                                st.write(f"**Note:** {truncate(media.get('note_body'), 100)}")
                            
                            if st.button("Download", key=f"download_{media.get('id')}"):
                                st.download_button(
                                    label="Download File",
                                    data=media.get("file_url"),
                                    file_name=media.get("filename"),
                                    key=f"dl_{media.get('id')}"
                                )
                else:
                    st.info("No media found for the search criteria")
                    
            except Exception as e:
                st.error(f"Media search failed: {e}")
    
    except Exception as e:
        st.error(f"Error in media search: {e}")

def show_settings():
    """Display settings interface."""
    try:
        st.title("⚙️ Settings")
        
        # Theme settings
        st.subheader("🎨 Theme")
        theme_mode = st.selectbox(
            "Choose theme",
            ["Light", "Dark", "Auto"],
            index=0
        )
        
        # Export settings
        st.subheader("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Notes as CSV"):
                try:
                    client = get_supabase_client()
                    filters = SearchFilters(limit=1000)  # Get more data for export
                    notes_response = asyncio.run(client.get_notes_feed(filters))
                    
                    # Convert to DataFrame
                    data = []
                    for note in notes_response.items:
                        data.append({
                            "id": str(note.id),
                            "body": note.body,
                            "category": note.category,
                            "driver": note.driver_name,
                            "track": note.track_name,
                            "series": note.series_name,
                            "created_at": note.created_at,
                            "tags": ", ".join([tag.get("label", "") for tag in note.tags])
                        })
                    
                    df = pd.DataFrame(data)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"racing_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    error_toast(f"Export failed: {e}")
        
        with col2:
            if st.button("Export Notes as JSON"):
                try:
                    client = get_supabase_client()
                    filters = SearchFilters(limit=1000)
                    notes_response = asyncio.run(client.get_notes_feed(filters))
                    
                    # Convert to JSON
                    data = [note.dict() for note in notes_response.items]
                    json_str = json.dumps(data, indent=2, default=str)
                    
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"racing_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                    
                except Exception as e:
                    error_toast(f"Export failed: {e}")
        
        # Cache management
        st.subheader("🗄️ Cache Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Cache"):
                CacheUtils.clear_cache()
                success_toast("Cache cleared successfully!")
        
        with col2:
            # Show cache stats
            cache_size = len(st.session_state.get("cache", {}))
            st.metric("Cached Items", cache_size)
        
        # Statistics
        st.subheader("📊 Statistics")
        
        try:
            client = get_supabase_client()
            stats = asyncio.run(client.get_stats())
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Notes", stats.get("notes_count", 0))
            
            with col2:
                st.metric("Media Files", stats.get("media_count", 0))
            
            with col3:
                st.metric("Tags", stats.get("tags_count", 0))
            
            with col4:
                storage_mb = stats.get("storage_usage_mb", 0)
                st.metric("Storage Used", f"{storage_mb:.1f} MB")
        
        except Exception as e:
            st.error(f"Failed to load statistics: {e}")
    
    except Exception as e:
        st.error(f"Error in settings: {e}")

def main():
    """Main application entry point."""
    try:
        # Initialize
        if not st.session_state.initialized:
            with st.spinner("Initializing Racing Notes..."):
                if init_clients():
                    st.session_state.initialized = True
                    success_toast("Racing Notes initialized successfully!")
                else:
                    st.error("Failed to initialize Racing Notes")
                    st.stop()
        
        # Main navigation
        with st.sidebar:
            st.title("🏁 Racing Notes V5")
            
            # Navigation menu
            selected = option_menu(
                menu_title=None,
                options=["Home Feed", "Create Note", "Media Search", "Settings"],
                icons=["house", "plus-circle", "camera", "gear"],
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#1E3A8A", "font-size": "18px"},
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
                    "nav-link-selected": {"background-color": "#3B82F6", "color": "white"},
                }
            )
            
            st.session_state.current_page = selected
            
            # Quick stats
            st.markdown("---")
            st.subheader("📊 Quick Stats")
            
            try:
                client = get_supabase_client()
                stats = asyncio.run(client.get_stats())
                
                st.metric("Notes", stats.get("notes_count", 0))
                st.metric("Media", stats.get("media_count", 0))
                st.metric("Storage", f"{stats.get('storage_usage_mb', 0):.1f} MB")
            except Exception:
                st.info("Stats unavailable")
        
        # Main content area
        if st.session_state.current_page == "Home Feed":
            show_notes_feed()
        elif st.session_state.current_page == "Create Note":
            create_note_form()
        elif st.session_state.current_page == "Media Search":
            show_media_search()
        elif st.session_state.current_page == "Settings":
            show_settings()
    
    except Exception as e:
        st.error(f"Application error: {e}")
        import traceback
        st.code(traceback.format_exc())
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main() 