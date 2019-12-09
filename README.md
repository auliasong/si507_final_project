# si507_final_project
Umich SI507 final project - Aulia Song.


Data Source:

    - tmdb_5000_credits.csv

    This dataset is manipulated and originally obtained from Kaggle
    (https://www.kaggle.com/tmdb/tmdb-movie-metadata/data#tmdb_5000_credits.csv)
    and contains 2000 movie titles.

    - OMDB api (requires api key, 1000 daily request limit)
    http://www.omdbapi.com/

    The 2000 movie titles in tmdb_5000_credits.csv were used to query the OMDB api
    to get all the movie information and construct the database table Movies.

    - Guardian api (requires api key, 5000 daily request limit)
    https://open-platform.theguardian.com/documentation/

    Each movie record obtained from the OMDB api was used to query the Guardian api
    to get a list of related articles on that movie. Each article record was stored
    in the database table Articles.


Database

    final_proj.db
    To recreate: run $ python3 create_database.py in the project root directory.

    - Table Movies (8 columns)
            id integer PRIMARY KEY AUTOINCREMENT,
            title text,
            year integer,
            runtime integer,
            director text,
            genre text,
            imdbRating real,
            boxOffice integer

    - Table Articles (7 columns)
            id integer PRIMARY KEY AUTOINCREMENT,
            sectionId text,
            sectionName text,
            webPublicationDate text,
            title text,
            webUrl text,
            movieId integer,
            FOREIGN KEY (movieId) REFERENCES Movies (id)


Code Structure

    - create_database.py

    Python program to create the sqlite3 database.
    How to run: $ python3 create_database.py

    - proj3.py

    Interactive python program to let user select from 4 different data presentations.
    How to run: $ python3 proj3.py

            Functions:

            - plot_avg_runtime_per_category

            For plotting average runtime against movie categories.

            - plot_num_movie_per_year

            For plotting number of movies released against year.

            - create_word_cloud

            For creating a wordcloud plot for a specific movie.

            - avg_rating_per_director

            For printing director info.

            
Data presentations

Commands available:

    average_runtime
            Description: Plot average movie runtime vs. movie category. Each category
                         will be split into two groups (top 50% and bottom 50%) based
                         on the specified parameter.

            Parameter:   * ratings|boxOffice [default: ratings]
                         Description: Split each movie category into two groups based
                         on ratings or boxOffice.

            Example:     $ average_runtime ratings

    movie_count
            Description: Plot number of movies vs. release year based on the
                         specified order.

            Parameter:   * top=<limit>|bottom=<limit> [default: top=10]
                         Description: Specifies whether to list the top <limit> matches
                         or the bottom <limit> matches.

    wordcloud
            Description: Create a wordcloud plot for a given movie.

            Parameter:   * <movie_name> (this parameter is required)

            Example:     $ wordcloud Avatar

    director
            Description: Lists directors with their average movie ratings and average
                         movie box office. Only directors who have directed at least 5
                         movies will be listed in the results.

            Parameter:   * top=<limit>|bottom=<limit> [default: top=10]
                         Description: Specifies whether to list the top <limit> matches
                         or the bottom <limit> matches.

                         * ratings|boxOffice [default: ratings]
                         Description: Specifies whether to order the results by average
                         movie ratings or average movie box office.

            Example:     $ director boxOffice top=15
