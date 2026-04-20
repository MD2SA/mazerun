-- MySQL Full Schema Dump
-- Rebuilt to include simulation tracking, foreign keys, room specifications, and missing tables.

DROP DATABASE IF EXISTS mazerun;
CREATE DATABASE mazerun;
USE mazerun;

-- Table `simulation`
CREATE TABLE `simulation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(255) NOT NULL,
  `team` int NOT NULL,
  `startDate` timestamp NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

-- Table `corridor`
CREATE TABLE `corridor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Rooma` int NOT NULL,
  `Roomb` int NOT NULL,
  `active` tinyint NOT NULL DEFAULT 1,
  `distance` int NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

-- Table `user`
CREATE TABLE `user` (
  `email` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `phone` varchar(12) NOT NULL,
  `type` varchar(3) NOT NULL,
  `birth` date NOT NULL,
  `team` int NOT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB;

-- Table `measures`
CREATE TABLE `measures` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL,
  `originRoom` int NOT NULL,
  `destinyRoom` int NOT NULL,
  `Marsami` int NOT NULL,
  `Status` int NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`simulation_id`) REFERENCES `simulation`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table `temperature`
CREATE TABLE `temperature` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL,
  `temperature` varchar(12) NOT NULL,
  `room` int NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`simulation_id`) REFERENCES `simulation`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table `sound`
CREATE TABLE `sound` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL,
  `sound` varchar(12) NOT NULL,
  `room` int NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`simulation_id`) REFERENCES `simulation`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table `message`
CREATE TABLE `message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL,
  `room` int NOT NULL,
  `sensor` varchar(10) NOT NULL,
  `reading` decimal(10,2) NOT NULL,
  `alertType` varchar(50) NOT NULL,
  `msg` varchar(100) NOT NULL,
  `insertTime` timestamp NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`simulation_id`) REFERENCES `simulation`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table `ocupation`
CREATE TABLE `ocupation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `oddMarsamis` int NOT NULL,
  `evenMarsamis` int NOT NULL,
  `Room` int NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`, `Room`),
  FOREIGN KEY (`simulation_id`) REFERENCES `simulation`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;
