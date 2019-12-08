from secret import OMDB_api_key, Guardian_api_key
import sqlite3
import json
import requests
import csv

CACHE_FNAME = "cache.json"
DBNAME = 'final_proj.db'
MOVIE_NAMES_CSV = 'tmdb_5000_credits.csv'

try:
## Open a file with the CACHE_FNAME file name.
    cache_file = open(CACHE_FNAME, 'r')
## Read the file into one big string.
    cache_contents = cache_file.read()
## Load the string into a Python object, saved in a variable called CACHE_DICTION.
    CACHE_DICTION = json.loads(cache_contents)
## Close the file.
    cache_file.close()
# Begin the except clause of the try/except statement:
except:
## Create a variable called CACHE_DICTION and give it the value of an empty dictionary.
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append('{}={}'.format(k, params[k]))
    return baseurl + '?' + "&".join(res)

def get_resp_using_cache(baseurl, params):
    unique_url = params_unique_combination(baseurl, params)
    if unique_url in CACHE_DICTION:
        return CACHE_DICTION[unique_url]
    else:
        resp = requests.get(unique_url)
        CACHE_DICTION[unique_url] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_url]

def create_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(
    """
        CREATE TABLE IF NOT EXISTS Movies (
            id integer PRIMARY KEY AUTOINCREMENT,
            title text,
            year integer,
            runtime integer,
            director text,
            genre text,
            imdbRating real,
            boxOffice integer
        );
    """
    )
    cur.execute(
    """
        CREATE TABLE IF NOT EXISTS Articles (
            id integer PRIMARY KEY AUTOINCREMENT,
            sectionId text,
            sectionName text,
            webPublicationDate text,
            title text,
            webUrl text,
            movieId integer,
            FOREIGN KEY (movieId) REFERENCES Movies (id)
        );
    """
    )
    insert_into_movies = """
        INSERT INTO Movies (title, year, runtime, director, genre, imdbRating, boxOffice) VALUES (?,?,?,?,?,?,?);
    """
    with open(MOVIE_NAMES_CSV, newline="") as csv_file:
        baseurl = "http://www.omdbapi.com/"
        reader = csv.DictReader(csv_file)
        for row in reader:
            params = {
                "t": row['title'],
                "apikey": OMDB_api_key
            }
            resp = get_resp_using_cache(baseurl, params)
            if resp['Response'] == "True":
                if 'BoxOffice' in resp:
                    box_office = int(float(resp['BoxOffice'][1:].replace(',', '') if resp['BoxOffice'] != "N/A" else 0))
                else:
                    box_office = 0
                movie_obj = (resp['Title'], resp['Year'], int(resp['Runtime'].split()[0] if resp['Runtime'] != "N/A" else 0), resp['Director'], resp['Genre'], resp['imdbRating'], box_office)
                cur.execute(insert_into_movies, movie_obj)

    insert_into_articles = """
        INSERT INTO Articles (sectionId, sectionName, webPublicationDate, title, webUrl, movieId) VALUES (?,?,?,?,?,?);
    """
    cur.execute("SELECT id, title FROM Movies")
    data = cur.fetchall()
    for row in data:
        baseurl = 'https://content.guardianapis.com/search'
        params = {
            'q': row[1].replace(':', ''),
            'section': 'film',
            'api-key': Guardian_api_key
        }
        resp = get_resp_using_cache(baseurl, params)['response']
        if 'results' in resp:
            for result in resp['results']:
                article_obj = (result['sectionId'], result['sectionName'], result['webPublicationDate'], result['webTitle'], result['webUrl'], row[0])
                cur.execute(insert_into_articles, article_obj)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
