#!/usr/bin/python
# try:
#################### import code - begin #################### 
import sys, os
os.chdir('/scripts/photoProcess/')
sys.path.append('lib')
sys.path.append('libPhoto')
from comWrap import *
from directory import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from fileFunctions import *
from fileSize import *
from listFunctions import *
from log import *
from photoFunctions import *
from sigTerm import *
from simpleMail import *
from time import *
from timeFunc import *
from userUtil import *
from systemUtil import *
from programUtil import *
from dictFunc import *
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

logCount = countFilesWithPrefix ("LOG","log_")
mailList = {}
from_addr = "ladmin@" + hostName
mailList['from_addr'] = from_addr
mailList['to_addr'] = to_addr
message = ""
start_time = time()

############## variable assignments - end #####################

l=log()
l.setData(prefix, "myLogger")
l.logDelete("LOG",logCount,logNum)
l.info("loglogNumcount: " + str(logNum))
l.info("log count: " + str(logCount))
l.info("start_time: " + str(start_time))
#if file does not exist =>  used to avoid double running the script
l.info (checkfile)
dirPath = os.path.dirname(checkfile)
dirObj=makeDirectoryObj(dirPath)
retValDir= dirObj.getRetVal()
if retValDir == 1:
	mailList['subject'] = "could not create directory:   ---" + dirPath
	message = "could not create directory:   ---" + dirPath
	l.abort(message)
	mailList['message'] = message
	shortMessage (mailList)
	sys.exit(1)
retDict=createRaceConditionFile(checkfile)
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
	
termHandler(checkfile)
# for i in ['SIGHUP','SIGINT','SIGTERM']:
# 	signum = getattr(signal,i)
# 	signal(signum, termHandler)


userName=getUsername()
l.info ("user name: " + userName)	
total = len(sys.argv)
if total == 3:
	stage=str(sys.argv[1])
	#default production
	#developement
	l.info ("First argument - stage: %s" % str(sys.argv[1]))
	l.info ("Second argument - overwrite: %s" % str(sys.argv[2]))
	stage = str(sys.argv[1])
	overWriteStr = str(sys.argv[2])
	l.info ("overWrite:  " + overWriteStr)

elif total == 2:
	stage=str(sys.argv[1])
	#default production
	#developement
	l.info ("First argument - stage: %s" % str(sys.argv[1]))
	stage = str(sys.argv[1])
	overWrite = False
	overWriteStr = "False"

else:
	stage="production"
	overWrite = False
	overWriteStr = "False"
	l.info ("overWrite:  " + overWriteStr)
	
if overWriteStr != "True":
	overWrite = False
	searchList = listFromFile(localSearchDirectories)
else:
	overWrite  = True
	searchList = listFromFile(overwriteDirectory)
#l.info ("stage:      " + stage)
#l.info ("overWrite:  " + overWriteStr)
#l.info ("overWrite:  " + str(overWrite))
############################# main - begin ###########################

