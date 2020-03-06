
function addGenre() {
    genre_list = document.getElementsByClassName("genres-selected")[0];
    genre = document.createElement('button');
    genre.setAttribute("class", "btn btn-primary genre-in");
    genre.setAttribute("id", "staged");
    options = document.getElementsByTagName('option');
    node = Array.from(options).filter( o => o.getAttribute('selected') == 'selected')
    genre.innerText = node[0].innerText.concat(" ")
    genre.value = node[0].getAttribute('value');
    remove = document.createElement('i');
    remove.setAttribute('class', 'fas fa-times');
    genre.appendChild(remove);
    genre_list.appendChild(genre);
}

function getValues() {
  selected = document.getElementsByClassName('genre-in');
  values = Array.from(selected).map( s => s.getAttribute('value'));
  input = document.getElementsByClassName("hidden-select")[0].setAttribute('value', values);
}

document.addEventListener('click', function(e) {
    console.log(e.target);
    if(e.target.getAttribute("id") == "genre-option") {
       options = document.getElementsByTagName('option');
       selected = Array.from(options).filter( o => o.getAttribute('selected') == 'selected');
       selected[0] .removeAttribute('selected', 'selected'); 
       e.target.setAttribute('selected', 'selected');
    }
    if(e.target.getAttribute("id") == "staged") {
        genre_list = document.getElementsByClassName("genres-selected")[0];
        // document.getElementById('add').setAttribute('value', 'true');
        genre_list.removeChild(e.target);
        e.preventDefault();
    }
    if(e.target.getAttribute("class") == "fas fa-times") {
        genre_list = document.getElementsByClassName("genres-selected")[0];
        // document.getElementById('add').setAttribute('value', 'true');
        genre_list.removeChild(e.parentNode);
        document.getElementById('add').setAttribute('value', 'true');
        e.preventDefault();
    }
    if(e.target.getAttribute('id') == 'add') {
        e.target.setAttribute('value', 'true');
        e.preventDefault();
    }
    if(e.target.getAttribute('id') == 'submit-form') {
        add = document.getElementById('add');
        document.getElementsByClassName("hidden-select")[0].click()
        add.setAttribute('value', 'false');
    }
}, false);

