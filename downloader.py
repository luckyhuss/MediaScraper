# This program provides download functions
# Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
# Date : 14/02/2016
# Version : 1.4

from datetime import date
import os
import time
import urllib2
import re
from urlparse import urlparse
import subprocess

# include custom files
import database
import utils
import mylogger

def generateTopLevelPages():
	# get the last year generated
	topLevelYear = database.getLastTopLevelYear()
	
	if topLevelYear[0] is None:
		topLevelYear = date.today().year
	else:
		# check if all previous links have been scraped
		if(int(topLevelYear[1]) == 0):
			# not yet scraped, return
			utils.warn("[D1]There are links to be scraped first")
			return
		# cast
		topLevelYear = int(topLevelYear[0])
		# decrement db year by one
		topLevelYear -= 1
	
	minYearValue = 1939	
	end = topLevelYear - 5
	while topLevelYear > end:		
		if topLevelYear < minYearValue:
			break		
		# insert line in db
		database.insertYear(topLevelYear)
		utils.info("[D2]Year generated : {0}".format(topLevelYear))
		# decrement counter
		topLevelYear -= 1

def checkIfDownloadsCompleted():
	downloads = utils.getDirectoryDownloads()
	#utils.info("List of directories/files at {0} : {1}".format(utils.PATH_DOWNLOADS, downloads))
	
	for album in database.listFileDowloading():
		fileId = album[0]
		filePackageName = album[1]
		albumId = album[2]
		
		try:
			if any(filePackageName in s for s in downloads):
				album_dir = os.path.normpath(utils.PATH_DOWNLOADS + "/" + filePackageName)
				
				# check if chunk is present in folder (i.e. download in progress)
				if utils.isChunkOrEmpty(album_dir):
					# album download in progress
					utils.info("Package download in progress : {0}".format(filePackageName))
				else:
					# album already downloaded, update flags
					database.fileDownloaded(fileId)
					# get album size in MB
					albumSize = utils.getDirectorySize(album_dir)
					# updat album size in DB
					database.setAlbumSize(albumId, albumSize)
					utils.info("Package download completed : {0} [Size={1}]".format(filePackageName, "%0.2f MB" % albumSize))
		except Exception as e:
			mylogger.logger.error("Error {0} : {1}".format(e, albumId))

def loadUrlInCache(webPageUrl):
	try:
		request = urllib2.Request(webPageUrl, headers=utils.CLIENT_HEADER)
		response = urllib2.urlopen(request)	
		content = response.read()
		content = content.replace("\n", "")
		return content
	except Exception as e:
		mylogger.logger.error("Error {0} : {1}".format(e, webPageUrl))

def launchPyLoad(packageName, url, albumId):
	pyLoad = utils.COMMAND_PYLOAD.format(packageName, url)
	try:
		#pyLoadCli add "Gabbar Is Back (2015) 128Kbps" "http://link.songspk.help/indian_movie/G_List/download.php?id=860"		
		subprocess.call(pyLoad, shell=True)
		utils.info("pyLoad >> " + packageName)		
		return 0 # success
	except Exception as e:
		mylogger.logger.error("Error {0} : {1}".format(e, pyLoad))
		return 1 # failure

def getPageTitle(urlContent):
	webPageTitle = re.findall(utils.patternTitle, urlContent)
	currentTitle = webPageTitle[0]
	currentTitle = currentTitle.replace("SongsPK.info &gt;&gt;", "")
	
	index = -1
	try:
		index = currentTitle.index(")")
	except Exception as e:
		mylogger.logger.error("Error {0} in title {1}".format(e, webPageTitle))

	if index != -1:
		# found
		currentTitle = currentTitle[:index + 1]	
	# return stripped version of title
	return currentTitle.strip()
	
def launchDownload(uniqueUrls, webPageTitle, albumId):
	zipFlag = False
	zipUrl = ""
	zipName = ""	
	
	for url, name in uniqueUrls.iteritems():		
		if "128kbps" in name.lower() or "320kbps" in name.lower():
			# zip found
			if "128kbps" in name.lower() and "320kbps" in zipName.lower():
				# 320kbps already found before 128kbps, therefore don't update
				continue
			# update flags and variables
			zipFlag = True
			zipUrl = url
			zipName = name
	
	if zipFlag == False:
		# zip not found, read page title		
		# set packageName to page title
		packageName = webPageTitle
		
		mylogger.logger.warning("No Zip file found, loading each MP3 file")
		
		urlList = ""
		# load all files in pyLoad
		for url, name in uniqueUrls.iteritems():
			# build complete url list for a single package
			urlList += "\"{0}\" ".format(url)
			
			# check if files already sent to pyLoad
		
		# load all (individual) files in pyLoad
		launched = launchPyLoad(packageName, urlList.strip(), albumId)
		if launched == 0:
			# on success			
			for url, name in uniqueUrls.iteritems():
				# insert files
				database.insertFile(albumId, url)
	
	elif zipFlag == True:		
		utils.info("Zip file found : {0}".format(zipName))	
		
		# check if file already sent to pyLoad
		
		# load zip file in pyLoad
		launched = launchPyLoad(zipName, "\"{0}\"".format(zipUrl), albumId)
		if launched == 0:
			# on success
			# insert file
			database.insertFile(albumId, zipUrl)
			# update packageName
			packageName = zipName

	if launched == 0:
		# on success
		# update album
		database.albumScraped(albumId, packageName)