if stage == "production":
	############################# production - begin  ###########################	
	l.info("production")
	os.putenv("MSSUSER", "jshipman")
	os.putenv("MSSHOST", "css-10g")
	key = "functionStatus"
	
	############################# photoFileMod - begin ###########################
	#create list of directory's content to insure photo does not enter more records and
	#lose data
	#input: directory where assets reside
	#output:  none
	l.info("#################photoFileMod#################")
	dirContentsList = []
	#get info from file
	
	for s in searchList:
		term = s.rstrip()
		dirContentsList = glob.glob(term + "/*" ) + dirContentsList
	listToFile(dirContentsList, dirContentsFile)
	
	indexForString = 0
	photoFileMod (l, mailList, dirContentsFile)
	############################# photoFileMod - end ###########################

	############################# correctName - begin ###########################
	#remove badly name files
	#input: directory where assets reside
	#output:  none
	l.info("#################correctName#################")
	dirContentsList = []
	#get info from file

	for s in searchList:
		term = s.rstrip()
		dirContentsList = glob.glob(term + "/*" ) + dirContentsList
	
	for d in dirContentsList:
		base = os.path.basename(d)
		retObjProper = imageProperlyNamed(base)
		retValProper = retObjProper.getRetVal()
		src = d
		dst = badName + "/" + base
		if retValProper == 1:
			l.warn ("improperly named file:  " + base)
			retObjFileMv=fileFunctions.fileMoveObj(src, dst)
			retValFileMv = retObjFileMv.getRetVal()
		
			if retValFileMv == 1:
				error = retObjFileMv.getError()
				l.warn ("error:  " + str(error))
				l.abort("move did not occur:  " + dst + " was NOT created")
				sys.exit(1)
			
	indexForString = 0
	
	for s in searchList:
		term = s.rstrip()
		dirContentsList = glob.glob(term + "/*" ) + dirContentsList
	listToFile(dirContentsList, dirContentsFile)
	
	############################# correctName - end ###########################

	
	################# check if assets already exists - end ###########################
	#input: directory where assets reside
	#output:  file with assets listed

	l.info("##################photoCheckExist#################")
	dirContentsList = []
	dirContentsListNoOverwrite = []
	for s in searchList:
		term = s.rstrip()
		dirContentsList = glob.glob(term + "/*" ) + dirContentsList
	
	if overWrite == False:
		for d in dirContentsList:
			retObjCheck = repoCheck2(d, repositorylist)
			if retObjCheck.getRetVal()== 1:
				error = retObjCheck.getError()
				l.warn (error)
				sys.exit(1)
			found = retObjCheck.getFound()
			
			if int(found) == 1:
				#did not find copy in repository add to list
				#l.info ("did not find copy in repository add to list")
				dirContentsListNoOverwrite.append(d)
			else:
				#found copy; move asset to duplicate directory
				#l.info ("found copy; move asset to duplicate directory")
				src = d
				#l.info ("src:  " + str(src))
				
				base = os.path.basename(d)
				#l.info ("base:  " + str(base))
				dst = duplicate + "/" + base
				#l.info ("dst:  " + str(dst))
				retObjFileMv=fileFunctions.fileMoveObj(src, dst)
				retValFileMv = retObjFileMv.getRetVal()
				
				if retValFileMv == 1:
					error = retObjFileMv.getError()
					l.info ("error:  " + str(error))
					l.abort(dst + " was NOT created")
					sys.exit(1)
		dirContentsList = list(dirContentsListNoOverwrite)
		listToFile(dirContentsList, dirContentsFile)	
	################# check if assets already exists - end ###########################
		
	############################# photoFileConvert - begin ###########################
	#input:	file with assets listed, 
	#		file with jpg assets listed
	#		dir for temp
	#		dir for bad named assets
	#		dir for bad tif assets
	#output:  jpg assets
				
	listToFile(dirContentsList, dirContentsFile)
	l.info("#################photoFileConvert#################")
	indexForString = 1
	retObjConvert = photoFileConvertObj (dirContentsFile, dirContentsFileJpg, baseTemp, badName, badTif)	
	
	retValConvert = retObjConvert.getRetVal()
	if retValConvert == 1:
		subject = scriptName +" script on " + hostName + ":  Problem with photoFileConvertObj \n"
		error = retObjConvert.getError()
		comment = retObjConvert.getComment()
		l.warn( "comments:  " + comment)
		l.warn( "error:  " + error)
		body = "error:  " + error + "/n"
		body = body + "comment:  " + comment + "/n"
		l.info(body)
		mailList['message'] = body
		mailList['subject'] = subject
		retObj=shortMessage2 (mailList)
		sys.exit(1)

	ConvertResult = retObjConvert.getResult()
	newDirContentsList = ConvertResult[0]
	
	dList = listFromFile(dirContentsFileJpg)

	listToFile(newDirContentsList, dirContentsFile)

	dirContentsList = listFromFile(dirContentsFile)


	############################# photoFileConvert - end ###########################

	############################# photoArchive - begin ###########################	
	#input:	file with assets listed, 
	#		file with archive dir names
	#		dir for error
	#		dir for checksums
	#		stage designation
	#output:  files pushed to css
	indexForString = 2
	l.info("#################photoArchive#################")
	retObjArchive = photoArchiveObj(dirContentsFile, archiveFile, baseError, chksumDir, stage)
	retValArchive = retObjArchive.getRetVal()
	if retValArchive == 1:
		subject = scriptName +" script on " + hostName + ":  Problem with photoArchiveObj \n"
		error = retObjArchive.getError()
		comment = retObjArchive.getComment()
		l.warn( "comments:  " + comment)
		l.warn( "error:  " + error)
		body = "error:  " + error + "/n"
		body = body + "comment:  " + comment + "/n"
		l.info(body)
		mailList['message'] = body
		mailList['subject'] = subject
		retObj=shortMessage2 (mailList)
		sys.exit(1)
	############################# photoArchive - end ###########################	

	############################# photoSort - begin ###########################	
	#input:	file with assets listed, 
	#		dict of variables
	#		dir for checksums
	#		stage designation
	#output:  move tif to respective location in repository
	l.info("#################photoSort#################")
	resposDict={}
	resposDict['repoProcess'] = repositoryProcess
	resposDict['repoRaw']  = repositoryRaw
 	indexForString = 3
	retObjSort = photoSortObj (dirContentsFile, resposDict, chksumDir, stage)
	retValSort = retObjSort.getRetVal()
	if retValSort == 1:
		subject = scriptName +" script on " + hostName + ":  Problem with retObjSort \n"
		error = retObjSort.getError()
		comment = retObjSort.getComment()
		l.warn( "comments:  " + comment)
		l.warn( "error:  " + error)
		body = "error:  " + error + "/n"
		body = body + "comment:  " + comment + "/n"
		l.info(body)
		mailList['message'] = body
		mailList['subject'] = subject
		retObj=shortMessage2 (mailList)
		sys.exit(1)
	############################# photoSort - end ###########################	

	############################# photoTransfer - begin ###########################	
	#input:	file with assets listed, 
	#		stage designation
	#		dir for temp
	#		file for ssh outputs
	#		file for cd name
	#		file for list of repository locations
	#output:  place jpg assets on webserver
	l.info("#################photoTransfer#################")	
	if fileExist(cdNameFile):
		fileDelete (cdNameFile)
	else:
		fileCreate(cdNameFile)	
	indexForString = 4
	retObjTransfer=photoTransferObj(stage, baseTemp, sshOutputFile, repositorylist)
	retValTransfer = retObjTransfer.getRetVal()
	if retValTransfer == 1:
		subject = scriptName +" script on " + hostName + ":  Problem with photoTransferObj \n"
		error = retObjTransfer.getError()
		comment = retObjTransfer.getComment()
		l.warn( "comments:  " + comment)
		l.warn( "error:  " + error)
		body = "error:  " + error + "/n"
		body = body + "comment:  " + comment + "/n"
		l.info(body)
		mailList['message'] = body
		mailList['subject'] = subject
		retObj=shortMessage2 (mailList)
		sys.exit(1)	
	############################# photoTransfer - end ###########################			
	############################# photoMysql - begin ###########################
	#input:	file with jpg listed, 
	#		stage designation
	#		file for cd name
	#		file for list of repository locations
	#output: enter changes into database
	l.info("#################photoMysql#################")				
	indexForString = 5
 	retObjMysql=photoMysqlObj(dirContentsFileJpg, stage, cdNameFile,  repositorylist)
	retValMysql = retObjMysql.getRetVal()
	if retValMysql == 1:
		subject = scriptName +" script on " + hostName + ":  Problem with photoMysqlObj \n"
		error = retObjMysql.getError()
		comment = retObjMysql.getComment()
		body = "error:  " + error + "/n"
		body = body + "comment:  " + comment + "/n"
		l.warn( "comments:  " + comment)
		l.warn( "error:  " + error)
		mailList['message'] = body
		mailList['subject'] = subject
		retObj=shortMessage2 (mailList)
		sys.exit(1)
	else:
		l.info( "comments:  " + comment)
	jpgList = retObjMysql.getResult()
	############################# photoMysql - end ###########################
	############################# production - end ###########################				
	
