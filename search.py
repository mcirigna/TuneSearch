#!/usr/bin/python3

import psycopg2
import re
import string
import sys

_PUNCTUATION = frozenset(string.punctuation)

def _remove_punc(token):
    """Removes punctuation from start/end of token."""
    i = 0
    j = len(token) - 1
    idone = False
    jdone = False
    while i <= j and not (idone and jdone):
        if token[i] in _PUNCTUATION and not idone:
            i += 1
        else:
            idone = True
        if token[j] in _PUNCTUATION and not jdone:
            j -= 1
        else:
            jdone = True
    return "" if i > j else token[i:(j+1)]

def _get_tokens(query):
    rewritten_query = []
    tokens = re.split('[ \n\r]+', query)
    for token in tokens:
        cleaned_token = _remove_punc(token)
        if cleaned_token:
            if "'" in cleaned_token:
                cleaned_token = cleaned_token.replace("'", "''")
            rewritten_query.append(cleaned_token)
    return rewritten_query

def search(query, query_type, page=0, new=True):
    tokens = _get_tokens(query)

    if new:
        # CREATE VIEW

        # collect tfidf scores for query
        scoreQuery = "SELECT song_id, COUNT(DISTINCT token) AS token_count, SUM(score) AS score FROM tfidf "
        for i in range (0, len(tokens)):
            if i == 0:
                scoreQuery += "WHERE "
            
            scoreQuery += "token=%s "
        
            lastToken = len(tokens) - 1
        
            if i != lastToken:
                scoreQuery += "OR "
            else:
                scoreQuery += "GROUP BY song_id ORDER BY score DESC"

            # join scores with song_name, artist_name, and page_link
        viewQuery = "DROP MATERIALIZED VIEW IF EXISTS song_results; CREATE MATERIALIZED VIEW IF NOT EXISTS song_results AS SELECT song_name, artist_name, page_link FROM ({0}) AS score JOIN song ON score.song_id=song.song_id JOIN artist ON song.artist_id=artist.artist_id ".format(scoreQuery)

        # and vs or query
        if query_type == "and":
            viewQuery += "WHERE token_count={0} ORDER BY score DESC;".format(len(tokens))
        else:
            viewQuery += "ORDER BY score DESC;"

        # execute queries
        try:
            conn = psycopg2.connect(user="postgres",
                            password="2332",
                            host="127.0.0.1",
                            port="5432",
                            database="tunesearch"
            )
            cur = conn.cursor()
            cur.execute(viewQuery, tokens)
            conn.commit()
        except psycopg2.Error as err:
            print("ME! Database Error: {0}".format(err))
        finally:
            cur.close()
            conn.close()


    # Search View
    countQuery = "SELECT COUNT(*) FROM song_results;"
    searchQuery = "SELECT * FROM song_results LIMIT %s OFFSET %s;"

    # input validation
    page = 0 if page < 0 else page
    offset = page * 20
    songcount = 0
    # validate offset
    try:
        conn = psycopg2.connect(user="postgres",
                            password="2332",
                            host="127.0.0.1",
                            port="5432",
                            database="tunesearch"
        )
        cur = conn.cursor()
        cur.execute(countQuery)
        count = cur.fetchone()
        songcount = count[0]
        offset = 0 if offset >= songcount else offset
        cur.execute(searchQuery, (20, offset))
        songs = cur.fetchall()
    except psycopg2.Error as err:
        print("ME! Database Error: {0}".format(err))
    finally:
        cur.close()
        conn.close()

    """
    1. Connect to the Postgres database.
    2. Graciously handle any errors that may occur (look into try/except/finally).
    3. Close any database connections when you're done.
    4. Write queries so that they are not vulnerable to SQL injections.
    5. The parameters passed to the search function may need to be changed for 1B. 
    """
    ret = { 'songcount': songcount, 'offset': offset, 'songs': songs, 'page': page }
    return ret



if __name__ == "__main__":
    if len(sys.argv) > 2:
        result = search(' '.join(sys.argv[2:]), sys.argv[1].lower())
        print(result)
    else:
        print("USAGE: python3 search.py [or|and] term1 term2 ...")

