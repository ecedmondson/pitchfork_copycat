from database.database_connector import DBConnection
from database.models.statements import (
    insert_statement,
    select_statement,
    inner_join,
    where,
    full_search_queries,
)
from jgt_common import only_item_of, must_get_key


class ArtistTable(DBConnection):
    def _select_all_artist_data(self, query_tuple):
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

    def _select_artist_id_from_name(self, name):
        select = select_statement("artist", column="id")[:-1]
        where_ = where("arist", "name", "=", f"'{name}'")
        statement = f"{statement} {where};"
        print(f"DEBUG SQL: {statement}")
        queries = self.execute_query(statement).fetchall()
        return only_item_of([query[0] for query in queries])

    def _format_search_helper(self, *args):
        return self._select_all_artist_data(*args)

    def _touch_helper(self, search_keyword):
        id = self._select_artist_id_from_name(search_keyword)
        select = select_statement("review", column="id")[:-1]
        where_ = where("review", "album_id", "=", id)
        statement = f"{statement} {where};"
        print(f"DEBUG SQL: {statement}")
        return self.execute_query(statement).fetchall()

    def add_new_artist(self):
        insert = insert_statement("artist", [], [])
        self.execute_query(insert)


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

    def _select_id_by_album_title(self, title):
        select = select_statement("album", column="id")[:-1]
        where_ = where("album", "title", "=", f"'{title}'")
        statement = f"{statement} {where};"
        print(f"DEBUG SQL: {statement}")
        queries = self.execute_query(statement).fetchall()
        return only_item_of([query[0] for query in queries])

    def _touch_helper(self, search_keyword):
        # Touch on review since it is the inner join
        # ID needed for relational query
        id = self._select_id_by_album_title(search_keyword)
        select = select_statement("review", column="id")[:-1]
        where_ = where("review", "album_id", "=", id)
        statement = f"{statement} {where};"
        print(f"DEBUG SQL: {statement}")
        return self.execute_query(statement).fetchall()

    def _full_search_parse(self, queries):
        ratings = []
        genres = []
        constants_checked = False
        for query in queries:
            if constants_checked:
                genre = query[-2]
                rating = query[-1]
            else:
                (
                    title,
                    art,
                    release_date,
                    publisher,
                    spotify_url,
                    artist,
                    genre,
                    rating,
                ) = query
            ratings.append(rating)
            genres.append(genre)
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
        select = select_statement("album")
        print(f"DEBUG SQL STATEMENT: {select}")
        queries = self.execute_query(select).fetchall()
        return [self._album_data(query) for query in queries]

    def main_page_album_query(self):
        select = select_statement(
            "album", column=["album_cover", "title", "name", "website", "spotify_url"]
        )[:-1]
        inner = inner_join("album", "artist", "artist_id", "id")
        statement = f"{select} {inner};"
        print(f"DEBUG SQL STATEMENT: {statement}")
        queries = self.execute_query(statement).fetchall()
        return [self._main_page_album_data(query) for query in queries]

    def get_album_id_from_name(self, name=None):
        if name is None:
            return None
        select = select_statement("album", column="id")[:-1]
        # MySQL client/Maria DB got mad when quotes weren't included.
        # That is why the where template call includes an f-string.
        where_ = where("album", "title", "=", f"'{name}'", and_=True)
        statement = f"{select} {where_};"
        print(f"DEBUG SQL STATEMENT: {statement}")
        queries = self.execute_query(statement).fetchall()
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
        select = select_statement(
            "review", column=["review_text", "rating", "firstname", "lastname"]
        )[:-1]
        inner = inner_join("review", "user", "user_id", "id")
        where_ = where("review", "album_id", "=", album_id, and_=True)
        statement = f"{select} {inner} {where_};"
        print(f"DEBUG SQL STATEMENT: {statement}")
        queries = self.execute_query(statement).fetchall()
        return [self._review_page_review_data(query) for query in queries]

    def add_new_review(self, review_text, rating, user_id, album_id):
        # Same quotation problem as above. This happens with strings, I think.
        insert = insert_statement(
            "review",
            ["review_text", "rating", "user_id", "album_id"],
            [f"'{review_text}'", rating, user_id, album_id],
        )
        print(f"DEBUG SQL STATEMENT: {insert}")
        query = self.execute_query(f"{insert};")


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

    def _format_search_helper(self, *args):
        data = self._select_all_user_data(*args)
        data["name"] = f"{data['firstname']} {data['lastname']}"
        data.pop("firstname")
        data.pop("lastname")
        return data

    def _touch_helper(self, id):
        # ID already passed due to name complexity with user
        select = select_statement("review", column="rating")[:-1]
        where_ = where("review", "userid", "=", id)
        statement = f"{statement} {where};"
        print(f"DEBUG SQL: {statement}")
        return self.execute_query(statement).fetchall()

    def add_new_user(self, firstname, lastname, email):
        insert = insert_statement(
            "user",
            ["firstname", "lastname", "email"],
            [f"'{firstname}'", f"'{lastname}'", f"'{email}'"],
        )
        print(f"DEBUG SQL STATEMENT: {insert}")
        self.execute_query(f"{insert};")

    def get_user_id_from_names_and_email(
        self, firstname=None, lastname=None, email=None
    ):
        if not all([v for v in locals().values()]):
            return None
        select = select_statement("user", column="id")[:-1]
        where_firstname = where("user", "firstname", "=", f"'{firstname}'")
        where_lastname = where(
            "user", "lastname", "=", f"'{lastname}'", chain=True, and_=True
        )
        where_email = where("user", "email", "=", f"'{email}'", chain=True, and_=True)
        statement = f"{select} {where_firstname} {where_lastname} {where_email};"
        print(f"DEBUG SQL STATEMENT: {statement}")
        queries = self.execute_query(statement).fetchall()
        if not queries:
            self.add_new_user(firstname, lastname, email)
            queries = self.execute_query(statement).fetchall()
        return only_item_of([query[0] for query in queries])

    def select_user_id_by_first_or_last_name(self, name_):
        select = select_statement(table, column="*")[:-1]
        where_first = where("user", "firstname", "like", f"'%{search_keyword}%'")
        where_last = where(
            "user", "lastname", "like", f"'%{search_keyword}%'", chain=True, and_=False
        )
        where_ = where_first + where_last
        statement = f"{select} {where_}"
        print(f"DEBUG SQL STATEMENT: {statement}")
        queries = self.execute_query(statement).fetchall()
        return only_item_of([query[0] for query in queries])


