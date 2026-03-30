"""
SQLite Schema definitions for Sky Sentinel.
Defines the cross-domain frame_index, normalised detected_objects,
alerts table, and FTS5 virtual tables for advanced text search.
"""

CREATE_FRAME_INDEX_TABLE = """
CREATE TABLE IF NOT EXISTS frame_index (
    frame_id INTEGER PRIMARY KEY,
    timestamp TEXT,
    location_name TEXT,
    latitude REAL,
    longitude REAL,
    altitude_meters REAL,
    is_night INTEGER,
    frame_image_path TEXT,
    raw_vlm_description TEXT,
    activity_description TEXT,
    has_people INTEGER,
    has_vehicles INTEGER,
    vehicle_types_json TEXT,
    person_count INTEGER,
    is_suspicious INTEGER,
    alert_ids_json TEXT,
    processing_timestamp TEXT
);
"""

CREATE_DETECTED_OBJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS detected_objects (
    object_id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id INTEGER,
    object_type TEXT,
    object_colour TEXT,
    object_description TEXT,
    FOREIGN KEY(frame_id) REFERENCES frame_index(frame_id) ON DELETE CASCADE
);
"""

CREATE_ALERTS_TABLE = """
CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    rule_id TEXT,
    frame_id INTEGER,
    timestamp TEXT,
    location_name TEXT,
    severity_level TEXT,
    alert_message TEXT,
    triggered_by TEXT,
    is_resolved INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY(frame_id) REFERENCES frame_index(frame_id) ON DELETE CASCADE
);
"""

# FTS5 Virtual Table for full-text search on VLM descriptions
CREATE_FTS5_VLM_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS vlm_search USING fts5(
    frame_id UNINDEXED,
    raw_vlm_description,
    content='frame_index',
    content_rowid='frame_id'
);
"""

# Triggers to keep the FTS5 table automatically synced with the frame_index table
CREATE_FTS5_TRIGGERS = [
    """
    CREATE TRIGGER IF NOT EXISTS frame_index_ai AFTER INSERT ON frame_index BEGIN
        INSERT INTO vlm_search(rowid, raw_vlm_description) VALUES (new.frame_id, new.raw_vlm_description);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS frame_index_ad AFTER DELETE ON frame_index BEGIN
        INSERT INTO vlm_search(vlm_search, rowid, raw_vlm_description) VALUES('delete', old.frame_id, old.raw_vlm_description);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS frame_index_au AFTER UPDATE ON frame_index BEGIN
        INSERT INTO vlm_search(vlm_search, rowid, raw_vlm_description) VALUES('delete', old.frame_id, old.raw_vlm_description);
        INSERT INTO vlm_search(rowid, raw_vlm_description) VALUES (new.frame_id, new.raw_vlm_description);
    END;
    """
]

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_timestamp ON frame_index(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_location ON frame_index(location_name);",
    "CREATE INDEX IF NOT EXISTS idx_is_night ON frame_index(is_night);",
    "CREATE INDEX IF NOT EXISTS idx_has_vehicles ON frame_index(has_vehicles);",
    "CREATE INDEX IF NOT EXISTS idx_has_people ON frame_index(has_people);"
]

def get_all_schema_statements() -> list[str]:
    """Returns all SQL statements required to initialise the database."""
    statements = [
        CREATE_FRAME_INDEX_TABLE,
        CREATE_DETECTED_OBJECTS_TABLE,
        CREATE_ALERTS_TABLE,
        CREATE_FTS5_VLM_TABLE
    ]
    statements.extend(CREATE_FTS5_TRIGGERS)
    statements.extend(CREATE_INDEXES)
    return statements
