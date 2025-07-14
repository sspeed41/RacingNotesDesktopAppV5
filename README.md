# Racing Notes Desktop App V5 🏁

A premium, robust racing notes application built with Python, Streamlit, and Supabase. Designed for NASCAR enthusiasts to track race insights, strategies, and observations with reliable media handling and an intuitive user experience.

## ✨ Features

### Core Functionality
- **📝 Rich Note Creation**: Create detailed notes with category tagging, driver/track associations, and session linking
- **🔍 Advanced Search & Filtering**: Full-text search with powerful filters by track, series, driver, tags, and date ranges
- **📱 Responsive Design**: Premium UI optimized for desktop with mobile compatibility
- **🏷️ Smart Tagging**: Auto-tag suggestions based on content with hashtag support
- **📊 Statistics Dashboard**: Track your notes, media usage, and activity patterns

### Media Management
- **📸 Reliable Media Upload**: Drag-and-drop support for images (PNG, JPG, HEIC) and videos (MP4, MOV)
- **🔄 Intelligent Compression**: Automatic image/video compression to prevent upload failures
- **☁️ Cloud Storage**: Supabase storage with CDN delivery for fast media access
- **🖼️ Media Search**: Dedicated media browser with preview and download capabilities
- **📱 Mobile-Friendly**: Optimized for iPhone/Mac photo uploads with HEIC support

### Data Management
- **💾 Export Capabilities**: Export notes to CSV, JSON, or Excel formats
- **🔄 Real-time Updates**: Live updates with optimistic UI patterns
- **🏁 NASCAR-Focused**: Pre-populated with NASCAR series, tracks, and drivers
- **📈 Performance Optimized**: Efficient caching and pagination for large datasets

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/racing-notes-v5.git
   cd racing-notes-v5
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start local Supabase**
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to start** (about 2-3 minutes)
   ```bash
   docker-compose logs -f db
   # Wait for "database system is ready to accept connections"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the application**
   - App: http://localhost:8501
   - Supabase Studio: http://localhost:3000
   - Email UI: http://localhost:9000

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Supabase Configuration
SUPABASE_URL=http://localhost:8000
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU

# Application Settings
LOG_LEVEL=INFO
CACHE_TTL=3600
MAX_UPLOAD_SIZE=104857600  # 100MB
```

### Database Setup
The application automatically creates the database schema and seeds it with NASCAR data on first run. To manually run the setup:

```bash
# Connect to the local database
psql -h localhost -p 5432 -U postgres -d postgres

# Run the schema (if needed)
\i schema.sql

# Run the seed data (if needed)
\i seed-data.sql
```

## 📖 Usage Guide

### Creating Notes
1. Navigate to "Create Note" in the sidebar
2. Enter your note content in the text area
3. Select relevant track, series, driver, and session type
4. Add tags (comma-separated or use auto-suggestions)
5. Upload media files (images/videos) via drag-and-drop
6. Click "Post Note" to save

### Searching & Filtering
- Use the search bar for full-text search across notes
- Apply filters in the sidebar:
  - **Track & Series**: Filter by specific venues or racing series
  - **Categories & Tags**: Narrow down by note categories or tags
  - **Date Range**: Find notes from specific time periods
- Results are paginated for performance

### Media Management
- Access "Media Search" for a dedicated media browser
- Preview images and videos directly in the interface
- Download media files with original filenames
- Media is automatically compressed for optimal storage

### Data Export
- Go to "Settings" to export your notes
- Choose from CSV, JSON, or Excel formats
- Export includes all note data, tags, and metadata

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Streamlit 1.46.1 with custom CSS theming
- **Backend**: Supabase (PostgreSQL + Auth + Storage + Realtime)
- **Language**: Python 3.12+ with async support
- **Media Processing**: Pillow (images) + MoviePy (videos)
- **Data Models**: Pydantic 2.11.7 for validation

### Project Structure
```
racing-notes-v5/
├── app.py                 # Main Streamlit application
├── models.py              # Pydantic data models
├── supabase_client.py     # Database client with async operations
├── storage_service.py     # Media compression and upload service
├── utils.py               # Utility functions and helpers
├── schema.sql             # Database schema definition
├── seed-data.sql          # Sample NASCAR data
├── docker-compose.yml     # Local Supabase development environment
├── kong.conf              # API gateway configuration
├── requirements.txt       # Python dependencies
├── tests.py               # Unit tests
└── README.md              # This file
```

