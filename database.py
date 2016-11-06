# This program provides a data access layer to the main application
# Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
# Date : 10/02/2016
# Version : 1.8

import sys

# include custom files and imports
import mylogger
import utils

# define configs depending on the environment

if sys.platform == "win32" or sys.platform == "darwin":
	# windows or mac osx
	import mysql.connector
	config = {
	  'user': 'mac',
	  'password': 'mysql',
	  'host': '192.168.100.100',
	  'database': 'mediascraper',
	  'raise_on_warnings': True,
	  'use_pure': False,
	}
elif sys.platform == "linux2":
	# linux
	import MySQLdb
	config = {
	  'user': 'root',
	  'passwd': 'mysql',
	  'host': '127.0.0.1',
	  'db': 'mediascraper',
	}

# Cleans an album name or a file name
def dbConnect():
	"""Connect to the MySQL database"""
	try:
		if sys.platform == "win32" or sys.platform == "darwin":
			# windows or mac osx
			connection = mysql.connector.connect(**config)
		elif sys.platform == "linux2":
			# linux
			connection = MySQLdb.connect(**config)
		return connection
	except Exception as e:
		utils.error(e)

def getParam(name):
	try:
		query = "SELECT param_value FROM param WHERE param_name = '{0}';"
		query = query.format(name)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)

		return cursor.fetchone()[0]
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def setParam(name, value):
	"""Sets the param value to the param name"""
	try:
		query = "UPDATE param SET param_value = '{1}' WHERE param_name = '{0}';"
		query = query.format(name, value)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getLastTopLevelYear():
	"""Get the last top level year scraped"""
	try:
		query = "SELECT MIN(year_value) as last_year," \
				" CASE WHEN (COUNT(1) = COUNT(CASE WHEN (year_scraped = 1 OR year_valid = 0) THEN year_scraped END)) THEN 1 ELSE 0 END as all_downloaded" \
				" FROM year;"
				
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchone()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getNextTopLevelURL():
	try:
		query = "SELECT year_url, year_value FROM year" \
				" WHERE year_value =" \
				" (SELECT MAX(year_value)" \
				" FROM year" \
				" WHERE year_scraped = 0 AND (year_valid IS NULL OR year_valid = 1));"
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchone()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def insertYear(year):
	try:
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()		
		
		# set arguments to SP
		args = (year, utils.PARAM_TopLevelPage)
		
		# execute stored procedure
		cursor.callproc("insert_year", args)
						
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def yearScraped(year):
	try:
		query = "UPDATE year SET year_scraped = 1, year_scraped_date = NOW(), year_valid = 1 WHERE year_value = {0};"
		query = query.format(year)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def countAlbums(year):
	try:
		query = "SELECT COUNT(1) as albumCount FROM album WHERE album_year_value = {0};"
		query = query.format(year)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchone()[0]
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getNextNAlbumsURL():
	try:
		query = "SELECT album_url, CASE WHEN album_scraped_date IS NULL THEN album_id ELSE -1 END as album_id" \
				" FROM album" \
				" WHERE (album_scraped = 0 AND album_scraped_error = 0) OR DATE(album_scraped_date) = DATE(NOW())" \
				" ORDER BY album_year_value DESC, album_name LIMIT {0};"
		query = query.format(getParam(utils.PARAM_MaxAlbumPerDay))
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchall()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getAlbumsWithoutSize():
	try:
		query = "SELECT DISTINCT album.album_id, album.album_pyload_name" \
				" FROM album" \
				" INNER JOIN file on album.album_id = file.file_album_id" \
				" INNER JOIN download on album.album_id = download.download_album_id" \
				" WHERE (album.album_size IS NULL OR album.album_size < 3) AND file.file_downloaded = 1;"
						
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchall()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)
		
