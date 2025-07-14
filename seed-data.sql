-- Racing Notes Desktop App V5 - Seed Data
-- This file populates the database with sample NASCAR data

-- Insert NASCAR Series
INSERT INTO series (id, name) VALUES
    ('11111111-1111-1111-1111-111111111111', 'NASCAR Cup Series'),
    ('22222222-2222-2222-2222-222222222222', 'NASCAR Xfinity Series'),
    ('33333333-3333-3333-3333-333333333333', 'NASCAR Craftsman Truck Series');

-- Insert Tracks
INSERT INTO tracks (id, name, type) VALUES
    -- Superspeedways
    ('a1111111-1111-1111-1111-111111111111', 'Daytona International Speedway', 'Superspeedway'),
    ('a2222222-2222-2222-2222-222222222222', 'Talladega Superspeedway', 'Superspeedway'),
    
    -- Intermediate Tracks
    ('b1111111-1111-1111-1111-111111111111', 'Charlotte Motor Speedway', 'Intermediate'),
    ('b2222222-2222-2222-2222-222222222222', 'Las Vegas Motor Speedway', 'Intermediate'),
    ('b3333333-3333-3333-3333-333333333333', 'Kansas Speedway', 'Intermediate'),
    ('b4444444-4444-4444-4444-444444444444', 'Texas Motor Speedway', 'Intermediate'),
    ('b5555555-5555-5555-5555-555555555555', 'Atlanta Motor Speedway', 'Intermediate'),
    ('b6666666-6666-6666-6666-666666666666', 'Homestead-Miami Speedway', 'Intermediate'),
    ('b7777777-7777-7777-7777-777777777777', 'Michigan International Speedway', 'Intermediate'),
    ('b8888888-8888-8888-8888-888888888888', 'Auto Club Speedway', 'Intermediate'),
    
    -- Short Tracks
    ('c1111111-1111-1111-1111-111111111111', 'Martinsville Speedway', 'Short Track'),
    ('c2222222-2222-2222-2222-222222222222', 'Bristol Motor Speedway', 'Short Track'),
    ('c3333333-3333-3333-3333-333333333333', 'Richmond Raceway', 'Short Track'),
    ('c4444444-4444-4444-4444-444444444444', 'Phoenix Raceway', 'Short Track'),
    ('c5555555-5555-5555-5555-555555555555', 'New Hampshire Motor Speedway', 'Short Track'),
    ('c6666666-6666-6666-6666-666666666666', 'Dover Motor Speedway', 'Short Track'),
    
    -- Road Courses
    ('d1111111-1111-1111-1111-111111111111', 'Watkins Glen International', 'Road Course'),
    ('d2222222-2222-2222-2222-222222222222', 'Sonoma Raceway', 'Road Course'),
    ('d3333333-3333-3333-3333-333333333333', 'Road America', 'Road Course'),
    ('d4444444-4444-4444-4444-444444444444', 'Charlotte Motor Speedway Roval', 'Road Course'),
    ('d5555555-5555-5555-5555-555555555555', 'Indianapolis Motor Speedway Road Course', 'Road Course'),
    ('d6666666-6666-6666-6666-666666666666', 'Circuit of the Americas', 'Road Course'),
    ('d7777777-7777-7777-7777-777777777777', 'Chicago Street Course', 'Road Course'),
    ('d8888888-8888-8888-8888-888888888888', 'Autodromo Hermanos Rodriguez', 'Road Course'),
    
    -- Additional tracks from 2025 schedule
    ('e1111111-1111-1111-1111-111111111111', 'Bowman Gray Stadium', 'Short Track'),
    ('e2222222-2222-2222-2222-222222222222', 'North Wilkesboro Speedway', 'Short Track'),
    ('e3333333-3333-3333-3333-333333333333', 'Nashville Superspeedway', 'Intermediate'),
    ('e4444444-4444-4444-4444-444444444444', 'Iowa Speedway', 'Short Track');

