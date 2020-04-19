## main file for dynamic beta analysis
import json, pickle, sys, re, math, csv, os
import ROOT as r
import numpy as np
from scipy.interpolate import interp1d
from array import array

#import FitManager
#import SG_Fit
#import SGConst_Fit
#import DG_Fit
#import DGConst_Fit
#from vdmUtilities import showAvailableFits

from inputDataReaderII_Ext import * 

#######################################
def readBaseTable(basetable):

    normBeamSep=[]
    DeltaBSXwrtBSX_Xscan=[]
    DeltaBSYwrtBSY_Xscan=[]
    DeltaBSXwrtBSX_Yscan=[]
    DeltaBSYwrtBSY_Yscan=[]

    pattern=re.compile(r"[\t,\n]")
    i=0
    for line in basetable:
        i=i+1
        if(i>5):
            numlist=pattern.split(line)
            normBeamSep.append(float(numlist[0]))
            DeltaBSXwrtBSX_Xscan.append(float(numlist[1]))
            DeltaBSYwrtBSY_Xscan.append(float(numlist[2]))
            DeltaBSXwrtBSX_Yscan.append(float(numlist[3]))
            DeltaBSYwrtBSY_Yscan.append(float(numlist[4]))

    SimDict={}
    SimDict['normBeamSep']=normBeamSep
    SimDict['DeltaBSXwrtBSX_Xscan']=DeltaBSXwrtBSX_Xscan
    SimDict['DeltaBSYwrtBSY_Xscan']=DeltaBSYwrtBSY_Xscan
    SimDict['DeltaBSXwrtBSX_Yscan']=DeltaBSXwrtBSX_Yscan
    SimDict['DeltaBSYwrtBSY_Yscan']=DeltaBSYwrtBSY_Yscan

    return SimDict
###################################
## Correction curves for colliding bcid, ScanX, ScanY
def defineCorrectionCurves(Nsim,emitXsim,emitYsim,refidx,simdict,ScanX,ScanY,bcid):

    NX=ScanX.averCurrPerBX[bcid]
    NY=ScanY.averCurrPerBX[bcid]
    emitX=ScanX.emitPerBX[bcid]
    emitY=ScanY.emitPerBX[bcid]


    KX=NX/Nsim*math.sqrt(emitXsim)*(math.sqrt(emitXsim)+math.sqrt(emitYsim))/math.sqrt(emitX)/(math.sqrt(emitX)+math.sqrt(emitY))
    KY=NY/Nsim*math.sqrt(emitYsim)*(math.sqrt(emitXsim)+math.sqrt(emitYsim))/math.sqrt(emitY)/(math.sqrt(emitX)+math.sqrt(emitY))

    BSXrefwrtBSX0_Xscan=KX*simdict['DeltaBSXwrtBSX_Xscan'][refidx]+1.0
    BSYrefwrtBSY0_Xscan=KY*simdict['DeltaBSYwrtBSY_Xscan'][refidx]+1.0
    BSXrefwrtBSX0_Yscan=KX*simdict['DeltaBSXwrtBSX_Yscan'][refidx]+1.0
    BSYrefwrtBSY0_Yscan=KY*simdict['DeltaBSYwrtBSY_Yscan'][refidx]+1.0
   
    Length=len(simdict['DeltaBSXwrtBSX_Xscan'])
    BSXwrtBSXref_Xscan=[]
    BSYwrtBSYref_Xscan=[]
    BSXwrtBSXref_Yscan=[]
    BSYwrtBSYref_Yscan=[]

    for idx in range(Length):
        val=(KX*simdict['DeltaBSXwrtBSX_Xscan'][idx]+1.0)/BSXrefwrtBSX0_Xscan
        BSXwrtBSXref_Xscan.append(val)
        val=(KY*simdict['DeltaBSYwrtBSY_Xscan'][idx]+1.0)/BSYrefwrtBSY0_Xscan
        BSYwrtBSYref_Xscan.append(val)
        val=(KX*simdict['DeltaBSXwrtBSX_Yscan'][idx]+1.0)/BSXrefwrtBSX0_Yscan
        BSXwrtBSXref_Yscan.append(val)
        val=(KY*simdict['DeltaBSYwrtBSY_Yscan'][idx]+1.0)/BSYrefwrtBSY0_Yscan
        BSYwrtBSYref_Yscan.append(val)

    CorrectionCurves=[BSXwrtBSXref_Xscan,BSYwrtBSYref_Xscan,BSXwrtBSXref_Yscan,BSYwrtBSYref_Yscan]
    
    return CorrectionCurves
