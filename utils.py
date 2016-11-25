# -*- coding: utf-8 -*-
# This program provides utility functions
# Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
# Date : 10/02/2016
# Version : 1.5

import os
import sys
import subprocess
import mylogger
import mail
import time
import datetime
from shutil import copyfile
import database

if sys.platform == "linux2":
	import paramiko

# RegEx
patternA = "<a.*</a>"
patternAGroup = "<a\s+(?:[^>]*?\s+)?href=\"([^\"]*)([^/]+).+"
patternTitle = "<title[^>]*>(.*?)<\/title>"
#patternUrl = "(?:(?:https?|ftp):\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,}))\.?)(?::\d{2,5})?(?:[/?#]\S*)?"

# application parameters
PARAM_LaunchCount = "Application.LaunchCount"
PARAM_TopLevelPage = "Download.TopLevelPage"
PARAM_MaxAlbumPerDay = "Download.MaxAlbumPerDay"

# application paths
if sys.platform == "win32" or sys.platform == "darwin":
	PATH_BASE = os.path.dirname(os.path.realpath(__file__))
elif sys.platform == "linux2":
	PATH_BASE = os.path.dirname("/media/shares/SEAGATE-II/RasperryPi/MediaScraper/")
PATH_LOG = os.path.normpath(PATH_BASE + "/logs")
PATH_FILES = os.path.normpath(PATH_BASE + "/files")
PATH_MYSQL = os.path.normpath(PATH_BASE + "/mysql")

# application files
FILE_REPORT =  os.path.normpath(PATH_FILES + "/report.txt")
FILE_MYSQLDUMP = os.path.normpath(PATH_MYSQL + "/dumpfile-{0}.sql")
FILE_MYSQLDUMP = FILE_MYSQLDUMP.format(time.strftime("%Y%m%d", time.localtime()))
FILE_LOG = os.path.normpath(PATH_LOG + "/main.log")
FILE_TREE =  os.path.normpath(PATH_FILES + "/MP3 repository.txt")

# custom names
EXT_MP3 = ".mp3"
TAG_MP3_INFO = "[SongsPK.info] "
TAG_MP3_RU = "[SongsPK.ru] "
TAG_MP3_PK = "[Songs.PK] "

if sys.platform == "win32":
	# windows
	PATH_DOWNLOADS = "E:/Perso/_movies/_download/"
elif sys.platform == "darwin":
	# mac osx
	PATH_DOWNLOADS = "/Users/anwar/Downloads/"
elif sys.platform == "linux2":
	# linux
	PATH_DOWNLOADS = "/media/shares/SEAGATE-II/Torrent/Others/"

# generic variables
CLIENT_HEADER = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}
COMMAND_PYLOAD = "pyLoadCli add \"{0}\" {1}"
COMMAND_MYSQLDUMP = "mysqldump -uroot -pmysql mediascraper > \"{0}\""
COMMAND_RSYNC = "sudo rsync -av --progress --log-file=" + PATH_LOG + "/{0}.log {1} {2}"

def error(e):
	mylogger.logger.error("Error {0}".format(e))
	
def info(message):
	mylogger.logger.info(message)
	
def warn(message):
	mylogger.logger.warning(message)

def startTimer():
	# get start time
	return time.time()
	
def stopTimer(startTimer):
	# set time taken to execute statement
	return str(round(time.time() - startTimer, 2))

def getDirectoryDownloads():
	return os.listdir(PATH_DOWNLOADS)
	
def isChunkOrEmpty(directory):
	"""Check if download folder contains chunk files or is empty or non existent"""
	# no chunk / folder not empty
	chunkOrEmpty = False
	if not os.path.exists(directory) or os.listdir(directory) == []:
		chunkOrEmpty = True

	for name in os.listdir(directory):
		# check if chunk file found
		if "chunk" in name.lower():
			# chunk file found, download is still in progress
			chunkOrEmpty = True
			break

	return chunkOrEmpty

def getDirectorySize(start_path):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return (total_size / (1024.0 * 1024.0))

def updateAlbumsSize():
	# set start time
	start = startTimer()

	albumsWithoutSize = database.getAlbumsWithoutSize()

	for albumWithoutSize in albumsWithoutSize:
		albumId = albumWithoutSize[0]
		packageName = albumWithoutSize[1]
		start_path = os.path.normpath(PATH_DOWNLOADS + "/" + packageName)

		if not os.path.isdir(start_path):
			continue

		#info("Computing size for package \"{0}\"".format(packageName))
		albumSize = getDirectorySize(start_path)
		# update DB
		database.setAlbumSize(albumId, albumSize)
		info("Album \"{0}\" updated [Size={1}]".format(packageName, "%0.2f MB" % albumSize))
	info("{0} seconds to update albums size".format(stopTimer(start)))

