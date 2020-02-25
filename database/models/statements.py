from jgt_common import must_get_key


def insert_statement(table_name, columns, values):
    columns = ", ".join(columns)
    values = ", ".join(values)
    return f"INSERT INTO {table_name} ({columns}) values ({values});"


def select_statement(table_name, column="*"):
    if isinstance(column, list):
        column = ", ".join(column)
    return f"SELECT {column} from {table_name};"


def inner_join(original_table, join_table, original_table_factor, join_table_factor):
    # Inner join provides an inner join statement that can be appended to another SQL query.
    # The appending must take place in the calling function before an SQL query is executed.
    return f"INNER JOIN {join_table} on {original_table}.{original_table_factor}={join_table}.{join_table_factor}"


def where(table, table_value, operation, filter_field, chain=False, and_=False):
    # Chain is a boolean used to distinguish whether multiple where
    # conditions are called. Like with inner_join, the chaining or
    # appending of where statements must take place in the calling function.
    # Including a boolean kwarg as a way of routing code has a bad code
    # smell, but I can't think of a better way to handle two otherwise
    # syntactically similar SQL clauses.
    conjunction = "and" if and_ else "or"
    if not chain:
        return f"WHERE {table}.{table_value} {operation} {filter_field}"
    return f"{conjunction} {table}.{table_value} {operation} {filter_field}"


full_search_queries = {
    "album": 
		{"touch": 
			"select * from  review where album_id=<<<ID>>>", 
		"reviews":
			"""select album.title, album.album_cover, album.release_date, album.publisher, album.spotify_url, artist.name, 
			genre.name as genre_name, review.rating from album as album inner join artist as artist on album.artist_id = artist.id 
			inner join album_genre on album.id = album_genre.album_id inner join genre as genre on album_genre.genre_id = genre.id 
			inner join review on album.id = review.album_id where album.id = <<<ID>>>;""",
		"no_reviews":
			"""select album.title, album.album_cover, album.release_date, album.publisher, album.spotify_url, artist.name, 
			genre.name as genre_name from album inner join artist on album.artist_id=artist.id inner join album_genre on 
			album.id = album_genre.album_id inner join genre on album_genre.genre_id = genre.id where album.id =<<<ID>>>;""",
                }
}
