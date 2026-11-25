import database_connection as database

connection = database.get_connection()
cursor = database.get_cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mbid TEXT UNIQUE,
        deezer_id INTEGER UNIQUE,
        audiodb_id TEXT UNIQUE,
        name TEXT NOT NULL,
        year_started TEXT,
        year_born TEXT,
        year_died TEXT,
        followers TEXT,
        popularity_percentage TEXT,
        style TEXT,
        audiodb_genre TEXT,
        mood TEXT,
        biography TEXT,
        gender TEXT,
        members TEXT,
        origin TEXT,
        origin_country TEXT,
        artist_label_company TEXT,
        label_company_audiodb_id TEXT,
        last_updated DATETIME,
        thumbnail_url TEXT,
        logo_url TEXT,
        cutout_url TEXT,
        clear_art_url TEXT,
        wide_thumbnail_url TEXT,
        fan_art_1_url TEXT,
        fan_art_2_url TEXT,
        fan_art_3_url TEXT,
        fan_art_4_url TEXT,
        artist_banner_url TEXT
    );"""
)

cursor.execute(
    """CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        genre TEXT UNIQUE,
        image_url TEXT
    );
    """
)

cursor.execute(
    """CREATE TABLE IF NOT EXISTS artist_genres (
        artist_id INTEGER,
        genre_id INTEGER,
        
        PRIMARY KEY (artist_id, genre_id),
    
        FOREIGN KEY (artist_id)
        REFERENCES artists(id),
        
        FOREIGN KEY (genre_id)
        REFERENCES genres(id)
    
    );"""
)

cursor.execute(
    """CREATE TABLE IF NOT EXISTS releases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mbid TEXT UNIQUE,
        audiodb_id TEXT UNIQUE,
        deezer_id INTEGER UNIQUE,
        genre_id INTEGER,
        deezer_genre_id INTEGER,
        artist_id INTEGER,
        title TEXT NOT NULL,
        type TEXT,
        release_date TEXT,
        explicit BOOL,
        release_label_company TEXT,
        release_label_company_audiodb_id TEXT,
        description TEXT,
        popularity_percentage TEXT,
        mood TEXT,
        tempo TEXT,
        thumbnail_url TEXT,
        back_url TEXT,
        cd_art_url TEXT,
        spine_url TEXT,
        d_case_url TEXT,
        d_flat_url TEXT,
        d_face_url TEXT,
        d_thumbnail_url TEXT,
        
        FOREIGN KEY (artist_id)
        REFERENCES artists(id),
        
        FOREIGN KEY (genre_id)
        REFERENCES genres(id)
    
    );"""
)

cursor.execute(
    """CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_type TEXT,
        album TEXT,
        title TEXT,
        artist TEXT,
        release_date TEXT
    );"""
)

cursor.execute(
    """CREATE TABLE IF NOT EXISTS cache (
        cache_key TEXT PRIMARY KEY,
        api_source TEXT,
        json_response TEXT,
        timestamp DATETIME
    );"""
)

connection.commit()
cursor.close()