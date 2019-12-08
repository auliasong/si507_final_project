import sqlite3
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

DBNAME = 'final_proj.db'

help_text = """

"""

def plot_avg_runtime_per_category(group_by):
    if group_by == "rating":
        order_by = "imdbRating"
    else:
        order_by = "boxOffice"
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

def interactive_prompt():
    response = input('Enter a command: ')
    while response != 'exit':
        if response == 'help':
            print(help_text)
            continue
        else:
            data = process_command(response)
            print_data(data)
        response = input('Enter a command: ')
    print("Bye!")

if __name__=="__main__":
    # plot_avg_runtime_per_category('rating')
    create_word_cloud('avatar')
    # interactive_prompt()
