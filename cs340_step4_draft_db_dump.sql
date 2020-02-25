-- MariaDB dump 10.17  Distrib 10.4.11-MariaDB, for Linux (x86_64)
--
-- Host: classmysql.engr.oregonstate.edu    Database: cs340_edmondem
-- ------------------------------------------------------
-- Server version	10.4.11-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `artist`
--

DROP TABLE IF EXISTS `artist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `artist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `website` varchar(500) NOT NULL,
  `image` varchar(500) DEFAULT NULL,
  `location` varchar(225) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artist`
--

LOCK TABLES `artist` WRITE;
/*!40000 ALTER TABLE `artist` DISABLE KEYS */;
INSERT INTO `artist` VALUES (1,'Harrison Lemke','https://harrisonlemke.com','https://i.ytimg.com/vi/PKh8uLq2Leo/maxresdefault.jpg','Austin, TX','A sort of emo gerard manley hopkins. Harrison writes hiss-tape symphonies to God.'),(2,'Ramshackle Glory','https://ramshackleglory.bandcamp.com','\"https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Pat_The_Bunny_Performs_Live_with_Ramshackle_Glory.png/320px-Pat_The_Bunny_Performs_Live_with_Ramshackle_Glory.png','Tucson, AZ','Ramshackle Glory is a retired anarchist punk band.'),(3,'The Stillwater Hobos','http://thestillwaterhobos.tumblr.com','https://f4.bcbits.com/img/0000793781_10.jpg','Asheville, NC','The Stillwater Hobos formed in 2010 when in Galway on their way to Rome.'),(4,'J Balvin','https://jbalvin.com','https://us.hola.com/images/0259-0e8907e35682-0f4a3e986f04-1000/horizontal-1150/j-balvin.jpg','Medellin, Colombia','J Balvin is a Colombian reggaeton artist. He gained popularity performing at clubs in the Medellin. Occasionally he disappears into the Andes mountains where his publicist can\'t find him.');
/*!40000 ALTER TABLE `artist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `album`
--

DROP TABLE IF EXISTS `album`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `album` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `artist_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `album_cover` varchar(500) DEFAULT NULL,
  `release_date` date DEFAULT NULL,
  `publisher` varchar(255) DEFAULT NULL,
  `spotify_url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `artist_id` (`artist_id`),
  CONSTRAINT `album_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artist` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `album`
--

