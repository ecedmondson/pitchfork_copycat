#!NOTE! The code in this file has been copied almost character for character
# from the Python/Flask starter kit provided to students of OSU cs340.
# Any credit for this code is to be given to the original author and
# the source can be found at: github.com/knightsamar/CS340_starter_flask_app
# Any code written independently of the above repo or modified will have
# a gloss above indicating such.

import MySQLdb as mariadb
import os
from MySQLdb._exceptions import OperationalError
from jgt_common import must_get_key

def connect_to_database(host=os.environ['HOST'], user=os.environ['USER'], passwd=os.environ['PW'], db=os.environ['DB']):
    """
    connects to a database and returns a database objects
    """
    db_connection = mariadb.connect(host, user, passwd, db)
    return db_connection


class DBConnection:
    def execute_query(self, query=None, query_params=None):
        """
        Executes a given SQL query on the given db connection and returns a Cursor object
        
            db_connection: a MySQLdb connection object created by connect_to_database()
            query: string containing SQL query
        
        returns: A Cursor object as specified at https://www.python.org/dev/peps/pep-0249/#cursor-objects.
        You need to run .fetchall() or .fetchone() on that object to actually acccess the results.
        """
        db_connection = connect_to_database()
        #if db_connection is None:
            #print(
                #"No connection to the database found! Have you called connect_to_database() first?"
            #)
            #return None

        if query is None or len(query.strip()) == 0:
            print("Query is empty! Please pass a SQL query in the query param")
            return None
        if bool(query_params):
            print(f"Executing %s with %s" % (query, query_params))
        # Create a cursor to execute query. C.f. PEP0249
        cursor = db_connection.cursor()
        query_execution = must_get_key({True: lambda: cursor.execute(query, query_params), False: lambda: cursor.execute(query)}, bool(query_params))
        """
        params = tuple()
        #create a tuple of parameters to send with the query
        for q in query_params:
            params = params + (q)
        """
        # TODO: Sanitize the query before executing it!!!
        # cursor.execute(query, query_params)
        try:
            query_execution()
        except OperationalError as e:
           print(f"DEBUG DB Connection: {e}")
           db_connection = connect_to_database()
           cursor = db_connection.cursor()
           query_execution = must_get_key({True: lambda: cursor.execute(query, query_params), False: lambda: cursor.execute(query)}, bool(query_params))
           query_execution()
        # this will actually commit any changes to the database. without this no
        # changes will be committed!
        # cursor.close()
        db_connection.commit()
        return cursor