class GenreTable(DBConnection):
    def _select_all_genre_data(self, query_tuple):
        id_, name = query_tuple
        return {"genre_id": id_, "genre_name": name}

    def _select_genre_id_by_name(self, name):
        select = select_statement("genre", column="id")[:-1]
        where_ = where("genre", "name" "=", f"'{name}'")
        statement = f"{select} {where};"
        print(f"DEBUG SQL STATEMENT: {statement}")
        queries = self.execute_query(statement)
        return only_item_of([query[0] for query in queries])

    def _format_search_helper(self, *args):
        return self._select_all_genre_data(*args)

    def _touch_helper(self, search_keyword):
        id = self._select_genre_id_by_name(search_keyword)
        select = select_statement("album_genre", column="album_id")[:-1]
        where_ = where("album_genre", "genre_id", "=", id)
        statement = f"{statement} {where};"
        print(f"DEBUG SQL: {statement}")
        return self.execute_query(statement).fetchall()

    def select_all_genres(self):
        select = select_statement("genre", column="*")
        print(f"DEBUG SQL STATEMENT: {select}")
        queries = self.execute_query(select).fetchall()
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
        self, search_keyword, search_by, table, column
    ):
        where_operator = "like"
        search_keyword = f"'%{search_keyword}%'"
        if search_by == "user":
            search_keyword = table.select_user_id_by_first_or_last_name(search_keyword)
            where_operator = "="
            search_keyword.replace("%", "")
        select = select_statement(table, column="*")[:-1]
        where_ = where(table, column, where_operator, search_keyword)
        statement = f"{select} {where_};"
        print(f"DEBUG SQL STATEMENT: {statement}")
        return self.execute_query(statement).fetchall()

    def _touch_database(self, search_keyword, table):
        return table._touch_helper(search_keyword)

    def _search_table_only(self, search_keyword, column, table):
        pass

    def _full_search(self, key, search_data, table_name):
        table = self.search_extract_dict[table_name][0]()
        query_options = must_get_key(full_search_queries, key)
        if self.execute_query(
            query_options["touch"].replace(
                "<<<ID>>>", str(only_item_of(search_data)["album_id"])
            )
        ).fetchall():
            queries = self.execute_query(
                query_options["reviews"].replace(
                    "<<<ID>>>", str(only_item_of(search_data)["album_id"])
                )
            ).fetchall()
        else:
            queries = self.execute_query(
                query_options["no_reviews"].replace(
                    "<<<ID>>>", str(only_item_of(search_data)["album_id"])
                )
            ).fetchall()
        return (1, table._full_search_parse(queries))

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
        queries = self._check_if_search_keyword_in_database(
            search_keyword, search_by, table_name, column
        )
        # Option 2
        if not queries:
            return []
        # Option 3
        if len(queries) > 1:
            return (len(queries), self._format_search_data(search_by, queries))
        # Option 4
        # Provide actual value so that a where like doesn't occur again
        search_keyword = only_item_of(queries)
        touch = self._touch_database(search_keyword, table)
        if touch:
            # Search against entity only
            return (1, self._search_table_only(search_keyword))
        # Full Search
        return (1, self._full_search(search_keyword))

        if search_by == "album":
            # This is temporary
            return self._full_search(
                search_by, self._search_data(search_by, queries), table
            )
        if search_by == "artist":
            queries = self.execute_query(
                f"select artist.name, artist.location, artist.website, artist.description, artist.image, album.title, album.release_date from artist as artist inner join album on artist.id=album.artist_id where artist.name like "
                + f"'%{search_keyword}%'"
                + ";"
            ).fetchall()
            for query in queries:
                (
                    name,
                    location,
                    website,
                    description,
                    image,
                    album_title,
                    album_release,
                ) = query
                return (
                    1,
                    {
                        "name": name,
                        "location": location,
                        "website": website,
                        "description": description,
                        "image": image,
                        "album_title": album_title,
                        "album_release": album_release,
                    },
                )
        if search_by == "genre":
            queries = self.execute_query(
                "select genre.name, album.title from genre inner join album_genre on genre.id = album_genre.genre_id inner join album on album_genre.album_id=album.id where genre.name ="
                + f"'{search_keyword}';"
            ).fetchall()
            print(queries)
            albums = []
            for query in queries:
                name, album = query
                albums.append(album)
            return (1, {"name": name, "albums": albums})
        return (len(queries), self._format_search_data(search_by, queries))