elif stage == "development":
	############################# development - begin ##########################	
	l.info("development")

	############################# development - end ##########################	

elif stage == "other":
	############################# other - begin  ###########################	
	l.info("other")
	
	############################# other - end ################################	

end_time = time()
timeDict = timeDuration (end_time, start_time)
printHours = timeDict['printHours']
printMins = timeDict['printMins']
printSec = timeDict['seconds']

if stage != "production":
	body = scriptName +" script on " + hostName + " took " + str(printHours) + ":" + str(printMins) + " or " + str(printSec) + " seconds to run"
	l.info(body)
	subject = hostName + " " + scriptNameMail
	mailList['message'] = body
	mailList['subject'] = subject
	retObj=shortMessage2 (mailList)
	retVal = retObj.getRetVal()
	if retVal == 1:
		print "there is a problem with mail sent to:  " + to_addr
	else:
		print "there is a NO problem with mail sent to:  " + to_addr
	print "##############################################################  "
	print ""
	############################### email photo archivist -- begin ###############################
	to_addr=to_addr2
	body = scriptName +" script on " + hostName + " took " + str(printSec) + " seconds to run \n"
	sizeOfjpgList=len(jpgList)
	body = body + "run time:  hh:mm - " +  str(printHours) + ":" + str(printMins) +"\n"
	body = body + "number of photos processed:  " + str(sizeOfjpgList) +"\n"
	for j in jpgList:
		j=j.rstrip()
		body = body +"\n" + j
	mailList['to_addr'] = to_addr
	mailList['message'] = body
	retObj=shortMessage2 (mailList)
	retVal = retObj.getRetVal()
	if retVal == 1:
		print "there is a problem with mail sent to:  " + to_addr
	else:
		print "there is a NO problem with mail sent to:  " + to_addr
	print "##############################################################  "
	print ""
	############################### email photo archivist -- end ###############################
	############################### email script developer -- begin ###############################
	to_addr=to_addr3
	body = scriptName +" script on " + hostName + " took " + str(printSec) + " seconds to run \n"
	sizeOfjpgList=len(jpgList)
	body = body + "run time:  hh:mm - " +  str(printHours) + ":" + str(printMins) +"\n"
	body = body + "number of photos processed:  " + str(sizeOfjpgList) +"\n"
	for j in jpgList:
		j=j.rstrip()
		body = body +"\n" + j
	mailList['to_addr'] = to_addr
	mailList['message'] = body
	retObj=shortMessage2 (mailList)
	retVal = retObj.getRetVal()
	if retVal == 1:
		print "there is a problem with mail sent to:  " + to_addr
	else:
		print "there is a NO problem with mail sent to:  " + to_addr
	print "##############################################################  "
	print ""
	############################### email script developer -- end ###############################

fileDelete(checkfile)

############################# main - end ###########################
