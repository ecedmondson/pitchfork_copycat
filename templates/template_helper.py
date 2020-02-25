from jgt_common import must_get_key
from html import escape, unescape

def _make_multiples_body_for(search_type):
    return unescape(
        """<ul>
	{% for result in query %}
    	<li>
	<a href="/route_to_search_results/<<<TYPE>>>/{{ result }}"><
        <<TYPE>>>: {{ result }}</a>
        </li>
    	{% endfor %}
	</ul>
	<h1>Not finding what you're looking for?</h1>
	<div><a href="/">Return Home</a></div>""".replace("<<<TYPE>>>", search_type.capitalize())
    )
