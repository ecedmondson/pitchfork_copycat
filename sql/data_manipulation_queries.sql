-- This first section is full of queries that were prepared for a Project Draft Step.
-- Main Page Queries
-- 1. Select Albums Data to Populate the Main Page
SELECT album_cover, title, name, website, spotify_url from album INNER JOIN artist on album.artist_id=artist.id;

-- Review Page Queries
-- 1. Select Reviews Data to Populate Reviews Div
SELECT review_text, rating, firstname, lastname from review INNER JOIN user on review.user_id=user.id WHERE review.album_id = <album_id>;
-- 2. Insert Into User to Create User (if user doesn't exist when review is submitted)
INSERT INTO user (firstname, lastname, email) values (<firstname>, <lastname>, <email>);
-- 3. Insert Into Reviews (when review is submitted)
INSERT INTO review (review_text, rating, user_id, album_id) values (<review_text>, <rating>, <user_id>, <album_id>);
-- 4. Update Review to Edit Comment
UPDATE review set review_text = <new_review_text> where review_id = <review_id>
-- 5. Delete Review to Delete Comment
-- DELETE FROM review where review_id = <review_id>;

-- Search Queries
-- 1. Select Artist Data to Search by artist
SELECT * from artist WHERE artist.name like '%<search>%';
-- 2. Select Album Data to Search by album
SELECT * from album WHERE album.title like '%<search>%';
-- 3. Select Genre Data to Search by genre
SELECT * from genre WHERE genre.name like '%<search>%';
-- 4. Select User Data to Search by user
SELECT * from user WHERE user.id = %s;
SELECT * from user WHERE user.firstname like '%<search>%'or user.lastname like '%<search>%'
-- 5. Select Data to populate artist page after search
select artist.name, artist.location, artist.website, artist.description, artist.image, album.title, album.release_date from artist as artist inner join album on artist.id=album.artist_id where artist.id = <artist_id>;
-- 6. Select Data to populate album page after search
SELECT album.title, album.album_cover, album.release_date, album.publisher, album.spotify_url, artist.name, 
genre.name as genre_name, review.rating from album as album inner join artist as artist on album.artist_id = artist.id 
inner join album_genre on album.id = album_genre.album_id inner join genre as genre on album_genre.genre_id = genre.id 
inner join review on album.id = review.album_id where album.id = <id>;
-- NOT FULL Album Search:
SELECT artist.name, album.id, album.title, album.album_cover, album.release_date, album.publisher,;
album.spotify_url, genre.name from album inner join artist on album.artist_id = artist.id
INNER JOIN album_genre on album.id = album_genre.album_id
INNER JOIN genre on album_genre.genre_id = genre.id
WHERE album.title = %s;
-- Once on the page there are edit and delete buttons, for these queries:
-- 7. Edit album 
   UPDATE album set album_cover = %s where id = %s;
-- 8. Delete album
   DELETE from album_genre where album_id = {id_};
   DELETE from album where id = %s;
-- 9. Select Data to populate user page after search
select   user.firstname,   user.lastname,   user.created_date,   album.title as album_name from   user   inner join review on user.id = review.user_id   inner join album on review.album_id = album_id where user.id = <user_id>;
-- 10. Select Data to populate genre page after search
select genre.name, album.title from genre inner join album_genre on genre.id = album_genre.genre_id inner join album on album_genre.album_id=album.id where genre.id = <id>;
-- 11. Various Touch Helpers (See if Entity has Relation to Other Entity) for Searching
SELECT review.id from review inner join album on review.album_id = album.id where album.title = %s;

-- Add Artist Queries
-- 1. Insert Into Artist to create artist
INSERT INTO artist (name, website, image, location, description) values (<name>, <website>, <image_url>, <location>, <description>);
-- 2. Insert into genre to create genre (if genre not already in db)
-- First check if it exists
SELECT id from genre where name=<potentially_new_genre>;
-- If not
INSERT INTO genre (name) values (<new_genre>);
-- 3. Insert M:M into artist_genre
INSERT INTO artist_genre (album_id, genre_id) values (<artist_id>, <genre_id>);

-- Add Album Queries
-- 1. Insert Into Album to create album
INSERT INTO album (artist_id, title, album_cover, release_date, publisher, spotify_url) values (<artist_id>, <title>, <album_cover>, <release_date>, <publisher>, <spotify_url>);
-- 2. Insert into genre to create genre (if genre not already in db)
-- First check if it exists
SELECT id from genre where name=<potentially_new_genre>;
INSERT INTO genre (name) values (<new_genre>);
-- 3. Insert M:M in album_genre
INSERT INTO album_genre (album_id, genre_id) values (1, 2);


-- These queries were added after the project draft step was completed and we realized that
-- more queries were needed to complete the functionality. The majority of these are from
-- the search feature which, at the time, was underdeveloped. This statement is not
-- universally true, for example, some of these reads allow better use of relations between
-- entites in the insertion queries (above) which before had relied on user input instead of
-- on DB relationships. It should be emphasized that the "before" was due to the in-progress
-- nature of the project rather than a design intention.
-- Other Read Queries
SELECT id from artist WHERE artist.name = %s;
SELECT id from album WHERE album.artist_id = %s;
SELECT * FROM artist;
SELECT * FROM artist WHERE artist.id = %s;
SELECT * FROM album WHERE artist_id = %s;
SELECT id from album WHERE album.title = %s;
SELECT title from album where album.id = %s;
SELECT rating from review WHERE review.user_id = %s;
SELECT * from genre; 


