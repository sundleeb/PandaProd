from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from subprocess import call, check_output

import sys, os
from re import findall

### CHECK THAT CMS env and it is correct
pwd = os.environ['PWD']
if 'CMSSW_VERSION' not in os.environ:
		print "Do cmsenv!"
		exit(0)
version = os.environ['CMSSW_VERSION']
ok = False
for dir in reversed(pwd.split('/')):
		if version == dir : 
				ok = True
				break
if not ok:
		print "Do (redo) cmsenv (2) !"
		exit(0)


config = config()

config.General.requestName = 'PandaProd_request_XXX'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = False

## JobType
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'prod.py'
#config.JobType.pyCfgParams=['config=Summer16']
config.JobType.pyCfgParams=['config=03Feb2017']
config.JobType.outputFiles = ['panda.root']

### DATA configuration
#config.Data.inputDataset = '/WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'
config.Data.inputDBS = 'global'
config.Data.ignoreLocality = True

config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 10
config.Data.totalUnits = -1

config.Site.storageSite = 'T3_US_FNALLPC' 
config.Data.outLFNDirBase = '/store/group/lpcmetx/pandaprod/80X-v1' #Please change USER to yours
config.Data.publication = False
config.Data.outputDatasetTag ='PandA'

config.Site.whitelist = ['T3_US_FNALLPC']
config.Site.ignoreGlobalBlacklist = True

