-- MySQL dump 10.13  Distrib 9.6.0, for Linux (x86_64)
--
-- Host: localhost    Database: mazerun
-- ------------------------------------------------------
-- Server version	9.6.0

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

--
-- Current Database: `mazerun`
--

/*!40000 DROP DATABASE IF EXISTS `mazerun`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `mazerun` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `mazerun`;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `name` varchar(100) NOT NULL,
  `phone` varchar(12) NOT NULL,
  `type` varchar(3) NOT NULL,
  `email` varchar(50) NOT NULL,
  `birth` date NOT NULL,
  `team` int NOT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `simulation`
--

DROP TABLE IF EXISTS `simulation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `simulation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` text NOT NULL,
  `team` int NOT NULL,
  `startDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_email` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_simulation_user` (`user_email`),
  CONSTRAINT `fk_simulation_user` FOREIGN KEY (`user_email`) REFERENCES `user` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `simulation`
--

LOCK TABLES `simulation` WRITE;
/*!40000 ALTER TABLE `simulation` DISABLE KEYS */;
/*!40000 ALTER TABLE `simulation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measure`
--

DROP TABLE IF EXISTS `measure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `measures` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `originRoom` int NOT NULL,
  `destinyRoom` int NOT NULL,
  `Marsami` int NOT NULL,
  `Status` int NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_measures_simulation` (`simulation_id`),
  CONSTRAINT `fk_measures_simulation`
    FOREIGN KEY (`simulation_id`) REFERENCES `simulation`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measure`
--

LOCK TABLES `measures` WRITE;
/*!40000 ALTER TABLE `measures` DISABLE KEYS */;
/*!40000 ALTER TABLE `measures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `room` int NOT NULL,
  `sensor` varchar(10) NOT NULL,
  `reading` decimal(10,2) NOT NULL,
  `alertType` varchar(50) NOT NULL,
  `msg` varchar(100) NOT NULL,
  `insertTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_message_simulation` (`simulation_id`),
  CONSTRAINT `fk_message_simulation` FOREIGN KEY (`simulation_id`) REFERENCES `simulation` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message`
--

LOCK TABLES `message` WRITE;
/*!40000 ALTER TABLE `message` DISABLE KEYS */;
/*!40000 ALTER TABLE `message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ocupation`
--

DROP TABLE IF EXISTS `ocupation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ocupation` (
  `id` int NOT NULL,
  `oddMarsamis` int NOT NULL,
  `evenMarsamis` int NOT NULL,
  `Room` int NOT NULL,
  PRIMARY KEY (`id`,`Room`),
  CONSTRAINT `fk_ocupation_simulation`
    FOREIGN KEY (`id`) REFERENCES `simulation`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ocupation`
--

LOCK TABLES `ocupation` WRITE;
/*!40000 ALTER TABLE `ocupation` DISABLE KEYS */;
/*!40000 ALTER TABLE `ocupation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sound`
--

DROP TABLE IF EXISTS `sound`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sound` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sound` decimal(5,2) NOT NULL,
  `room` int NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sound_simulation` (`simulation_id`),
  CONSTRAINT `fk_sound_simulation` FOREIGN KEY (`simulation_id`) REFERENCES `simulation` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sound`
--

LOCK TABLES `sound` WRITE;
/*!40000 ALTER TABLE `sound` DISABLE KEYS */;
/*!40000 ALTER TABLE `sound` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `temperature`
--

DROP TABLE IF EXISTS `temperature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temperature` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `temperature` decimal(5,2) NOT NULL,
  `room` int NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_temperature_simulation` (`simulation_id`),
  CONSTRAINT `fk_temperature_simulation` FOREIGN KEY (`simulation_id`) REFERENCES `simulation` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temperature`
--

LOCK TABLES `temperature` WRITE;
/*!40000 ALTER TABLE `temperature` DISABLE KEYS */;
/*!40000 ALTER TABLE `temperature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invalid_moves`
--

DROP TABLE IF EXISTS `invalid_move`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invalid_move` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `originRoom` int NOT NULL,
  `destinyRoom` int NOT NULL,
  `marsami` int NOT NULL,
  `status` int NOT NULL,
  `reason` varchar(100) NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_invalid_moves_simulation` (`simulation_id`),
  CONSTRAINT `fk_invalid_moves_simulation` FOREIGN KEY (`simulation_id`) REFERENCES `simulation` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invalid_move`
--

LOCK TABLES `invalid_move` WRITE;
/*!40000 ALTER TABLE `invalid_move` DISABLE KEYS */;
/*!40000 ALTER TABLE `invalid_move` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `outlier`
--

DROP TABLE IF EXISTS `outlier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `outlier` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sensor` varchar(10) NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `reason` varchar(100) NOT NULL,
  `simulation_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outlier`
--

LOCK TABLES `outlier` WRITE;
/*!40000 ALTER TABLE `outlier` DISABLE KEYS */;
/*!40000 ALTER TABLE `outlier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `action`
--

DROP TABLE IF EXISTS `action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `action` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `action_type` varchar(50) NOT NULL,
  `target` varchar(50) NOT NULL,
  `value` int DEFAULT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_actions_simulation` (`simulation_id`),
  CONSTRAINT `fk_action_simulation`
    FOREIGN KEY (`simulation_id`) REFERENCES `simulation`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actions`
--

LOCK TABLES `action` WRITE;
/*!40000 ALTER TABLE `action` DISABLE KEYS */;
/*!40000 ALTER TABLE `action` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `processed_event`
--

DROP TABLE IF EXISTS `processed_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `processed_event` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mongo_id` varchar(50) NOT NULL,
  `processed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_mongo_id` (`mongo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `processed_event`
--

LOCK TABLES `processed_event` WRITE;
/*!40000 ALTER TABLE `processed_event` DISABLE KEYS */;
/*!40000 ALTER TABLE `processed_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'mazerun'
--

--
-- Dumping routines for database 'mazerun'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-11 21:09:33

