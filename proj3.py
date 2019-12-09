import sqlite3
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

DBNAME = 'final_proj.db'

help_text = """
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

            Example:     $ director boxOffice top=15"""

def plot_avg_runtime_per_category(group_by="ratings"):
    if group_by == "ratings":
        order_by = "imdbRating"
    elif group_by == "boxOffice":
        order_by = "boxOffice"
    else:
        print("Invalid command!")
        return
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute("SELECT id, runtime, genre, imdbRating, boxOffice FROM Movies WHERE runtime != 0 AND imdbRating != 0 AND boxOffice != 0 ORDER BY " + order_by + " DESC")
    data = cur.fetchall()
    genre_dict = {}
    for movie in data:
        genres = movie[2].split(', ')
        for genre in genres:
            if genre in genre_dict:
                genre_dict[genre].append(movie[1])
            else:
                genre_dict[genre] = [movie[1]]
    res_dict = {}
    for genre in genre_dict:
        length = len(genre_dict[genre])
        first_half = genre_dict[genre][:int(length / 2)]
        second_half = genre_dict[genre][int(length / 2):]
        res_dict[genre] = [sum(first_half) / float(len(first_half)), sum(second_half) / float(len(second_half))]
    sorted_res_dict = sorted(res_dict.items(), key=lambda kv: kv[1][0], reverse=True)
    genre_lst = []
    avg_runtime_lst1 = []
    avg_runtime_lst2 = []
    for i in range(10):
        genre_lst.append(sorted_res_dict[i][0])
        avg_runtime_lst1.append(sorted_res_dict[i][1][0])
        avg_runtime_lst2.append(sorted_res_dict[i][1][1])

    fig = go.Figure([
        go.Bar(name='Top 50% in ' + group_by, x=genre_lst, y=avg_runtime_lst1),
        go.Bar(name='Bottom 50% in ' + group_by, x=genre_lst, y=avg_runtime_lst2)
    ])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(barmode='group', title_text='Average Runtime VS. Category', xaxis_tickangle=-45)
    fig.show()
    conn.close()

def plot_num_movie_per_year(param="top", limit="10"):
    if param == "top":
        order = "DESC"
    else:
        order = "ASC"
    query = "SELECT year, cnt FROM (SELECT year, count(*) AS cnt FROM Movies GROUP BY year) ORDER BY cnt " + order + " LIMIT " + limit
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(query)
    data = cur.fetchall()
    year_lst = []
    cnt_lst = []
    for row in data:
        year_lst.append(str(row[0]))
        cnt_lst.append(row[1])
    fig = go.Figure([
        go.Bar(x=year_lst, y=cnt_lst)
    ])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(title_text='Number of Movies Released Each Year')
    fig.update_xaxes(type="category")
    fig.show()
    conn.close()

def create_word_cloud(title):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    txt = ""
    cur.execute('SELECT a.webUrl FROM Movies as m, Articles as a WHERE a.movieId = m.id AND m.title = "' + title + '" COLLATE NOCASE')
    data = cur.fetchall()
    for row in data:
        # print(row[0])
        page = requests.get(row[0]).text
        soup = BeautifulSoup(page)
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            txt += p.get_text()
    if txt == "":
        print("No such movie found in the database!")
        conn.close()
        return
    stopwords = set(STOPWORDS)
    wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(txt)

    # plot the WordCloud image
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)

    plt.show()
    conn.close()

def avg_rating_per_director(order_by="ratings", param="top", limit="10"):
    if param == "top":
        order = "DESC"
    else:
        order = "ASC"
    if order_by == "ratings":
        order_by_column = "a.avg_rating"
    else:
        order_by_column = "avg_box_office"
    query = """SELECT a.director, a.cnt, a.avg_rating, a.total_box_office / a.cnt2 AS avg_box_office
            FROM (SELECT director, count(id) as cnt, avg(imdbRating) as avg_rating, count(NULLIF(boxOffice, 0)) as cnt2, sum(boxOffice) as total_box_office
            FROM Movies WHERE imdbRating != 0 GROUP BY director) as a
            WHERE a.cnt >= 5
            ORDER BY """ + order_by_column + " " + order + " LIMIT " + limit
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(query)
    data = cur.fetchall()
    for row in data:
        print("{:<20} {:>3}   {:.1f}   ${:>12}".format(
            row[0] if len(row[0]) <= 20 else row[0][:17] + "...",
            str(row[1]),
            row[2],
            str("{:,d}".format(int(row[3])))
        ))
    conn.close()

def interactive_prompt():
    response = input('Enter a command (type "help" for more info, "exit" to quit): ')
    while response != 'exit':
        if response == 'help':
            print(help_text)
        else:
            if not response:
                pass
            else:
                response = response.split()
                if len(response) == 0:
                    pass
                elif response[0] == "average_runtime":
                    if len(response) > 1:
                        if response[1] == "ratings":
                            plot_avg_runtime_per_category()
                        elif response[1] == "boxOffice":
                            plot_avg_runtime_per_category("boxOffice")
                        else:
                            print("Invalid command!")
                    else:
                        plot_avg_runtime_per_category()
                elif response[0] == "movie_count":
                    if len(response) > 1:
                        if "top=" in response[1] or "bottom=" in response[1]:
                            param = response[1].split('=')[0]
                            limit = response[1].split('=')[1]
                            plot_num_movie_per_year(param, limit)
                        else:
                            print("Invalid command!")
                    else:
                        plot_num_movie_per_year()
                elif response[0] == "wordcloud":
                    if len(response) < 2:
                        print("Invalid command!")
                    else:
                        create_word_cloud(" ".join(response[1:]))
                elif response[0] == "director":
                    order_by="ratings"
                    param="top"
                    limit="10"
                    invalid = False
                    for i in range(1, len(response)):
                        if '=' in response[i]:
                            temp = response[i].split('=')
                            if temp[0] == 'top':
                                limit = str(int(temp[1]))
                            elif temp[0] == 'bottom':
                                param = "bottom"
                                limit = str(int(temp[1]))
                            else:
                                print("Invalid command!")
                                invalid = True
                        else:
                            if response[i] == "boxOffice":
                                order_by = "boxOffice"
                            elif response[i] != "ratings":
                                print("Invalid command!")
                                invalid = True
                    if not invalid:
                        avg_rating_per_director(order_by, param, limit)
                else:
                    print("Invalid command!")
        print()
        response = input('Enter a command (type "help" for more info, "exit" to quit): ')
    print("Bye!")

if __name__=="__main__":
    interactive_prompt()