LOCK TABLES `album` WRITE;
/*!40000 ALTER TABLE `album` DISABLE KEYS */;
INSERT INTO `album` VALUES (1,3,'My Love, She\'s in America','https://f4.bcbits.com/img/a0087179614_10.jpg','2014-03-02','Echo Mountain Recording','https://open.spotify.com/album/09HYKvt82nT0DoJ13uIHHh'),(2,1,'More Postcards from Purgatory','https://f4.bcbits.com/img/a1378511799_16.jpg','2015-02-02','HPL','https://open.spotify.com/album/3JPNeLTHGuVjx69S7H3qHN'),(3,2,'Live the dream','https://f4.bcbits.com/img/a3617947760_10.jpg','2015-05-12','Plan-It-X','https://open.spotify.com/album/6LoWh2KXtS4sVhFLgeT7Yo'),(4,4,'Oasis','https://upload.wikimedia.org/wikipedia/en/7/7f/J_Balvin_and_Bad_Bunny_-_Oasis.png','2019-06-28','Universal Latin','https://open.spotify.com/album/6ylFfzx32ICw4L1A7YWNLN');
/*!40000 ALTER TABLE `album` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(255) NOT NULL,
  `lastname` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `created_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fullname` (`firstname`,`lastname`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Moe','Howard','moe@stooges.com','2020-02-21 18:56:02'),(2,'Curly','Howard','curly@stooges.com','2020-02-21 18:56:31'),(3,'Larry','Fine','larry@stooges.com','2020-02-21 18:56:55'),(4,'Emily','Edmondson','ecedmondson@gmail.com','2020-02-21 18:58:51'),(5,'Bender Bending','Rodriguez','bender@futurama.com','2020-02-25 00:56:24'),(6,'TestUserFirst','TestUserLast','test@test.com','2020-02-25 01:43:57');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `review`
--

DROP TABLE IF EXISTS `review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `review` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `review_text` varchar(5000) NOT NULL,
  `rating` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `album_id` int(11) NOT NULL,
  `created_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `album_id` (`album_id`),
  CONSTRAINT `review_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `review_ibfk_2` FOREIGN KEY (`album_id`) REFERENCES `album` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review`
--

LOCK TABLES `review` WRITE;
/*!40000 ALTER TABLE `review` DISABLE KEYS */;
INSERT INTO `review` VALUES (1,'I went to Purgatory, CO on vacation once and there were no postcards available for purchase. I\'m glad Mr. Lemke is musically solving this problem.',10,4,2,'2020-02-21 22:06:42'),(2,'This album\'s title is misleading, as it spent a lot of time singing about love interests that were outside of America (Ireland and France come to mind.)',7,2,1,'2020-02-21 22:10:07'),(3,'Dios bendiga la reggaeton, amen u\'U0001F64F\'',9,3,4,'2020-02-21 22:37:53'),(5,'Once I heard a traveling street preacher talk about Purgatory and have been traumatized by the concept ever since.',5,1,2,'2020-02-23 19:55:30'),(6,'Me parece que debe incluir a Bad Bunny no?',10,1,4,'2020-02-23 22:31:12'),(7,'Wow these guys are super depressed',4,1,3,'2020-02-23 22:49:04'),(8,'Au contraire, Moe, these guys are brilliant!',10,2,3,'2020-02-23 22:46:52'),(9,'This is a fun test comment which I have written in order to test this SQL query. I am not a robot. ',10,5,3,'2020-02-25 00:57:30'),(10,'Hehe, I\'m not a robot!',10,5,1,'2020-02-25 01:54:13');
/*!40000 ALTER TABLE `review` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genre`
--

DROP TABLE IF EXISTS `genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genre` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genre`
--

LOCK TABLES `genre` WRITE;
/*!40000 ALTER TABLE `genre` DISABLE KEYS */;
INSERT INTO `genre` VALUES (1,'Folk'),(2,'Acoustic'),(3,'Punk'),(4,'Reggaeton'),(5,'Anarchist'),(6,'Neo-Traditional');
/*!40000 ALTER TABLE `genre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `album_genre`
--

DROP TABLE IF EXISTS `album_genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `album_genre` (
  `album_id` int(11) NOT NULL,
  `genre_id` int(11) NOT NULL,
  KEY `album_id` (`album_id`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `album_genre_ibfk_1` FOREIGN KEY (`album_id`) REFERENCES `album` (`id`) ON DELETE CASCADE,
  CONSTRAINT `album_genre_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `genre` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `album_genre`
--

LOCK TABLES `album_genre` WRITE;
/*!40000 ALTER TABLE `album_genre` DISABLE KEYS */;
INSERT INTO `album_genre` VALUES (1,1),(1,6),(2,2),(3,1),(3,2),(3,3),(3,5),(4,4);
/*!40000 ALTER TABLE `album_genre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `artist_genre`
--

DROP TABLE IF EXISTS `artist_genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `artist_genre` (
  `artist_id` int(11) NOT NULL,
  `genre_id` int(11) NOT NULL,
  KEY `artist_id` (`artist_id`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `artist_genre_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artist` (`id`) ON DELETE CASCADE,
  CONSTRAINT `artist_genre_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `genre` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artist_genre`
--

LOCK TABLES `artist_genre` WRITE;
/*!40000 ALTER TABLE `artist_genre` DISABLE KEYS */;
INSERT INTO `artist_genre` VALUES (1,2),(1,1),(4,4);
/*!40000 ALTER TABLE `artist_genre` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-02-24 18:49:02
