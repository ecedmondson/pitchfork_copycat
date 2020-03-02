-- In this file I am trying to revamp the SQL data definitions that are found in
-- the tables.sql file. That file was only ever a test definition that I wrote up
-- very quickly so that I could begin development. I've made a few changes here
-- specifically that I think are worth noting:
-- 1. I added in the relational tables for the M:M relationships
-- 2. I commented out some of the FK ids in 1:M relationships on the 1 side
--    since we will need to fetch those with a join.

-- Note: I haven't run these yet. I need to remove the old test tables first.

CREATE TABLE `artist` (
   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
   `name` varchar(255) NOT NULL,
   -- `album_id` int(11) NOT NULL,
   -- this ID has been commented out
   -- since Artist:Album is 1:M respectively
   -- I think the Album table takes the place
   -- of having the attribute in artist and then
   -- the album_id(s) should be obtained with
   -- an inner join
   `website` varchar(500) NOT NULL,
   `image` varchar(500),
   `location` varchar(225),
   `description` varchar(1000)
);


create table `album` (
    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `artist_id` int(11) NOT NULL,
    `title` varchar(255) NOT NULL,
    `album_cover` varchar(500),
    `release_date` date,
	  `publisher` varchar(255),
    `spotify_url` varchar(500),
    -- `review_id` int(11) NOT NULL
	-- I have commented out this review_id because I realized since Album:Review
	-- is a 1:M relationship that this attribute should not be in album
	-- and should be retrieved through a join. We will probably need to
	-- update our DB ERD/schema/table etc. I will ask in slack about how
	-- to go about updating these things/if we even need to do so for
	-- credit in the course.
    FOREIGN KEY (artist_id) REFERENCES artist(id) ON DELETE CASCADE
);

CREATE TABLE `review` (
    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `review_text` varchar(5000) NOT NULL,
    `rating` int(11) NOT NULL,
    `user_id` int(11) NOT NULL,
    `album_id` int(11) NOT NULL,
    `created_date` timestamp NOT NULL,
    FOREIGN KEY (user_id) references user(id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) references album(id) ON DELETE CASCADE
);

CREATE TABLE `genre` (
    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` varchar(255)
    -- changed description to name
    -- `album_id` int(11),
    -- FOREIGN KEY (album_id) references album(id)
	-- removed this to create the foreign key M:M table
);


CREATE TABLE `user` (
   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
   `firstname` varchar(255) NOT NULL,
   `lastname` varchar(255) NOT NULL,
   `email` varchar(255) NOT NULL,
   `created_date` timestamp
   -- `review_id` int(11)
   -- see above comments about 1:M
);

CREATE TABLE `album_genre` (
  `album_id` int(11) NOT NULL,
  `genre_id` int(11) NOT NULL,
  FOREIGN KEY (album_id) references album(id) ON DELETE CASCADE,
  FOREIGN KEY (genre_id) references genre(id) ON DELETE CASCADE
);

CREATE TABLE `artist_genre` (
	`artist_id` int(11) NOT NULL,
	`genre_id` int(11) NOT NULL,
	FOREIGN KEY (artist_id) references artist(id) ON DELETE CASCADE,
	FOREIGN KEY (genre_id) references genre(id) ON DELETE CASCADE
);

-- These alter table statements might not be necessary now that I've normalized the 1:M relationships.
-- I am leaving them in just in case I want to retain the code:
-- ALTER TABLE `album`
-- ADD FOREIGN KEY (`artist_id`) REFERENCES `artist` (`id`);


-- ALTER TABLE `album`
-- ADD FOREIGN KEY (`review_id`) REFERENCES `review` (`id`);


-- ALTER TABLE `artist`
-- ADD FOREIGN KEY (`album_id`) REFERENCES `album` (`id`);


-- ALTER TABLE `user`
-- ADD FOREIGN KEY (`review_id`) REFERENCES `review` (`id`);

