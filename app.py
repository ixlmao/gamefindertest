from flask import Flask, render_template, request, abort
import sqlite3

app = Flask(__name__)

DATABASE = 'gamedatabase.db'

@app.route("/")
def index():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, image
        FROM games
        ORDER BY metacritic_score DESC
        LIMIT 4
    """)
    featured_games = cur.fetchall()
    conn.close()
    return render_template("index.html", featured_games=featured_games)

@app.route("/games")
def products():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sort_by = request.args.get('sort', 'score_desc')

    if sort_by == 'score_asc':
        order_clause = "ORDER BY metacritic_score ASC"
    elif sort_by == 'year_desc':
        order_clause = "ORDER BY release_year DESC"
    elif sort_by == 'year_asc':
        order_clause = "ORDER BY release_year ASC"
    elif sort_by == 'name_asc':
        order_clause = "ORDER BY name ASC"
    elif sort_by == 'name_desc':
        order_clause = "ORDER BY name DESC"
    else:
        sort_by = 'score_desc'
        order_clause = "ORDER BY metacritic_score DESC"

    sql_query = f"SELECT id, name, metacritic_score, release_year, image FROM games {order_clause}"
    cur.execute(sql_query)

    games = cur.fetchall()
    conn.close()

    return render_template("games.html", games=games, current_sort=sort_by, genre_id=None, genre_name="Visas")

@app.route("/genres")
def show_genres():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, genre_name FROM genres ORDER BY genre_name ASC")
    genres = cur.fetchall()
    conn.close()
    return render_template("genres.html", genres=genres)

@app.route("/genre/<int:genre_id>")
def show_genre_games(genre_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT genre_name FROM genres WHERE id = ?", (genre_id,))
    genre_data = cur.fetchone()

    if genre_data is None:
        conn.close()
        abort(404)
    genre_name = genre_data['genre_name']

    sort_by = request.args.get('sort', 'score_desc')

    if sort_by == 'score_asc':
        order_clause = "ORDER BY metacritic_score ASC"
    elif sort_by == 'year_desc':
        order_clause = "ORDER BY release_year DESC"
    elif sort_by == 'year_asc':
        order_clause = "ORDER BY release_year ASC"
    elif sort_by == 'name_asc':
        order_clause = "ORDER BY name ASC"
    elif sort_by == 'name_desc':
        order_clause = "ORDER BY name DESC"
    else:
        sort_by = 'score_desc'
        order_clause = "ORDER BY metacritic_score DESC"

    sql_query = f"SELECT id, name, metacritic_score, release_year, image FROM games WHERE genre_id = ? {order_clause}"
    cur.execute(sql_query, (genre_id,))

    games = cur.fetchall()
    conn.close()

    return render_template("games.html", games=games, current_sort=sort_by, genre_id=genre_id, genre_name=genre_name)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/games/<int:game_id>")
def products_show(game_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            g.id, g.name, g.release_year, g.metacritic_score, g.image, g.description,
            p.publisher_name
        FROM
            games g
        LEFT JOIN
            publishers p ON g.publisher_id = p.id
        WHERE
            g.id = ?
        """,
        (game_id,),
    )
    game = cur.fetchone()
    conn.close()

    if game is None:
        abort(404)

    return render_template("games_show.html", game=game)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)