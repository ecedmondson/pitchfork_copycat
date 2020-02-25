-- Genre Insertions:
insert into genre (name) values ('Folk');
insert into genre (name) values ('Accoustic');
insert into genre (name) values ('Punk');
insert into genre (name) values ('Anarchist');
insert into genre (name) values ('Reggaeton');

--Artist Insertions:
insert into artist (name, website, image, location, description) values ('Harrison Lemke', 'https://harrisonlemke.com', 'https://i.ytimg.com/vi/PKh8uLq2Leo/maxresdefault.jpg', 'Austin, TX', 'A sort of emo gerard manley hopkins. Harrison writes hiss-tape symphonies to God.');
insert into artist (name, website, image, location, description) values ('Ramshackle Glory', 'https://ramshackleglory.bandcamp.com', '"https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Pat_The_Bunny_Performs_Live_with_Ramshackle_Glory.png/320px-Pat_The_Bunny_Performs_Live_with_Ramshackle_Glory.png', 'Tucson, AZ', 'Ramshackle Glory is a retired anarchist punk band.');
insert into artist (name, website, image, location, description) values ('The Stillwater Hobos', 'http://thestillwaterhobos.tumblr.com', 'https://f4.bcbits.com/img/0000793781_10.jpg', 'Asheville, NC', 'The Stillwater Hobos formed in 2010 when in Galway on their way to Rome.');
insert into artist (name, website, image, location, description) values ('J Balvin', 'https://jbalvin.com', 'https://us.hola.com/images/0259-0e8907e35682-0f4a3e986f04-1000/horizontal-1150/j-balvin.jpg', 'Medellin, Colombia', 'J Balvin is a Colombian reggaeton artist. He gained popularity performing at clubs in the Medellin. Occasionally he disappears into the Andes mountains where his publicist can\'t find him.');

--Album Insertions:
insert into album (artist_id, title, album_cover, release_date, publisher, spotify_url) values (3, "My Love, She\'s in America", 'https://f4.bcbits.com/img/a0087179614_10.jpg', "2014-03-02", 'Echo Mountain Recording', 'https://open.spotify.com/album/09HYKvt82nT0DoJ13uIHHh');
insert into album (artist_id, title, album_cover, release_date, publisher, spotify_url) values (1, "More Postcards from Purgatory", 'https://f4.bcbits.com/img/a1378511799_16.jpg', "2015-02-02", 'HPL', 'https://open.spotify.com/album/3JPNeLTHGuVjx69S7H3qHN');
insert into album (artist_id, title, album_cover, release_date, publisher, spotify_url) values (2, "Live the dream", 'https://f4.bcbits.com/img/a3617947760_10.jpg', "2015-05-12", 'Plan-It-X', 'https://open.spotify.com/album/6LoWh2KXtS4sVhFLgeT7Yo');
insert into album (artist_id, title, album_cover, release_date, publisher, spotify_url) values (4, "Oasis", 'https://upload.wikimedia.org/wikipedia/en/7/7f/J_Balvin_and_Bad_Bunny_-_Oasis.png', "2019-06-28", 'Universal Latin', 'https://open.spotify.com/album/6ylFfzx32ICw4L1A7YWNLN');

--Album Genre Insertions:
-- for album_id 1(My Love She's in America):
insert into album_genre (album_id, genre_id) values (1, 1);
insert into album_genre (album_id, genre_id) values (1, 6);
-- More Postcards from Purgatory
insert into album_genre (album_id, genre_id) values (1, 2);
-- Live the Dream
insert into album_genre (album_id, genre_id) values (3, 1);
insert into album_genre (album_id, genre_id) values (3, 2);
insert into album_genre (album_id, genre_id) values (3, 3);
insert into album_genre (album_id, genre_id) values (3, 5);


--User Insertions:
insert into user (firstname, lastname, email) values ('Moe', "Howard", "moe@stooges.com");
insert into user (firstname, lastname, email) values ('Curly', "Howard", "curly@stooges.com");
insert into user (firstname, lastname, email) values ('Larry', "Fine", "larry@stooges.com");

-- Review Insertions:
insert into review (review_text, rating, user_id, album_id) values ("I went to Purgatory, CO on vacation once and there were no postcards available for purchase. I'm glad Mr. Lemke is musically solving this problem.", 10, 4, 2);
insert into review (review_text, rating, user_id, album_id) values ("This album's title is misleading, as it spent a lot of time singing about love interests that were outside of America (Ireland and France come to mind.)", 7, 2, 1);
insert into review (review_text, rating, user_id, album_id) values ("Dios bendiga la reggaeton, amen u'\U0001F64F'", 9, 3, 4);

-- Artist Genre Insertions:
insert into artist_genre (artist_id, genre_id) values (1, 2);
insert into artist_genre (artist_id, genre_id) values (1, 1);
insert into artist_genre (artist_id, genre_id) values (4, 4);

-- M:M General Select for Albums and Genres
select   album.title,   genre.name from   album   inner join album_genre as ag on album.id = ag.album_id   inner join genre on ag.genre_id = genre.id;





