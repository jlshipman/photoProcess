#!/usr/bin/python
try:
	import socket, os, sys
	sys.path.append('lib')
	sys.path.append('libPhoto')
	from listFunctions import *
	from photoFunctions import *
	from comWrap import *
	from directory import *
	from fileSize import *
	from log import *
	from simpleMail import *
except ImportError:
	print "missing modules for photoProcess.py"
	sys.exit(1)
	
def photoProcess (lg, mailList, stage="production"):
	lg.setPrefix ("photoProcess")
	lg.info ("photoProcess function")	
	lg.info ("   stage:  " + stage)
	################directories################
	baseConfig='/scripts/photoProcess/'
	baseList=baseConfig+'LIST/'
	baseListTemp=baseList+'TEMP/'
	baseError=baseConfig+'ERROR/'
	baseTemp=baseConfig+'TEMP/'
	baseLog=baseConfig+'LOG/'
	archive="/Volumes/VST_Xsan"
		
	############## variable assignments - begin #####################
	sshConnect="msbwcup@lamp.larc.nasa.gov"
	hostName=socket.gethostname()
	cutOff=1991
	
	cssDir=hostName+".ndc.nasa.gov/repository/"
	repositoryProcess="/Volumes/repository2/processed/"
	repositoryRaw="/Volumes/repository1/raw/"
	repositoryRaw2="/Volumes/repository2/raw/"
	chksumDir=baseTemp+"checksum/"
	archiveDir=baseTemp+'archive/'
	unprocessedjpg="/Volumes/repository3/unprocessedjpg"	
	bad="/Volumes/repository3/bad"
		
	localSearchDirectories=baseList+"localSearchDirectories.txt"
	archiveFile=baseList+"archive.txt"
	dirContentsFile=baseTemp+"dirContentsFile.txt"	
	dirContentsFileJpg=baseTemp+"dirContentsFileJpg.txt"	
	############## variable assignments - end #####################

	############################# main - begin ###########################
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css")
	
	#create list to insure photo does not enter more records and
	#lose data
	dirContentsList = []
	#get info from file
	searchList = listFromFile(localSearchDirectories)
	for s in searchList:
		term = s.rstrip()
		dirContentsList = glob.glob(term + "/*" ) + dirContentsList
	listToFile(dirContentsList, dirContentsFile)
	
	photoFileMod (lg, mailList, dirContentsFile)
	
	dirContentsList = []
	for s in searchList:
		term = s.rstrip()
		dirContentsList = glob.glob(term + "/*" ) + dirContentsList
	listToFile(dirContentsList, dirContentsFile)
	
  	photoFileConvert (lg, mailList, dirContentsFile, unprocessedjpg, dirContentsFileJpg)	
 			
  	photoArchive(lg, mailList, dirContentsFile, archiveFile, baseError, chksumDir, stage)
  	
 	resposDict={}
 	resposDict['reposProcess'] = repositoryProcess
 	resposDict['reposProcessLower'] = 0 
 	resposDict['reposProcessUpper'] = 3000
 	resposDict['noYearProcess'] =repositoryProcess
 	resposDict['repos1'] = repositoryRaw
 	resposDict['repos1Lower'] = 0 
 	resposDict['repos1Upper'] = 1991
 	resposDict['repos2'] =repositoryRaw2
 	resposDict['repos2Lower'] =1992
 	resposDict['repos2Upper'] =3000
 	resposDict['noYearRaw'] =repositoryRaw
  	photoSort(lg, mailList, dirContentsFile, resposDict, chksumDir, stage)
 	
  	photoTransfer(lg, mailList, unprocessedjpg, archiveDir, stage)
  	
#  	photoMysql(lg, mailList, dirContentsFileJpg, stage)