### Database Schema
- **tracks**: Racing venues with type classification
- **series**: NASCAR series (Cup, Xfinity, Trucks)
- **drivers**: Driver roster by series
- **sessions**: Practice, qualifying, and race sessions
- **notes**: User-generated content with metadata
- **media**: File storage records with compression info
- **tags**: Categorization and search optimization
- **notes_with_details**: Materialized view for efficient queries

## 🧪 Testing

Run the test suite:
```bash
pytest tests.py -v
```

### Test Coverage
- Database operations (CRUD)
- Media compression and upload
- Search and filtering
- Data validation
- Error handling

### Manual Testing
1. Create notes with various content types
2. Upload different media formats (JPG, PNG, HEIC, MP4, MOV)
3. Test search functionality with different filters
4. Verify export capabilities
5. Test responsive design on mobile devices

## 📈 Performance Optimization

### Caching Strategy
- **Static Data**: Tracks, series, and drivers cached for 1 hour
- **Dynamic Data**: Note feeds cached for 5 minutes
- **Search Results**: Cached per unique filter combination
- **Media Previews**: Browser-cached with appropriate headers

### Media Optimization
- **Images**: Resized to max 1920x1080, 85% quality JPEG
- **Videos**: Compressed to 720p, 1Mbps bitrate
- **HEIC/HEIF**: Automatically converted to JPEG
- **Progressive Loading**: Lazy-loaded media previews

### Database Performance
- **Indexed Fields**: All commonly queried fields have indexes
- **Materialized Views**: Pre-computed joins for complex queries
- **Full-Text Search**: PostgreSQL GIN indexes for text search
- **Pagination**: Efficient offset-based pagination

## 🚀 Deployment

### Local Development
Follow the Quick Start guide above for local development setup.

### Production Deployment

#### Streamlit Cloud
1. Push your code to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables for your production Supabase instance
4. Deploy with automatic updates

#### Docker Deployment
```bash
# Build the application image
docker build -t racing-notes-v5 .

# Run with environment variables
docker run -p 8501:8501 --env-file .env racing-notes-v5
```

#### Supabase Production
1. Create a new project at https://supabase.com
2. Run the schema.sql in the SQL editor
3. Run the seed-data.sql for initial data
4. Set up storage bucket "racing-notes-media"
5. Update environment variables

## 🔒 Security

### Data Protection
- **Row Level Security**: Enabled for all tables (prepared for multi-user)
- **Input Validation**: Pydantic models validate all data
- **File Upload Security**: Type checking and size limits
- **SQL Injection Prevention**: Parameterized queries via Supabase

### Privacy
- **Single-User Mode**: No authentication required for local use
- **Data Ownership**: All notes and media belong to the user
- **No External Tracking**: No analytics or tracking services

## 🤝 Contributing

### Development Setup
1. Follow the installation guide
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `pytest tests.py`
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Add docstrings for all functions
- Run `black` for code formatting
- Use `mypy` for type checking

### Issue Reporting
- Use GitHub issues for bug reports
- Include steps to reproduce
- Provide screenshots for UI issues
- Mention your OS and Python version

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏁 Roadmap

### Upcoming Features
- **🔐 Multi-User Support**: Authentication and user management
- **📊 Advanced Analytics**: Detailed statistics and insights
- **🤖 AI Integration**: Auto-tagging and content suggestions
- **📱 Mobile App**: Native iOS/Android applications
- **🔄 Real-time Collaboration**: Live updates and sharing
- **📈 Data Visualization**: Charts and graphs for race analysis

### Performance Improvements
- **⚡ Caching Layer**: Redis integration for better performance
- **🗄️ Database Optimization**: Query optimization and indexing
- **📦 CDN Integration**: Global content delivery
- **🔄 Background Processing**: Async media processing

## 🆘 Support

### Documentation
- **API Reference**: See inline docstrings and type hints
- **Database Schema**: Refer to schema.sql for table definitions
- **Configuration**: Check environment variables section

### Community
- **GitHub Discussions**: For questions and feature requests
- **Issue Tracker**: For bug reports and technical issues
- **Discord**: [Join our community](https://discord.gg/racing-notes) (coming soon)

### Troubleshooting

**Common Issues:**
1. **Database Connection Failed**: Ensure Docker services are running
2. **Media Upload Errors**: Check file size limits and formats
3. **Slow Performance**: Clear cache or restart the application
4. **Missing Dependencies**: Run `pip install -r requirements.txt`

**Reset Database:**
```bash
docker-compose down -v
docker-compose up -d
```

---

**Built with ❤️ for the NASCAR community**

*Racing Notes Desktop App V5 - Where every lap tells a story* 🏁 