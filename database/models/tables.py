from database.database_connector import DBConnection
from jgt_common import only_item_of, must_get_key
from flask import abort
import logging

logging.basicConfig(filename='runtime_sql_queries.log', level=logging.DEBUG)


class ArtistTable(DBConnection):
    def _format_all_artist_data(self, query_tuple):
        # Data formatted for select all artist call
        artist_id, artist_name, website, image, location, description = query_tuple
        return {
            "artist_id": artist_id,
            "artist_name": artist_name,
            "website": website,
            "image": image,
            "location": location,
            "description": description,
        }
    
    def _get_search_keyword(self, queries):
        if len(queries) == 1:
            return only_item_of(queries)[1]
        return None

    def _select_artist_id_from_name(self, name):
        statement = "SELECT id from artist WHERE artist.name = %s"
        print(f"Artist ID from Artist Name: {statement}, KWARGS ({name},)")
        logging.debug(f"Artist ID from Artist Name: {statement}, KWARGS ({name},)")
        queries = self.execute_query(statement, (name,)).fetchall()
        return only_item_of([query[0] for query in queries])

    def _format_search_helper(self, *args):
        return self._format_all_artist_data(*args)

    def _touch_helper(self, search_keyword):
        # NEEDS WORK
        id = self._select_artist_id_from_name(search_keyword)
        statement = "SELECT id from review WHERE review.album_id = %s"
        print(f"Artist Touch Helper: {statement}, KWARGS: ({search_keyword},)")
        logging.debug(f"Artist Touch Helper: {statement}, KWARGS: ({search_keyword},)")
        return self.execute_query(statement, (search_keyword, )).fetchall()

    def _search_entity_only(self, search_keyword):
        # This is dependent on PR 9
        abort(404)

    def _full_search(self, search_keyword):
        # This is dependent on PR 9
        abort(404)

    def add_new_artist(self, request):
        #TODO: GenreTable and related ones need to be updated when a new artist is added
        artist_to_add = request.form.to_dict()
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
        self.execute_query(statement)
        return

    def all_artists(self):
        statement = ("SELECT * FROM artist")
        queries = self.execute_query(statement).fetchall()
        return [self._format_all_artist_data(query) for query in queries]

    def _select_single_artist_page(self, artist_id):
        statement = ("SELECT * FROM artist WHERE artist.id = %s" % artist_id) 
        queries = self.execute_query(statement).fetchone()
        return self._format_all_artist_data(queries)

    def _select_albums_from_artist(self, artist_id):
        statement = ("SELECT * FROM album WHERE artist_id = %s" % artist_id)
        queries = self.execute_query(statement).fetchall()
        return [AlbumTable._album_data(AlbumTable, query) for query in queries]
        
