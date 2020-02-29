from flask import Flask, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View
from forms.review_form import ReviewForm
from forms.search_form import SearchForm
from database.models.tables import AlbumTable, ReviewTable, UserTable, SearchSQL
from jgt_common import must_get_key, only_item_of

#######
# App #
#######

app = Flask(__name__)
app.config["SECRET_KEY"] = "derp"
Bootstrap(app)

##########
# Tables #
##########

albums = AlbumTable()
reviews = ReviewTable()
users = UserTable()
search = SearchSQL()

#################
# Route Helpers #
#################


def _route_syntax(value):
    return value.lower().replace(" ", "_")


def _readable_syntax(route):
    return " ".join([x.capitalize() for x in route.split("_")])


def _sql_escapes(route):
    return (
        route.replace("'", "\\'")
        .replace('"', '\\"')
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


##################
# Search Helpers #
##################

unique_search_result_pages = {
    "artist": "single_artist_page.html",
    "album": "single_album_page.html",
    "user": "single_user_page.html",
    "genre": "single_genre_page.html",
}


def _no_search_results(search_type):
    return redirect(url_for("no_search_results", search_type=search_type))


def _handle_search_input(search_results, search_type):
    result_length, query = search_results
    if result_length == 1:
        if isinstance(query, list):
            query = only_item_of(query)
            return render_template(
                must_get_key(unique_search_result_pages, search_type), query=query,
            )
        return redirect(
            url_for("multiple_search_results"), search_type=search_type, query=query
        )


#################
# Search Routes #
#################


@app.route("/search_yields_none", methods=("GET", "POST"))
def no_search_results(search_type=None):
    # Search Type None because it is not required
    return render_template("search_results_none.html", search_type=search_type)


@app.route("/multiple_search_results", methods=("GET", "POST"))
def multiple_search_results(search_type, query):
    return render_template(
        "too_many_search_results.html", query=query, search_type=search_type,
    )


##################
# Error Handling #
##################


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


#################
# Route Helpers #
#################

# These route helpers provide an easy way to
# add a link on the href attribute of the various
# buttons scattered throughout the website.


@app.route("/route_to_add_new_artist", methods=("GET", "POST"))
def route_add_artist_page():
    return redirect(url_for("add_artist_page"))


@app.route("/route_to_add_new_album", methods=("GET", "POST"))
def route_add_album_page():
    return redirect(url_for("add_album_page"))


@app.route("/route_to_review_page/<album>/<artist>", methods=("GET", "POST"))
def route(album, artist):
    return redirect(
        url_for("review_page", album=_route_syntax(album), artist=_route_syntax(artist))
    )


# Pass in args about what i'm editing
# then use must get key to choose a specific
# redirect url
@app.route("/route_to_edit", methods=("GET", "POST"))
def route_to_edit():
    return render_template("500.html", title="500"), 500


@app.route("/route_to_delete", methods=("GET", "POST"))
def route_to_delete():
    return render_template("500.html", title="500"), 500


#########
# Pages #
#########

# Home / Main / Index Page
@app.route("/", methods=("GET", "POST"))
def home():
    form = SearchForm()
    if form.is_submitted():
        if form.select_search.data:
            search_results = search.execute_search(
                _sql_escapes(form.search_keyword.data), form.select_search.data
            )
        if search_results:
            _handle_search_input(search_results, form.select_search.data)
        return redirect(url_for("no_search_results"), search_type=search_type)
    return render_template(
        "main.html",
        form=form,
        albums_available_for_review=albums.main_page_album_query(),
    )


# Single Artist Page
# This page dynamically populates based on the information
# provided in the route
@app.route("/artists/<artist_name>", methods=("GET", "POST"))
def get_single_artist(artist_name):
    return render_template("single_artist.html")


# Review Page
# This page dynamically populates based on the information
# provided in the route
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
        album_id = albums.get_album_id_from_name(
            name=_sql_escapes(_readable_syntax(album))
        )
        # TODO: add a real rating system in
        reviews.add_new_review(
            _sql_escapes(form.body.data), "10", str(user_id), str(album_id)
        )
    return render_template(
        "review_page.html",
        form=form,
        existing_reviews=reviews.get_reviews_for_an_album(
            album_id=albums.get_album_id_from_name(
                _sql_escapes(_readable_syntax(album))
            )
        ),
        album=_readable_syntax(album),
    )


# Add Artist Page
@app.route("/add_artist", methods=("GET", "POST"))
def add_artist_page():
    return render_template("add_artist.html")


# Add Album Page
@app.route("/add_album", methods=("GET", "POST"))
def add_album_page():
    return render_template("add_album.html")


#######
# Run #
#######
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5151)