def downloadMp3(webPageUrl, topLevelYear=0, albumId=0, rePassYear=0):
	"""Fetch download links for a given Url
	webPageUrl = url to be scraped and saved in DB
	topLevelYear = year to be scraped (0 for album scraping)
	albumId = Id of album to be scraped (0 for year scraping
	"""
	# set start time
	start_time = time.time()
	
	# get web page content to scrape
	urlContent = loadUrlInCache(webPageUrl)

	if urlContent is None:
		return
	
	# read page title for logging and others
	webPageTitle = getPageTitle(urlContent)
	
	# get execution time
	utils.info("{0} seconds to load [{1}] page @ {2}".format(str(round(time.time() - start_time, 2)), webPageTitle, webPageUrl))
	
	# add break line after each ending anchor tag </a> (for RegEx)
	urlContent = urlContent.replace("</A>", "</a>").replace("</a>", "</a>\n")

	# scrape all urls found on this web page
	getAllUrls = re.findall(utils.patternAGroup, urlContent)

	# create dictionary to keep unique url
	uniqueUrls = dict()

	for url in getAllUrls:	
		# url[0] = Download url
		# url[1] = Download name
		downloadName = url[1].lower()
		downloadUrl = url[0]
		
		if topLevelYear == 0:
			# real download page
			# if url is not that of download or javascript in it, continue  (and "zip" not in downloadName) <= not used
			if ("download" not in downloadUrl or "javascript:" in downloadUrl):
				continue
		else:
			# top level page, get albums
			if (str(topLevelYear) not in downloadUrl or "video_songs" in downloadUrl or "src=\"http" in downloadName):
				continue
		
		# clean album / file name
		downloadName = utils.cleanAlbumName(downloadName)
		
		if downloadUrl not in uniqueUrls:
			uniqueUrls[downloadUrl] = downloadName
		
	utils.info("{0}/{1} valid urls scraped".format(len(uniqueUrls), len(getAllUrls)))
	
	if topLevelYear == 0:
		# real download page
		# launch urls to download (pyLoad)
		launchDownload(uniqueUrls, webPageTitle, albumId)
	else:
		# top level page, insert albums
		if rePassYear == 0:
			for url, name in uniqueUrls.iteritems():			
				database.insertAlbum(name, url, topLevelYear)
				utils.info("Album {0}:{1} inserted".format(name, url))			
			# update year
			database.yearScraped(topLevelYear)
		else:
			# repassing the current year for new albums
			albumsOnline = len(uniqueUrls)
			albumsBD = int(database.countAlbums(topLevelYear))
			utils.info("Albums online : {0}, Albums database : {1}".format(albumsOnline, albumsBD))

			if albumsOnline == albumsBD :
				utils.info("No new album added")
			else:
				utils.info("Adding {0} new albums".format(albumsOnline - albumsBD))
				for url, name in uniqueUrls.iteritems():			
					database.insertAlbum(name, url, topLevelYear)
					utils.info("Album {0}:{1} inserted".format(name, url))
				# update year
				database.yearScraped(topLevelYear)

def downloadNextNAlbums():
	"""Download the next N albums in list"""
	# get next N albums to download
	nextNAlbumsURL = database.getNextNAlbumsURL()
	
	if len(nextNAlbumsURL) > 0:
		# not all albums have been downloaded
		utils.warn("There are albums to be scraped first")
		
		countDownloaded = 0
		# download current 2 albums
		for nextAlbumURL in nextNAlbumsURL:
			albumUrl = nextAlbumURL[0]
			albumId = nextAlbumURL[1]
			
			# if max albums per day downloaded
			if int(albumId) == -1:
				countDownloaded += 1
				continue
			else:
				# check if files already sent to pyLoad (necessary if error occured when lauching pyLoad downloads)
				if database.isFileDownloading(albumId):
					# already downloading
					utils.warn("{0} : File(s) already downloading".format(albumId))
					break
				# else download new albums for the day
				downloadMp3(nextAlbumURL[0], 0, nextAlbumURL[1])
		
		# check if max albums downloaded for the day
		if len(nextNAlbumsURL) == countDownloaded:
			# check if nb return albums is correct
			if len(nextNAlbumsURL) < int(database.getParam(utils.PARAM_MaxAlbumPerDay)):
				print len(nextNAlbumsURL)
				print database.getParam(utils.PARAM_MaxAlbumPerDay)
				# nb of albums returned is less than max allowable, therefore fetch nextTopLevelURL
				nextTopLevelURL = database.getNextTopLevelURL()
				if nextTopLevelURL is not None:
					# download all albums found in this next available topLevelPage
					downloadMp3(nextTopLevelURL[0], nextTopLevelURL[1], 0)
			else:
				utils.info("Max albums have been downloaded for the day")
	else:
		nextTopLevelURL = database.getNextTopLevelURL()
		if nextTopLevelURL is not None:
			# download all albums found in this next available topLevelPage
			downloadMp3(nextTopLevelURL[0], nextTopLevelURL[1], 0)

def checkNewAlbumsThisYear():
	"""Check for news albums in the current year"""
	# check if current year list has new albums
	currentYear = utils.formatDateTime("%Y")
	utils.info("Checking for new albums : year {0}".format(currentYear))

	topLevelPageURL = str(database.getParam(utils.PARAM_TopLevelPage))
	topLevelPageURL = topLevelPageURL.replace("[0]", currentYear)

	downloadMp3(topLevelPageURL, int(currentYear), 0, 1)