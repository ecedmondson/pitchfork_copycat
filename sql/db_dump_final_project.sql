-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: classmysql.engr.oregonstate.edu:3306
-- Generation Time: Mar 18, 2020 at 09:44 PM
-- Server version: 10.4.11-MariaDB-log
-- PHP Version: 7.0.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cs340_edmondem`
--

-- --------------------------------------------------------

--
-- Table structure for table `album`
--

CREATE TABLE `album` (
  `id` int(11) NOT NULL,
  `artist_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `album_cover` varchar(500) DEFAULT NULL,
  `release_date` date DEFAULT NULL,
  `publisher` varchar(255) DEFAULT NULL,
  `spotify_url` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `album`
--

INSERT INTO `album` (`id`, `artist_id`, `title`, `album_cover`, `release_date`, `publisher`, `spotify_url`) VALUES
(1, 3, 'My Love Shes in America', 'https://f4.bcbits.com/img/a0087179614_10.jpg', '2014-03-02', 'Echo Mountain Recording', 'https://open.spotify.com/album/09HYKvt82nT0DoJ13uIHHh'),
(2, 1, 'More Postcards from Purgatory', 'https://f4.bcbits.com/img/a1378511799_16.jpg', '2015-02-02', 'HPL', 'https://open.spotify.com/album/3JPNeLTHGuVjx69S7H3qHN'),
(3, 2, 'Live the dream', 'https://f4.bcbits.com/img/a3617947760_10.jpg', '2015-05-12', 'Plan-It-X', 'https://open.spotify.com/album/6LoWh2KXtS4sVhFLgeT7Yo'),
(4, 4, 'Oasis', 'https://upload.wikimedia.org/wikipedia/en/7/7f/J_Balvin_and_Bad_Bunny_-_Oasis.png', '2019-06-28', 'Universal Latin', 'https://open.spotify.com/album/6ylFfzx32ICw4L1A7YWNLN'),
(6, 1, 'Apocryphal Blues', 'https://f4.bcbits.com/img/a2927992142_10.jpg', '2018-03-11', 'HPL', 'https://open.spotify.com/album/2H5sm8ujl2cTsZP5M6aKLp'),
(10, 27, 'Symphony No. 9', 'https://i.ytimg.com/vi/qynu8yNiTrY/maxresdefault.jpg', '0000-00-00', 'Beethoven', 'https://www.youtube.com/watch?v=t3217H8JppI');

-- --------------------------------------------------------

--
-- Table structure for table `album_genre`
--

