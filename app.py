from flask import Flask, render_template, request, url_for, redirect
from forms.review_form import ReviewForm
from database.models.tables import AlbumTable

app = Flask(__name__)
app.config['SECRET_KEY'] = 'derp'

albums = AlbumTable()

@app.route('/', methods=('GET', 'POST'))
def home():
    return render_template('main.html', albums_available_for_review=albums.get_all_albums())

@app.route('/route_to_review_page', methods=('GET', 'POST'))
def route():
    return redirect(url_for('review_page'))

@app.route('/route_to_add_new_artist', methods=('GET', 'POST'))
def route_add_artist_page():
    return redirect(url_for('add_artist_page'))

@app.route('/reviews', methods=('GET', 'POST'))
def review_page():
    form = ReviewForm()
    if form.validate_on_submit():
        return redirect(url_for('success'))
    return render_template('review_page.html', form=form)

@app.route('/add_artist', methods=('GET', 'POST'))
def add_artist_page():
    return render_template('add_artist.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5162)