def updateAlbumsPackageId():
	# set start time
	start = startTimer()

	albumsWithoutPackageId = database.getAlbumsWithoutPackageId()

	for albumWithoutPackageId in albumsWithoutPackageId:
		albumId = albumWithoutPackageId[0]
		packageName = albumWithoutPackageId[1]
		
		info("Updating pyLoad pid for \"{0}\"".format(packageName))
		
		# query pyLoad queue
		value = getPyloadQueue(packageName, "pid")
		
		# no more present on pyLoad
		if len(value) == 0:
			# update DB
			database.setAlbumPackageId(albumId, -1)
			info("Album \"{0}\" updated [pid=-1]".format(packageName))
			# then continue with next album
			continue
		else:
			# update DB
			database.setAlbumPackageId(albumId, value)
			info("Album \"{0}\" updated [pid={1}]".format(packageName, value))
	info("{0} seconds to update albums pyLoad pid".format(stopTimer(start)))

def updateAlbumsError():
	# set start time
	start = startTimer()

	albumsError = database.getAlbumsError()

	for albumError in albumsError:
		albumId = albumError[0]
		packageName = albumError[1]
		pyLoadId = albumError[2]
				
		# del package in pyLoad
		exit_code = deletePyloadPackage(pyLoadId)

		if exit_code == 0:
			# on success
			# update album (error)
			database.albumScrapedError(albumId)
			info("Album \"{0}\" is in error".format(packageName))		
	info("{0} seconds to update albums error".format(stopTimer(start)))

def getPyloadQueue(packageName, param):
	# check output
	out = subprocess.check_output("pyLoadCli queue_detail \"{0}\"".format(packageName), shell=True)
	# sample
	# pid:86|fid:86|pname:Bewakoofiyaan (2014) 320Kbps|fname:Bewakoofiyaan-2014-320kbps[SongsPK.info].zip|furl:http://link.songspk.help/indian_movie/B_List/download.php?id=1599|status:finished|size:47.07 MiB
		
	# no more present on pyLoad
	if len(out) == 0:
		return ""

	# get key-value pair
	for kvp in out.split("|"):
		key = str(kvp).split(":")[0]
		value = str(kvp).split(":")[1]			
		if key == param:
			return value

def deletePyloadPackage(pid):
	try:
		# call del
		subprocess.call("pyLoadCli del_package {0}".format(pid), shell=True)
		# sample
		# pyLoadCli del_package 333
		return 0 # success
	except Exception as e:
		error(e)
		return 1 # failure

def renameFiles():
	# set start time
	start = startTimer()

	filePackages = database.getFileToRename()
	
	for filePackage in filePackages:
		fileId = filePackage[0]
		packageName = filePackage[1]
		albumId = filePackage[2]

		start_path = os.path.normpath(PATH_DOWNLOADS + "/" + packageName)

		if not os.path.isdir(start_path):
			continue

		renamed = False
		#info("Renaming files in \"{0}\"".format(packageName))
		for dirpath, dirnames, filenames in os.walk(start_path):
			for f in filenames:
				if(EXT_MP3 in f.lower()):
					renamed = True
					newf = f.replace(TAG_MP3_INFO, "").replace(TAG_MP3_RU, "").replace(TAG_MP3_PK, "")
					fp = os.path.join(dirpath, f)
					newfp = os.path.join(dirpath, newf)
					# rename files
					os.rename(fp, newfp)
					info("{0} has been renamed and saved".format(f))
					# compute file size
					total_size = os.path.getsize(newfp)
					fsize = (total_size / (1024.0 * 1024.0))
					# update DB
					database.insertDownload(albumId, fileId, newf, fsize)
		
		if renamed:
			# update DB, if at least one .mp3 renamed
			database.fileRenamed(fileId)
	info("{0} seconds to rename and save files".format(stopTimer(start)))

