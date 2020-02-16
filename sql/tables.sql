CREATE TABLE `user` (
   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
   `firstname` varchar(255) NOT NULL,
   `lastname` varchar(255) NOT NULL,
   `email` varchar(255) NOT NULL,
   `created_date` timestamp,
   `review_id` int(11)
);

create table `album` (
    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `artist_id` int(11) NOT NULL,
    `title` varchar(255) NOT NULL,
    `album_cover` varchar(500),
    `release_date` date,
    `spotify_url` varchar(5255),
    `review_id` int(11) NOT NULL
);

CREATE TABLE `artist` (
   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
   `name` varchar(255) NOT NULL,
   `album_id` int(11) NOT NULL,
   `website` varchar(255) NOT NULL,
   `image` varchar(255),
   `location` varchar(225),
   `description` varchar(1000)
);

CREATE TABLE `review` (
    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `review_text` varchar(5000) NOT NULL,
    `rating` int(11) NOT NULL,
    `user_id` int(11) NOT NULL,
    `album_id` int(11) NOT NULL,
    `created_date` date NOT NULL,
    FOREIGN KEY (user_id) references user(id),
    FOREIGN KEY (album_id) references album(id)
);

CREATE TABLE `genre` (
    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `description` varchar(500),
    `album_id` int(11),
    FOREIGN KEY (album_id) references album(id)
);
    

ALTER TABLE `album`
ADD FOREIGN KEY (`artist_id`) REFERENCES `artist` (`id`);

ALTER TABLE `album`
ADD FOREIGN KEY (`review_id`) REFERENCES `review` (`id`);

ALTER TABLE `artist`
ADD FOREIGN KEY (`album_id`) REFERENCES `album` (`id`);

ALTER TABLE `user`
ADD FOREIGN KEY (`review_id`) REFERENCES `review` (`id`);
