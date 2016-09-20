-- This SQL script updates the db for mediascraper
-- Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
-- Date : 15/02/2016
-- version : 1.9

-- insert new parameters
INSERT INTO `mediascraper`.`param` (`param_name`, `param_value`) 
VALUES
('Database.LastSQLScript', '01-database.sql');

-- update the column name of file_name -> file_package_name
ALTER TABLE `mediascraper`.`file` 
CHANGE COLUMN `file_name` `file_package_name` VARCHAR(100) NOT NULL COMMENT 'File name of package sent to pyLoad' ;