############################################
## find DynamicBeta at scanpoints (per BX)
def interpolateDynBeta(Table,Scan,CorrCurves):
   
    normBeamSep=Table['normBeamSep']
    maxval=max(normBeamSep)

    collBunches=Scan.usedCollidingBunches
    DynBetaPerBX={}
    for bx in collBunches:
        CorrCurve=CorrCurves[bx]
        interpolateDB=interp1d(normBeamSep,CorrCurve)
        Shift=math.sqrt(2.0)*Scan.meanPerBX[bx]/Scan.CapSigmaPerBX[bx]
        SPList=Scan.normBeamSepPerBX_BBcorr[bx]
        Length=len(SPList)
        DynBeta=[]
        for sp in range(Length):
            coord=math.fabs(SPList[sp]-Shift)
            if coord<=maxval:
                val=interpolateDB(coord)
                val1=val.tolist()
                pair=(sp,val1)
                DynBeta.append(pair)
        if len(DynBeta)<Length:
            print "Warning from interpolateDynBeta: there were points out of the interpolation range, Scan", Scan.scanNumber, ", bx=", bx
        DynBetaPerBX[bx]=DynBeta

    return DynBetaPerBX
###############################
## find lumi correction factor per bx
def calculateLumiCorrFactor(Scan,DynBeta1,DynBeta2):

    collBunches=Scan.usedCollidingBunches
    LumiCorrFactorPerBX={}
    for bx in collBunches:
        dynbeta1=DynBeta1[bx]
        dynbeta2=DynBeta2[bx]
        splist=Scan.normBeamSepPerBX_BBcorr[bx]

        #fast check
        Length1=len(dynbeta1)
        Length2=len(dynbeta2)
        if Length1!=Length2:
            print "Error in calculateLumiCorrFactor: exit program"
            sys.exit()
        for idx in range(Length1):
            db1=dynbeta1[idx]
            db2=dynbeta2[idx]
            if db1[0]!=db2[0]:
                print "Error in calcLumiCorrFactor: exit program"
                sys.exit()
        
        LumiCorrFactor=[]
        for idx in range(Length1):
            db1=dynbeta1[idx]
            db2=dynbeta2[idx]
            spidx=db1[0]
            coord=splist[spidx]
            val1=1.0/db1[1]
            val=math.sqrt(db1[1]*db2[1])*math.exp(-0.25*coord*coord*(1.0-val1))
            pair=(spidx,val)
            LumiCorrFactor.append(pair)
        LumiCorrFactorPerBX[bx]=LumiCorrFactor    

    return LumiCorrFactorPerBX

##############################
def doMakeDynamicBeta(ConfigInfo):

## load simulated table
    #if base table is changed, this code should be overwritten from here -->

    #normalized emittance in um*rad  
    emitXsim=4.0
    emitYsim=4.0
    #intensity of opposing bunch, proton/bunch
    Nsim=8.5E10

    simtable=open(r"dynBetaCrctnTable_v1.0_22May13.txt","rt")
    SimDict=readBaseTable(simtable)
    simtable.close()

    #<-- till here (may be, together with readBaseTable())

## vdm data reading

    inputScanFile = str(ConfigInfo['InputScanFile'])
    inputBeamCurrentFile = str(ConfigInfo['InputBeamCurrentFile'])
    inputRatesFile = str(ConfigInfo['InputRatesFile'])
    inputBeamBeamFile=str(ConfigInfo['InputBeamBeamFile'])
    inputFitResultsFile=str(ConfigInfo['InputFitResultsFile'])
    Scanpairs=ConfigInfo['Scanpair']

    # For scan 1, which is always there as long as there are any scans at all:
    inData1 = vdmInputData_Ext(1)

    inData1.GetScanInfo(inputScanFile)
    #inData1.PrintScanInfo()

    inData1.GetBeamCurrentsInfo(inputBeamCurrentFile)
    #inData1.PrintBeamCurrentsInfo()

    inData1.GetLuminometerData(inputRatesFile)
    #inData1.PrintLuminometerData()

    inData1.GetBeamBeamData(inputBeamBeamFile)

    inData1.GetFitResults(inputFitResultsFile)

    Fill = inData1.fill

    inData=[]
    inData.append(inData1)

    # for the remaining scans

    for i in range(1,len(inData1.scanNamesAll)):
        inDataNext = vdmInputData_Ext(i+1)
        inDataNext.GetScanInfo(inputScanFile)
        inDataNext.GetBeamCurrentsInfo(inputBeamCurrentFile)
        inDataNext.GetLuminometerData(inputRatesFile)
        inDataNext.GetBeamBeamData(inputBeamBeamFile)
        inDataNext.GetFitResults(inputFitResultsFile)
        inData.append(inDataNext)

    for entry in inData:
        entry.applyBeamBeam() 
        entry.averageCurrent()
        entry.normalizeBeamSeparation()
        entry.calculateEmittance()

