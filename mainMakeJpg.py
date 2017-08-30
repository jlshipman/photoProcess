#!/usr/bin/python
# try:
#################### import code - begin #################### 
import sys, os
os.chdir('/scripts/photoProcess/')
sys.path.append('lib')
sys.path.append('libPhoto')
import comWrap
import directory
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import fileFunctions
import fileSize
import listFunctions
import log
import photoFunctions
import sigTerm
import simpleMail
import time
import timeFunc
import userUtil
import imageFunc
import userUtil
import systemUtil
import programUtil
import dictFunc
import pwd
import signal
import socket 
import mysqlFunctions

# except ImportError:
# 	print "missing modules for main.py"
# 	sys.exit(1)
#################### import code - end #################### 

############### script setup - begin #####################

############## variable assignments - begin #####################
variableAssign="LIST/baseVariables.txt"
baseVar = dictFunc.fileToDict(variableAssign, ",")
	
variableAssign="LIST/variableAssign.txt"
dictVar = dictFunc.fileToDict(variableAssign, "#")
sizeOfBaseDict = len (baseVar)
for x in range(0, sizeOfBaseDict):
	for (n, v) in dictVar.items():
		var = dictVar[n]
		for (key, value) in baseVar.items():
			searchTerm="<"+str(key)+">"
			retVal=var.find(searchTerm)
			if retVal != -1:
				newString = var.replace(searchTerm, value)
				dictVar[n]=newString

for (n, v) in dictVar.items():
	exec('%s=%s' % (n, repr(v)))
os.chdir(scriptDir)

hostName=socket.gethostname()
cssDir=hostName+".ndc.nasa.gov/repository/"

logCount = directory.countFilesWithPrefix ("LOG","log_")
mailList = {}
from_addr = "ladmin@" + hostName
mailList['from_addr'] = from_addr
mailList['to_addr'] = to_addr
message = ""
start_time = time.time()

############## variable assignments - end #####################

l=log.log()
l.setData(prefix, "myLogger2")
l.logDelete("LOG",logCount,logNum)
l.info("loglogNumcount: " + str(logNum))
l.info("log count: " + str(logCount))
l.info("start_time: " + str(start_time))
#if file does not exist =>  used to avoid double running the script
l.info (checkfile2)
dirPath = os.path.dirname(checkfile2)
dirObj=directory.makeDirectoryObj(dirPath)
retValDir= dirObj.getRetVal()
if retValDir == 1:
	mailList['subject'] = "could not create directory:   ---" + dirPath
	message = "could not create directory:   ---" + dirPath
	l.abort(message)
	mailList['message'] = message
	shortMessage (mailList)
	sys.exit(1)
retDict=systemUtil.createRaceConditionFile(checkfile2)
retVal=int(retDict['retVal'])
comment=retDict['comment']
if retVal == 1:
	mailList['subject'] = "double run script fault - " + scriptNameMail2 + ":  --- " + checkfile2 +" exists ---"
	message = "double run script fault - " + scriptNameMail2  + ":  --- "+ checkfile2 + " exists --- \n"
	message = message + comment
	l.abort(message)
	mailList['message'] = message
	shortMessage (mailList)
	sys.exit(1)
	
sigTerm.termHandler(checkfile2)
# for i in ['SIGHUP','SIGINT','SIGTERM']:
# 	signum = getattr(signal,i)
# 	signal(signum, termHandler)


userName=userUtil.getUsername()
l.info ("user name: " + userName)	
total = len(sys.argv)
if total == 2:
	stage=str(sys.argv[1])
	#default production
	#developement
	l.info ("First argument: %s" % str(sys.argv[1]))
else:
	stage="production"
############################# main - begin ###########################

