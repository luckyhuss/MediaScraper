#!/bin/bash

# This program setup MediaScraper for usage
# Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
# Date : 26/02/2016
# Version : 1.2
# chmod 755 setup.sh
# ./setup.sh

clear
echo "Launching setup for MediaScraper"

# Create directories

# Apply permissions
chmod 755 /home/pi/mypython/MediaScraper/sh/everyhour.sh

# Update database
mysql -uroot -pmysql < "/home/pi/mypython/MediaScraper/mysql/04-database.sql"

echo "MediaScraper setup completed"
