-- PitchIQ SQLite Schema
-- Stores player analysis sessions so users can revisit past results.

CREATE TABLE IF NOT EXISTS analysis_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_token TEXT    NOT NULL UNIQUE,
    player_name   TEXT    NOT NULL DEFAULT 'Anonymous',
    player_age    INTEGER,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Raw attributes (1-99)
    pace          INTEGER NOT NULL,
    shooting      INTEGER NOT NULL,
    passing       INTEGER NOT NULL,
    dribbling     INTEGER NOT NULL,
    defending     INTEGER NOT NULL,
    physical      INTEGER NOT NULL,
    stamina       INTEGER NOT NULL,
    strength      INTEGER NOT NULL,
    agility       INTEGER NOT NULL,
    vision        INTEGER NOT NULL,

    -- Computed results (stored as JSON text)
    predictions   TEXT,   -- JSON: [{position, confidence}, ...]
    gap_analysis  TEXT,   -- JSON: {position, gaps, strengths, weaknesses}
    training_plan TEXT,   -- JSON: {drills, weekly_plan, ...}
    cluster_info  TEXT    -- JSON: {cluster_id, cluster_size, ...}
);

CREATE INDEX IF NOT EXISTS idx_sessions_token
    ON analysis_sessions(session_token);

CREATE INDEX IF NOT EXISTS idx_sessions_created
    ON analysis_sessions(created_at);
