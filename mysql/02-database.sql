-- This SQL script updates the db for mediascraper
-- Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
-- Date : 20/02/2016
-- version : 2.0

-- change DB
USE MediaScraper;

-- update new parameters
UPDATE `mediascraper`.`param` 
SET `param_value` = '02-database.sql'
WHERE `param_name` = 'Database.LastSQLScript';

-- add new columns
ALTER TABLE `mediascraper`.`album` 
ADD COLUMN `album_size` FLOAT(6,2) NULL COMMENT 'Album total downloaded size (MB)' AFTER `album_scraped_date`;

ALTER TABLE `mediascraper`.`file` 
ADD COLUMN `file_renamed` TINYINT(1) NULL DEFAULT '0' COMMENT 'Files renamed or not for the package' AFTER `file_date_downloaded`;