def outputSystemInfo():
	"""Output system info to file"""
	fileName = FILE_REPORT
	# delete file first (for append)	
	if os.path.exists(fileName):
		os.remove(fileName)
			
	cmd = ["uptime", "-s"]
	with open(fileName, 'a') as out:
		return_code = subprocess.call(cmd, stdout=out)
		
		cmd = ["uptime", "-p"]
		return_code = subprocess.call(cmd, stdout=out)
		
		cmd = ["vcgencmd", "measure_temp"]	
		return_code = subprocess.call(cmd, stdout=out)
		
		cmd = ["free"]	
		return_code = subprocess.call(cmd, stdout=out)
		
		cmd = ["df", "-h"]	
		return_code = subprocess.call(cmd, stdout=out)
		
		#cmd = ["ps", "-aux"]	
		#return_code = subprocess.call(cmd, stdout=out)

		cmd = ["pyLoadCli", "status"]	
		return_code = subprocess.call(cmd, stdout=out)

		#sudo smartctl -a /dev/sda | less

		# copy log file also to mail fodler
		copyfile(FILE_LOG, os.path.normpath(PATH_FILES + "/log.txt"))
		copyfile(FILE_MYSQLDUMP, os.path.normpath(PATH_FILES + "/mediascraper.sql"))

	# email the report
	mail.sendMail("[RPi][SYS INFO] : {0}".format(time.strftime("%d/%m %H:%M:%S", time.localtime())), "Please find attached the files")	

def formatDateTime(format):
	"""Return a formated date/time depending on format"""
	return time.strftime(format, time.localtime())

def cleanAlbumName(albumName):
	"""Clean an album name or a file name"""
	# : for preventing pyLoad package name error
	albumName = albumName.replace("<br", "").replace(":", "-"). \
		replace("<", "").replace(">", "").replace("\"", ""). \
		replace("download", "").replace("zip", ""). \
		replace("&amp;", "&").replace("&#039;", "'").strip().title()
	return albumName
	
def clearScreen():
	"""Clear the user screen (important when not run as daemon)"""
	if os.name == "nt":
		# windows
		os.system("cls")
	else:
		# linux
		os.system("clear")

def bool(value):
	"""Convert a value (yes|true|t|1) to bool"""
	# cast to string
	value = str(value)
	return value.lower() in ("yes", "true", "t", "1")

def dumpDatabase():
	# Backup
	#mysqldump -u root -pmysql mediascraper > "E:\Google Drive\WinApp\MediaScraper\mysql\dumpfile-20160215.sql"
	# Restore
	#mysql -u root -pmysql mediascraper1 < "E:\Google Drive\WinApp\MediaScraper\mysql\dumpfile-20160215.sql"
	
	# set start time
	start = startTimer()

	# get filname + command
	mySQLDump = COMMAND_MYSQLDUMP.format(FILE_MYSQLDUMP)
	
	subprocess.call(mySQLDump, shell=True)
	info("{0} seconds to backup full database".format(stopTimer(start)))

def oneShotDumpDownload():
	start_curr = startTimer()

	albumsWithoutDownload = database.getAlbumsWithoutDownload()

	for albumWithoutDownload in albumsWithoutDownload:
		albumId = albumWithoutDownload[0]
		fileId = albumWithoutDownload[1]
		packageName = albumWithoutDownload[2]

		start_path = os.path.normpath(PATH_DOWNLOADS + "/" + packageName)

		if not os.path.isdir(start_path):
			warn("Album \"{0}\" does not exist on disk".format(packageName))
			continue

		countMP3 = 0
		for dirpath, dirnames, filenames in os.walk(start_path):
			for f in filenames:
				if(EXT_MP3 in f.lower()):
					fp = os.path.join(dirpath, f)
					total_size = os.path.getsize(fp)
					fsize = (total_size / (1024.0 * 1024.0))
					# update DB
					database.insertDownload(albumId, fileId, f, fsize)
					countMP3 += 1
		info("{0} MP3 set for \"{1}\"".format(countMP3, packageName))

	info("{0} seconds to dump downloads".format(stopTimer(start_curr)))