-- Insert NASCAR Cup Series Drivers
INSERT INTO drivers (id, name, series_id) VALUES
    ('cup01111-1111-1111-1111-111111111111', 'Kyle Larson', '11111111-1111-1111-1111-111111111111'),
    ('cup02222-2222-2222-2222-222222222222', 'Alex Bowman', '11111111-1111-1111-1111-111111111111'),
    ('cup03333-3333-3333-3333-333333333333', 'Ross Chastain', '11111111-1111-1111-1111-111111111111'),
    ('cup04444-4444-4444-4444-444444444444', 'Daniel Suarez', '11111111-1111-1111-1111-111111111111'),
    ('cup05555-5555-5555-5555-555555555555', 'Austin Dillon', '11111111-1111-1111-1111-111111111111'),
    ('cup06666-6666-6666-6666-666666666666', 'Connor Zilisch', '11111111-1111-1111-1111-111111111111'),
    ('cup07777-7777-7777-7777-777777777777', 'Carson Kvapil', '11111111-1111-1111-1111-111111111111'),
    ('cup08888-8888-8888-8888-888888888888', 'Austin Hill', '11111111-1111-1111-1111-111111111111'),
    ('cup09999-9999-9999-9999-999999999999', 'Jesse Love', '11111111-1111-1111-1111-111111111111'),
    ('cup10000-0000-0000-0000-000000000000', 'Nick Sanchez', '11111111-1111-1111-1111-111111111111'),
    ('cup11111-1111-1111-1111-111111111111', 'Daniel Dye', '11111111-1111-1111-1111-111111111111'),
    ('cup12222-2222-2222-2222-222222222222', 'Grant Enfinger', '11111111-1111-1111-1111-111111111111'),
    ('cup13333-3333-3333-3333-333333333333', 'Daniel Hemric', '11111111-1111-1111-1111-111111111111'),
    ('cup14444-4444-4444-4444-444444444444', 'Connor Mosack', '11111111-1111-1111-1111-111111111111'),
    ('cup15555-5555-5555-5555-555555555555', 'Kaden Honeycutt', '11111111-1111-1111-1111-111111111111'),
    ('cup16666-6666-6666-6666-666666666666', 'Rajah Caruth', '11111111-1111-1111-1111-111111111111'),
    ('cup17777-7777-7777-7777-777777777777', 'Andres Perez', '11111111-1111-1111-1111-111111111111'),
    ('cup18888-8888-8888-8888-888888888888', 'Matt Mills', '11111111-1111-1111-1111-111111111111'),
    ('cup19999-9999-9999-9999-999999999999', 'Dawson Sutton', '11111111-1111-1111-1111-111111111111'),
    ('cup20000-0000-0000-0000-000000000000', 'Tristan McKee', '11111111-1111-1111-1111-111111111111'),
    ('cup21111-1111-1111-1111-111111111111', 'Hailie Meza', '11111111-1111-1111-1111-111111111111'),
    ('cup22222-2222-2222-2222-222222222222', 'Corey Day', '11111111-1111-1111-1111-111111111111'),
    ('cup23333-3333-3333-3333-333333333333', 'Ben Maier', '11111111-1111-1111-1111-111111111111'),
    ('cup24444-4444-4444-4444-444444444444', 'Tyler Reif', '11111111-1111-1111-1111-111111111111'),
    ('cup25555-5555-5555-5555-555555555555', 'Brenden Queen', '11111111-1111-1111-1111-111111111111');

