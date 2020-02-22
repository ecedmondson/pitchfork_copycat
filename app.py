from flask import Flask, render_template, request, url_for, redirect
from forms.review_form import ReviewForm
from forms.search_form import SearchForm
from database.models.tables import AlbumTable, ReviewTable, UserTable, SearchSQL
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config["SECRET_KEY"] = "derp"

albums = AlbumTable()
reviews = ReviewTable()
users = UserTable()
search = SearchSQL()
Bootstrap(app)

def _route_syntax(value):
    return value.lower().replace(" ", "_")

def _readable_syntax(route):
    return " ".join([x.capitalize() for x in route.split("_")])

def _sql_escapes(route):
    return route.replace("'", "\\'")
    

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html')


@app.route("/", methods=("GET", "POST"))
def home():
    form = SearchForm()
    print(dir(form))
    if form.is_submitted():
       print(form.select_search.data)
       print(form.search_keyword.data)
    if form.select_search.data:
        search_results = search.execute_search(form.search_keyword.data, form.select_search.data)
    print(search_results)
    return render_template(
        "main2.html", form=form, albums_available_for_review=albums.main_page_album_query()
    )


@app.route("/route_to_review_page/<album>/<artist>", methods=("GET", "POST"))
def route(album, artist):
    return redirect(
        url_for("review_page", album=_route_syntax(album), artist=_route_syntax(artist))
    )


@app.route("/route_to_add_new_artist", methods=("GET", "POST"))
def route_add_artist_page():
    return redirect(url_for("add_artist_page"))


@app.route("/reviews/<album>/<artist>", methods=("GET", "POST"))
def review_page(album, artist):
    form = ReviewForm()
    if form.is_submitted():
        # TODO: validate data
        print(form.firstname.data)
        print(form.lastname.data)
        print(form.email.data) 
        user_id = users.get_user_id_from_names_and_email(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
        )
        album_id = albums.get_album_id_from_name(name=_readable_syntax(album))
        # TODO: add a real rating system in
        reviews.add_new_review(form.body.data, "10", str(user_id), str(album_id))
    return render_template(
        "review_page.html",
        form=form,
        existing_reviews=reviews.get_reviews_for_an_album(
            album_id=albums.get_album_id_from_name(_sql_escapes(_readable_syntax(album)))
        ),
        album=_readable_syntax(album),
    )


@app.route("/add_artist", methods=("GET", "POST"))
def add_artist_page():
    return render_template("add_artist.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5162)
