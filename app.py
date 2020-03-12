from flask import Flask, flash, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View
from forms.review_form import ReviewForm
from forms.search_form import SearchForm
from database.models.tables import AlbumTable, ReviewTable, UserTable, SearchSQL, ArtistTable, GenreTable
from jgt_common import must_get_key, only_item_of
import json


app = Flask(__name__)
app.config["SECRET_KEY"] = "derp"

Bootstrap(app)

albums = AlbumTable()
artist = ArtistTable()
reviews = ReviewTable()
users = UserTable()
search = SearchSQL()
genres = GenreTable()

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

@app.route("/artists")
def all_artists():
    artists = artist.all_artists()
    return render_template("all_artists.html", artists=artists)

@app.route("/create_user", methods=("GET", "POST"))
def create_new_user():
   valid_email_endings = ['.com', '.net', '.org', '.edu'] 
   if request.method == 'POST':
        data = request.form.to_dict()
        exists = users.get_user_id_from_names_and_email(data['firstname'], data['lastname'], data['email'])
        if exists:
           flash(f"User already exists.")
        if '@' in data['email'] and not exists:
           users.add_new_user(data['firstname'], data['lastname'], data['email'])
           flash(f"(User {data['firstname']} {data['lastname']} added.")
        if '@' not in data['email']:
            flash("Please enter valid e-mail.") 
   return render_template("create_user.html")

@app.route("/artists/<artist_name>", methods=("GET", "POST"))
def route_single_artist_page(artist_name):
    artist_id = artist._select_artist_id_from_name(artist_name)
    single_artist = artist._select_single_artist_page(artist_id)
    albums = artist._select_albums_from_artist(artist_id)
    return render_template("single_artist_page.html", query=single_artist, albums=albums)


ud_context = []

def _parse_edit_review_content(content):
    print(content.split("-"))
    album, artist, review_id = content.split("-")
    return {
        "album": album,
        "artist": artist,
        "review_id": review_id
    }

@app.route("/route_to_edit/<page>/<validator>/<content>", methods=("GET", "POST"))
def route_to_edit_page(page, validator, content):
     kwargs = {"user_id": validator, "content": content}
     ud_context.append(kwargs)
     return redirect(url_for((must_get_key({"review": "edit_review_comment"}, page))))

@app.route("/edit_review_comment", methods=("GET", "POST"))
def edit_review_comment(**kwargs):
    context = only_item_of(ud_context)
    user_id = context['user_id']
    content = _parse_edit_review_content(context['content'])
    review = reviews.get_single_review_by_id(content['review_id'])
    if request.method == 'POST':
        data = request.form.to_dict()
        submitted_user_id = users.get_user_id_from_names_and_email(data['firstname'], data['lastname'], data['email'])
        if user_id == str(submitted_user_id):
            thing = reviews.update_comment(data['comment'], data['rating'], content['review_id'])
            ud_context.clear()
            return redirect(url_for("review_page", album =content['album'], artist=content['artist']))
        else:
            flash("Error: User details submitted for edit do not match user details associated with this review.")
    return render_template("edit_review_comment.html", review=review)
    

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
        user_id = users.get_user_id_from_names_and_email(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
        )
        if user_id:
            album_id = albums.get_album_id_from_name(name=_readable_syntax(album))
            # TODO: add a real rating system in
            reviews.add_new_review(form.body.data, form.review_select.data, str(user_id), str(album_id))
        else:
           flash("User not found")
    return render_template(
        "review_page.html",
        form=form,
        existing_reviews=reviews.get_reviews_for_an_album(
            album_id=albums.get_album_id_from_name(_readable_syntax(album))
        ),
        album=_readable_syntax(album),
        artist=_readable_syntax(artist),
    )

@app.route("/new_genre", methods=(["POST"]))
def new_genre():
    id = genres.insert_genre(json.loads(request.data))
    if id > 0:
        flash("Genre successfully added!")
    else:
        flash(f"ERROR: {id}")
    return json.dumps({"id": id})

@app.route("/add_artist", methods=("GET", "POST"))
def add_artist_page():
    genre_all = genres.select_all_genres()
    if request.method == 'POST':
        data = request.form.to_dict()
        print(data)
        result = artist.add_new_artist(request)
        if isinstance(result, str):
            flash(f"ERROR: {result}")
        else:
            return redirect(url_for("home"))
    return render_template("add_artist.html", genres=genre_all)

@app.route("/add_album", methods=("GET", "POST"))
def add_album_page():
    genre_all = genres.select_all_genres()
    artist_all = artist.all_artists()
    if request.method == 'POST':
        data = request.form.to_dict()
        print(data)
        result = albums.create_new_album(data)
        if isinstance(result, str):
            flash(f"ERROR: {result}")
        else:
            return redirect(url_for("home"))
    return render_template("add_album.html", genres=genre_all, artists=artist_all)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4740)