if stage == "production":
	l.info("production")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")

	############################# get list of photo assets to add metaData from dir - begin ###########################
	l.info("#############################" + stage +  "##############################") 
	l.info("get list of photo assets to add metaData from dir")
	
	dirPath = "/Volumes/photoRepository/testingRenameSrc"
	retObj=directory.listFilesSuffixNoDups2( dirPath, "tif" )
	searchList = retObj.getResult()
	############################# get list of photo assets to add metaData from dir - end ###########################

	############################# get size of tif - begin ###########################
	l.info("get size of tif")

	wholeArray = []
	for s in searchList:
		imageRetObj = imageFunc.getInfo (s)	
		base = os.path.basename(s)
		result = imageRetObj.getResult()
		xsize = result['xsize']
		ysize = result['ysize']	
		itemArray = [base, xsize, ysize]
		l.info("base:  " + base)
		l.info("xsize: " + str(xsize))
		l.info("ysize: " + str(ysize))
		dict = {'base': base, 'xsize': xsize, 'ysize': ysize}	
		wholeArray.append(dict)
	############################# get size of tif  - end ###########################

	############################# place size information in database  - begin ###########################			
	l.info("place size information in database")
	for w in wholeArray:
		xsize = w['xsize']
		ysize = w['ysize']	
		base =  w['base']
		
		##get year and seq from name
		retObjProper=photoFunctions.imageProperlyNamed(base)
		if retObjProper.getRetVal() == 0:
			l.info("\tnew format names")
			retObjPart=photoFunctions.photoParts(base, "tif")
		else:
			l.info("\told format names")
			retObjPart=photoFunctions.photoPartsOld2(base, "tif")
		
		result = retObjPart.getResult()
		year=result['year']
		seq=result['seq']
		
		##update database with size info
		retObjConn = photoFunctions.photoConnectMysql2(stage)
		if retObjConn.getRetVal() == 1:
			retObj.setError("photoConnectMysql2:  problem with mysql connection")
			errorFunc = retObjConn.getError()
			error = error + "\n" + errorFunc
			retObj.setError(error)
			retObj.setComment(comments)
		else:
			conn = retObjConn.getResult()
		
		noSuffixName = base.replace(".tif", "")
		
		nameJpg = noSuffixName + ".jpg"
		retObjExists = photoFunctions.photoExistObj2 (conn, nameJpg)
		if retObjExists.getRetVal() == 0:
			retObjInsert = photoFunctions.photoUpdatePixel(conn, noSuffixName, xsize, ysize)
			if retObjConn.getRetVal() == 1:
				retObj.setError("photoInsertPixel:  unexpected error")
				errorFunc = retObjConn.getError()
				error = error + "\n" + errorFunc
				retObj.setError(error)
				retObj.setComment(comments)		
		else:
			retObjInsert = photoFunctions.photoInsertPixel(conn, noSuffixName, xsize, ysize)
			if retObjConn.getRetVal() == 1:
				retObj.setError("photoInsertPixel:  unexpected error")
				errorFunc = retObjConn.getError()
				error = error + "\n" + errorFunc
				retObj.setError(error)
				retObj.setComment(comments)
	############################# place size information in database  - end ###########################
# 				
# 	############################# convert tif to jpg - begin ###########################			
# 	fileFunctions.listToFile(searchList, dirContentsFile)
# 	l.info("################# convert tif to jpg #################")
# 	retObj = photoFunctions.photoFileConvertObj (dirContentsFile, dirContentsFileJpg, baseTemp, badName, badTif, False)	
# 	############################# convert tif to jpg - end ###########################
# 
# 	############################# push jpg to webserver - begin ###########################			
# 	l.info("################# transfer jpg #################")
# 	retObj = photoFunctions.photoTransferObj(stage, baseTemp, sshOutputFile, repositorylist)
# 	############################# push jpg to webserver - end ###########################			
#  
elif stage == "development":
	l.info("development")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")

	############################# get list of photo assets to add metaData from dir - begin ###########################
	l.info("#############################" + stage +  "##############################") 
	l.info("get list of photo assets to add metaData from dir")
	
	dirPath = "/Volumes/photoRepository/testingRenameMaster"
	retObj=directory.listFilesSuffixNoDups2( dirPath, "tif" )
	searchList = retObj.getResult()
	############################# get list of photo assets to add metaData from dir - end ###########################

	############################# get size of tif - begin ###########################
	l.info("get size of tif")

	wholeArray = []
	for s in searchList:
		imageRetObj = imageFunc.getInfo (s)	
		base = os.path.basename(s)
		result = imageRetObj.getResult()
		xsize = result['xsize']
		ysize = result['ysize']	
		itemArray = [base, xsize, ysize]
		l.info("base:  " + base)
		l.info("xsize: " + str(xsize))
		l.info("ysize: " + str(ysize))
		dict = {'base': base, 'xsize': xsize, 'ysize': ysize}	
		wholeArray.append(dict)
	############################# get size of tif  - end ###########################

	############################# place size information in database  - begin ###########################			
	l.info("place size information in database")
	for w in wholeArray:
		xsize = w['xsize']
		ysize = w['ysize']	
		base =  w['base']
		
		##get year and seq from name
		retObjProper=photoFunctions.imageProperlyNamed(base)
		if retObjProper.getRetVal() == 0:
			l.info("\tnew format names")
			retObjPart=photoFunctions.photoParts(base, "tif")
		else:
			l.info("\told format names")
			retObjPart=photoFunctions.photoPartsOld2(base, "tif")
		
		result = retObjPart.getResult()
		year=result['year']
		seq=result['seq']
		
		##update database with size info
		retObjConn = photoFunctions.photoConnectMysql2(stage)
		if retObjConn.getRetVal() == 1:
			retObj.setError("photoConnectMysql2:  problem with mysql connection")
			errorFunc = retObjConn.getError()
			error = error + "\n" + errorFunc
			retObj.setError(error)
			retObj.setComment(comments)
		else:
			conn = retObjConn.getResult()
		
		noSuffixName = base.replace(".tif", "")
		
		nameJpg = noSuffixName + ".jpg"
		retObjExists = photoFunctions.photoExistObj2 (conn, nameJpg)
		if retObjExists.getRetVal() == 0:
			retObjInsert = photoFunctions.photoUpdatePixel(conn, noSuffixName, xsize, ysize)
			if retObjConn.getRetVal() == 1:
				retObj.setError("photoInsertPixel:  unexpected error")
				errorFunc = retObjConn.getError()
				error = error + "\n" + errorFunc
				retObj.setError(error)
				retObj.setComment(comments)		
		else:
			retObjInsert = photoFunctions.photoInsertPixel(conn, noSuffixName, xsize, ysize)
			if retObjConn.getRetVal() == 1:
				retObj.setError("photoInsertPixel:  unexpected error")
				errorFunc = retObjConn.getError()
				error = error + "\n" + errorFunc
				retObj.setError(error)
				retObj.setComment(comments)
	############################# place size information in database  - end ###########################
