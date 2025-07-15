-- Racing Notes Desktop App V5 - Database Schema
-- This schema creates all tables, indexes, and materialized views for the application

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create custom types/enums
CREATE TYPE track_type AS ENUM ('Superspeedway', 'Intermediate', 'Short Track', 'Road Course');
CREATE TYPE session_type AS ENUM ('Practice', 'Qualifying', 'Race');
CREATE TYPE note_category AS ENUM ('General', 'Track Specific', 'Strategy', 'Other');
CREATE TYPE media_type AS ENUM ('image', 'video');

-- Tracks table
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    type track_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Series table
CREATE TABLE series (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Drivers table
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    series_id UUID NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, series_id)
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    type session_type NOT NULL,
    track_id UUID NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    series_id UUID NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    label VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notes table
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    body TEXT NOT NULL,
    shared BOOLEAN DEFAULT FALSE,
    driver_id UUID REFERENCES drivers(id) ON DELETE SET NULL,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    category note_category DEFAULT 'General',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Full text search column
    search_vector tsvector
);

-- Media table
CREATE TABLE media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    type media_type NOT NULL,
    size_mb DECIMAL(10,2) NOT NULL CHECK (size_mb >= 0),
    filename VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Note-Tag junction table
CREATE TABLE note_tags (
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (note_id, tag_id)
);

-- Likes table for future social features
CREATE TABLE likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    user_id UUID, -- For future multi-user support
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(note_id, user_id)
);

-- Replies table for future social features
CREATE TABLE replies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    reply_text TEXT NOT NULL,
    user_id UUID, -- For future multi-user support
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance

-- Tracks indexes
CREATE INDEX idx_tracks_name ON tracks(name);
CREATE INDEX idx_tracks_type ON tracks(type);

-- Series indexes
CREATE INDEX idx_series_name ON series(name);

-- Drivers indexes
CREATE INDEX idx_drivers_name ON drivers(name);
CREATE INDEX idx_drivers_series_id ON drivers(series_id);

-- Sessions indexes
CREATE INDEX idx_sessions_date ON sessions(date);
CREATE INDEX idx_sessions_type ON sessions(type);
CREATE INDEX idx_sessions_track_id ON sessions(track_id);
CREATE INDEX idx_sessions_series_id ON sessions(series_id);
CREATE INDEX idx_sessions_date_type ON sessions(date, type);

-- Tags indexes
CREATE INDEX idx_tags_label ON tags(label);
CREATE INDEX idx_tags_label_trgm ON tags USING gin(label gin_trgm_ops);

-- Notes indexes
CREATE INDEX idx_notes_created_at ON notes(created_at DESC);
CREATE INDEX idx_notes_shared ON notes(shared);
CREATE INDEX idx_notes_driver_id ON notes(driver_id);
CREATE INDEX idx_notes_session_id ON notes(session_id);
CREATE INDEX idx_notes_category ON notes(category);
CREATE INDEX idx_notes_search_vector ON notes USING gin(search_vector);
CREATE INDEX idx_notes_body_trgm ON notes USING gin(body gin_trgm_ops);

-- Media indexes
CREATE INDEX idx_media_note_id ON media(note_id);
CREATE INDEX idx_media_type ON media(type);
CREATE INDEX idx_media_created_at ON media(created_at DESC);

-- Note-Tags indexes
CREATE INDEX idx_note_tags_note_id ON note_tags(note_id);
CREATE INDEX idx_note_tags_tag_id ON note_tags(tag_id);

-- Likes indexes
CREATE INDEX idx_likes_note_id ON likes(note_id);
CREATE INDEX idx_likes_created_at ON likes(created_at DESC);

-- Replies indexes
CREATE INDEX idx_replies_note_id ON replies(note_id);
CREATE INDEX idx_replies_created_at ON replies(created_at DESC);

-- Create functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_tracks_updated_at 
    BEFORE UPDATE ON tracks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_series_updated_at 
    BEFORE UPDATE ON series 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_drivers_updated_at 
    BEFORE UPDATE ON drivers 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at 
    BEFORE UPDATE ON sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tags_updated_at 
    BEFORE UPDATE ON tags 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notes_updated_at 
    BEFORE UPDATE ON notes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_updated_at 
    BEFORE UPDATE ON media 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_replies_updated_at 
    BEFORE UPDATE ON replies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to update search vector
