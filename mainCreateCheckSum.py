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
import  fileFunctions
import  fileSize
import  listFunctions
import  log
import  photoFunctions
import  sigTerm
import  simpleMail
import  time
import  timeFunc
import  userUtil
import  systemUtil
import  programUtil
import  dictFunc
import pwd
import signal
import socket 
import glob
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
body = ""
start_time = time.time()

############## variable assignments - end #####################

l=log.log()
l.setData(prefix, "myLogger")
l.logDelete("LOG",logCount,logNum)
l.info("loglogNumcount: " + str(logNum))
l.info("log count: " + str(logCount))
l.info("start_time: " + str(start_time))
#if file does not exist =>  used to avoid double running the script
l.info (checkfile)
dirPath = os.path.dirname(checkfile)
dirObj=directory.makeDirectoryObj(dirPath)
retValDir= dirObj.getRetVal()
if retValDir == 1:
	mailList['subject'] = "could not create directory:   ---" + dirPath
	message = "could not create directory:   ---" + dirPath
	l.abort(message)
	mailList['message'] = message
	shortMessage (mailList)
	sys.exit(1)
retDict=systemUtil.createRaceConditionFile(checkfile)
retVal=int(retDict['retVal'])
comment=retDict['comment']
if retVal == 1:
	mailList['subject'] = "double run script fault - " + scriptNameMail + ":  --- " + checkfile +" exists ---"
	message = "double run script fault - " + scriptNameMail  + ":  --- "+ checkfile + " exists --- \n"
	message = message + comment
	l.abort(message)
	mailList['message'] = message
	shortMessage (mailList)
	sys.exit(1)
	
sigTerm.termHandler(checkfile)
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
	l.info ("First argument - stage: %s" % str(sys.argv[1]))
	stage = str(sys.argv[1])
	l.info (stage)
else:
	stage="production"
	l.info (stage)
	

############################# main - begin ###########################

if stage == "production":
	############################# production - begin  ###########################	
	l.info("production")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")
	key = "functionStatus"
	
		
	
elif stage == "development":
	############################# production - begin  ###########################	
	l.info("development")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")
	key = "functionStatus"
	resultListAll = []
	resultListAllSuffix = []
	rList=listFunctions.listFromFile(repositorylist)
# 	for r in rList:
# 		print "r:  " + r
# 		items=r.split("#" )
# 		dirPath = items[1] + "/"
# 		print "dirPath:  " +  dirPath
# 		retObj=directory.listFilesSuffixSortCreate( dirPath, "tif.ck" )
# 		retVal = retObj.getRetVal()
# 		if retVal == 0:
# 			resultList = retObj.getResult()
# 			resultListAllSuffix = resultListAllSuffix + resultList
# 	for r in resultListAllSuffix:
# 		print "tif.ck.  files:  " + r
# 		if fileFunctions.fileExist(r):
# 			os.unlink(r)	
			
	##if file does not exist chksumCheckFileAll file
	if not os.path.exists(chksumCheckFileAll):
		rList=listFunctions.listFromFile(repositorylist)
		for r in rList:
			print "r:  " + r
			items=r.split("#" )
			dirPath = items[1] + "/"
			print "dirPath:  " +  dirPath
			retObj=directory.listFilesSuffixSortCreate( dirPath, "tif" )

			retVal = retObj.getRetVal()
			if retVal == 0:
				resultList = retObj.getResult()
				resultListAll = resultListAll + resultList
			else:
				print "problem with listFilesSuffixSortCreate"
		fileFunctions.listToFile(resultListAll, chksumCheckFileAll)
	
# 	resultListAll = glob.glob('/Volumes/photoRepository/source/1921/pic/*.tif')
# 	for g in resultListAll:
# 		print "g:  " + g
	fileFunctions.listToFile(resultListAll, chksumCheckFileAll)		
	checkAmount = len(resultListAll)
	count = 0
	for t in resultListAll:
		count = count + 1
		print "count:  " + str(count) + " out of " + str(checkAmount)
		print "\tAsset:  " + t
		
		fileName = t.replace(".tif", ".ck")
		fileName = fileName.replace("/pic/", "/ck/")
		delFile1 = fileName
		if fileFunctions.fileExist(delFile1):
			os.unlink(delFile1)
		
		delFile2 = t.replace(".tif", ".tif.ck")
		delFile2 = delFile2.replace("/pic/", "/ck/")
		if fileFunctions.fileExist(delFile2):
			os.unlink(delFile2)

		print "\tCk:  " + fileName
 		retObjCheckSum = comWrap.checkSum(t)
 		retVal = retObjCheckSum.getRetVal()
 		if retVal == 0:
 			stdOutCheckSum = retObjCheckSum.getStdout()
 			checkSumItems=stdOutCheckSum.split()
 			print "\t\t\tstdOutCheckSum:  " + stdOutCheckSum
 			retObjWrite = fileFunctions.fileCreateWrite ( fileName, stdOutCheckSum)	
 			retVal = retObjWrite.getRetVal()
 			if retVal == 0:
 				print "\tCreated Checksum:  " + fileName
 			else:
 				print "\tCould not created Checksum:  " + fileName
 				body = body  + "\nCould not created Checksum:  " + fileName


else:
	############################# other - begin  ###########################	
	l.info("other")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")
	key = "functionStatus"
	


end_time = time.time()
timeDict = timeFunc.timeDuration (end_time, start_time)
printHours = timeDict['printHours']
printMins = timeDict['printMins']
printSec = timeDict['seconds']

if stage != "production":
	############################### email script developer -- begin ###############################
	to_addr=to_addr3
	subject =  "CreateCheckSum script on " + hostName + " took " + str(printSec) + " seconds to run \n"
	topic = 	"CreateCheckSum script\n"	
	runtime =  "run time:  hh:mm - " +  str(printHours) + ":" + str(printMins) +"\n"
	body = runtime + topic + body
	mailList['subject'] = subject
	mailList['to_addr'] = to_addr
	mailList['message'] = body
	retObj=simpleMail.shortMessage2 (mailList)
	retVal = retObj.getRetVal()
	if retVal == 1:
		print "there is a problem with mail sent to:  " + to_addr
	else:
		print "there is a NO problem with mail sent to:  " + to_addr
	print "##############################################################  "
	print ""
	############################### email script developer -- end ###############################

fileFunctions.fileDelete(checkfile)

############################# main - end ###########################
