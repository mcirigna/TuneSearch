CREATE MATERIALIZED VIEW IF NOT EXISTS songcount AS
       SELECT COUNT(*)
       FROM song;

CREATE TABLE IF NOT EXISTS idf (
    token VARCHAR(255) PRIMARY KEY,
    score INTEGER
);

REFRESH MATERIALIZED VIEW songcount;

INSERT INTO idf (token, score)
SELECT token, LOG((SELECT * FROM songcount) / COUNT(DISTINCT song_id))::REAL AS score
FROM token
GROUP BY token;

INSERT INTO tfidf (song_id, token, score)
SELECT song_id, token.token, count * idf.score AS score
FROM token JOIN idf ON token.token=idf.token;