## correction curves.

    BSXwrtBSX_ref=[{} for s in range(len(inData))]
    BSYwrtBSY_ref=[{} for s in range(len(inData))]

    ## if reference point or base table is changed, check next lines. From here -->
    # reference point
    refidx=SimDict['normBeamSep'].index(0.0)
    for entry in Scanpairs:
        numX=entry[0]
        numY=entry[1]
        ScanX=inData[numX-1]
        ScanY=inData[numY-1]
        collBunches=ScanX.usedCollidingBunches
        for bx in collBunches:
            CorrCurves=defineCorrectionCurves(Nsim,emitXsim,emitYsim,refidx,SimDict,ScanX,ScanY,bx)
            BSXwrtBSX_ref[numX-1][bx]=CorrCurves[0]
            BSXwrtBSX_ref[numY-1][bx]=CorrCurves[2]
            BSYwrtBSY_ref[numX-1][bx]=CorrCurves[1]
            BSYwrtBSY_ref[numY-1][bx]=CorrCurves[3]
    ## <-- till here

## dynamic beta at scanpoints et al

    graphsListAll = {'Scan_'+ str(n+1):{} for n in range(len(inData))}

    for idx in range(len(inData)):
        Scan=inData[idx]
        DynBetaX=interpolateDynBeta(SimDict,Scan,BSXwrtBSX_ref[idx])
        DynBetaY=interpolateDynBeta(SimDict,Scan,BSYwrtBSY_ref[idx])

        scanNumber = Scan.scanNumber
        prefix = ''
        if 'X' in Scan.scanName:
            prefix = str(scanNumber) +'_X_'
            LumiCorrFactor=calculateLumiCorrFactor(Scan,DynBetaX,DynBetaY)
        if 'Y' in Scan.scanName:
            prefix = str(scanNumber)+'_Y_'
            LumiCorrFactor=calculateLumiCorrFactor(Scan,DynBetaY,DynBetaX)

        graphsList = {}
        for bx in Scan.usedCollidingBunches:
            Lumi=Scan.lumiPerBX[bx]
            Lumie=Scan.lumiErrPerBX[bx]
            CorrFactor=LumiCorrFactor[bx]

            CurrentB1=Scan.avrgFbctB1PerBX[bx]
            CurrentB2=Scan.avrgFbctB2PerBX[bx]

            CoordList=Scan.corrspPerBX[bx]

            Length=len(Lumi)
            Length1=len(CorrFactor)
            if Length<Length1:
                print "Error in doMakeDynamicBeta: exit program"
                sys.exit()

            # There could be extra scanpoints in Rates: at scan start and at the end
            minidx=CorrFactor[0][0]
            maxidx=CorrFactor[Length1-1][0]

            corrLumi=[]
            corrErr=[]
            Coord=[]
            k=0
            for idx in range(minidx,maxidx+1):
                factor=CorrFactor[k][1]
                val=Lumi[idx]*factor/CurrentB1[idx]/CurrentB2[idx]*1E22
                #pair=(idx,val)
                #print pair
                corrLumi.append(val)
                val=Lumie[idx]*factor/CurrentB1[idx]/CurrentB2[idx]*1E22
                #pair=(idx,val)
                corrErr.append(val)
                Coord.append(CoordList[idx])
                k=k+1

            CoordErr=[0.0 for a in Coord]

            Coord=array("d",Coord)
            CoordErr=array("d",CoordErr)
            corrLumi=array("d",corrLumi)
            corrErr=array("d",corrErr)
            name = prefix +str(bx)
            graph = r.TGraphErrors(Length1,Coord,corrLumi,CoordErr,corrErr)
            graph.SetName(name)
            graph.SetTitle(name)
            graph.SetMinimum(0.000001)

            graphsList[int(bx)]=graph

        graphsListAll['Scan_'+ str(scanNumber)]=graphsList

    return Fill,graphsListAll

#############################################
if __name__ == '__main__':

## read config file
    ConfigFile = sys.argv[1]
    Config=open(ConfigFile)
    ConfigInfo=json.load(Config)
    Config.close()

    graphsListAll={}

    Fill,graphsListAll=doMakeDynamicBeta(ConfigInfo)

    outputDir='graphs/'
    outFileName=str('graphs_')+str(Fill)+str('_DynBeta')
    
## save TGraphs in a ROOT file
    rfile = r.TFile(outputDir+outFileName+'.root',"recreate")

    for key in sorted(graphsListAll.iterkeys()):
        graphsList = graphsListAll[key]
        for key_bx in sorted(graphsList.iterkeys()):
            graphsList[key_bx].Write()

    rfile.Write()
    rfile.Close()

    with open(outputDir + outFileName + '.pkl', 'wb') as file:
        pickle.dump(graphsListAll, file)


