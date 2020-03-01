from requests import get, post
from jgt_common import generate_random_string
from time import time, sleep


class Timer(object):
    """A very simple object useful for timing things"""

    def __init__(self):
        self.start_time = time()

    def elapsed(self, end_time=None):
        """
        Will Return the elapsed seconds.

        Args:
            end_time (int / float): The end_time to calculate elapsed against, or now (time()) if
            not supplied.
        """
        return end_time or time() - self.start_time

    def reset(self):
        """Reset the start time."""
        self.start_time = time()


def get_payload_for_add_review(body, firstname, lastname, email):
    return {
        "body": f"{generate_random_string()}_load_test_review_comment",
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "submit": "Submit",
    }


review_payload = get_payload_for_add_review(
    "automated_comment via python requests",
    "Emily",
    "Edmondson",
    "ecedmondson@gmail.com",
)

# Might want to make the port a comman dline arg
def post_review(payload):
    return post(
        "http://flip3.engr.oregonstate.edu:5162/reviews/more_postcards_from_purgatory/harrison_lemke",
        data=payload,
    )


def run_events(count_or_time, limit, payload):
    timer = Timer()
    total_count = 0
    calls = []

    while timer.elapsed() < limit if count_or_time == "time" else total_count < limit:
        x = post_review(payload)
        calls.append(x)
        total_count += 1
        # sleep(1)

    run_sec = int(timer.elapsed())
    print(f"POSTED {total_count} TOTAL EVENTS IN {run_sec} SECONDS")
    return calls


def load_test_adding_a_review():
    calls = run_events("time", 60, review_payload)
    print(f"Total of {len(calls)} api calls made.")
    status_codes = [x.status_code for x in calls]
    set_of_status_codes = set(status_codes)
    for code in set_of_status_codes:
        print(
            f"Found status code {code} in responses {status_codes.count(code)} times which is {status_codes.count(code) / len(calls) * 100} of the time."
        )


# Might want to make the port a command line arg
def post_search(payload):
    return post("http://flip1.engr.oregonstate.edu:5123", data=payload)


def search_payload_generator(search_by, search_keyword):
    return {
        "select_search": search_by,
        "search_keyword": search_keyword,
        "submit": "Submit",
    }

def _validate(when, then, and_, response):
    if response.status_code == 200:
        print(f"{when}....PASSED")
        print(f"{then}...PASSED")
    if response.status_code > 200:
        print(f"{when}...PASSED")
        print(f"{then}....FAILED with status code {response.status_code}")
        print(f"{and_}...SKIPPED")
        return
    type_search = {
        'non-existing': "can't seem to find",
        'vague': 'Whoops!',
        'existing': {'artist': 'Artist Name', 'album': 'associated with this album', 'user': 'member since', 'genre': 'Genre Name'},
        'albumless': {'artist': 'Artist Name', 'album': 'assocaited with this album', 'user': 'member since', 'genre': 'Genre Name'},
        'reviewless':{'artist': 'Artist Name', 'album': 'associated with this album', 'user': 'member since', 'genre': 'Genre Name'},
    }
    type_ = when.split(" ")[-1]
    search = when.split(" ")[-2] 
    assertion = type_search[search]
    if search in ('existing', 'albumless', 'reviewless'):
        assertion = assertion[type_]
    if assertion in  response.text:
        print(f"{and_}...PASSED")
    else:
        print(f"{and_}...FAILED with wrong HTML page returned.")

def functional_test_of_search_options():
    search_bys = ["artist", "album", "user", "genre"]
    search_keywords = {
        "artist": {"non-existing": "asdf", "vague": "h", "existing": "Harrison", "albumless": "Mozart"},
        "album": {
            "non-existing": "asdf",
            "vague": "m",
            "existing": "More Postcards from Purgatory",
            "reviewless": "Apocryphal Blues",
        },
        "user": {
            "non-existing": "asdf",
            "vague": "Howard",
            "existing": "Emily",
            "reviewless": "TestUserFirst",
        },
        "genre": {
            "non-existing": "asdf",
            "vague": "a",
            "existing": "Acoustic",
            "albumless": "Latin",
        },
    }
    when = "When I POST a search for a <<<TYPE>>> <<<SEARCH>>>"
    then = "Then the response is OK"
    and_ =  "And the search routes correctly"
    tests = []
    for search in search_bys:
        types = search_keywords[search].keys()
        for type_ in types:
            tests.append(
                [
                    when.replace("<<<SEARCH>>>", search).replace("<<<TYPE>>>", type_),
                    search_payload_generator(search, search_keywords[search][type_]),
                    type_
                ]
            )
    num = 0
    print(len(tests))
    for test in tests:
        when, payload, type = test
        # try:
        print(f"TEST NUMBER: {num + 1}")
        r = post_search(payload)
        #except Exception as e:
            #print(f"{when}\n{then}\n{and_}...ALL FAILED\nwith error {e}")
        num += 1 
        print()
        _validate(when, then, and_, r)

# Comment out the one you want to test
# load_test_adding_a_review()
# functional_test_of_search_options()
