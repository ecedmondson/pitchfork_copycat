from flask import Flask, flash, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View
from forms.review_form import ReviewForm
from forms.search_form import SearchForm
from database.models.tables import AlbumTable, ReviewTable, UserTable, SearchSQL, ArtistTable, GenreTable
from jgt_common import must_get_key, only_item_of
from werkzeug.exceptions import HTTPException
import json
import uuid



app = Flask(__name__)
app.config["SECRET_KEY"] = "derp"

Bootstrap(app)

#################
# Table Objects #
#################

albums = AlbumTable()
artist = ArtistTable()
reviews = ReviewTable()
users = UserTable()
search = SearchSQL()
genres = GenreTable()

###########
# Helpers #
###########

# This section contains functions which help perform

def _route_syntax(value):
    """Take data and format it so that it can be easily read in a route for a URL."""
    return value.lower().replace(" ", "_")

def _readable_syntax(route):
    """Take a URL route and make it easily useable as data to interact with backend."""
    return " ".join([x.capitalize() for x in route.split("_")])

##################
# Error Handling #
##################

@app.errorhandler(HTTPException)
def handle_werk(e):
    """Route Werkzeug Programming Errors to 500 server error."""
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', error=e)

##################################
# Routing and Template Rendering #
##################################

@app.route("/", methods=("GET", "POST"))
def home():
    """Renders the home/main/index/etc. page and handles POST request to the search form."""
    form = SearchForm()
    if form.is_submitted():
        if form.select_search.data:
            # Check to see if search in database
            search_results = search.execute_search(
                form.search_keyword.data, form.select_search.data
            )
        # If search in DB: 
        if search_results:
            result_length, query = search_results
	    # Route for exact match
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
	    # Route for multiple search matches
            return render_template(
                "too_many_search_results.html",
                query=query,
                search_type=form.select_search.data,
            )
        # Route for no matches
        return render_template(
            "search_results_none.html", search_type=form.select_search.data
        )
    return render_template(
        "main.html",
        form=form,
        albums_available_for_review=albums.main_page_album_query(),
    )

@app.route("/edit_album", methods=("GET", "UPDATE"))
def edit_album():
    """API endpoint to handle editing the album image. No template. Handles form on edit album page."""
    if request.method == 'GET':
       data = request.args.to_dict()
       if not data['album-art']:
           albums.update_or_set_nullable_album_art("NULL", data['album-uuid'])
           return redirect(url_for("home"))
       if data['album-art'][:4].lower() == 'http':
           albums.update_or_set_nullable_album_art(data['album-art'], data['album-uuid'])
       else:
           return render_template("edit_failed.html")
    return redirect(url_for("home"))

@app.route("/delete_album", methods=("GET", "POST"))
def delete_album():
    """API endpoint to handle deleting an album. No template. Handles form on edit album page."""
    if request.method == 'GET':
        data = request.args.to_dict()
        if data['delete-album'] == 'delete':
            # This function handles M:M deletes as well.
            albums.delete_entire_album(data['album-uuid'])
    return redirect(url_for("home"))

@app.route("/route_to_review_page/<album>/<artist>", methods=("GET", "POST"))
def route(album, artist):
    """Route to review page after user clicks on link."""
    return redirect(
        url_for("review_page", album=_route_syntax(album), artist=_route_syntax(artist))
    )

@app.route("/artists")
def all_artists():
    """Renders the view all artists page."""
    artists = artist.all_artists()
    return render_template("all_artists.html", artists=artists)

@app.route("/create_user", methods=("GET", "POST"))
def create_new_user():
   """Renders the create user form/page and handles POST requests to create form."""
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
    """Handles routing to single artist page when clicked from button (especially in grid)."""
    artist_id = artist._select_artist_id_from_name(artist_name)
    single_artist = artist._select_single_artist_page(artist_id)
    albums = artist._select_albums_from_artist(artist_id)
    return render_template("single_artist_page.html", query=single_artist, albums=albums)

# Update/Delete Context. This dict stores data to help render the appropriate
# comment for editing/deletion when a request is made to edit or delete
# a comment from a given reviews page.
ud_context = {}

def _parse_edit_review_content(content):
    """Helper takes content from a UI field and parses it for rendering in the edit review comment page."""
    album, artist, review_id = content.split("-")
    return {
        "album": album,
        "artist": artist,
        "review_id": review_id
    }

@app.route("/route_to_delete/<page>/<validator>/<content>", methods=("GET", "POST"))
def route_to_delete_page(page, validator, content):
    """Route to delete a review comment page based on which comment is being reviewed."""
    kwargs = {"user_id": validator, "content" : content}
    uuid_ = uuid.uuid4()
    ud_context[str(uuid_)] = kwargs
    return redirect(url_for((must_get_key({"review" : "delete_review_comment"}, page)), uuid=uuid))

