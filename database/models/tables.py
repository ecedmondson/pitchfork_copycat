from database.database_connector import DBConnection
from jgt_common import only_item_of, must_get_key
from flask import abort
import logging

logging.basicConfig(filename='runtime_sql_queries.log', level=logging.DEBUG)


class ArtistTable(DBConnection):
    """This class handles all SQL queries for CRUD interactions with the Artist table.
    
    Occasionally there are joins with other tables on foreign keys.
    """
    
    def _format_all_artist_data(self, query_tuple):
        """Format the data returned from querying DB for all artist columns."""
        artist_id, artist_name, website, image, location, description = query_tuple
        return {
            "artist_id": artist_id,
            "artist_name": artist_name,
            "website": website,
            "artist_image": image,
            "location": location,
            "description": description,
        }
    
    def _get_search_keyword(self, queries):
        """Search helpers. Returns id for matched Artist search queries."""
        if len(queries) == 1:
            return only_item_of(queries)[0]
        return None

    # Read
    def _select_artist_id_from_name(self, name):
        """Retrieve artist id when singluar artist name provided."""
        statement = "SELECT id from artist WHERE artist.name = %s"
        print(f"Artist ID from Artist Name: {statement}, KWARGS ({name},)")
        logging.debug(f"Artist ID from Artist Name: {statement}, KWARGS ({name},)")
        queries = self.execute_query(statement, (name,)).fetchall()
        return only_item_of([query[0] for query in queries])

    def _format_search_helper(self, *args):
        """Wrapper function for format all data used by Search."""
        data = self._format_all_artist_data(*args)
        data['id'] = data['artist_id']
        return data

    # Read
    def _touch_helper(self, search_keyword):
        """Search helper to see if an artist has any albums."""
        statement = "SELECT id from album WHERE album.artist_id = %s"
        print(f"Artist Touch Helper: {statement}, KWARGS: ({search_keyword},)")
        logging.debug(f"Artist Touch Helper: {statement}, KWARGS: ({search_keyword},)")
        return self.execute_query(statement, (search_keyword, )).fetchall()

    # Read
    def _search_entity_only(self, search_keyword):
        """Search performed on exact match where artist has no albums in DB.
        
        This function is a wrapper on a function used for both search and
        data population in JINJA templates.
        """
        results = self._select_single_artist_page(search_keyword)
        results["full"] = False
        results["artist_website"] = results["website"]
        results["artist"] = results["artist_name"]
        return [results]

    def _full_search_parse(self, queries):
       """Format data from full search."""
       genres = list(set([query[-1] for query in queries]))
       dates = list(set([query[-2] for query in queries]))
       u_albums = list(set([query[-3] for query in queries]))
       albums = []
       for query in queries:
          if query[-3] in u_albums and query[-2] in dates:
              albums.append({query[-3]: query[-2]})
              dates.remove(query[-2])
              u_albums.remove(query[-3])
       # Rest of the data should be the same in all the "rows"/tuples of the query.
       artist, location, artist_website, description, artist_image, album, release, genre = queries[0]
       return {
           "artist": artist,
           "location": location,
           "artist_website": artist_website,
           "description": description,
           "artist_image": artist_image,
           "album": albums,
           "genre": genres,
           "full": True,
       }
    
    # Read
    def _full_search(self, search_keyword):
        """Search performed on exact match where artist has albums in DB."""
        statement = (
            """
            select artist.name, artist.location, artist.website, artist.description,
            artist.image, album.title, album.release_date, genre.name from artist as artist 
            inner join album on artist.id=album.artist_id
            inner join artist_genre on artist_genre.artist_id=artist.id
            inner join genre on artist_genre.genre_id=genre.id
            where artist.id = %s
            """
        )
        print(f"Artist Full Search Debug: {statement} and artist id {search_keyword}")
        logging.debug(f"Artist Full Search Debug: {statement} and artist id {search_keyword}")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return [self._full_search_parse(queries)]

    # Read
    def _does_artist_exist(self, artist):
        """Checks to see if artist already lives in DB."""
        statement = "SELECT id from artist where artist.name = %s"
        print(f"DEBUG IF ARTIST EXISTs: {statement} and {artist}")
        logging.debug(f"DEBUG IF ARTIST EXISTs: {statement} and {artist}")
        return self.execute_query(statement, (artist,)).fetchall()
    
    def _validate_insert_artist_data(self, data):
        """Helper to validate user input data for artist creation."""
        if not data['artistName']:
            return (False, 'artist name must be present')
        if data['artistImage'][:4] != 'http':
           return (False, 'website was not URL')
        if data['artistWebsite'][:4] != 'http':
           return (False, 'image was not URL')
        if self._does_artist_exist(data['artistName']):
           return (False, 'artist already exists')
        if not data['artistGenres']:
           return (False, 'must add genre')
        return False

    # Update
    def _update_artist_genre(self, genres, artist_id):
       """Helper to update M:M relationship in relational table.
       
       Nota bene: table is artist_genre, not artist.
       """
       genres = [int(x) for x in genres.split(",")] 
       statement = "INSERT into artist_genre (artist_id, genre_id) VALUES (%s, %s);"
       for genre in genres:
           logging.debug(f"UPDATING M:M SQL FOR ARTIST_GENRE: {statement} {genre}")
           self.execute_query(statement, (artist_id, genre,)).fetchall()
 
    # Create      
    def add_new_artist(self, request):
        """Query to insert new artist."""
        artist_to_add = request.form.to_dict()
        validated = self._validate_insert_artist_data(artist_to_add)
        if validated:
            return validated[1]
        statement = (
            "INSERT INTO artist (name, website, image, location, description) VALUES ('{}', '{}', '{}', '{}', '{}')".format
                (
                    artist_to_add['artistName'], 
                    artist_to_add['artistWebsite'],
                    artist_to_add['artistImage'],
                    artist_to_add['artistLocation'],
                    artist_to_add['artistDescription']
                )
        )
        id = self.execute_query(statement).lastrowid
        self._update_artist_genre(artist_to_add['artistGenres'], id)
        return

    # Read
    def all_artists(self):
        """Retrieve all artists currently in DB."""
        statement = ("SELECT * FROM artist")
        queries = self.execute_query(statement).fetchall()
        return [self._format_all_artist_data(query) for query in queries]

    # Read
    def _select_single_artist_page(self, artist_id):
        """Retrieve data for single artist page.
        
        When used with search, is used for exact match with no full search.
        """
        statement = ("SELECT * FROM artist WHERE artist.id = %s" % artist_id) 
        print(f"DEBUG SELECT SINGLE ARTIST PAGE: {statement} and artist id {artist_id}")
        queries = self.execute_query(statement).fetchone()
        return self._format_all_artist_data(queries)

    # Read
    def _select_albums_from_artist(self, artist_id):
        """Retrieve albums per artist basis."""
        statement = ("SELECT * FROM album WHERE artist_id = %s" % artist_id)
        queries = self.execute_query(statement).fetchall()
        return [AlbumTable._album_data(AlbumTable, query) for query in queries]
        
