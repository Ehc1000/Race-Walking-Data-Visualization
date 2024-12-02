-- Drop existing tables to ensure a clean slate
DROP TABLE IF EXISTS honors;
DROP TABLE IF EXISTS progressions;
DROP TABLE IF EXISTS personal_bests;
DROP TABLE IF EXISTS rankings;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS athletes;

-- Athletes Table
CREATE TABLE IF NOT EXISTS athletes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    profile_image_url TEXT
);

-- Events Table
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL,
    event_title TEXT NOT NULL,
    race_title TEXT,
    race_name TEXT,
    date TEXT,
    country TEXT,
    FOREIGN KEY (athlete_id) REFERENCES athletes (id)
);

-- Rankings Table
CREATE TABLE IF NOT EXISTS rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL,
    event_title TEXT NOT NULL,
    ranking_position INTEGER,
    ranking_score INTEGER,
    weeks_at_position INTEGER,
    FOREIGN KEY (athlete_id) REFERENCES athletes (id)
);

-- Personal Bests Table
CREATE TABLE IF NOT EXISTS personal_bests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL,
    event_title TEXT NOT NULL,
    performance_time TEXT,
    performance_score INTEGER,
    FOREIGN KEY (athlete_id) REFERENCES athletes (id)
);

-- Progressions Table
CREATE TABLE IF NOT EXISTS progressions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL,
    event_title TEXT NOT NULL,
    year INTEGER NOT NULL,
    time TEXT,
    race_name TEXT,
    date TEXT,
    FOREIGN KEY (athlete_id) REFERENCES athletes (id)
);

-- Honors Table
CREATE TABLE IF NOT EXISTS honors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL,
    event_title TEXT NOT NULL,
    placement INTEGER,
    race_title TEXT,
    date TEXT,
    FOREIGN KEY (athlete_id) REFERENCES athletes (id)
);
