# This program scrapes the web page to get download urls for mp3
# Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
# Date : 01/03/2016
# Version : 3.1
# sudo crontab -l
# sudo crontab -e
# m h  dom mon dow   command
# reboot Rapsberry Pi every midnight
#0 0 * * * sudo reboot
# launch MediaScraper every 3 hours:15mins
#15 */3 * * * python /home/pi/mypython/MediaScraper/main.py

#import os
import sys

# include custom files
import mylogger
import utils
import database
import downloader

def initialise():
	utils.clearScreen()
	mylogger.initLogging()
	utils.info("Starting program with BASE : {0}".format(utils.PATH_BASE))

	# get launch count
	launchCount = database.getParam(utils.PARAM_LaunchCount)
	launchCount = int(launchCount) + 1

	# update count in database
	utils.info("Run {0} times".format(launchCount))
	database.setParam(utils.PARAM_LaunchCount, launchCount)

	#utils.info("Dump @ {0}".format(utils.FILE_MYSQLDUMP))

def main():
	# initialise application
	initialise()
	
	if len(sys.argv) > 1 and sys.argv[1] == "tree":
		# generate tree view for downloaded albums
		utils.treeDownloads()
		return

	# generate top level pages (by year)
	downloader.generateTopLevelPages()

	# check for new albums in current year
	downloader.checkNewAlbumsThisYear()

	# download the next N albums in waiting list
	downloader.downloadNextNAlbums()
	
	# check if any download has already completed
	downloader.checkIfDownloadsCompleted()	
	
	# rename all files not yet renamed
	utils.renameFiles()

	# set size of all albums without size
	utils.updateAlbumsSize()

	# update package id for all albums without
	utils.updateAlbumsPackageId()

	# update all albums in error
	utils.updateAlbumsError()

	# one-shot run only
	#utils.oneShotDumpDownload()

	# full backup of database
	if sys.platform != "win32" and sys.platform != "darwin":
		# if not windows nor mac osx
		utils.dumpDatabase()
		# get the reports
		utils.outputSystemInfo()

	# dumps downloads folder content
	# package name + size update => OK
	# rename files => OK
	# automate setup on linux through shell => OK
	# database backup => OK
	# 06/11/2016
	# check if WDMyCloud has been loaded (electricity cut) => KO
	# automate rsync in python instead of cron => KO

	utils.info("Exiting program")
	
# call main function
main()