# 				
# 	############################# convert tif to jpg - begin ###########################			
# 	fileFunctions.listToFile(searchList, dirContentsFile)
# 	l.info("################# convert tif to jpg #################")
# 	retObj = photoFunctions.photoFileConvertObj (dirContentsFile, dirContentsFileJpg, baseTemp, badName, badTif, False)	
# 	############################# convert tif to jpg - end ###########################
# 
# 	############################# push jpg to webserver - begin ###########################			
# 	l.info("################# transfer jpg #################")
# 	retObj = photoFunctions.photoTransferObj(stage, baseTemp, sshOutputFile, repositorylist)
# 	############################# push jpg to webserver - end ###########################			
#  		


else:
	l.info("other")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")
	stage="production"

############################# main - end ###########################

end_time = time.time()
timeDict = timeFunc.timeDuration (end_time, start_time)
printHours = timeDict['printHours']
printMins = timeDict['printMins']
printSec = timeDict['seconds']
body = scriptName +" script on " + hostName + " took " + str(printHours) + ":" + str(printMins) + " or " + str(printSec) + " seconds to run"
l.info(body)
# subject = hostName + " " + scriptNameMail
# mailList['message'] = body
# mailList['subject'] = subject
# retObj=shortMessage2 (mailList)
# retVal = retObj.getRetVal()
# if retVal == 1:
# 	print "there is a problem with mail sent to:  " + to_addr
# else:
# 	print "there is a NO problem with mail sent to:  " + to_addr
# print "##############################################################  "
# print ""
# 
# 
# ############################### email photo archivist -- begin ###############################
# to_addr=to_addr2
# body = scriptName +" script on " + hostName + " took " + str(printSec) + " seconds to run \n"
# sizeOfjpgList=len(jpgList)
# body = body + "run time:  hh:mm - " +  str(printHours) + ":" + str(printMins) +"\n"
# body = body + "number of photos processed:  " + str(sizeOfjpgList) +"\n"
# for j in jpgList:
# 	j=j.rstrip()
# 	body = body +"\n" + j
# mailList['to_addr'] = to_addr
# mailList['message'] = body
# retObj=shortMessage2 (mailList)
# retVal = retObj.getRetVal()
# # if retVal == 1:
# # 	print "there is a problem with mail sent to:  " + to_addr
# # else:
# # 	print "there is a NO problem with mail sent to:  " + to_addr
# # print "##############################################################  "
# # print ""
# ############################### email photo archivist -- end ###############################
# ############################### email script developer -- begin ###############################
# to_addr=to_addr3
# body = scriptName +" script on " + hostName + " took " + str(printSec) + " seconds to run \n"
# sizeOfjpgList=len(jpgList)
# body = body + "run time:  hh:mm - " +  str(printHours) + ":" + str(printMins) +"\n"
# body = body + "number of photos processed:  " + str(sizeOfjpgList) +"\n"
# for j in jpgList:
# 	j=j.rstrip()
# 	body = body +"\n" + j
# mailList['to_addr'] = to_addr
# mailList['message'] = body
# retObj=shortMessage2 (mailList)
# retVal = retObj.getRetVal()
# # if retVal == 1:
# # 	print "there is a problem with mail sent to:  " + to_addr
# # else:
# # 	print "there is a NO problem with mail sent to:  " + to_addr
# # print "##############################################################  "
# # print ""
# ############################### email script developer -- end ###############################

fileFunctions.fileDelete(checkfile2)

