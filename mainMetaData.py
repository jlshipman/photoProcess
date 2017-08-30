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
import systemUtil
import programUtil
import dictFunc
import pwd
import signal
import socket 

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
	l.info("########################################################################") 
	l.info("get list of photo assets to add metaData from dir")
	
	dirPath = "/Volumes/photoRepository/testingMiss"
	retObj=directory.listFilesSuffixNoDups2( dirPath, "tif" )
	searchList = retObj.getResult()
	############################# get list of photo assets to add metaData from dir - end ###########################
		
	############################# create tif and jpg list - begin ###########################
	l.info("########################################################################") 
	l.info("create tif and jpg list")
	tifList = []
	jpgList = []
	for s in searchList:
		term = s.rstrip()
		baseAsset = term.split('.')
		tifAsset = baseAsset[0] + '.tif'
		jpgAsset = baseAsset[0] + '.jpg'
		tifList.append(tifAsset)
		jpgList.append(jpgAsset)
		l.info("\t" +  tifAsset)
	############################# create tif and jpg list - end ###########################

 	############################ add metadata to assets assets from database - begin ###########################				
	l.info("########################################################################") 
	l.info("add metadata to assets from database ")
	retObjConn = photoFunctions.photoConnectMysql2(stage)
	conn = retObjConn.getResult()
	for t in tifList:
		l.info ("\t" + t)
		retObjMeta = photoFunctions.setImageMetaData (conn, t, metaDataFile)
		l.info ("\t\t" + t)
		#print "return value:  " + str(retObjMeta.getRetVal())
		if retObjMeta.getRetVal() == 1:
			error = retObjMeta.getError()
			l.warn("\t\tasset:  " + t + " \n"  + error)
			sys.exit(1)
 	############################ add metadata to assets assets from database - end ###########################

 
elif stage == "development":
	l.info("development")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")
	key = "functionStatus"

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