if __name__ == '__main__':

	from CRABAPI.RawCommand import crabCommand
	from CRABClient.ClientExceptions import ClientException
	from httplib import HTTPException

	# We want to put all the CRAB project directories from the tasks we submit here into one common directory.
	# That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).
	config.General.workArea = 'Submission_mc3'

	def submit(config):
		### for some reason only the first dataset is submitted correctly, work around
		if len(sys.argv) ==1:
			## book the command and run python
			cmd = "python " + sys.argv[0] + " '" + config.General.requestName + "'"
			#print "calling: "+cmd
			call(cmd,shell=True)
			return
		if len(sys.argv) > 1:
			## if it is not in the request try the next
			if sys.argv[1] !=	config.General.requestName: return
			###
			#print "--- Submitting " + "\033[01;32m" + config.Data.inputDataset.split('/')[1] + "\033[00m+ " ---"
			config.Data.outputDatasetTag = config.General.requestName
			try:
				crabCommand('submit', config = config)
			except HTTPException as hte:
				print "Failed submitting task: %s" % (hte.headers)
			except ClientException as cle:
				print "Failed submitting task: %s" % (cle)

	def setdata(value="True"):
		if value=='True':
			#config.Data.splitting = 'LumiBased'
			#config.Data.splitting = 'FileBased'
			config.Data.splitting = 'EventAwareLumiBased'
			#config.Data.lumiMask=None
                        url = "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/"
			config.Data.lumiMask = url + "Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
		else:
			config.Data.lumiMask = None
			config.Data.splitting = 'FileBased'

		for idx,par in enumerate(config.JobType.pyCfgParams):
			if "isData" in par:
				config.JobType.pyCfgParams[idx] = "isData=" + value
				return 

	def setsignal(value):
		for idx,par in enumerate(config.JobType.pyCfgParams):
			if "isSignal" in par:
				config.JobType.pyCfgParams[idx] = "isSignal=" + value
				return 


        def submitList(l):
                for ll in l:
                        split = ll.split('/')
                        if split[1] == "uscms_data":
                                with open(ll) as f:
                                 for line in f:
                                     Line = line.strip(' \t\n\r')
                                     config.Data.inputDataset = Line
                                     split_line = line.split('/')
                                     if 'ext' in split_line[-2]:
                                             ext = findall('ext[0-9]+',split_line[-2])
                                             if len(ext)>0:
                                                     config.General.requestName = split_line[1] + '_' + ext[0]
                                             else:
                                                     config.General.requestName = split_line[1]
                                     else:
                                             #private file
                                             #config.General.requestName = split_line[1]+'_'+split_line[2]
                                             config.General.requestName = split_line[1]
                                             #config.General.requestName = split_line[-1].split('.')[0]
                                     submit(config)

                        else:
                                config.Data.inputDataset = ll
                        if split[-1]=='MINIAOD':
                                config.General.requestName = split[1]+'_'+split[2]
                        elif 'ext' in split[-2]:
                                ext = findall('ext[0-9]+',split[-2])
                                if len(ext)>0:
                                        config.General.requestName = split[1] + '_' + ext[0]
                                else:
                                        config.General.requestName = split[1]
                        else:
                                #private file
                                #config.General.requestName = split[1]
                                config.General.requestName = split[-1].split('.')[0]
                        #submit(config)

	#############################################################################################
	## From now on that's what users should modify: this is the a-la-CRAB2 configuration part. ##
	#############################################################################################
 
                         
        '''                 
       ###################################################
        setdata("False")
        ###################################################
        config.Data.splitting = 'FileBased'
        config.Data.unitsPerJob = 1
        
        setsignal("False")
        submitList([
                        '/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/DYJetsToLL_HT.txt',
        ])

        '''                 
       ###################################################
        setdata("False")
        ###################################################
        config.Data.splitting = 'FileBased'
        config.Data.unitsPerJob = 1
        
        setsignal("False")
        submitList([
                        '/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/DYJetsToLL_HT.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/Diboson.txt',
                       # '/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/GJets_HT.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/QCD.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/Top.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/WJetsToLNu_HT.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/Wminus.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/VBFHtoBB.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/ttHtobb.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/mc/80X/GluGLuHToBB.txt',
        ])

        '''                 
        ###################################################
        setdata("True")
        ###################################################
        config.Data.unitsPerJob = 20000

        submitList([
                        '/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/data/80X/MET.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/data/80X/SingleElectron.txt',
                        #'/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/data/80X/SingleMuon.txt',
                       # '/uscms_data/d3/naina25/Panda_2018/Panda_Prod_2016/CMSSW_8_0_29/src/PandaProd/Producer/cfg/file_lists2016/data/80X/SinglePhoton.txt',
                        ])
            
        '''                 
        '''                 
	###################################################
	setdata("True")
	###################################################
	config.Data.unitsPerJob = 22000

	submitList([
                      '/MET/Run2017B-PromptReco-v2/MINIAOD',
		      '/MET/Run2017B-PromptReco-v1/MINIAOD',
		      '/MET/Run2017C-PromptReco-v3/MINIAOD',
		      '/MET/Run2017C-PromptReco-v2/MINIAOD',
		      '/MET/Run2017C-PromptReco-v1/MINIAOD',
		      '/MET/Run2017D-PromptReco-v1/MINIAOD',
		      '/MET/Run2017F-PromptReco-v1/MINIAOD',
		      '/MET/Run2017A-PromptReco-v3/MINIAOD',
		      '/MET/Run2017A-PromptReco-v2/MINIAOD',
		      '/MET/Run2017A-PromptReco-v1/MINIAOD',
			])
	
        ''' 	
        ''' 	
	###################################################
	setdata("True")
	###################################################
	config.Data.unitsPerJob = 1000

	submitList([
                      '/MET/Run2017A-PromptReco-v3/MINIAOD'
			])
	
	'''
	'''
	
	config.Data.unitsPerJob = 30
	
	submitList([
                     '/SingleElectron/Run2017A-PromptReco-v3/MINIAOD'
			])
	'''
	'''
	
	config.Data.unitsPerJob = 80
	
	submitList([
                     '/SinglePhoton/Run2017A-PromptReco-v3/MINIAOD'
		])
	
        '''
	###################################################
	###################################################
	
	'''
	###################################################
	setdata("False")
	config.Data.splitting = 'FileBased'
	config.Data.unitsPerJob = 1
	
	setsignal("False")
	submitList([
                        '/WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM' 
	])
	
        '''
        '''
	setdata("False")
	config.Data.splitting = 'FileBased'
	config.Data.unitsPerJob = 1
	
	setsignal("True")
	submitList([
		])
        '''
        '''