def getAlbumsWithoutPackageId():
	try:
		query = "SELECT album_id, album_pyload_name" \
				" FROM album" \
				" WHERE album_scraped_date IS NOT NULL AND album_pyload_id IS NULL;"
						
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchall()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getAlbumsError():
	try:
		# album size of less than 3 MB is considered in error too
		query = "SELECT album_id, album_name, album_pyload_id" \
				" FROM album LEFT OUTER JOIN file" \
				" ON album.album_id = file.file_album_id" \
				" WHERE album.album_scraped_error <> 1" \
				" AND ((file.file_album_id IS NULL AND album.album_scraped_date IS NOT NULL)" \
				" OR album.album_size < 3);"
						
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchall()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def albumScraped(albumId, packageName):
	try:
		query = "UPDATE album SET album_scraped = 1, album_pyload_name = '{1}', album_scraped_date = NOW() WHERE album_id = {0};"
		query = query.format(albumId, packageName)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def albumScrapedError(albumId):
	try:
		query = "UPDATE album SET album_scraped_error = 1 WHERE album_id = {0};"
		query = query.format(albumId)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def insertAlbum(albumName, albumUrl, albumYear):
	try:
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()		
		
		insert = ("INSERT INTO album" \
				" (album_name, album_url, album_year_value)" \
				" VALUES (%(album_name)s, %(album_url)s, %(album_year_value)s)")

		data = {
		  'album_name': albumName,
		  'album_url': albumUrl,
		  'album_year_value': albumYear,
		}
		
		# execute insert
		cursor.execute(insert, data)
						
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def setAlbumSize(albumId, albumSize):
	try:
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()		
		
		query = ("UPDATE album SET album_size = {0} WHERE album_id = {1};")
		query = query.format(albumSize, albumId)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
						
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def setAlbumPackageId(albumId, packageId):
	try:
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()		
		
		query = ("UPDATE album SET album_pyload_id = {0} WHERE album_id = {1};")
		query = query.format(packageId, albumId)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
						
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def insertFile(albumId, fileUrl):
	try:
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()		
		
		insert = ("INSERT INTO file" \
				" (file_album_id, file_url)" \
				" VALUES (%(file_album_id)s, %(file_url)s)")
		
		data = {
		  'file_album_id': albumId,
		  'file_url': fileUrl,
		}
		
		# execute insert
		cursor.execute(insert, data)
		
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)
		
def isFileDownloading(albumId):
	try:
		query = "SELECT COUNT(1) as download FROM file where file_album_id = {0};"
		query = query.format(albumId)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return utils.bool(cursor.fetchone()[0])
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)
		
def listFileDowloading():
	try:
		query = "SELECT file.file_id, album.album_pyload_name, album.album_id" \
				" FROM file INNER JOIN album ON file.file_album_id = album.album_id" \
				" WHERE file.file_downloaded = 0;"
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchall()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)
		
def fileDownloaded(fileId):
	try:
		query = "UPDATE file SET file_downloaded = 1, file_date_downloaded = NOW() WHERE file_id = {0};"
		query = query.format(fileId)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getFileToRename():
	try:
		query = "SELECT file.file_id, album.album_pyload_name, album.album_id" \
				" FROM file INNER JOIN album ON file.file_album_id = album.album_id" \
				" WHERE file.file_renamed = 0 AND file.file_downloaded = 1;"
						
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchall()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def fileRenamed(fileId):
	try:
		query = "UPDATE file SET file_renamed = 1 WHERE file_id = {0};"
		query = query.format(fileId)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def insertDownload(albumId, fileId, downloadName, downloadSize):
	try:
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()		
		
		insert = ("INSERT INTO download" \
				" (download_album_id, download_file_id, download_name, download_size)" \
				" VALUES (%(download_album_id)s, %(download_file_id)s, %(download_name)s, %(download_size)s)")

		data = {
		  'download_album_id': albumId,
		  'download_file_id': fileId,
		  'download_name': downloadName,
		  'download_size': downloadSize,		  
		}
		
		# execute insert
		cursor.execute(insert, data)
						
		try:
			connection.commit()
		except:
			connection.rollback()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getAlbumsWithoutDownload():
	try:
		query = "SELECT album.album_id, file.file_id, album.album_pyload_name" \
				" FROM album LEFT JOIN file ON album.album_id = file.file_album_id" \
				" WHERE album.album_scraped_error = 0 AND album.album_scraped = 1" \
				" AND file.file_renamed = 0" \
				" ORDER BY album_pyload_name;"

		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchall()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getDownloadInfo():
	try:
		query = "SELECT DISTINCT (SELECT COUNT(1) FROM download) as total_download," \
				" album.album_year_value AS last_year, album.album_pyload_name AS last_album," \
				" (SELECT TRUNCATE(SUM(album_size) / 1024.0, 2) from album) AS album_size" \
				" FROM download" \
				" INNER JOIN album ON album.album_id = download.download_album_id" \
				" INNER JOIN file ON file.file_id = download.download_file_id" \
				" ORDER BY album.album_year_value, album.album_name DESC" \
				" LIMIT 1;"
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchone()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)

def getDownloads(start, end):
	try:
		query = "SELECT album.album_year_value, album.album_pyload_name," \
				" DATE_FORMAT(file.file_date_downloaded, '%d/%m/%y') AS date_ripped," \
				" CONCAT(download_name, ' => ', download_size, ' MB') AS file_name" \
				" FROM download" \
				" INNER JOIN album ON album.album_id = download.download_album_id" \
				" INNER JOIN file ON file.file_id = download.download_file_id" \
				" ORDER BY album.album_year_value DESC, album.album_name, download.download_name" \
				" LIMIT {0}, {1};"
		query = query.format(start, end)
		
		# open connection
		connection = dbConnect()
		cursor = connection.cursor()
		
		# execute query
		cursor.execute(query)
		
		return cursor.fetchall()
		
		# close connection
		cursor.close()
		connection.close()
	except Exception as e:
		utils.error(e)