-- Insert NASCAR Xfinity Series Drivers
INSERT INTO drivers (id, name, series_id) VALUES
    ('xfn01111-1111-1111-1111-111111111111', 'Austin Cindric', '22222222-2222-2222-2222-222222222222'),
    ('xfn02222-2222-2222-2222-222222222222', 'Ty Gibbs', '22222222-2222-2222-2222-222222222222'),
    ('xfn03333-3333-3333-3333-333333333333', 'AJ Allmendinger', '22222222-2222-2222-2222-222222222222'),
    ('xfn04444-4444-4444-4444-444444444444', 'Noah Gragson', '22222222-2222-2222-2222-222222222222'),
    ('xfn05555-5555-5555-5555-555555555555', 'Justin Allgaier', '22222222-2222-2222-2222-222222222222'),
    ('xfn06666-6666-6666-6666-666666666666', 'Sam Mayer', '22222222-2222-2222-2222-222222222222'),
    ('xfn07777-7777-7777-7777-777777777777', 'Josh Berry', '22222222-2222-2222-2222-222222222222'),
    ('xfn08888-8888-8888-8888-888888888888', 'Brandon Jones', '22222222-2222-2222-2222-222222222222'),
    ('xfn09999-9999-9999-9999-999999999999', 'Sheldon Creed', '22222222-2222-2222-2222-222222222222'),
    ('xfn10000-0000-0000-0000-000000000000', 'Riley Herbst', '22222222-2222-2222-2222-222222222222');

-- Insert NASCAR Truck Series Drivers
INSERT INTO drivers (id, name, series_id) VALUES
    ('trk01111-1111-1111-1111-111111111111', 'Corey Heim', '33333333-3333-3333-3333-333333333333'),
    ('trk02222-2222-2222-2222-222222222222', 'Christian Eckes', '33333333-3333-3333-3333-333333333333'),
    ('trk03333-3333-3333-3333-333333333333', 'Chandler Smith', '33333333-3333-3333-3333-333333333333'),
    ('trk04444-4444-4444-4444-444444444444', 'Ty Majeski', '33333333-3333-3333-3333-333333333333'),
    ('trk05555-5555-5555-5555-555555555555', 'Ben Rhodes', '33333333-3333-3333-3333-333333333333'),
    ('trk06666-6666-6666-6666-666666666666', 'Zane Smith', '33333333-3333-3333-3333-333333333333'),
    ('trk07777-7777-7777-7777-777777777777', 'Stewart Friesen', '33333333-3333-3333-3333-333333333333'),
    ('trk08888-8888-8888-8888-888888888888', 'Matt Crafton', '33333333-3333-3333-3333-333333333333'),
    ('trk09999-9999-9999-9999-999999999999', 'Carson Hocevar', '33333333-3333-3333-3333-333333333333'),
    ('trk10000-0000-0000-0000-000000000000', 'Tyler Ankrum', '33333333-3333-3333-3333-333333333333');

-- Insert Common Racing Tags
INSERT INTO tags (id, label) VALUES
    ('tag01111-1111-1111-1111-111111111111', 'restart'),
    ('tag02222-2222-2222-2222-222222222222', 'aero'),
    ('tag03333-3333-3333-3333-333333333333', 'pit-strategy'),
    ('tag04444-4444-4444-4444-444444444444', 'tire-wear'),
    ('tag05555-5555-5555-5555-555555555555', 'fuel-mileage'),
    ('tag06666-6666-6666-6666-666666666666', 'setup'),
    ('tag07777-7777-7777-7777-777777777777', 'handling'),
    ('tag08888-8888-8888-8888-888888888888', 'qualifying'),
    ('tag09999-9999-9999-9999-999999999999', 'practice'),
    ('tag10000-0000-0000-0000-000000000000', 'race'),
    ('tag11111-1111-1111-1111-111111111111', 'caution'),
    ('tag12222-2222-2222-2222-222222222222', 'debris'),
    ('tag13333-3333-3333-3333-333333333333', 'crash'),
    ('tag14444-4444-4444-4444-444444444444', 'weather'),
    ('tag15555-5555-5555-5555-555555555555', 'track-position'),
    ('tag16666-6666-6666-6666-666666666666', 'drafting'),
    ('tag17777-7777-7777-7777-777777777777', 'overtake'),
    ('tag18888-8888-8888-8888-888888888888', 'pole-position'),
    ('tag19999-9999-9999-9999-999999999999', 'championship'),
    ('tag20000-0000-0000-0000-000000000000', 'playoff'),
    ('tag21111-1111-1111-1111-111111111111', 'stage-winner'),
    ('tag22222-2222-2222-2222-222222222222', 'leader'),
    ('tag23333-3333-3333-3333-333333333333', 'lap-down'),
    ('tag24444-4444-4444-4444-444444444444', 'green-flag'),
    ('tag25555-5555-5555-5555-555555555555', 'checkered-flag'),
    ('tag26666-6666-6666-6666-666666666666', 'strategy'),
    ('tag27777-7777-7777-7777-777777777777', 'speed'),
    ('tag28888-8888-8888-8888-888888888888', 'mechanical'),
    ('tag29999-9999-9999-9999-999999999999', 'suspension'),
    ('tag30000-0000-0000-0000-000000000000', 'engine');

