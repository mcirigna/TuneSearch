CREATE TABLE artist (
	artist_id INTEGER PRIMARY KEY,
	artist_name VARCHAR(255)
);


CREATE TABLE token (
	song_id INTEGER,
	token VARCHAR(255),
	count INTEGER,
	PRIMARY KEY (song_id, token)
);

CREATE TABLE song (
	song_id INTEGER PRIMARY KEY,
	artist_id INTEGER REFERENCES artist(artist_id),
	song_name VARCHAR(255),
	page_link VARCHAR(1000)
	/* , FOREIGN KEY (artist_id) REFERENCES artist (artist_id) */
);

CREATE TABLE tfidf (
	song_id INTEGER,
	token VARCHAR(255),
	score FLOAT,
	PRIMARY KEY(song_id, token)
);

\copy artist FROM '/Users/mcirigna/Desktop/artist.csv' DELIMITER ',' QUOTE '"' CSV;
\copy song   FROM '/Users/mcirigna/Desktop/song.csv'   DELIMITER ',' QUOTE '"' CSV;
\copy token  FROM '/Users/mcirigna/Desktop/token.csv'  DELIMITER ',' QUOTE '"' CSV;