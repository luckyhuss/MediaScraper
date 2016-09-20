-- This SQL script updates the db for mediascraper
-- Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
-- Date : 01/03/2016
-- version : 2.1

-- change DB
USE `mediascraper`;

-- update new parameters
UPDATE `mediascraper`.`param` 
SET `param_value` = '04-database.sql'
WHERE `param_name` = 'Database.LastSQLScript';

CREATE TABLE `mediascraper`.`download` (
  `download_id` INT NOT NULL AUTO_INCREMENT COMMENT 'Auto Download ID',
  `download_album_id` INT NOT NULL COMMENT 'FK Album ID',
  `download_file_id` INT NOT NULL COMMENT 'FK File ID',
  `download_name` VARCHAR(100) NOT NULL COMMENT 'Downloaded file\'s name',
  `download_size` FLOAT(6,2) NOT NULL COMMENT 'Downloaded file\'s size',  
  PRIMARY KEY (`download_id`),
  INDEX `FK_DOWNLOAD_ALBUM_idx` (`download_album_id` ASC),
  INDEX `FK_DOWNLOAD_FILE_idx` (`download_file_id` ASC),
  CONSTRAINT `FK_DOWNLOAD_ALBUM`
    FOREIGN KEY (`download_album_id`)
    REFERENCES `mediascraper`.`album` (`album_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `FK_DOWNLOAD_FILE`
    FOREIGN KEY (`download_file_id`)
    REFERENCES `mediascraper`.`file` (`file_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE);

ALTER TABLE `mediascraper`.`download` 
ADD UNIQUE INDEX `UNIQUE_DOWNLOAD` (`download_album_id` ASC, `download_name` ASC);

-- done 03/03/2016
ALTER TABLE `mediascraper`.`album` 
DROP INDEX `album_name_UNIQUE` ,
ADD UNIQUE INDEX `UNIQUE_ALBUM` (`album_name` ASC, `album_year_value` ASC);

-- done 06/03/2015
ALTER TABLE `mediascraper`.`file` 
DROP INDEX `UNIQUE_ALBUM_FILE` ,
ADD INDEX `UNIQUE_ALBUM_FILE` (`file_album_id` ASC);