class AlbumTable(DBConnection):
    def _album_data(self, query_tuple):
        # Data formatter for get_all_albums call
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
        return self._album_data(*args)

    def _get_search_keyword(self, queries):
        if len(queries) == 1:
            return only_item_of(queries)[2]
        return None

    def _select_id_by_album_title(self, title):
        statement = "SELECT id from album WHERE album.title = %s"
        print(f"Select ID by Album Title: {statement} KWARGS: ({title},)")
        logging.debug(f"Select ID by Album Title: {statement} KWARGS: ({title},)")
        queries = self.execute_query(statement, (title,)).fetchall()
        return only_item_of([query[0] for query in queries])

    def _touch_helper(self, search_keyword):
        # Touch on review since it is the inner join
        # ID needed for relational query
        id = self._select_id_by_album_title(search_keyword)
        statement = "SELECT id from review WHERE review.album_id = %s"
        print(f"Album touch helper: {statement}, kwargs: ({search_keyword},)")
        logging.debug(f"Album touch helper: {statement}, kwargs: ({search_keyword},)")
        return self.execute_query(statement, (search_keyword, )).fetchall()

    def _format_entity_search(self, queries):
        # Only 1 Genre
        if len(queries) == 1:
            for (
                artist,
                title,
                art,
                release_date,
                publisher,
                spotify_url,
                genre,
            ) in queries:
                return {
                    "artist": artist,
                    "title": title,
                    "art": art,
                    "release_date": release_date,
                    "publisher": publisher,
                    "genre": genre,
                }
        # More than one Genre
        genres = [query[-1] for query in queries]
        # Other data should stay the same so return the first
        print(queries)
        print(queries[0])
        artist, title, art, release_date, publisher, spotify_url, genre = queries[0]
        return {
                "artist": artist,
                "title": title,
                "art": art,
                "release_date": release_date,
                "publisher": publisher,
                "genre": genres,
        }

    def _search_entity_only(self, search_keyword):
        # Search for when no reviews exist
        statement = ("""
            SELECT artist.name, album.title, album.album_cover, album.release_date, album.publisher,
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
        # Multiples
        ratings = [query[-1] for query in queries]
        genres = [query[-2] for query in queries]
        constants_checked = False
        # Other data should stay the same so return the first
        (
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

    def _full_search(self, search_keyword):
        statement = ("""
            SELECT album.title, album.album_cover, album.release_date, album.publisher, album.spotify_url, artist.name, 
            genre.name as genre_name, review.rating from album as album INNER JOIN artist as artist on album.artist_id = artist.id 
            INNER JOIN album_genre on album.id = album_genre.album_id INNER JOIN genre as genre on album_genre.genre_id = genre.id 
            INNER JOIN review on album.id = review.album_id WHERE album.title = %s
         """
        )
        print(f"Album Full Search: {statement}, Kwargs: ({search_keyword},)")
        logging.debug(f"Album Full Search: {statement}, Kwargs: ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword, )).fetchall()
        return self._full_search_parse(queries)

    def _main_page_album_data(self, query_tuple):
        album_art, album_title, artist_name, artist_page, spotify_url = query_tuple
        return {
            "album_art": album_art,
            "album_title": album_title,
            "artist_name": artist_name,
            "artist_page": artist_page,
            "spotify_url": spotify_url,
        }

    def get_all_albums(self):
        statement = "SELECT * from album;"
        print(f"Get All Albums: {statement}")
        logging.debug(f"Get All Albums: {statement}")
        queries = self.execute_query(statement).fetchall()
        return [self._album_data(query) for query in queries]

    def main_page_album_query(self):
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

    def get_album_id_from_name(self, name=None):
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


class ReviewTable(DBConnection):
    # https://stackoverflow.com/questions/7469656/fill-mysql-records-one-to-many-related-tables-in-one-action
    # ^^ might need to adopt the above as a way to update the users with their reviews. not sure yet
    # should ask in piazza
    def _review_page_review_data(self, query_tuple):
        review_text, rating, firstname, lastname = query_tuple
        return {
            "review_text": review_text,
            "rating": rating,
            "name": f"{firstname} {lastname}",
        }

    def get_reviews_for_an_album(self, album_id=None):
        # I only have one review in the DB Table right now so this statement works
        # but I will need to add a where statement for where album_id=arg
        if album_id is None:
            return []
        statement = (
            """
            SELECT review_text, rating, firstname, lastname from review 
            INNER JOIN user on review.user_id=user.id WHERE review.album_id = %s
            """
        )
        print("DEBUG SQL STATEMENT: {statement} KWARGS: ({album_id})")
        logging.debug("DEBUG SQL STATEMENT: {statement} KWARGS: ({album_id})")
        queries = self.execute_query(statement, (album_id,)).fetchall()
        return [self._review_page_review_data(query) for query in queries]

    def add_new_review(self, review_text, rating, user_id, album_id):
        statement = "INSERT INTO review (review_text, rating, user_id, album_id) values (%s, %s, %s, %s)"
        print("Add New Review: {statement}, KWARGS: (review_text, rating, user_id, album_id,)")
        logging.debug("Add New Review: {statement}, KWARGS: (review_text, rating, user_id, album_id,)")
        params = (review_text, rating, user_id, album_id,)
        query = self.execute_query(statement, params)


class UserTable(DBConnection):
    def _select_all_user_data(self, query_tuple):
        id_, firstname, lastname, email, created_date = query_tuple
        return {
            "user_id": id_,
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "created_date": created_date,
        }

    def _get_search_keyword(self, queries):
        return only_item_of(queries)[0]

    def _format_search_helper(self, *args):
        data = self._select_all_user_data(*args)
        data["name"] = f"{data['firstname']} {data['lastname']}"
        data.pop("firstname")
        data.pop("lastname")
        return data

    def _touch_helper(self, id):
        # ID already passed due to name complexity with user
        statement = "SELECT rating from review WHERE review.user_id = %s"
        print(f"User Touch Helper: {statement}, Kwargs ({id},)")
        logging.debug(f"User Touch Helper: {statement}, Kwargs ({id},)")
        return self.execute_query(statement, (id,)).fetchall()

    def _search_entity_only(self, search_keyword):
        statement = "SELECT * from user WHERE user.id = %s"
        print(f"User Search Entity Only: {statement}, Kwargs: ({search_keyword},)")
        logging.debug(f"User Search Entity Only: {statement}, Kwargs: ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return only_item_of([self._select_all_user_data(query) for query in queries])

    def _format_full_search_data(self, queries):
        albums_artists = [{query[-2]: [query[-3], query[-1]]} for query in queries]
        # Rest of the data should be the same
        firstname, lastname, created_date, album, name, rating =  queries[0]
        return {
            "firstname": firstname,
            "lastname": lastname,
            "created_date": created_date,
            "album_artists": albums_artists,
        }

    def _full_search(self, search_keyword):
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
        return self._format_full_search_data(queries)

    def add_new_user(self, firstname, lastname, email):
        statement = "INSERT INTO user (firstname, lastname, email) values (%s, %s, %s)"
        print(f"Add New User: {statement}")
        logging.debug(f"Add New User: {statement}")
        self.execute_query(statement, (firstname, lastname, email,))

    def get_user_id_from_names_and_email(
        self, firstname=None, lastname=None, email=None
    ):
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

    def select_user_id_by_first_or_last_name(self, name_):
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
    def _select_all_genre_data(self, query_tuple):
        id_, name = query_tuple
        return {"genre_id": id_, "genre_name": name}
    
    def _get_search_keyword(self, queries):
        if len(queries) == 1:
           # Must be ID for genre
           return only_item_of(queries)[1]
        return None

    def _select_genre_id_by_name(self, name):
        statement = "SELECT id from genre WHERE genre.name = %s"
        print(f"Select Genre ID by Name: {statement}, Kwargs({name},)")
        logging.debug(f"Select Genre ID by Name: {statement}, Kwargs({name},)")
        queries = self.execute_query(statement, (name, )).fetchall()
        return only_item_of([query[0] for query in queries])

    def _format_search_helper(self, *args):
        return self._select_all_genre_data(*args)

    def _search_entity_only(self, search_keyword):
        statement = "SELECT * from genre WHERE genre.name = %s"
        print(f"Search Entity Only: {statement}, Kwargs: ({search_keyword},)")
        logging.debug(f"Search Entity Only: {statement}, Kwargs: ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return only_item_of([self._select_all_genre_data(query) for query in queries])

    def _format_full_search_data(self, queries):
        album_artist = [{query[-2]: query[-1]} for query in queries]
        # Other data should be the same
        genre, title, artist = queries[0]
        return {"genre": genre, "album_artist": album_artist}

    def _full_search(self, search_keyword):
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
        return self._format_full_search_data(queries)

    def _touch_helper(self, search_keyword):
        statement = "SELECT album_id from album_genre WHERE album_genre.genre_id = %s"
        search_keyword = self._select_genre_id_by_name(search_keyword)
        print(f"Genre Touch Helper Search: {statement}, ({search_keyword},)")
        logging.debug(f"Genre Touch Helper Search: {statement}, ({search_keyword},)")
        queries = self.execute_query(statement, (search_keyword,)).fetchall()
        return queries

    def select_all_genres(self):
        statement = "SELECT * from genre;"
        print(f"Select All Genres: {statement}")
        logging.debug(f"Select All Genres: {statement}")
        queries = self.execute_query(statement).fetchall()
        return [_select_all_genre_data(query) for query in queries]


# These dictionaries allow the code to by DRYish
search_dict = {
    "album": ("album", "title", "album_title", lambda: AlbumTable()),
    "artist": ("artist", "name", "artist_name", lambda: ArtistTable()),
    "user": ("user", "id", "name", lambda: UserTable()),
    "genre": ("genre", "name", "genre_name", lambda: GenreTable()),
}


class SearchSQL(DBConnection):
    def _format_search_data(self, search_by, queries, table, key):
        queries = [table._format_search_helper(query) for query in queries]
        # If too many search results, return only the relevant information
        if len(queries) > 1:
            return [query[key] for query in queries]
        return queries

    def _check_if_search_keyword_in_database(
        self, search_keyword, search_by, table_name, column, table
    ):
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
        return table._touch_helper(search_keyword)

    def _search_entity_only(self, search_keyword, table):
        return table._search_entity_only(search_keyword)

    def _full_search(self, search_keyword, table):
        return table._full_search(search_keyword)

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
        touch = self._touch_database(search_keyword, table)
        logging.debug(f"SEARCH BY {search_by} for {search_keyword} TOUCH QUERY RESULTS: {touch}")
        if not touch:
            # Search against entity only
            results = self._search_entity_only(search_keyword, table)
            print(f"ENTITY ONLY: {results}")
            return (1, results)
        # Full Search
        full = self._full_search(search_keyword, table)
        print(f"FULL ONLY: {full}")
        return (1, full)