CREATE OR REPLACE FUNCTION update_notes_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = to_tsvector('english', 
        COALESCE(NEW.body, '') || ' ' ||
        COALESCE((SELECT string_agg(t.label, ' ') FROM tags t 
                  JOIN note_tags nt ON t.id = nt.tag_id 
                  WHERE nt.note_id = NEW.id), '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for search vector
CREATE TRIGGER update_notes_search_vector_trigger
    BEFORE INSERT OR UPDATE ON notes
    FOR EACH ROW
    EXECUTE FUNCTION update_notes_search_vector();

-- Create materialized view for joined note data
CREATE MATERIALIZED VIEW notes_with_details AS
SELECT 
    n.id,
    n.body,
    n.shared,
    n.driver_id,
    n.session_id,
    n.category,
    n.created_at,
    n.updated_at,
    n.search_vector,
    
    -- Driver info
    d.name as driver_name,
    
    -- Session info
    s.type as session_type,
    s.date as session_date,
    
    -- Track info
    t.name as track_name,
    t.type as track_type,
    
    -- Series info
    ser.name as series_name,
    
    -- Aggregate counts
    COALESCE(likes_count.count, 0) as likes_count,
    COALESCE(replies_count.count, 0) as replies_count,
    COALESCE(media_count.count, 0) as media_count,
    
    -- Tags as array
    COALESCE(tags_array.tags, '{}') as tags,
    
    -- Media as array
    COALESCE(media_array.media, '{}') as media

FROM notes n
LEFT JOIN drivers d ON n.driver_id = d.id
LEFT JOIN sessions s ON n.session_id = s.id
LEFT JOIN tracks t ON s.track_id = t.id
LEFT JOIN series ser ON (s.series_id = ser.id OR d.series_id = ser.id)
LEFT JOIN (
    SELECT note_id, COUNT(*) as count
    FROM likes
    GROUP BY note_id
) likes_count ON n.id = likes_count.note_id
LEFT JOIN (
    SELECT note_id, COUNT(*) as count
    FROM replies
    GROUP BY note_id
) replies_count ON n.id = replies_count.note_id
LEFT JOIN (
    SELECT note_id, COUNT(*) as count
    FROM media
    GROUP BY note_id
) media_count ON n.id = media_count.note_id
LEFT JOIN (
    SELECT nt.note_id, array_agg(
        json_build_object(
            'id', tg.id,
            'label', tg.label,
            'created_at', tg.created_at,
            'updated_at', tg.updated_at
        )
    ) as tags
    FROM note_tags nt
    JOIN tags tg ON nt.tag_id = tg.id
    GROUP BY nt.note_id
) tags_array ON n.id = tags_array.note_id
LEFT JOIN (
    SELECT m.note_id, array_agg(
        json_build_object(
            'id', m.id,
            'file_url', m.file_url,
            'type', m.type,
            'size_mb', m.size_mb,
            'filename', m.filename,
            'created_at', m.created_at,
            'updated_at', m.updated_at
        )
    ) as media
    FROM media m
    GROUP BY m.note_id
) media_array ON n.id = media_array.note_id;

-- Create indexes on materialized view
CREATE INDEX idx_notes_with_details_created_at ON notes_with_details(created_at DESC);
CREATE INDEX idx_notes_with_details_shared ON notes_with_details(shared);
CREATE INDEX idx_notes_with_details_driver_id ON notes_with_details(driver_id);
CREATE INDEX idx_notes_with_details_session_id ON notes_with_details(session_id);
CREATE INDEX idx_notes_with_details_category ON notes_with_details(category);
CREATE INDEX idx_notes_with_details_search_vector ON notes_with_details USING gin(search_vector);

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_notes_with_details()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY notes_with_details;
END;
$$ LANGUAGE plpgsql;

-- Create RLS policies (for future multi-user support)
ALTER TABLE tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE series ENABLE ROW LEVEL SECURITY;
ALTER TABLE drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE media ENABLE ROW LEVEL SECURITY;
ALTER TABLE note_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE replies ENABLE ROW LEVEL SECURITY;

-- For now, allow all operations (single-user mode)
CREATE POLICY "Allow all operations" ON tracks FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON series FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON drivers FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON sessions FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON tags FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON notes FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON media FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON note_tags FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON likes FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON replies FOR ALL USING (true);

-- Setup storage buckets for media files
INSERT INTO storage.buckets (id, name, public) VALUES 
    ('racing-notes-v5-media', 'racing-notes-v5-media', true);

-- Create storage policy for media bucket
CREATE POLICY "Allow all operations on media bucket"
    ON storage.objects FOR ALL
    USING (bucket_id = 'racing-notes-v5-media');

-- Create view for easy querying
CREATE VIEW notes_feed AS
SELECT * FROM notes_with_details
ORDER BY created_at DESC;

-- Create view for media search
CREATE VIEW media_search AS
SELECT 
    m.*,
    n.body as note_body,
    n.category as note_category,
    n.created_at as note_created_at,
    d.name as driver_name,
    t.name as track_name,
    ser.name as series_name
FROM media m
JOIN notes n ON m.note_id = n.id
LEFT JOIN drivers d ON n.driver_id = d.id
LEFT JOIN sessions s ON n.session_id = s.id
LEFT JOIN tracks t ON s.track_id = t.id
LEFT JOIN series ser ON (s.series_id = ser.id OR d.series_id = ser.id)
ORDER BY m.created_at DESC; 