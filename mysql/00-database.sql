-- This SQL script sets up the db for mediascraper
-- Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
-- Date : 10/02/2016
-- version : 1.8

-- create schema
CREATE SCHEMA `mediascraper` DEFAULT CHARACTER SET utf8 ;

-- create param
CREATE TABLE `mediascraper`.`param` (
  `param_name` VARCHAR(50) NOT NULL COMMENT 'Parameter name',
  `param_value` VARCHAR(100) NOT NULL COMMENT 'Parameter value',
  `param_added` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date of entry',
  PRIMARY KEY (`param_name`),
  UNIQUE INDEX `param_name_UNIQUE` (`param_name` ASC))
COMMENT = 'Keeps track of parameters';

-- create year
CREATE TABLE `mediascraper`.`year` (
  `year_value` INT NOT NULL COMMENT 'Year for top level download page',
  `year_url` VARCHAR(500) NOT NULL COMMENT 'URL for top level download page per year',
  `year_scraped` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Top level download page scraped or not',
  `year_scraped_date` DATETIME DEFAULT NULL COMMENT 'Top level download page scraping date',
  `year_valid` TINYINT(1) DEFAULT NULL COMMENT 'URL is valid or not',
  `year_added` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date of entry',
  PRIMARY KEY (`year_value`))
COMMENT = 'Tracks the years scraped';

-- create album
CREATE TABLE `mediascraper`.`album` (
  `album_id` INT NOT NULL AUTO_INCREMENT COMMENT 'Auto Album ID',
  `album_name` VARCHAR(100) NOT NULL COMMENT 'Album name from download page',
  `album_url` VARCHAR(500) NOT NULL COMMENT 'URL for album download page',
  `album_year_value` INT NOT NULL COMMENT 'Year of the album',
  `album_scraped` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Album files scraped or not',
  `album_scraped_date` DATETIME DEFAULT NULL COMMENT 'Album files scraping date',
  `album_moved` TINYINT(1) DEFAULT 0 COMMENT 'Album moved (from download disk) or not',
  `album_added` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date of entry',
  PRIMARY KEY (`album_id`),
  UNIQUE KEY `album_name_UNIQUE` (`album_name`),
  FOREIGN KEY (`album_year_value`)
  REFERENCES `mediascraper`.`year` (`year_value`)
  ON DELETE RESTRICT ON UPDATE CASCADE)
COMMENT = 'Tracks all albums that are scraped';

-- create file
CREATE TABLE `mediascraper`.`file` (
  `file_id` INT NOT NULL AUTO_INCREMENT COMMENT 'Auto File ID',
  `file_album_id` INT NOT NULL COMMENT 'FK Album ID',
  `file_name` VARCHAR(100) NOT NULL COMMENT 'File name from album download page',
  `file_url` VARCHAR(500) NOT NULL COMMENT 'URL for file download',
  `file_downloaded` TINYINT(1) DEFAULT 0 COMMENT 'File downloaded or not',
  `file_date_downloaded` DATETIME DEFAULT NULL COMMENT 'File download date',
  `file_added` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date of entry',
  PRIMARY KEY (`file_id`),
  UNIQUE KEY `UNIQUE_ALBUM_FILE` (`file_album_id`,`file_name`),
  FOREIGN KEY (`file_album_id`)
  REFERENCES `mediascraper`.`album` (`album_id`)
  ON DELETE RESTRICT ON UPDATE CASCADE)
COMMENT = 'Tracks all files that are sent for download (pyLoad)';
  
# create procedure insert_year
USE `mediascraper`;
DROP procedure IF EXISTS `insert_year`;

DELIMITER $$
USE `mediascraper`$$
CREATE PROCEDURE `insert_year` (IN current_year INT, IN topLevelPage CHAR(50))
BEGIN
	INSERT INTO year (year_value, year_url) 
		SELECT current_year, REPLACE(param.param_value, '[0]', current_year) FROM param WHERE param.param_name = topLevelPage;
END$$
DELIMITER ;

-- insert parameters
INSERT INTO `mediascraper`.`param` (`param_name`, `param_value`) 
VALUES
('Application.LaunchCount', '0'),
('Download.TopLevelPage', 'http://www.songspk.help/indian_movie/[0]_List.html'),
('Download.MaxAlbumPerDay', '5'),
('SMTP.Login', 'innovativecoltd@gmail.com'),
('SMTP.Password', 'Bp#72gu107'),
('SMTP.Server', 'smtp.gmail.com'),
('SMTP.Port', '587'),
('SMTP.From', 'innovativecoltd@gmail.com'),
('SMTP.To', 'luckyhuss@gmail.com');