-- Insert Sample Sessions (2025 NASCAR Schedule)
INSERT INTO sessions (id, date, type, track_id, series_id) VALUES
    -- Daytona 500 Weekend 2025
    ('ses01111-1111-1111-1111-111111111111', '2025-02-14 10:00:00-05', 'Practice', 'a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111'),
    ('ses02222-2222-2222-2222-222222222222', '2025-02-15 14:00:00-05', 'Qualifying', 'a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111'),
    ('ses03333-3333-3333-3333-333333333333', '2025-02-16 14:30:00-05', 'Race', 'a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111'),
    
    -- Atlanta Weekend 2025
    ('ses04444-4444-4444-4444-444444444444', '2025-02-22 10:00:00-05', 'Practice', 'b5555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111'),
    ('ses05555-5555-5555-5555-555555555555', '2025-02-23 14:00:00-05', 'Qualifying', 'b5555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111'),
    ('ses06666-6666-6666-6666-666666666666', '2025-02-23 14:30:00-05', 'Race', 'b5555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111'),
    
    -- Las Vegas Weekend 2025
    ('ses07777-7777-7777-7777-777777777777', '2025-03-01 10:00:00-08', 'Practice', 'b2222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111'),
    ('ses08888-8888-8888-8888-888888888888', '2025-03-02 14:00:00-08', 'Qualifying', 'b2222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111'),
    ('ses09999-9999-9999-9999-999999999999', '2025-03-02 14:30:00-08', 'Race', 'b2222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111'),
    
    -- Circuit of the Americas Weekend 2025
    ('ses10000-0000-0000-0000-000000000000', '2025-03-07 10:00:00-06', 'Practice', 'd6666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111'),
    ('ses11111-1111-1111-1111-111111111111', '2025-03-08 14:00:00-06', 'Qualifying', 'd6666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111'),
    ('ses12222-2222-2222-2222-222222222222', '2025-03-09 14:30:00-06', 'Race', 'd6666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111'),
    
    -- Phoenix Weekend 2025
    ('ses13333-3333-3333-3333-333333333333', '2025-03-14 10:00:00-07', 'Practice', 'c4444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111'),
    ('ses14444-4444-4444-4444-444444444444', '2025-03-15 14:00:00-07', 'Qualifying', 'c4444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111'),
    ('ses15555-5555-5555-5555-555555555555', '2025-03-16 14:30:00-07', 'Race', 'c4444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111');