CREATE TABLE `album_genre` (
  `album_id` int(11) NOT NULL,
  `genre_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `album_genre`
--

INSERT INTO `album_genre` (`album_id`, `genre_id`) VALUES
(1, 1),
(1, 6),
(2, 2),
(3, 1),
(3, 2),
(3, 3),
(3, 5),
(4, 4),
(6, 2),
(10, 12);

-- --------------------------------------------------------

--
-- Table structure for table `artist`
--

CREATE TABLE `artist` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `website` varchar(500) NOT NULL,
  `image` varchar(500) DEFAULT NULL,
  `location` varchar(225) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `artist`
--

INSERT INTO `artist` (`id`, `name`, `website`, `image`, `location`, `description`) VALUES
(1, 'Harrison Lemke', 'https://harrisonlemke.com', 'https://i.ytimg.com/vi/PKh8uLq2Leo/maxresdefault.jpg', 'Austin, TX', 'A sort of emo gerard manley hopkins. Harrison writes hiss-tape symphonies to God.'),
(2, 'Ramshackle Glory', 'https://ramshackleglory.bandcamp.com', 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Pat_The_Bunny_Performs_Live_with_Ramshackle_Glory.png/320px-Pat_The_Bunny_Performs_Live_with_Ramshackle_Glory.png', 'Tucson, AZ', 'Ramshackle Glory is a retired anarchist punk band.'),
(3, 'The Stillwater Hobos', 'http://thestillwaterhobos.tumblr.com', 'https://f4.bcbits.com/img/0000793781_10.jpg', 'Asheville, NC', 'The Stillwater Hobos formed in 2010 when in Galway on their way to Rome.'),
(4, 'J Balvin', 'https://jbalvin.com', 'https://us.hola.com/images/0259-0e8907e35682-0f4a3e986f04-1000/horizontal-1150/j-balvin.jpg', 'Medellin, Colombia', 'J Balvin is a Colombian reggaeton artist. He gained popularity performing at clubs in the Medellin. Occasionally he disappears into the Andes mountains where his publicist can\'t find him.'),
(5, 'Mozart', 'www.wolfgang-amadeus.at', NULL, NULL, NULL),
(7, 'Lady Gaga', 'https://www.ladygaga.com/', 'https://akns-images.eonline.com/eol_images/Entire_Site/201981/rs_634x1024-190901105622-634-lady-gaga.cm.9119.jpg?fit=inside|900:auto&output-quality=90', 'New York', 'Stefani Joanne Angelina Germanotta, known professionally as Lady Gaga, is an American singer, songwriter, and actress. She is known for reinventing herself throughout her career and for her versatility in numerous areas of the entertainment industry.'),
(9, 'George Harrison', 'https://www.georgeharrison.com/', 'https://en.wikipedia.org/wiki/George_Harrison#/media/File:George_Harrison_1974.jpg', '', ''),
(25, 'The Head and the Heart', 'https://www.theheadandtheheart.com/', 'https://subpop-img.s3.amazonaws.com/asset/artist_images/attachments/000/005/136/max_960/thath-clinch.jpg', 'Seattle, WA', 'Mostly acoustic.'),
(27, 'Ludwig van Beethoven', 'https://en.wikipedia.org/wiki/Ludwig_van_Beethoven', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Beethoven.jpg/440px-Beethoven.jpg', 'Salzburg, Austria', 'You know who he is.');

-- --------------------------------------------------------

--
-- Table structure for table `artist_genre`
--

CREATE TABLE `artist_genre` (
  `artist_id` int(11) NOT NULL,
  `genre_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `artist_genre`
--

INSERT INTO `artist_genre` (`artist_id`, `genre_id`) VALUES
(1, 2),
(1, 1),
(2, 5),
(3, 1),
(3, 2),
(4, 7),
(4, 4),
(5, 8),
(7, 9),
(25, 1),
(25, 2),
(27, 12),
(27, 8);

-- --------------------------------------------------------

--
-- Table structure for table `genre`
--

CREATE TABLE `genre` (
  `id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `genre`
--

INSERT INTO `genre` (`id`, `name`) VALUES
(1, 'Folk'),
(2, 'Acoustic'),
(3, 'Punk'),
(4, 'Reggaeton'),
(5, 'Anarchist'),
(6, 'Neo-Traditional'),
(7, 'Latin'),
(8, 'Classical'),
(9, 'Pop'),
(10, 'Alternative'),
(11, 'Rock'),
(12, 'Beethoven');

-- --------------------------------------------------------

--
-- Table structure for table `review`
--

CREATE TABLE `review` (
  `id` int(11) NOT NULL,
  `review_text` varchar(5000) NOT NULL,
  `rating` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `album_id` int(11) NOT NULL,
  `created_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `review`
--

INSERT INTO `review` (`id`, `review_text`, `rating`, `user_id`, `album_id`, `created_date`) VALUES
(1, 'I went to Purgatory, CO on vacation once and there were no postcards available for purchase. I\'m glad Mr. Lemke is musically solving this problem.', 10, 4, 2, '2020-02-21 22:06:42'),
(2, 'This album\'s title is misleading, as it spent a lot of time singing about love interests that were outside of America (Ireland and France come to mind.)', 7, 2, 1, '2020-02-21 22:10:07'),
(3, 'Dios bendiga la reggaeton, amen u\'U0001F64F\'', 9, 3, 4, '2020-02-21 22:37:53'),
(5, 'Once I heard a traveling street preacher talk about Purgatory and have been traumatized by the concept ever since.', 5, 8, 2, '2020-02-26 02:24:06'),
(6, 'Me parece que debe incluir a Bad Bunny no?', 10, 1, 4, '2020-02-23 22:31:12'),
(7, 'Wow these guys are super depressed', 4, 1, 3, '2020-02-23 22:49:04'),
(8, 'Au contraire, Moe, these guys are brilliant!', 10, 2, 3, '2020-02-23 22:46:52'),
(9, 'This is a fun test comment which I have written in order to test this SQL query. I am not a robot. ', 10, 5, 3, '2020-02-25 00:57:30'),
(10, 'Hehe, I\'m not a robot!', 10, 5, 1, '2020-02-25 01:54:13'),
(12, 'This is a dope ass album', 10, 7, 2, '2020-02-25 18:09:47'),
(19, 'Reviewing the review function', 10, 14, 1, '2020-03-04 19:29:38'),
(21, 'Reviewing functionality!', 10, 15, 2, '2020-03-05 00:11:12'),
(24, 'Thank you for the tens. ', 10, 16, 1, '2020-03-06 02:35:15'),
(25, 'Wow excellent', 10, 17, 4, '2020-03-06 02:39:46'),
(26, 'Radiohead > Oasis. ', 10, 18, 4, '2020-03-06 02:54:42'),
(27, 'test test', 8, 20, 1, '2020-03-09 20:37:02'),
(29, 'didn\'t listen to it', 5, 22, 1, '2020-03-13 03:42:05'),
(31, 'Fun Test Comment', 6, 27, 6, '2020-03-19 03:03:17');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `firstname` varchar(255) NOT NULL,
  `lastname` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `created_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `firstname`, `lastname`, `email`, `created_date`) VALUES
(1, 'Moe', 'Howard', 'moe@stooges.com', '2020-02-21 18:56:02'),
(2, 'Curly', 'Howard', 'curly@stooges.com', '2020-02-21 18:56:31'),
(3, 'Larry', 'Fine', 'larry@stooges.com', '2020-02-21 18:56:55'),
(4, 'Emily', 'Edmondson', 'ecedmondson@gmail.com', '2020-02-21 18:58:51'),
(5, 'Bender Bending', 'Rodriguez', 'bender@futurama.com', '2020-02-25 00:56:24'),
(6, 'TestUserFirst', 'TestUserLast', 'test@test.com', '2020-02-25 01:43:57'),
(7, 'Lord', 'Gordon', 'LordieMaGordie@gmail.com', '2020-02-25 18:09:47'),
(8, 'Sean', 'Opnel', 'sean@sean.com', '2020-02-26 02:23:12'),
(14, 'daniel', 'loseke', 'loseked@oregonstate.edu', '2020-03-04 19:28:57'),
(15, 'Emily ', 'Dominguez', 'fake_email@gmail.com', '2020-03-05 00:10:29'),
(16, 'The ', 'StillWater Hobos', 'thestillwaterhobos@gmail.com', '2020-03-06 02:35:15'),
(17, 'meow', 'mix', '2020@oregonstate.edu', '2020-03-06 02:39:46'),
(18, 'Liam ', 'Gallagher', 'thomyorkeisbetterthanmeineveryway@gmail.com', '2020-03-06 02:54:42'),
(20, 'John', 'Anderson', 'janderson@gmail.com', '2020-03-09 20:36:05'),
(22, 'c', 'r', 'rhoadsc@oregonstate.edu', '2020-03-13 03:41:08'),
(27, 'Jordan', 'Sakakeeny', 'noemail@gmail.com', '2020-03-19 02:59:19');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `album`
--
ALTER TABLE `album`
  ADD PRIMARY KEY (`id`),
  ADD KEY `artist_id` (`artist_id`);

--
-- Indexes for table `album_genre`
--
ALTER TABLE `album_genre`
  ADD KEY `album_id` (`album_id`),
  ADD KEY `genre_id` (`genre_id`);

--
-- Indexes for table `artist`
--
ALTER TABLE `artist`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `artist_genre`
--
ALTER TABLE `artist_genre`
  ADD KEY `artist_id` (`artist_id`),
  ADD KEY `genre_id` (`genre_id`);

--
-- Indexes for table `genre`
--
ALTER TABLE `genre`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `review`
--
ALTER TABLE `review`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `album_id` (`album_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fullname` (`firstname`,`lastname`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `album`
--
ALTER TABLE `album`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `artist`
--
ALTER TABLE `artist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `genre`
--
ALTER TABLE `genre`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `review`
--
ALTER TABLE `review`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `album`
--
ALTER TABLE `album`
  ADD CONSTRAINT `album_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artist` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `album_genre`
--
ALTER TABLE `album_genre`
  ADD CONSTRAINT `album_genre_ibfk_1` FOREIGN KEY (`album_id`) REFERENCES `album` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `album_genre_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `genre` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `artist_genre`
--
ALTER TABLE `artist_genre`
  ADD CONSTRAINT `artist_genre_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artist` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `artist_genre_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `genre` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `review`
--
ALTER TABLE `review`
  ADD CONSTRAINT `review_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `review_ibfk_2` FOREIGN KEY (`album_id`) REFERENCES `album` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

