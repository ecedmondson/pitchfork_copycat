from flask import Flask, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View
from forms.review_form import ReviewForm
from forms.search_form import SearchForm
from database.models.tables import AlbumTable, ReviewTable, UserTable, SearchSQL, ArtistTable
from jgt_common import must_get_key, only_item_of


app = Flask(__name__)
app.config["SECRET_KEY"] = "derp"

Bootstrap(app)

albums = AlbumTable()
artist = ArtistTable()
reviews = ReviewTable()
users = UserTable()
search = SearchSQL()


def _route_syntax(value):
    return value.lower().replace(" ", "_")


def _readable_syntax(route):
    return " ".join([x.capitalize() for x in route.split("_")])


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html')


@app.route("/", methods=("GET", "POST"))
def home():
    form = SearchForm()
    if form.is_submitted():
        if form.select_search.data:
            search_results = search.execute_search(
                form.search_keyword.data, form.select_search.data
            )
        if search_results:
            result_length, query = search_results
            if result_length == 1:
                return render_template(
                    must_get_key(
                        {
                            "artist": "single_artist_page.html",
                            "album": "single_album_page.html",
                            "user": "single_user_page.html",
                            "genre": "single_genre_page.html",
                        },
                        form.select_search.data,
                    ),
                    query=only_item_of(query),
                    subquery=[],
                )
            return render_template(
                "too_many_search_results.html",
                query=query,
                search_type=form.select_search.data,
            )
        return render_template(
            "search_results_none.html", search_type=form.select_search.data
        )
    return render_template(
        "main.html",
        form=form,
        albums_available_for_review=albums.main_page_album_query(),
    )


@app.route("/route_to_review_page/<album>/<artist>", methods=("GET", "POST"))
def route(album, artist):
    return redirect(
        url_for("review_page", album=_route_syntax(album), artist=_route_syntax(artist))
    )


@app.route("/artists/<artist_name>", methods=("GET", "POST"))
def get_single_artist(artist_name):
    artist_albums = []
    single_artist = artist.get_single_artist_info(artist_name)
    albums_temp = artist.get_albums_for_artist(artist_name)
    for album in albums_temp:
        album_to_add = {
            "id" : album[0],
            "title" : album[1],
            "release_date" : album[2]
        }
        artist_albums.append(album_to_add)
    return render_template("single_artist_page.html", query=single_artist, albums=artist_albums)


@app.route("/route_to_add_new_artist", methods=("GET", "POST"))
def route_add_artist_page():
    return redirect(url_for("add_artist_page"))


@app.route("/route_to_add_new_album", methods=("GET","POST"))
def route_add_album_page():
	return redirect(url_for("add_album_page"))


@app.route(
    "/route_to_search_results/<search_type>/<search_desired>", methods=("GET", "POST")
)
def route_search(search_type, search_desired):
    #TODO: implement single page for each
    # Clicking on a link from a multiple results found
    # search result will end in a TypeError since this function
    # is not yet implemented
    pass


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
    app.run(debug=True, host="0.0.0.0", port=5162)