-- Insert Sample Notes
INSERT INTO notes (id, body, shared, driver_id, session_id, category) VALUES
    ('note01111-1111-1111-1111-111111111111', 
     'Great qualifying run! The car was handling really well in turns 1 and 2. Need to work on the exit speed for the race setup.',
     true, 
     'cup01111-1111-1111-1111-111111111111',
     'ses02222-2222-2222-2222-222222222222',
     'Track Specific'),
    
    ('note02222-2222-2222-2222-222222222222',
     'Pit strategy will be crucial tomorrow. The tire wear is higher than expected, especially on the right rear. Might need to adjust the air pressure.',
     true,
     'cup03333-3333-3333-3333-333333333333',
     'ses01111-1111-1111-1111-111111111111',
     'Strategy'),
    
    ('note03333-3333-3333-3333-333333333333',
     'Watching the draft patterns - seems like the outside line is stronger today. Track position will be key for the 500.',
     true,
     NULL,
     'ses01111-1111-1111-1111-111111111111',
     'General'),
    
    ('note04444-4444-4444-4444-444444444444',
     'Aero package seems to be working well. Cars are closer together than last year. Should make for exciting racing!',
     true,
     NULL,
     'ses03333-3333-3333-3333-333333333333',
     'General'),
    
    ('note05555-5555-5555-5555-555555555555',
     'Las Vegas practice notes: Track is gripping up nicely. Might see some good battles for position tonight.',
     true,
     'cup02222-2222-2222-2222-222222222222',
     'ses07777-7777-7777-7777-777777777777',
     'Track Specific'),
    
    ('note06666-6666-6666-6666-666666666666',
     'Fuel window is about 80 laps. Green flag stops around lap 60 and 140 if we go green. Weather looks good.',
     false,
     NULL,
     'ses09999-9999-9999-9999-999999999999',
     'Strategy'),
    
    ('note07777-7777-7777-7777-777777777777',
     'COTA is a challenging road course. The elevation changes and technical sections will separate the field. Braking zones are critical.',
     true,
     'cup04444-4444-4444-4444-444444444444',
     'ses10000-0000-0000-0000-000000000000',
     'Track Specific'),
    
    ('note08888-8888-8888-8888-888888888888',
     'Phoenix restart zones are key. Clean air is premium. Track position battle will be intense in the desert.',
     true,
     'cup01111-1111-1111-1111-111111111111',
     'ses13333-3333-3333-3333-333333333333',
     'Strategy'),
    
    ('note09999-9999-9999-9999-999999999999',
     'Atlanta repave has changed everything. Multiple grooves and side-by-side racing is back. Should be exciting!',
     true,
     'cup05555-5555-5555-5555-555555555555',
     'ses04444-4444-4444-4444-444444444444',
     'Track Specific'),
    
    ('note10000-0000-0000-0000-000000000000',
     'Young drivers are showing a lot of promise this season. The future of NASCAR looks bright with this talent.',
     true,
     'cup06666-6666-6666-6666-666666666666',
     NULL,
     'General');

-- Insert Sample Note-Tag Relationships
INSERT INTO note_tags (note_id, tag_id) VALUES
    ('note01111-1111-1111-1111-111111111111', 'tag08888-8888-8888-8888-888888888888'), -- qualifying
    ('note01111-1111-1111-1111-111111111111', 'tag06666-6666-6666-6666-666666666666'), -- setup
    ('note01111-1111-1111-1111-111111111111', 'tag07777-7777-7777-7777-777777777777'), -- handling
    
    ('note02222-2222-2222-2222-222222222222', 'tag03333-3333-3333-3333-333333333333'), -- pit-strategy
    ('note02222-2222-2222-2222-222222222222', 'tag04444-4444-4444-4444-444444444444'), -- tire-wear
    ('note02222-2222-2222-2222-222222222222', 'tag26666-6666-6666-6666-666666666666'), -- strategy
    
    ('note03333-3333-3333-3333-333333333333', 'tag16666-6666-6666-6666-666666666666'), -- drafting
    ('note03333-3333-3333-3333-333333333333', 'tag15555-5555-5555-5555-555555555555'), -- track-position
    
    ('note04444-4444-4444-4444-444444444444', 'tag02222-2222-2222-2222-222222222222'), -- aero
    ('note04444-4444-4444-4444-444444444444', 'tag10000-0000-0000-0000-000000000000'), -- race
    
    ('note05555-5555-5555-5555-555555555555', 'tag09999-9999-9999-9999-999999999999'), -- practice
    ('note05555-5555-5555-5555-555555555555', 'tag15555-5555-5555-5555-555555555555'), -- track-position
    
    ('note06666-6666-6666-6666-666666666666', 'tag05555-5555-5555-5555-555555555555'), -- fuel-mileage
    ('note06666-6666-6666-6666-666666666666', 'tag26666-6666-6666-6666-666666666666'), -- strategy
    ('note06666-6666-6666-6666-666666666666', 'tag14444-4444-4444-4444-444444444444'), -- weather
    
    ('note07777-7777-7777-7777-777777777777', 'tag10000-0000-0000-0000-000000000000'), -- race
    ('note07777-7777-7777-7777-777777777777', 'tag27777-7777-7777-7777-777777777777'), -- speed
    
    ('note08888-8888-8888-8888-888888888888', 'tag01111-1111-1111-1111-111111111111'), -- restart
    ('note08888-8888-8888-8888-888888888888', 'tag15555-5555-5555-5555-555555555555'), -- track-position
    ('note08888-8888-8888-8888-888888888888', 'tag26666-6666-6666-6666-666666666666'), -- strategy
    
    ('note09999-9999-9999-9999-999999999999', 'tag10000-0000-0000-0000-000000000000'), -- race
    ('note09999-9999-9999-9999-999999999999', 'tag27777-7777-7777-7777-777777777777'), -- speed
    ('note09999-9999-9999-9999-999999999999', 'tag15555-5555-5555-5555-555555555555'), -- track-position
    
    ('note10000-0000-0000-0000-000000000000', 'tag22222-2222-2222-2222-222222222222'); -- leader

