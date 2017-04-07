import CorrectionManager
import BeamBeam_Corr
import LengthScale_Corr
import Ghosts_Corr
import Satellites_Corr
import ROOT as r
import sys
import json
import math

from inputDataReaderII import * 
from vdmUtilities import showAvailableCorrs

###################
#check for missed data
def checkScanpointList(vdMData):
    
    BCIDListLength=len(vdMData.usedCollidingBunches)
    SPListLength=vdMData.nSP
    SPList=vdMData.displacement
    missedData="BCID:list of missed scanpoints\n"
    
    missedSP=[[] for a in range(BCIDListLength)]
    for i, bx in enumerate(vdMData.usedCollidingBunches):
        for j, sp in enumerate(SPList):
            if sp not in vdMData.spPerBX[bx]:
                missedSP[i].append(j+1)

    for i, bx in enumerate(vdMData.usedCollidingBunches):
        length=len(missedSP[i])
        if length!=0:
            BCID=str(bx)
            missedSPList=str(missedSP[i])
            missedData=missedData+BCID+":"+missedSPList+"\n"

    return missedData

###########################
def doMakeGraphsFile(ConfigInfo):

    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    Luminometer = str(ConfigInfo['Luminometer'])
    inputScanFile = str(ConfigInfo['InputScanFile'])
    inputBeamCurrentFile = str(ConfigInfo['InputBeamCurrentFile'])
    inputLuminometerData = str(ConfigInfo['InputLuminometerData'])
    corrName = ConfigInfo['Corr']

# For scan 1, which is always there as long as there are any scans at all:

    inData1 = vdmInputData(1)

    inData1.GetScanInfo(AnalysisDir + '/'+ inputScanFile)
#inData1.PrintScanInfo()

    inData1.GetBeamCurrentsInfo(AnalysisDir + '/' + inputBeamCurrentFile)
#    inData1.PrintBeamCurrentsInfo()

    inData1.GetLuminometerData(AnalysisDir + '/' + inputLuminometerData)
#    inData1.PrintLuminometerData()

    Fill = inData1.fill
    
    inData = []
    inData.append(inData1)

# For the remaining scans:

    for i in range(1,len(inData1.scanNamesAll)):
        inDataNext = vdmInputData(i+1)
        inDataNext.GetScanInfo(AnalysisDir + '/' + inputScanFile)
        inDataNext.GetBeamCurrentsInfo(AnalysisDir + '/' + inputBeamCurrentFile)
        inDataNext.GetLuminometerData(AnalysisDir + '/' + inputLuminometerData)
        inData.append(inDataNext)

#Check for missing data
    missedDataInfo="Information on missed data\n"
    if "BeamBeam" in corrName:
        missedDataInfo=missedDataInfo+"BeamBeam has been applied: Only BCIDs with complete scanpoint lists are considered\n See BeamBeam_.log for the list of excluded BCID\n"
    else:
        missedDataInfo=missedDataInfo+"BeamBeam has not been applied\n\n"

    for entry in inData:
        scanNumber = entry.scanNumber
        prefix = ''
        if 'X' in entry.scanName:
            prefix = str(scanNumber) +'_X'
        if 'Y' in entry.scanName:
            prefix = str(scanNumber)+'_Y'
        missedDataInfo=missedDataInfo+"Scan_"+prefix+"\n"
        missedSPList=checkScanpointList(entry)
        missedDataInfo=missedDataInfo+missedSPList+"\n"

# Apply corrections
# Note that calibrating SumFBCT to DCCT is done in makeBeamCurrentFile.py if calibration flag in config file is set to true

    showAvailableCorrs()

    availableCorr = CorrectionManager.get_plugins(CorrectionManager.CorrectionProvider)

    print "The following corrections will be applied, in order: "
    for i, entry in enumerate(corrName):
        print "Corr #"+str(i+1)  + ": " +entry

    corrFull = ''

    for entry in corrName:

        print "Now applying correction: ", entry

# Check whether correction requested in config json actually exists

        key = entry+'_Corr'
        if key in availableCorr:
            corrector= availableCorr[entry+'_Corr']()        
        else:
            if not entry == "noCorr":
                print "Correction " + entry + " requested via json file does not exist, ignore."
            continue

# Read Corr config in here

        corrValueFile = AnalysisDir + '/corr/'+ entry + '_' + Fill +'.pkl' 
        if entry == "BeamBeam":
            corrValueFile = AnalysisDir + '/corr/'+ entry + '_' +Luminometer + '_' + Fill +'.pkl' 
            
        corrector.doCorr(inData, corrValueFile)

        corrFull = corrFull + '_' + entry 

# check if any corrections are to be applied at all, if yes, define corr description string accordingly
# if no use "noCorr"

    import os

# empty strings are false, so if no corrections are to be applied, use noCorr as corr descriptor
    if  not corrFull:
        corrFull = "_noCorr"


