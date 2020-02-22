from database.database_connector import DBConnection
from database.models.statements import (
    insert_statement,
    select_statement,
    inner_join,
    where,
)
from jgt_common import only_item_of, must_get_key


search_dict = {
    "album": ("album", "title"),
    "artist": ("artist", "name"),
    "user": ("user", "firstname", "lastname"),
    "genre": ("genre", "name")
}


class ArtistTable(DBConnection):
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
            spotify_url,
            review_id,
        ) = query_tuple
        return {
            "album_id": album_id,
            "artist_id": artist_id,
            "album_title": album_title,
            "album_art": album_art,
            "release_date": release_date,
            "spotify_url": spotify_url,
            "review_id": review_id,
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
        where_ = where("album", "title", "=", f"'{name}'")
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
        where_ = where("review", "album_id", "=", album_id)
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
        where_lastname = where("user", "lastname", "=", f"'{lastname}'", chain=True)
        where_email = where("user", "email", "=", f"'{email}'", chain=True)
        statement = f"{select} {where_firstname} {where_lastname} {where_email};"
        print(f"DEBUG SQL STATEMENT: {statement}")
        queries = self.execute_query(statement).fetchall()
        if not queries:
            self.add_new_user(firstname, lastname, email)
            queries = self.execute_query(statement).fetchall()
        return only_item_of([query[0] for query in queries])

class SearchSQL(DBConnection):
    def _search_data(search_by, queries):
        pass
    
    def execute_search(self, search_keyword, search_by):
        if not all([search_keyword, search_by]):
            return []
        search_info = must_get_key(search_dict, search_by)
        if search_by == "user":
            table, first, last = search_info
        table, column = search_info
        select = select_statement(table, column="*")[:-1]
        if search_by == "user":
            where_first = where(table, first, "like", f"'%{search_keyword}%'")
            where_last = where(table, last, "like", f"'%{search_keyword}%'", chain=True, and_=False)
            where_ = where_first + where_last
        else:
            where_ = where(table, column, "like", f"'%{search_keyword}%'") 
        statement = f"{select} {where_};"
        print(f"DEBUG SQL STATEMENT: {statement}")
        queries = self.execute_query(statement).fetchall()
        print([query for query in queries])
        if not queries:
            return []
        # return (len(queries), _search_data(search_by, queries))


