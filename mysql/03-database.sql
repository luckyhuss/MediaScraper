-- This SQL script updates the db for mediascraper
-- Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
-- Date : 20/02/2016
-- version : 2.0

-- change DB
USE `mediascraper`;

-- update new parameters
UPDATE `mediascraper`.`param` 
SET `param_value` = '03-database.sql'
WHERE `param_name` = 'Database.LastSQLScript';

-- add new columns
ALTER TABLE `mediascraper`.`album` 
ADD COLUMN `album_scraped_error` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Indicates if there was an error while scraping the album (1)' AFTER `album_scraped`;

ALTER TABLE `mediascraper`.`album` 
ADD COLUMN `album_pyload_id` INT(11) NULL COMMENT 'pid from pyLoad is saved here for restarting package later or for automated delete' AFTER `album_year_value`;

ALTER TABLE `mediascraper`.`album` 
ADD COLUMN `album_pyload_name` VARCHAR(100) NULL COMMENT 'Name of package sent to pyLoad' AFTER `album_pyload_id`;

ALTER TABLE `mediascraper`.`album` 
DROP INDEX `album_name_UNIQUE`,
ADD UNIQUE INDEX `album_name_UNIQUE` (`album_name` ASC, `album_pyload_name` ASC);

-- update all package name from file to album
UPDATE `mediascraper`.`album`
INNER JOIN `mediascraper`.`file`
ON `album`.`album_id` = `file`.`file_album_id`
SET `album`.`album_pyload_name` = `file`.`file_package_name`;

-- drop redundant column from file
ALTER TABLE `mediascraper`.`file` 
DROP COLUMN `file_package_name`,
DROP INDEX `UNIQUE_ALBUM_FILE` ,
ADD UNIQUE INDEX `UNIQUE_ALBUM_FILE` (`file_album_id` ASC);
