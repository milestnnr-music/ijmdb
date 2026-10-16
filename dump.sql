-- MySQL dump 10.13  Distrib 26.7.0, for macos26.6 (arm64)
--
-- Host: localhost    Database: ijmdb
-- ------------------------------------------------------
-- Server version	26.7.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '92e723be-c4dc-11f1-808e-5f484a9922de:1-94';

--
-- Temporary view structure for view `album_list`
--

DROP TABLE IF EXISTS `album_list`;
/*!50001 DROP VIEW IF EXISTS `album_list`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `album_list` AS SELECT 
 1 AS `album_name`,
 1 AS `recorded_by`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `albums`
--

DROP TABLE IF EXISTS `albums`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `albums` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `entity_id` varchar(15) NOT NULL,
  `name` varchar(180) NOT NULL,
  `release_year` year DEFAULT NULL,
  `release_month` tinyint unsigned DEFAULT NULL,
  `release_day` tinyint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `album_names` (`name`),
  KEY `albums_by_year` (`name`,`release_year`)
) ENGINE=InnoDB AUTO_INCREMENT=13208 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `instrument_count`
--

DROP TABLE IF EXISTS `instrument_count`;
/*!50001 DROP VIEW IF EXISTS `instrument_count`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `instrument_count` AS SELECT 
 1 AS `name`,
 1 AS `count`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `instruments`
--

DROP TABLE IF EXISTS `instruments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `instruments` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `entity_id` varchar(15) NOT NULL,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=211 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `labels`
--

DROP TABLE IF EXISTS `labels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `labels` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `entity_id` varchar(15) NOT NULL,
  `name` varchar(65) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=612 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `musician_stats`
--

DROP TABLE IF EXISTS `musician_stats`;
/*!50001 DROP VIEW IF EXISTS `musician_stats`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `musician_stats` AS SELECT 
 1 AS `name`,
 1 AS `year_of_birth`,
 1 AS `instrument`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `musicians`
--

DROP TABLE IF EXISTS `musicians`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `musicians` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `entity_id` varchar(15) NOT NULL,
  `name` varchar(40) NOT NULL,
  `year_of_birth` smallint unsigned DEFAULT NULL,
  `month_of_birth` tinyint unsigned DEFAULT NULL,
  `day_of_birth` tinyint unsigned DEFAULT NULL,
  `year_of_death` year DEFAULT NULL,
  `month_of_death` tinyint unsigned DEFAULT NULL,
  `day_of_death` tinyint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `musician_names` (`name`),
  KEY `musicians_by_birth_year` (`name`,`year_of_birth`)
) ENGINE=InnoDB AUTO_INCREMENT=11688 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `played`
--

DROP TABLE IF EXISTS `played`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `played` (
  `musician_id` mediumint unsigned NOT NULL,
  `instrument_id` mediumint unsigned NOT NULL,
  PRIMARY KEY (`musician_id`,`instrument_id`),
  KEY `instrument_id` (`instrument_id`),
  CONSTRAINT `played_ibfk_1` FOREIGN KEY (`musician_id`) REFERENCES `musicians` (`id`),
  CONSTRAINT `played_ibfk_2` FOREIGN KEY (`instrument_id`) REFERENCES `instruments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recorded_by`
--

DROP TABLE IF EXISTS `recorded_by`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recorded_by` (
  `musician_id` mediumint unsigned NOT NULL,
  `album_id` mediumint unsigned NOT NULL,
  PRIMARY KEY (`musician_id`,`album_id`),
  KEY `album_id` (`album_id`),
  CONSTRAINT `recorded_by_ibfk_1` FOREIGN KEY (`musician_id`) REFERENCES `musicians` (`id`),
  CONSTRAINT `recorded_by_ibfk_2` FOREIGN KEY (`album_id`) REFERENCES `albums` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recorded_on`
--

DROP TABLE IF EXISTS `recorded_on`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recorded_on` (
  `album_id` mediumint unsigned NOT NULL,
  `label_id` mediumint unsigned NOT NULL,
  PRIMARY KEY (`album_id`,`label_id`),
  KEY `label_id` (`label_id`),
  CONSTRAINT `recorded_on_ibfk_1` FOREIGN KEY (`album_id`) REFERENCES `albums` (`id`),
  CONSTRAINT `recorded_on_ibfk_2` FOREIGN KEY (`label_id`) REFERENCES `labels` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `temp_played`
--

DROP TABLE IF EXISTS `temp_played`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temp_played` (
  `musician_id` varchar(32) DEFAULT NULL,
  `instrument_id` varchar(32) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `temp_recorded_by`
--

DROP TABLE IF EXISTS `temp_recorded_by`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temp_recorded_by` (
  `musician_id` varchar(32) DEFAULT NULL,
  `album_id` varchar(32) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `temp_recorded_on`
--

DROP TABLE IF EXISTS `temp_recorded_on`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temp_recorded_on` (
  `album_id` varchar(32) DEFAULT NULL,
  `label_id` varchar(32) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `album_list`
--

/*!50001 DROP VIEW IF EXISTS `album_list`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `album_list` AS select `albums`.`name` AS `album_name`,`musicians`.`name` AS `recorded_by` from ((`albums` join `recorded_by` on((`recorded_by`.`album_id` = `albums`.`id`))) join `musicians` on((`recorded_by`.`musician_id` = `musicians`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `instrument_count`
--

/*!50001 DROP VIEW IF EXISTS `instrument_count`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `instrument_count` AS select `instruments`.`name` AS `name`,count(0) AS `count` from (`played` join `instruments` on((`played`.`instrument_id` = `instruments`.`id`))) group by `played`.`instrument_id` order by `count` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `musician_stats`
--

/*!50001 DROP VIEW IF EXISTS `musician_stats`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `musician_stats` AS select distinct `musicians`.`name` AS `name`,`musicians`.`year_of_birth` AS `year_of_birth`,`instruments`.`name` AS `instrument` from ((`musicians` left join `played` on((`played`.`musician_id` = `musicians`.`id`))) left join `instruments` on((`instruments`.`id` = `played`.`instrument_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-15 14:09:08