# Now fill graphs for all scans
# Counting of scans starts with 1
    graphsListAll = {'Scan_'+ str(n+1):{} for n in range(len(inData))} 

    missedDataInfo=missedDataInfo+"Excluded BCIDs with too short scanpoint list:\n"

    for entry in inData:
    
        scanNumber = entry.scanNumber
        print "Now at Scan number ", scanNumber
        nBX = len(entry.usedCollidingBunches)
        prefix = ''
        if 'X' in entry.scanName:
            prefix = str(scanNumber) +'_X_'
        if 'Y' in entry.scanName:
            prefix = str(scanNumber)+'_Y_'

        omittedBXList=[]
    # convert for TGraph
        from array import array

        graphsList = {}

        for i, bx in enumerate(entry.usedCollidingBunches):
# BCIDs written at small number of SP are omitted (the list of short omitted bunches is added to log)            
# to avoid problems in vdmFitter: the number of SP should exceed the minimal number of freedom degrees for fitting

             if len(entry.spPerBX[bx])>5:
                coord=entry.spPerBX[bx]
                coorde = [0.0 for a in coord] 
                coord = array("d",coord)
                coorde = array("d", coorde)
                currProduct = [ a*b/1e22 for a,b in zip(entry.avrgFbctB1PerBX[bx],entry.avrgFbctB2PerBX[bx])]
                if len(entry.spPerBX[bx])!=len(entry.splumiPerBX[bx]):
                    print "Attention: bx=", bx, ", number of scanpoints for lumi and currents do not match, normalization is not correct"         
                lumi = [a/b for a,b in zip(entry.lumiPerBX[bx],currProduct)]
                lumie = [a/b for a,b in zip(entry.lumiErrPerBX[bx],currProduct)]
                #lumi = [a/b for a,b in zip(entry.lumi[i],currProduct)]
                #lumie = [a/b for a,b in zip(entry.lumiErr[i],currProduct)]

                lumie = array("d",lumie)
                lumi = array("d",lumi)
                name = prefix +str(bx)
                graph = r.TGraphErrors(len(coord),coord,lumi,coorde,lumie)
                graph.SetName(name)
                graph.SetTitle(name)
                graph.SetMinimum(0.000001)
                graphsList[int(bx)] = graph
             else:
                omittedBXList.append(bx)
# same for the sum, as double check, where sumLumi comes from avgraw
        try:
            coord = entry.displacement
            coorde = [0.0 for a in coord] 
            coord = array("d",coord)
            coorde = array("d", coorde)
            currProduct = [ a*b/1e22 for a,b in zip(entry.sumCollAvrgFbctB1,entry.sumCollAvrgFbctB2)]
            lumi = [a/b for a,b in zip(entry.sumLumi,currProduct)]
            lumie = [a/b for a,b in zip(entry.sumLumiErr,currProduct)]
            lumie = array("d",lumie)
            lumi = array("d",lumi)
            name = prefix + 'sum'
            graph = r.TGraphErrors(len(coord),coord,lumi,coorde,lumie)
            graph.SetName(name)
            graph.SetTitle(name)
            graphsList['sum'] = graph
        except KeyError,e: 
            print 'KeyError in makeGraphsFile- reason "%s"' % str(e)


        graphsListAll['Scan_'+ str(scanNumber)]=graphsList
        missedDataInfo=missedDataInfo+"Scan_"+prefix+":"+str(omittedBXList)+"\n" 

    return corrFull, graphsListAll, missedDataInfo

################################################
if __name__ == '__main__':

    configFile = sys.argv[1]

    config=open(configFile)
    ConfigInfo = json.load(config)
    config.close()

    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    Luminometer = str(ConfigInfo['Luminometer'])
    Fill = str(ConfigInfo['Fill'])
    OutputSubDir = str(ConfigInfo['OutputSubDir'])

    graphsListAll = {}

    corrFull, graphsListAll, missedDataBuffer = doMakeGraphsFile(ConfigInfo) 

    outputDir = AnalysisDir +'/' + Luminometer + '/' + OutputSubDir + '/'
    outFileName = 'graphs_' + str(Fill) + corrFull

# save TGraphs in a ROOT file
    rfile = r.TFile(outputDir + outFileName + '.root',"recreate")

    for key in sorted(graphsListAll.iterkeys()):
        graphsList = graphsListAll[key]
        for key_bx in sorted(graphsList.iterkeys()):
            graphsList[key_bx].Write()

    rfile.Write()
    rfile.Close()

    with open(outputDir + outFileName + '.pkl', 'wb') as file:
        pickle.dump(graphsListAll, file)

    misseddata=open(outputDir+"makeGraphsFile_MissedData.log",'w')
    misseddata.write(missedDataBuffer)
    misseddata.close()

