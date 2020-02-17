from flask import Flask, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View
from forms.review_form import ReviewForm
from database.models.tables import AlbumTable, ReviewTable, UserTable
from test_data import *
app = Flask(__name__)
app.config["SECRET_KEY"] = "derp"

Bootstrap(app)

albums = AlbumTable()
reviews = ReviewTable()
users = UserTable()


def _route_syntax(value):
    return value.lower().replace(" ", "_")


def _readable_syntax(route):
    return " ".join([x.capitalize() for x in route.split("_")])


@app.route("/", methods=("GET", "POST"))
def home():
    return render_template(
        "main.html", albums_available_for_review=albums.main_page_album_query()
    )


@app.route("/route_to_review_page/<album>/<artist>", methods=("GET", "POST"))
def route(album, artist):
    return redirect(
        url_for("review_page", album=_route_syntax(album), artist=_route_syntax(artist))
    )
@app.route("/artists/<artist_name>", methods=("GET", "POST"))
def get_single_artist(artist_name):
    return render_template("single_artist.html", artist=artists[0], albums=test_albums[0])

@app.route("/route_to_add_new_artist", methods=("GET", "POST"))
def route_add_artist_page():
    return redirect(url_for("add_artist_page"))

@app.route("/route_to_add_new_album", methods=("GET","POST"))
def route_add_album_page():
	return redirect(url_for("add_album_page"))


@app.route("/reviews/<album>/<artist>", methods=("GET", "POST"))
def review_page(album, artist):
    form = ReviewForm()
    if form.is_submitted():
        # TODO: validate data
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
            album_id=albums.get_album_id_from_name(_readable_syntax(album))
        ),
        album=_readable_syntax(album),
    )


@app.route("/add_artist", methods=("GET", "POST"))
def add_artist_page():
    return render_template("add_artist.html")

@app.route("/add_album", methods=("GET","POST"))
def add_album_page():
	return render_template("add_album.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5162)
