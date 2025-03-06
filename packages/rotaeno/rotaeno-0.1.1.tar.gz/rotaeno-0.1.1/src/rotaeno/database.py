import sqlite3
from thefuzz import fuzz
from . import config

class songAlias:
    def __init__(self, database_path):
        self.database_path = database_path
        self.initDatabase()
        self.conn = sqlite3.connect(self.database_path, check_same_thread=False)
    
    def initDatabase(self):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS song_alias (
                alias TEXT PRIMARY KEY,
                id TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def getSongID(self, songAlias):
        cursor = self.conn.cursor()
        cursor.execute("SELECT alias, id FROM song_alias")
        records = cursor.fetchall()
        
        res = {}
        if records:
            aliases = [record[0] for record in records]
            match = []
            for alias in aliases:
                match.append((alias, fuzz.token_set_ratio(songAlias, alias)))
            if match:
                for i in match:
                    if i[1] >= 80:
                        cursor.execute("SELECT id FROM song_alias WHERE alias = ?", (i[0],))
                        result = cursor.fetchone()
                        if result is None: continue
                        res[i[0]] = result[0]
            if len(res) > 1:
                for i in res:
                    if i.lower() == songAlias.lower(): return {i: res[i]}
        return res
    
    def addSongAlias(self, songAlias, songID):
        try:
            self.conn.cursor().execute("INSERT INTO song_alias (alias, id) VALUES (?, ?)", (songAlias, songID))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Error: The alias '{songAlias}' already exists.")
    
    def delSongAlias(self, songAlias):
        self.conn.cursor().execute("DELETE FROM song_alias WHERE alias = ?", (songAlias,))
        self.conn.commit()

class songData:
    def __init__(self, database_path):
        self.database_path = database_path
        self.initDatabase()
        self.conn = sqlite3.connect(self.database_path, check_same_thread=False)
    
    def initDatabase(self):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS song_levels (
                id TEXT PRIMARY KEY,
                I FLOAT NOT NULL,
                II FLOAT NOT NULL,
                III FLOAT NOT NULL,
                IV FLOAT NOT NULL,
                IV_Alpha FLOAT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def addSong(self, songID, songTitle, songArtist, songLevels):
        try:
            self.conn.cursor().execute("INSERT INTO songs (id, title, artist) VALUES (?, ?, ?)", (songID, songTitle, songArtist))
            self.conn.cursor().execute("INSERT INTO song_levels (id, I, II, III, IV, IV_Alpha) VALUES (?, ?, ?, ?, ?, ?)",
                                       (songID, songLevels["I"], songLevels["II"], songLevels["III"], songLevels["IV"], songLevels["IV_Alpha"] if "IV_Alpha" in songLevels else 0))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Error: The song '{songID}' already exists.")
    
    def delSong(self, songID):
        self.conn.cursor().execute("DELETE FROM songs WHERE id = ?", (songID,))
        self.conn.commit()
    
    def getSong(self, songID):
        res = {}
        cursor = self.conn.cursor()
        cursor.execute("SELECT title, artist FROM songs WHERE id = ?", (songID,))
        result = cursor.fetchone()
        if result is None: return res
        res["id"] = songID
        res["title"] = result[0]
        res["artist"] = result[1]
        cursor.execute("SELECT I, II, III, IV, IV_Alpha FROM song_levels WHERE id = ?", (songID,))
        result = cursor.fetchone()
        if result is None: return res
        res["levels"] = [
            result[0], # I
            result[1], # II
            result[2], # III
            result[3], # IV
            result[4] # IV_Alpha
        ]
        res["__levels"] = {
            "I": result[0], # I
            "II": result[1], # II
            "III": result[2], # III
            "IV": result[3], # IV
            "IV_Alpha": result[4] # IV_Alpha
        }
        return res
    
    def getSongsRatingRealRange(self, songRatingReal1, songRatingReal2):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, I, II, III, IV, IV_Alpha
            FROM song_levels
            WHERE (I BETWEEN ? AND ?)
            OR (II BETWEEN ? AND ?)
            OR (III BETWEEN ? AND ?)
            OR (IV BETWEEN ? AND ?)
            OR (IV_Alpha BETWEEN ? AND ?)
        ''', (songRatingReal1, songRatingReal2, songRatingReal1, songRatingReal2, songRatingReal1, songRatingReal2, songRatingReal1, songRatingReal2, songRatingReal1, songRatingReal2))
        # return cursor.fetchall()
        res = []
        level_map = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "IV_Alpha"}
        for row in cursor.fetchall():
            tmp = {}
            for level in level_map:
                if row[level] >= songRatingReal1 and row[level] <= songRatingReal2 and row[level] != 0:
                    tmp["id"] = row[0]
                    try:
                        tmp["levels"].append(level_map[level])
                    except:
                        tmp["levels"] = [level_map[level]]
            if tmp != {}: res.append(tmp)
        return res

songAlias = songAlias(config.songAliasDBPath)
songData = songData(config.songDataDBPath)
