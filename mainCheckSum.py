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
# except ImportError:
# 	l.info("missing modules for main.py"
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
l.info (checkfileChkSum)
dirPath = os.path.dirname(checkfileChkSum)
dirObj=directory.makeDirectoryObj(dirPath)
retValDir= dirObj.getRetVal()
if retValDir == 1:
	mailList['subject'] = "could not create directory:   ---" + dirPath
	message = "could not create directory:   ---" + dirPath
	l.abort(message)
	mailList['message'] = message
	shortMessage (mailList)
	sys.exit(1)
retDict=systemUtil.createRaceConditionFile(checkfileChkSum)
retVal=int(retDict['retVal'])
comment=retDict['comment']
if retVal == 1:
	mailList['subject'] = "double run script fault - " + scriptNameMail + ":  --- " + checkfileChkSum +" exists ---"
	message = "double run script fault - " + scriptNameMail  + ":  --- "+ checkfileChkSum + " exists --- \n"
	message = message + comment
	l.abort(message)
	mailList['message'] = message
	shortMessage (mailList)
	sys.exit(1)
	
sigTerm.termHandler(checkfileChkSum)
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
	resultListAll = []
	l.info("###Create List of all tif####")
	l.info("###if file does not exist create file####")
	if not os.path.exists(chksumCheckFileAll):
		rList=listFunctions.listFromFile(repositorylist)
		for r in rList:
			l.info("\tr:  " + r)
			items=r.split("#" )
			dirPath = items[1] + "/"
			l.info("\tdirPath:  " +  dirPath)
			retObj=directory.listFilesSuffixSortCreate( dirPath, "tif" )

			retVal = retObj.getRetVal()
			if retVal == 0:
				resultList = retObj.getResult()
				resultListAll = resultListAll + resultList
			else:
				l.info("\tproblem with listFilesSuffixSortCreate")
		fileFunctions.listToFile(resultListAll, chksumCheckFileAll)
	
	l.info("#####if contents of file is empty, create new file with contents####")
	resultListAll=listFunctions.listFromFile(chksumCheckFileAll)
	if len(resultListAll) == 0:
		rList=listFunctions.listFromFile(repositorylist)
		for r in rList:
			l.info("\tr:  " + r)
			items=r.split("#" )
			dirPath = items[1] + "/"
			l.info("\tdirPath:  " +  dirPath)
			retObj=directory.listFilesSuffixSortCreate( dirPath, "tif" )

			retVal = retObj.getRetVal()
			if retVal == 0:
				resultList = retObj.getResult()
				resultListAll = resultListAll + resultList
			else:
				l.info("problem with listFilesSuffixSortCreate")
		fileFunctions.listToFile(resultListAll, chksumCheckFileAll)
		
	resultCheckGood = []
	resultCheckBad = []
	checkAmount = 10000
	top1000 = resultListAll[:checkAmount]
	count = 0
	for t in top1000:
		count = count + 1
		l.info("count:  " + str(count) + " out of " + str(checkAmount))
		l.info("\tt:  " + t)

		fileName = t.replace(".tif", ".ck")
		fileName = fileName.replace("/pic/", "/ck/")
		l.info("\t\tcheckSum fileName:  " + fileName)
		retObjCatFile = comWrap.catFile(fileName)
		stdOutCatFile = retObjCatFile.getStdout()
		l.info("\t\tCat of ck file")
		l.info("\t\t\tstdOutCatFile:  " + stdOutCatFile)
		
		retVal = retObjCatFile.getRetVal()
		if retVal == 0:
			l.info("\t\tCheck sum of existing file")
			stdOutCatFile = retObjCatFile.getStdout()
			catItems=stdOutCatFile.split()
						
			l.info("\t\t\tfileName:  " + t)
			retObjCheckSum = comWrap.checkSum(t)
			stdOutCheckSum = retObjCheckSum.getStdout()
			checkSumItems=stdOutCheckSum.split()
			l.info("\t\t\tstdOutCheckSum:  " + stdOutCheckSum)
			
			
			#test first two items 
			if ((checkSumItems[0] ==  catItems[0]) and (checkSumItems[1] ==  catItems[1])):
				l.info("\t\t\t\tFile and checksum resolve")
				resultCheckGood.append(t)
			else:
				l.warn("\t\t\t\tFile and checksum DO NOT resolve")
				body = body + "\n" + fileName
				resultCheckBad.append(t)
			resultListAll.remove(t)	
			l.info("")
			fileFunctions.listToFile(resultCheckGood, resultCheckGoodFile)
			fileFunctions.listToFile(resultCheckBad, resultCheckBadFile)
			fileFunctions.listToFile(resultListAll, chksumCheckFileAll)
		else:
			l.warn("problem with checkSum")	
		