class AlbumTable(DBConnection):
    """This class handles all SQL queries for CRUD interactions with the album table.
    
    Occasionally there are joins with other tables on foreign keys.
    """
    def _album_data(self, query_tuple):
        """Data formatter for get_all_albums call."""
        (
            album_id,
            artist_id,
            album_title,
            album_art,
            release_date,
            publisher,
            spotify_url,
        ) = query_tuple
        return {
            "album_id": album_id,
            "artist_id": artist_id,
            "album_title": album_title,
            "album_art": album_art,
            "release_date": release_date,
            "publisher": publisher,
            "spotify_url": spotify_url,
        }

    def _format_search_helper(self, *args):
        """Wrapper function for format all data used by Search."""
        data = self._album_data(*args)
        data['id'] = data['album_id']
        return data

    def _get_search_keyword(self, queries):
        """Search helpers. Returns id for matched album search queries."""
        if len(queries) == 1:
            # print(only_item_of(queries))
            return only_item_of(queries)[2]
        return None

    # Read
    def _select_id_by_album_title(self, title):
        statement = "SELECT id from album WHERE album.title = %s"
        print(f"Select ID by Album Title: {statement} KWARGS: ({title},)")
        logging.debug(f"Select ID by Album Title: {statement} KWARGS: ({title},)")
        queries = self.execute_query(statement, (title,)).fetchall()
        return only_item_of([query[0] for query in queries])

    # Read
    def _select_title_by_album_id(self, id):
        """Search helper from redirect."""
        statement = "SELECT title from album where album.id = %s"
        print(f"Select title by album id: {statement} kwargs {id}.")
        logging.debug(f"Select title by album id {statement} kwargs {id}.")
        queries = self.execute_query(statement, (id,)).fetchall()
        return only_item_of([query[0] for query in queries])

    # Read
    def _touch_helper(self, search_keyword):
        """Search helper to see if an album has any reviews."""
        if search_keyword.isnumeric():
            search_keyword = self._select_title_by_album_id(search_keyword)
        statement = "SELECT review.id from review inner join album on review.album_id = album.id where album.title = %s"
        print(f"Album touch helper: {statement}, kwargs: ({search_keyword},)")
        logging.debug(f"Album touch helper: {statement}, kwargs: ({search_keyword},)")
        return self.execute_query(statement, (search_keyword, )).fetchall()

    def _format_entity_search(self, queries):
        """Helper to format data for an exact match entity search."""
        # Only 1 Genre
        if len(queries) == 1:
            for (
                artist,
                id_,
                title,
                art,
                release_date,
                publisher,
                spotify_url,
                genre,
            ) in queries:
                return {
                    "artist": artist,
                    "id": id_,
                    "title": title,
                    "art": art,
                    "release_date": release_date,
                    "publisher": publisher,
                    "genre": genre,
                }
        # More than one Genre
        genres = [query[-1] for query in queries]
        # Other data should stay the same so return the first
        artist, id_, title, art, release_date, publisher, spotify_url, genre = queries[0]
        return {
                "artist": artist,
                "id": id_,
                "title": title,
                "art": art,
                "release_date": release_date,
                "publisher": publisher,
                "genre": genres,
        }

    # Read
    def _search_entity_only(self, search_keyword):
        """Search when there is an exact match for an album with no reviews."""
        if search_keyword.isnumeric():
           search_keyword = self._select_title_by_album_id(search_keyword)
        statement = ("""
            SELECT artist.name, album.id, album.title, album.album_cover, album.release_date, album.publisher,
            album.spotify_url, genre.name from album inner join artist on album.artist_id = artist.id
            INNER JOIN album_genre on album.id = album_genre.album_id
            INNER JOIN genre on album_genre.genre_id = genre.id
            WHERE album.title = %s
            """
        )
        print(f"Album Search Entity Only: {statement}, KWARGS: ({search_keyword},)")
        logging.debug(f"Album Search Entity Only: {statement}, KWARGS: ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return [self._format_entity_search(queries)]

    def _full_search_parse(self, queries):
        """Format data for full search."""
        # Multiples
        ratings = [query[-1] for query in queries]
        genres = [query[-2] for query in queries]
        constants_checked = False
        # Other data should stay the same so return the first
        (
            id_,
            title,
            art,
            release_date,
            publisher,
            spotify_url,
            artist,
            genre,
            rating,
        ) = queries[0]
        genres = list(set(genres))
        rating_multiplicative_factor = len(genres)
        set_ratings = list(set(ratings))
        rating_count = [
            {rating: ((ratings.count(rating) // rating_multiplicative_factor))}
            for rating in set_ratings
        ]
        total_unique_ratings = sum(
            [v for set_ in rating_count for k, v in set_.items()]
        )
        rating_average = (
            sum([k * v for set_ in rating_count for k, v in set_.items()])
            / total_unique_ratings
        )
        return {
            "id": id_,
            "title": title,
            "art": art,
            "release_date": release_date,
            "publisher": publisher,
            "spotify_Url": spotify_url,
            "artist": artist,
            "genre": genres,
            "total_ratings": total_unique_ratings,
            "rating_average": rating_average,
        }

    # Read
    def _full_search(self, search_keyword):
        """Search performed on an exact match where album has reviews in DB."""
        if search_keyword.isnumeric():
           search_keyword = self._select_title_by_album_id(search_keyword)
        statement = ("""
            SELECT album.id, album.title, album.album_cover, album.release_date, album.publisher, album.spotify_url, artist.name, 
            genre.name as genre_name, review.rating from album as album INNER JOIN artist as artist on album.artist_id = artist.id 
            INNER JOIN album_genre on album.id = album_genre.album_id INNER JOIN genre as genre on album_genre.genre_id = genre.id 
            INNER JOIN review on album.id = review.album_id WHERE album.title = %s
         """
        )
        print(f"Album Full Search: {statement}, Kwargs: ({search_keyword},)")
        logging.debug(f"Album Full Search: {statement}, Kwargs: ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword, )).fetchall()
        return [self._full_search_parse(queries)]

    def _main_page_album_data(self, query_tuple):
        """Format data for presentation on main/inhex/home page."""
        album_art, album_title, artist_name, artist_page, spotify_url = query_tuple
        return {
            "album_art": album_art,
            "album_title": album_title,
            "artist_name": artist_name,
            "artist_page": artist_page,
            "spotify_url": spotify_url,
        }

    # Read
    def get_all_albums(self):
        """Retrieve all albums."""
        statement = "SELECT * from album;"
        print(f"Get All Albums: {statement}")
        logging.debug(f"Get All Albums: {statement}")
        queries = self.execute_query(statement).fetchall()
        return [self._album_data(query) for query in queries]

    # Update
    def update_or_set_nullable_album_art(self, value, id_):
        """Updates album art. Can also set to NULL."""
        statement = "UPDATE album set album_cover = %s where id = %s;"
        print(f"Update or Nullify album debug: {statement} {value}, {id_}")
        logging.debug(f"Update or Nullify album debug: {statement} {value}, {id_}")
        queries = self.execute_query(statement, (value, id_,)).fetchone()
        return

    # Delete
    def _remove_from_album_genre(self, id_):
        """Removes row from album_genre when a delete call to albums is made."""
        statement="DELETE from album_genre where album_id = %s;"
        queries = self.execute_query(statement, (id_),).fetchall()

    # Delete
    def delete_entire_album(self, id_):
        """Removes entire album from DB."""
        self._remove_from_album_genre(id_)
        statement = "DELETE from album where id = %s;"
        queries = self.execute_query(statement, (id_,)).fetchone()
        return

    # Read
    def main_page_album_query(self):
        """Retrieves data for main/index/home page."""
        statement = (
            """
            SELECT album_cover, title, name, website, spotify_url from album 
            INNER JOIN artist on album.artist_id=artist.id;
            """
        )
        print(f"Main Page Albums Query: {statement}")
        logging.debug(f"Main Page Albums Query: {statement}")
        queries = self.execute_query(statement).fetchall()
        return [self._main_page_album_data(query) for query in queries]

    # Read
    def get_album_id_from_name(self, name=None):
        """Retrieves album id provided a name is given."""
        if name is None:
            return None
        statement = "SELECT id from album WHERE album.title = %s"
        print(f"Get Album Id From Name: {statement} kwargs: ({name})")
        logging.debug(f"Get Album Id From Name: {statement} kwargs: ({name})")
        queries = self.execute_query(statement, (name,)).fetchall()
        # This should return only one ID. However, just in case
        # something goes wrong with the DB/SQL the only_item_of
        # call can help us debug. It is possible to have called
        # fetchone() but that might have masked a problem.
        # This is extra/verbose code that serves as a safeguard.
        return only_item_of([query[0] for query in queries])

    # Read
    def _does_album_exist(self, album):
        """Returns a DB row if an album name is in the DB."""
        statement = "SELECT id from album where album.title = %s;"
        print(f"DEBUG IF ALBUM EXISTs: {statement} and {album}")
        logging.debug(f"DEBUG IF ALBUM EXISTs: {statement} and {album}")
        return self.execute_query(statement, (album,)).fetchall()

    def _validate_insert_album_data(self, data):
        """Helper to validate album creation data."""
        if not data['albumTitle']:
            return 'album name must be present'
        if not data['albumArtist']:
            return 'artist name must be present'
        if data['albumCover'][:4] != 'http':
           return 'website was not URL (hint: try leading with http)'
        if self._does_album_exist(data['albumTitle']):
           return 'album already exists'
        if not data['albumGenres']:
           return 'must add at least one genre'
        return True

    # Update
    def _update_album_genre(self, genres, album_id):
       """Update M:M relationship in relational table."""
       print(genres)
       print(len(genres))
       genres = [int(x) for x in genres.split(",")] 
       statement = "INSERT into album_genre (album_id, genre_id) VALUES (%s, %s);"
       for genre in genres:
           logging.debug(f"UPDATING M:M SQL FOR ALBUM_GENRE: {statement} {genre}")
           self.execute_query(statement, (album_id, genre,)).fetchall()

    # Create
    def create_new_album(self, data):
        """Inserts new album into DB from user input data."""
        validated = self._validate_insert_album_data(data)
        if isinstance(validated, str):
            return validated
        statement = (
	    """
	    INSERT INTO album (title, artist_id, album_cover, release_date, publisher, spotify_url) VALUES (%s, %s, %s, %s, %s, %s);
	    """
	)
        id = self.execute_query(statement, (data['albumTitle'], data['albumArtist'], data['albumCover'], data['albumDate'], data['albumPublisher'], data['spotifyURL'],)).lastrowid
        self._update_album_genre(data['albumGenres'], id)
        return

class ReviewTable(DBConnection):
    """This class handles all SQL queries for CRUD interactions with the Review table.
    
    Occasionally there are joins with other tables on foreign keys.
    """
    # https://stackoverflow.com/questions/7469656/fill-mysql-records-one-to-many-related-tables-in-one-action
    # ^^ might need to adopt the above as a way to update the users with their reviews. not sure yet
    # should ask in piazza
    def _review_page_review_data(self, query_tuple):
        """Formats review data for display on review jinja templates."""
        review_id, review_text, rating, firstname, lastname, user_id = query_tuple
        return {
            "review_id": review_id,
            "review_text": review_text,
            "rating": rating,
            "name": f"{firstname} {lastname}",
            "user_id": user_id,
        }
    
    def _edit_review(self, query_tuple):
        """Helper to format data for a user to edit a review."""
        review_text, rating = query_tuple
        return {
             "review_text": review_text,
             "rating": rating,
        }

    # Read
    def get_single_review_by_id(self, id):
        """Retrieve review details with a given review ID."""
        statement = (
                """
                SELECT review.review_text, review.rating from review where review.id = %s;
                """
        )
        print(f"DEBUG GET SINGLE REVIEW ID: {statement}, id: {id}")
        queries = self.execute_query(statement, (id,)).fetchall()
        return only_item_of([self._edit_review(query) for query in queries])

    # Delete
    def delete_review(self, review_id):
        """Delete a review by id from the DB."""
        statement = (
            """
            DELETE FROM review WHERE id = %s;
            """
        )
        queries = self.execute_query(statement, (review_id, )).fetchone()
        return queries

    # Update
    def update_comment(self, review_text, rating, review_id):
        """Modify review comment and rating by a specific id."""
        statement = (
                 """
                 UPDATE review set review_text = %s, rating = %s where review.id = %s;
                 """
        )
        queries = self.execute_query(statement, (review_text, rating, review_id,)).fetchall()
        return queries

    # Read
    def get_reviews_for_an_album(self, album_id=None):
        """Retrieve reviews for an album by a specific album id."""
        # I only have one review in the DB Table right now so this statement works
        # but I will need to add a where statement for where album_id=arg
        if album_id is None:
            return []
        statement = (
            """
            SELECT review.id, review.review_text, review.rating, user.firstname, user.lastname, user.id from review 
            INNER JOIN user on review.user_id=user.id WHERE review.album_id = %s
            """
        )
        print("DEBUG SQL STATEMENT: {statement} KWARGS: ({album_id})")
        logging.debug("DEBUG SQL STATEMENT: {statement} KWARGS: ({album_id})")
        queries = self.execute_query(statement, (album_id,)).fetchall()
        return [self._review_page_review_data(query) for query in queries]

    # Create
    def add_new_review(self, review_text, rating, user_id, album_id):
        """Insert new review for a specific album."""
        statement = "INSERT INTO review (review_text, rating, user_id, album_id) values (%s, %s, %s, %s)"
        print("Add New Review: {statement}, KWARGS: (review_text, rating, user_id, album_id,)")
        logging.debug("Add New Review: {statement}, KWARGS: (review_text, rating, user_id, album_id,)")
        params = (review_text, rating, user_id, album_id,)
        query = self.execute_query(statement, params)


class UserTable(DBConnection):
    """This class handles all SQL queries for CRUD interactions with the User table.
    
    Occasionally there are joins with other tables on foreign keys.
    """
    def _select_all_user_data(self, query_tuple):
        """Format data for querying DB for all User columns."""
        id_, firstname, lastname, email, created_date = query_tuple
        return {
            "user_id": id_,
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "created_date": created_date,
            "full": False,
        }

    def _get_search_keyword(self, queries):
        """Search helper. Returns id for matched User search queries."""
        return only_item_of(queries)[0]

    def _format_search_helper(self, *args):
        """Search helper. Formats search data on exact match."""
        data = self._select_all_user_data(*args)
        data['id'] = data['user_id']
        data["name"] = f"{data['firstname']} {data['lastname']}"
        data.pop("firstname")
        data.pop("lastname")
        return data

    # Read
    def _touch_helper(self, id):
        """Search helper to see if user has created any reviews."""
        # ID already passed due to name complexity with user
        statement = "SELECT rating from review WHERE review.user_id = %s"
        print(f"User Touch Helper: {statement}, Kwargs ({id},)")
        logging.debug(f"User Touch Helper: {statement}, Kwargs ({id},)")
        return self.execute_query(statement, (id,)).fetchall()

    # Read
    def _search_entity_only(self, search_keyword):
        """Search performed on exact match where artist has not created any reviews."""
        statement = "SELECT * from user WHERE user.id = %s"
        print(f"User Search Entity Only: {statement}, Kwargs: ({search_keyword},)")
        logging.debug(f"User Search Entity Only: {statement}, Kwargs: ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return [self._select_all_user_data(query) for query in queries]

    def _format_full_search_data(self, queries):
        """Helper to format full search."""
        albums_artists = [{query[-2]: [query[-3], query[-1]]} for query in queries]
        # Rest of the data should be the same
        firstname, lastname, created_date, album, name, rating =  queries[0]
        return {
            "firstname": firstname,
            "lastname": lastname,
            "created_date": created_date,
            "album_artists": albums_artists,
            "full": True,
        }

    # Read
    def _full_search(self, search_keyword):
        """Search performed on exact match where user has created reviews."""
        statement = """
        SELECT distinct user.firstname, user.lastname, user.created_date,
        album.title as album_name, artist.name, review.rating from user
        INNER JOIN review on user.id = review.user_id
        INNER JOIN album on review.album_id = album.id
        INNER JOIN artist on album.artist_id = artist.id
        WHERE review.user_id = %s;
        """
        print(f"User Full Search: {statement}, Kwargs: ({search_keyword},)")
        logging.debug(f"User Full Search: {statement}, Kwargs: ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return [self._format_full_search_data(queries)]

    # Create
    def add_new_user(self, firstname, lastname, email):
        """Insert new user into DB."""
        statement = "INSERT INTO user (firstname, lastname, email) values (%s, %s, %s)"
        print(f"Add New User: {statement}")
        logging.debug(f"Add New User: {statement}")
        self.execute_query(statement, (firstname, lastname, email,))

    # Read
    def get_user_id_from_names_and_email(
        self, firstname=None, lastname=None, email=None
    ):
        """Retrieve user id based on key info provided by user."""
        # Used on Review Page
        if not all([v for v in locals().values()]):
            return None
        statement = "SELECT id from user WHERE user.firstname = %s and user.lastname = %s and user.email = %s"
        print(f"DEBUG SQL STATEMENT: {statement}, kwargs: (firstname, lastname, email,)")
        logging.debug(f"DEBUG SQL STATEMENT: {statement}, kwargs: (firstname, lastname, email,)")
        queries = self.execute_query(statement, (firstname, lastname, email,)).fetchall()
        # Handle this better
        if not queries:
            return None
            # self.add_new_user(firstname, lastname, email)
            # queries = self.execute_query(statement, (firstname, lastname, email,)).fetchall()
        return only_item_of([query[0] for query in queries])

    # Read
    def select_user_id_by_first_or_last_name(self, name_):
        """Search helper for either first or last name. Searching is hard."""
        # Used in Search Function
        # Called select user id by first or last name but used
        # also to route for multiple search results
        statement = f"SELECT * from user WHERE user.firstname like {name_}  or user.lastname like {name_}"
        print(f"User ID by First or Last: {statement}, Kwargs: ({name_},)")
        logging.debug(f"User ID by First or Last: {statement}, Kwargs: ({name_},)")
        # Params not working
        queries = self.execute_query(statement).fetchall()
        print(len(queries))
        if not queries:
            return None
        if len(queries) > 1:
            return queries
        return only_item_of(queries)[0]

class GenreTable(DBConnection):
    """This class handles all SQL queries for CRUD interactions with the genre table.
    
    Occasionally there are joins with other tables on foreign keys.
    """
    def _select_all_genre_data(self, query_tuple):
        """Format all genre data for use in templating."""
        id_, name = query_tuple
        return {"genre_id": id_, "genre_name": name, "full": False}
    
    def _get_search_keyword(self, queries):
        """Return search keyword of id."""
        if len(queries) == 1:
           # Must be ID for genre
           return only_item_of(queries)[1]
        return None

    # Read
    def _select_genre_id_by_name(self, name):
        """retrieve genre id when name is provided."""
        statement = "SELECT id from genre WHERE genre.name = %s"
        print(f"Select Genre ID by Name: {statement}, Kwargs({name},)")
        logging.debug(f"Select Genre ID by Name: {statement}, Kwargs({name},)")
        queries = self.execute_query(statement, (name, )).fetchall()
        return only_item_of([query[0] for query in queries])

    def _format_search_helper(self, *args):
        """Wrapper for Search to retrieve genre data."""
        data = self._select_all_genre_data(*args)
        data['id'] = data['genre_name']
        return data

    # Read
    def _search_entity_only(self, search_keyword):
        """Retrieve genre that has no albums associated."""
        statement = "SELECT * from genre WHERE genre.name = %s"
        print(f"Search Entity Only: {statement}, Kwargs: ({search_keyword},)")
        logging.debug(f"Search Entity Only: {statement}, Kwargs: ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return [self._select_all_genre_data(query) for query in queries]

    def _format_full_search_data(self, queries):
        """Helper to format search data."""
        album_artist = [{query[-2]: query[-1]} for query in queries]
        # Other data should be the same
        genre, title, artist = queries[0]
        return {"genre": genre, "album_artist": album_artist, "full": True}

    # Read
    def _full_search(self, search_keyword):
        """Search performed with an exact genre match that has albums associated."""
        search_keyword = self._select_genre_id_by_name(search_keyword)
        statement = """
            SELECT genre.name, album.title, artist.name from genre 
            INNER JOIN album_genre on genre.id = album_genre.genre_id 
            INNER JOIN album on album_genre.album_id=album.id
            INNER JOIN artist on album.artist_id = artist.id 
            WHERE genre.id = %s
            """
        print(f"Genre Full Search: {statement}, ({search_keyword},)")
        logging.debug(f"Genre Full Search: {statement}, ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return [self._format_full_search_data(queries)]

    # Read
    def _touch_helper(self, search_keyword):
        """Checks DB for albums associated with a given genre."""
        statement = "SELECT album_id from album_genre WHERE album_genre.genre_id = %s"
        search_keyword = self._select_genre_id_by_name(search_keyword)
        print(f"Genre Touch Helper Search: {statement}, ({search_keyword},)")
        logging.debug(f"Genre Touch Helper Search: {statement}, ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return queries

    # Read
    def select_all_genres(self):
        """Retrieve all genre data."""
        statement = "SELECT * from genre;"
        print(f"Select All Genres: {statement}")
        logging.debug(f"Select All Genres: {statement}")
        queries = self.execute_query(statement).fetchall()
        return [self._select_all_genre_data(query) for query in queries]
    
    # Create
    def insert_genre(self, data):
        """Insert new genre into DB."""
        statement = "INSERT INTO genre (name) VALUES (%s)"
        newGenre = data.get('genre')
        print(f"{(statement, (newGenre, ))}")
        id = self.execute_query(statement, (newGenre, )).lastrowid
        return id

# These dictionaries allow the code to by DRYish and are used in searching.
search_dict = {
    "album": ("album", "title", "album_title", lambda: AlbumTable()),
    "artist": ("artist", "name", "artist_name", lambda: ArtistTable()),
    "user": ("user", "id", "name", lambda: UserTable()),
    "genre": ("genre", "name", "genre_name", lambda: GenreTable()),
}


class SearchSQL(DBConnection):
    """This class handles the search functionality for the app.
    
    Searching is done by selecting the correct entity table from the
    search_dict and then calling functions which are named the same
    in each class to perform a search. This allows the code to be DRY.
    
    Terminology used:
        touch: see if an entity has relationships with other entites in DB
        search entity: retrieve data from columns only on an entity's table
        full search: retrieve data from columns on an entity table and tables
                    in relationship with the entity through joins
    """

    def _format_search_data(self, search_by, queries, table, key):
        """Formats search data by calling the helper in appropriate table."""
        queries = [table._format_search_helper(query) for query in queries]
        # If too many search results, return only the relevant information
        if len(queries) > 1:
            return [(query['id'], query[key]) for query in queries]
        return queries

    # Read
    def _check_if_search_keyword_in_database(
        self, search_keyword, search_by, table_name, column, table
    ):
        """Checks to see if user input is in the DB at all based on search type."""
        # Can't get this one working with query params
        where_operator = "like"
        search_keyword = f"'%{search_keyword}%'"
        if search_by == "user":
            search_keyword = table.select_user_id_by_first_or_last_name(search_keyword)
            if not search_keyword:
                return (search_keyword, None)
            if isinstance(search_keyword, tuple):
                return(search_keyword, None)
            where_operator = "="
        statement = f"SELECT * from {table_name} where {column} {where_operator} {search_keyword};"
        print(f"DEBUG SQL STATEMENT: {statement}, KWARGS: ({table_name}, {column}, {where_operator}, {search_keyword}, )")
        logging.debug(f"DEBUG SQL STATEMENT: {statement}, KWARGS: ({table_name}, {column}, {where_operator}, {search_keyword}, )")
        queries = self.execute_query(statement).fetchall()
        return (queries, table._get_search_keyword(queries))

    def _touch_database(self, search_keyword, table):
        """See if query will qualify for full search."""
        return table._touch_helper(search_keyword)

    def _search_entity_only(self, search_keyword, table):
        """Search to perform on exact match that does not qualify for full search."""
        return table._search_entity_only(search_keyword)

    def _full_search(self, search_keyword, table):
        """Search to perform on an exact match with relationships."""
        return table._full_search(search_keyword)

    # Read
    def complete_full_search_from_main_or_redirect(self, table, search_keyword):
        """Separate out logic for full or entity search into different function.
        
        This allows multiple results options page to redirect to the correct result.
        """
        touch = self._touch_database(search_keyword, table)
        logging.debug(f"SEARCH BY {table} for {search_keyword} TOUCH QUERY RESULTS: {touch}")
        if not touch:
            # Search against entity only
            results = self._search_entity_only(search_keyword, table)
            print(f"ENTITY ONLY: {results}")
            return (1, results)
        # Full Search
        full = self._full_search(search_keyword, table)
        print(f"FULL ONLY: {full}")
        return (1, full)

    # Read  
    def execute_search(self, search_keyword, search_by):
        """ 
        Main search execution function. 
        
        Routes data to helper function dependent on need.
        Searching has these options:
            1. Search submitted with no value in text field
                    - return None
            2. Search submitted with data, but no data found
                   - return Empty List
            3. Search submitted with data and returns multiple rows
                   -  return tuple (number of rows, structured data from rows)
            4. Search submitted with data and returns one result
                   - touches database to see if inner joins on
                      tables with foreign keys will yield results
                          - if so: performs full query with inner joins
                          - if not: performs full query against search entity
        
        Parameters:
            search_keyword (string): data input by user
            search_by (string): data from search select dropdown
        
        Returns variable    
        """
        # Option 1
        if not all([search_keyword, search_by]):
            return None
        table_name, column, key, table = must_get_key(search_dict, search_by)
        table = table()
        queries, search_keyword = self._check_if_search_keyword_in_database(
            search_keyword, search_by, table_name, column, table
        )
        # Option 2
        if not queries:
            return []
        # Option 3
        if len(queries) > 1:
            return (len(queries), self._format_search_data(search_by, queries, table, key))
        # Option 4
        return self.complete_full_search_from_main_or_redirect(table, search_keyword)