def treeDownloads():
	start_curr = startTimer()

	downloadInfo = database.getDownloadInfo()

	if downloadInfo is None:
		return

	total_download = downloadInfo[0]
	last_year = downloadInfo[1]
	last_album = downloadInfo[2]
	album_size = downloadInfo[3]

	# building blocks
	verticalLine = "│"
	tBranch = "├"
	lBranch = "└"
	horizontalLine = "─"
	space = " "
	newLine = "\n"

	outputFile = FILE_TREE
	# delete file first (for append)	
	if os.path.exists(outputFile):
		os.remove(outputFile)		
	b = open(outputFile, 'a')	

	currentYear = 0
	currentAlbum = ""

	b.write("Total size : {0} GB @ {1} (Bolly)".format(album_size, formatDateTime("%d/%m/%Y")))
	b.write(newLine)
	b.write("MP3")
	b.write(newLine)

	lineCount = 0
	while lineCount < int(total_download):

		#downloads = database.getDownloads(1200, 1260)
		downloads = database.getDownloads(lineCount, lineCount + 30000)
						
		for download in downloads:
			albumYear = download[0]		
			packageName = download[1]
			dateRipped = download[2]
			fileName = download[3]

			if currentYear != int(albumYear):
				currentYear = int(albumYear)
				if last_year != currentYear:
					b.write("{2}{0}{0} {1}".format(horizontalLine, currentYear, tBranch))
				else:
					b.write("{2}{0}{0} {1}".format(horizontalLine, currentYear, lBranch))
				b.write(newLine)			
			else:
				# same year
				pass

			if currentAlbum != packageName:
				currentAlbum = packageName
				if last_year == currentYear :
					b.write("{0}{0}{0}{0}{0}{1}".format(space, verticalLine))
					b.write(newLine)
				else:
					b.write("{1}{0}{0}{0}{0}{1}".format(space, verticalLine))
					b.write(newLine)

				if last_album == currentAlbum and last_year != currentYear:
					b.write("{4}{0}{0}{0}{0}{1}{2}{2}{2} {3} [Ripped : {5}]".format(space, lBranch, horizontalLine, currentAlbum, verticalLine, dateRipped))
					b.write(newLine)
				elif last_album == currentAlbum and last_year == currentYear:
					b.write("{0}{0}{0}{0}{0}{1}{2}{2}{2} {3} [Ripped : {5}]".format(space, lBranch, horizontalLine, currentAlbum, verticalLine, dateRipped))
					b.write(newLine)
				elif last_album != currentAlbum and last_year != currentYear:
					b.write("{4}{0}{0}{0}{0}{1}{2}{2}{2} {3} [Ripped : {5}]".format(space, tBranch, horizontalLine, currentAlbum, verticalLine, dateRipped))
					b.write(newLine)				
				else:
					b.write("{0}{0}{0}{0}{0}{1}{2}{2}{2} {3} [Ripped : {5}]".format(space, tBranch, horizontalLine, currentAlbum, verticalLine, dateRipped))
					b.write(newLine)

				if last_album == currentAlbum and last_year == currentYear:
					b.write("{0}{0}{0}{0}{0}{0}".format(space, verticalLine))
					b.write(newLine)
				elif last_album != currentAlbum and last_year == currentYear:
					b.write("{0}{0}{0}{0}{0}{1}".format(space, verticalLine))
					b.write(newLine)
				else:
					b.write("{1}{0}{0}{0}{0}{1}".format(space, verticalLine))
					b.write(newLine)
			else:
				# same album
				pass
		
			# write file name
			if last_album == currentAlbum and last_year == currentYear:
				b.write("{0}{0}{0}{0}{0}{0}{0}{0}{0}{0}{0}{0}{0}{2}".format(space, verticalLine, fileName))
			elif last_album != currentAlbum and last_year == currentYear:
				b.write("{0}{0}{0}{0}{0}{1}{0}{0}{0}{0}{0}{0}{0}{2}".format(space, verticalLine, fileName))
			else:
				b.write("{1}{0}{0}{0}{0}{1}{0}{0}{0}{0}{0}{0}{0}{2}".format(space, verticalLine, fileName))
			b.write(newLine)

		lineCount += 30000

	b.close()

	info("{0} seconds to tree downloads".format(stopTimer(start_curr)))

def checkWDMyCloud():
	"""Open SSHv2 connection to WDMyCloud and kill processes"""
	info("Connecting to WDMyCloud ..")

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect('192.168.100.101', username='root', password='wdmycloud')
	info("Connected to WDMyCloud")

	#/etc/init.d/wdmcserverd stop
	#/etc/init.d/wdphotodbmergerd stop
	info("Stopping wdmcserverd ..")
	stdin, stdout, stderr = ssh.exec_command("/etc/init.d/wdmcserverd stop")
	info(stdout.readlines())
	info("Stopping wdphotodbmergerd ..")
	stdin, stdout, stderr = ssh.exec_command("/etc/init.d/wdphotodbmergerd stop")
	info(stdout.readlines())

def launchRsync(logName, sourceFolder, destinationFolder):
	"""One-way synchronisation of two folders"""
	rSync = COMMAND_RSYNC.format(logName, sourceFolder, destinationFolder)
	try:
		info("Launching rsync ..")
		#sudo rsync -av --progress --log-file=/media/shares/SEAGATE-II/RasperryPi/rsync_torrents.log /var/lib/transmission-daemon/info/torrents/ /media/shares/SEAGATE-II/RasperryPi/torrents/		
		subprocess.call(rSync, shell=True)
		info("rsync : " + sourceFolder + " >> " + destinationFolder)		
		return 0 # success
	except Exception as e:
		mylogger.logger.error("Error {0} : {1}".format(e, rSync))
		return 1 # failure