elif stage == "development":
	############################# development - begin  ###########################	
	l.info("development")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")
	key = "functionStatus"
	resultListAll = []
	l.info("###Create List of all tif####")
	l.info("###if file does not exist create file####")
	if not os.path.exists(chksumCheckFileAll):
		rList=listFunctions.listFromFile(repositorylist)
		for r in rList:
			l.info("\tr:  " + r)
			items=r.split("#" )
			dirPath = items[1] + "/"
			l.info("\tdirPath:  " +  dirPath)
			retObj=directory.listFilesSuffixSortCreate( dirPath, "tif" )

			retVal = retObj.getRetVal()
			if retVal == 0:
				resultList = retObj.getResult()
				resultListAll = resultListAll + resultList
			else:
				l.info("\tproblem with listFilesSuffixSortCreate")
		fileFunctions.listToFile(resultListAll, chksumCheckFileAll)
	
	l.info("#####if contents of file is empty, create new file with contents####")
	resultListAll=listFunctions.listFromFile(chksumCheckFileAll)
	if len(resultListAll) == 0:
		rList=listFunctions.listFromFile(repositorylist)
		for r in rList:
			l.info("\tr:  " + r)
			items=r.split("#" )
			dirPath = items[1] + "/"
			l.info("\tdirPath:  " +  dirPath)
			retObj=directory.listFilesSuffixSortCreate( dirPath, "tif" )

			retVal = retObj.getRetVal()
			if retVal == 0:
				resultList = retObj.getResult()
				resultListAll = resultListAll + resultList
			else:
				l.info("problem with listFilesSuffixSortCreate")
		fileFunctions.listToFile(resultListAll, chksumCheckFileAll)
		
	resultCheckGood = []
	resultCheckBad = []
	checkAmount = 10
	top1000 = resultListAll[:checkAmount]
	count = 0
	for t in top1000:
		count = count + 1
		l.info("count:  " + str(count) + " out of " + str(checkAmount))
		l.info("\tt:  " + t)

		fileName = t.replace(".tif", ".ck")
		fileName = fileName.replace("/pic/", "/ck/")
		l.info("\t\tcheckSum fileName:  " + fileName)
		retObjCatFile = comWrap.catFile(fileName)
		stdOutCatFile = retObjCatFile.getStdout()
		l.info("\t\tCat of ck file")
		l.info("\t\t\tstdOutCatFile:  " + stdOutCatFile)
		
		retVal = retObjCatFile.getRetVal()
		if retVal == 0:
			l.info("\t\tCheck sum of existing file")
			stdOutCatFile = retObjCatFile.getStdout()
			catItems=stdOutCatFile.split()
						
			l.info("\t\t\tfileName:  " + t)
			retObjCheckSum = comWrap.checkSum(t)
			stdOutCheckSum = retObjCheckSum.getStdout()
			checkSumItems=stdOutCheckSum.split()
			l.info("\t\t\tstdOutCheckSum:  " + stdOutCheckSum)
			
			
			#test first two items 
			if ((checkSumItems[0] ==  catItems[0]) and (checkSumItems[1] ==  catItems[1])):
				l.info("\t\t\t\tFile and checksum resolve")
				resultCheckGood.append(t)
			else:
				l.warn("\t\t\t\tFile and checksum DO NOT resolve")
				body = body + "\n" + fileName
				resultCheckBad.append(t)
			resultListAll.remove(t)	
			l.info("")
			fileFunctions.listToFile(resultCheckGood, resultCheckGoodFile)
			fileFunctions.listToFile(resultCheckBad, resultCheckBadFile)
			fileFunctions.listToFile(resultListAll, chksumCheckFileAll)
		else:
			l.warn("problem with checkSum")

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

if stage == "production":
	############################### email script developer -- begin ###############################
	to_addr=to_addr3
	subject =  "CheckSum script on " + hostName + " took " + str(printSec) + " seconds to run \n"
	topicBad = 	"Files that do not resolve and need to be checked\n"
	topicGood = "All files resolved\n"	
	runtime =  "run time:  hh:mm - " +  str(printHours) + ":" + str(printMins) +"\n"
	if len(resultCheckBad) == 0:
		body = runtime + topicBad + body
	else:
		body = runtime + topicGood
	mailList['subject'] = subject
	mailList['to_addr'] = to_addr
	mailList['message'] = body
	retObj=simpleMail.shortMessage2 (mailList)
	retVal = retObj.getRetVal()
	if retVal == 1:
		l.info("there is a problem with mail sent to:  " + to_addr)
	else:
		l.info("there is a NO problem with mail sent to:  " + to_addr)
	l.info("##############################################################  ")
	l.info("")
	############################### email script developer -- end ###############################

fileFunctions.fileDelete(checkfileChkSum)

############################# main - end ###########################