@app.route("/delete_review_comment/<uuid>", methods=("GET", "POST"))
def delete_review_comment(uuid,**kwargs):
    """Renders the delete review comment form/page and handled POST requests to delete a review comment."""
    context = ud_context[uuid]
    user_id = context['user_id']
    content = _parse_edit_review_content(context['content'])
    review = reviews.get_single_review_by_id(content['review_id'])
    if request.method == 'POST':
        data = request.form.to_dict()
        submitted_user_id = users.get_user_id_from_names_and_email(data['firstname'], data['lastname'], data['email'])
        if user_id == str(submitted_user_id):
            thing = reviews.delete_review(content['review_id'])
            return redirect(url_for("review_page", album=content['album'], artist=content['artist']))
        else:
            flash("Error: User details submitted for edit do not match user details associated with this review.")
    return render_template("delete_review_comment.html", uuid=uuid, review=review)


@app.route("/route_to_edit/<page>/<validator>/<content>", methods=("GET", "POST"))
def route_to_edit_page(page, validator, content):
    """Route to edit a review comment page based on which comment is being reviewed."""
    kwargs = {"user_id": validator, "content": content}
    uuid_ = uuid.uuid4()
    ud_context[str(uuid_)] = kwargs
    return redirect(url_for((must_get_key({"review": "edit_review_comment"}, page)), uuid=uuid_))

@app.route("/edit_review_comment/<uuid>", methods=("GET", "POST"))
def edit_review_comment(uuid, **kwargs):
    """Renders the edit review comment form/page and handled POST requests to edit a review comment."""
    context = ud_context[uuid]
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
    return render_template("edit_review_comment.html", uuid=uuid, review=review)
    

@app.route("/route_to_add_new_artist", methods=("GET", "POST"))
def route_add_artist_page():
    """Redirects to add artist page from a link."""
    return redirect(url_for("add_artist_page"))


@app.route("/route_to_add_new_album", methods=("GET","POST"))
def route_add_album_page():
    """Redirects to add album page from a link."""
    return redirect(url_for("add_album_page"))


@app.route(
    "/route_to_search_results/<search_type>/<search_desired>", methods=("GET", "POST")
)
def route_search(search_type, search_desired):
    """Handling user input after multiple search results.

    When multiple search results are found after querying the DB, this routing
    function handles further user input against the multiple results template
    by allowing the user to choose a specific result and navigating to the appropriate
    page.
    """
    table = must_get_key({
			"artist": artist,
                        "album": albums,
                        "user": users,
                        "genre": genres,
                        }, search_type)
    # The main search will handle this if specific enough
    # data is provided. If data returns multiple results, the app
    # will redirect to a page providing the user with links to the
    # various results. Those links are routed here, where the search is
    # completed, hence the search table name from "main" or "redirect".
    length, full_search = search.complete_full_search_from_main_or_redirect(table, search_desired)
    return render_template(
                    must_get_key(
                        {
                            "artist": "single_artist_page.html",
                            "album": "single_album_page.html",
                            "user": "single_user_page.html",
                            "genre": "single_genre_page.html",
                        },
                        search_type,
                    ),
                    query=only_item_of(full_search),
    )


@app.route("/reviews/<album>/<artist>", methods=("GET", "POST"))
def review_page(album, artist):
    """Renders the reviews page for a given album and handles POST requests to submit a new review of an album."""
    form = ReviewForm()
    if form.is_submitted():
        user_id = users.get_user_id_from_names_and_email(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
        )
        if user_id:
            album_id = albums.get_album_id_from_name(name=_readable_syntax(album))
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
    """API endpoint for handling a new genre. No templates. Handles form on add album/artist pages."""
    id = genres.insert_genre(json.loads(request.data))
    if id > 0:
        flash("Genre successfully added!")
    else:
        flash(f"ERROR: {id}")
    return json.dumps({"id": id})

@app.route("/add_artist", methods=("GET", "POST"))
def add_artist_page():
    """Renders the add artist form page and handles POST request to create a new artist."""
    genre_all = genres.select_all_genres()
    if request.method == 'POST':
        data = request.form.to_dict()
        result = artist.add_new_artist(request)
        if isinstance(result, str):
            flash(f"ERROR: {result}")
        else:
            return redirect(url_for("home"))
    return render_template("add_artist.html", genres=genre_all)

@app.route("/add_album", methods=("GET", "POST"))
def add_album_page():
    """Renders the add album form page and handles POST request to create a new album."""
    genre_all = genres.select_all_genres()
    # Was getting a blank in there somewhow....
    artist_all = list(filter(lambda x: x != "", artist.all_artists()))
    if request.method == 'POST':
        data = request.form.to_dict()
        result = albums.create_new_album(data)
        if isinstance(result, str):
            flash(f"ERROR: {result}")
        else:
            return redirect(url_for("home"))
    return render_template("add_album.html", genres=genre_all, artists=artist_all)

#######
# Run #
#######
		 
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4740)