-- Refresh the materialized view to include the seed data
REFRESH MATERIALIZED VIEW notes_with_details;

-- Insert sample user preferences (for future use)
-- This would be useful when multi-user support is added
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- For future multi-user support
    theme VARCHAR(20) DEFAULT 'light',
    notifications_enabled BOOLEAN DEFAULT true,
    default_series_id UUID REFERENCES series(id),
    favorite_drivers UUID[] DEFAULT '{}',
    favorite_tracks UUID[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default preferences
INSERT INTO user_preferences (user_id, theme, default_series_id) VALUES
    (NULL, 'light', '11111111-1111-1111-1111-111111111111');

-- Create some sample likes and replies for demonstration
INSERT INTO likes (id, note_id, user_id) VALUES
    ('like01111-1111-1111-1111-111111111111', 'note01111-1111-1111-1111-111111111111', NULL),
    ('like02222-2222-2222-2222-222222222222', 'note01111-1111-1111-1111-111111111111', NULL),
    ('like03333-3333-3333-3333-333333333333', 'note02222-2222-2222-2222-222222222222', NULL),
    ('like04444-4444-4444-4444-444444444444', 'note03333-3333-3333-3333-333333333333', NULL),
    ('like05555-5555-5555-5555-555555555555', 'note04444-4444-4444-4444-444444444444', NULL),
    ('like06666-6666-6666-6666-666666666666', 'note04444-4444-4444-4444-444444444444', NULL),
    ('like07777-7777-7777-7777-777777777777', 'note05555-5555-5555-5555-555555555555', NULL);

INSERT INTO replies (id, note_id, reply_text, user_id) VALUES
    ('reply01111-1111-1111-1111-111111111111', 'note01111-1111-1111-1111-111111111111', 'Great insight! The car setup looked really balanced during that session.', NULL),
    ('reply02222-2222-2222-2222-222222222222', 'note02222-2222-2222-2222-222222222222', 'Agreed on the tire strategy. That right rear deg was concerning in practice.', NULL),
    ('reply03333-3333-3333-3333-333333333333', 'note03333-3333-3333-3333-333333333333', 'The outside line was definitely the preferred groove. Should be exciting!', NULL),
    ('reply04444-4444-4444-4444-444444444444', 'note04444-4444-4444-4444-444444444444', 'This new aero package is producing some great racing. Love the close competition!', NULL);

-- Final refresh to ensure all data is properly indexed
REFRESH MATERIALIZED VIEW notes_with_details; 