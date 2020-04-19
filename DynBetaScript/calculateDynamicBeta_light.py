# calculate dynamic beta corrections for single bunch
import json, pickle, sys, re, math, csv, os
import ROOT as r
import numpy as np
from scipy.interpolate import interp1d
from array import array

import FitManager
import SG_Fit
import SGConst_Fit
import DG_Fit
import DGConst_Fit
from vdmUtilities import showAvailableFits

########## find averaged current for the bunch from Currents file
def findCurrent(ScanTable,SPNumber,BCID):
    Currents1=[{} for idx in range(SPNumber)]
    Currents2=[{} for idx in range(SPNumber)]
    for entry in ScanTable:
        Currents1[int(entry[2])-1]=entry[7]
        Currents2[int(entry[2])-1]=entry[8]

    CurrentsB1=[]
    CurrentsB2=[]
    for idx in range(SPNumber):
        val=Currents1[idx].get(BCID)
        CurrentsB1.append(val)
        val=Currents2[idx].get(BCID)
        CurrentsB2.append(val)

    #the prescription from "W. Kozanecki, Updated implementation of the dynamic-b correction, LLCMWG meeting, 5 Aug 2013" is implemented
    #so, the average current is used as the intensity of opposite bunch
    averCurrents=[]
    for idx in range(SPNumber):
        averCurrents.append(0.5*(CurrentsB1[idx]+CurrentsB2[idx]))

    Current=0.0 
    for idx in range(SPNumber):
        Current=Current+averCurrents[idx]
    Current=Current/SPNumber

    return CurrentsB1,CurrentsB2,Current

###########
def findRates(ScanTable,SPNumber,BCID):

    Rates=[{} for idx in range(SPNumber)]
    RatesErr=[{} for idx in range(SPNumber)]
    for entry in ScanTable:
        Rates[int(entry[2])-1]=entry[3][0]
        RatesErr[int(entry[2])-1]=entry[3][1]

    RatesBCID=[]
    RatesErrBCID=[]
    for idx in range(SPNumber):
        val=Rates[idx].get(BCID)
        RatesBCID.append(val)
        val=RatesErr[idx].get(BCID)
        RatesErrBCID.append(val)

    return RatesBCID,RatesErrBCID

########## find BeamBeam correction for the bunch in BeamBeam file
def findBeamBeamCorr(Scan_key,ScanTable,SPNumber,BCID):

    if Scan_key=='X':
        pos=3
    elif Scan_key=='Y':
        pos=4
    else:
        "something wrong with Scan_key; exit program"
        sys.exit
    BeamBeamCorr=[{} for idx in range(SPNumber)]
    for entry in ScanTable:
        BeamBeamCorr[int(entry[2])-1]=entry[pos]

    BBCorr_forBCID=[]
    for idx in range(SPNumber):
        val=BeamBeamCorr[idx].get(BCID)
        BBCorr_forBCID.append(val)

    return BBCorr_forBCID

########## find CapSigma for BCID in FitResults.pkl
def findCapSigma(Scan_num,Scan_key,FitTable,BCID):

    captions=FitTable[0]
    idx1=-1
    idx2=-1
    for idx, cap in enumerate(captions):
        if cap=="CapSigma":
            idx1=idx
        if cap=="Mean":
            idx2=idx
    if (idx1==-1) | (idx2==-1):
        print "Fit results has not column CapSigma or Mean"
        exit() 

    for entry in FitTable:
        if((entry[0]==Scan_num) and (entry[1]==Scan_key) and (entry[2]==BCID)):
            #CapSigma=entry[15]
            #Mean=entry[11]
            CapSigma=entry[idx1]
            Mean=entry[idx2]
            break

    #print CapSigma

    return CapSigma,Mean

########## 
def readScanData(ConfigInfo):
    ScanFilePath=str(ConfigInfo['ScanFilePath'])
    Scanpair=ConfigInfo['Scanpair']

    with open(ScanFilePath,'rb') as f:
        ScanInfo=pickle.load(f)

    Fill=ScanInfo["Fill"]
    #unperturbed BetaStar, m
    BetaStar=float(ScanInfo["BetaStar"])
    # There is the suggestion: both beams have the equal energy
    # Energy in GeV
    Energy=float(ScanInfo["EnergyB1"])

    key_X="Scan_"+str(Scanpair[0])
    key_Y="Scan_"+str(Scanpair[1])
    ScanX=ScanInfo[key_X]
    ScanY=ScanInfo[key_Y]
    SPListX=[entry[5] for entry in ScanX]
    SPListY=[entry[5] for entry in ScanY]

    return Fill, BetaStar, Energy, key_X, key_Y, SPListX, SPListY
###########
def readCurrentsData(ConfigInfo,key_X,key_Y,lenX,lenY):

    CurrentFilePath=str(ConfigInfo['CurrentFilePath'])
    BCID=str(ConfigInfo['BCID'])
    with open(CurrentFilePath,'rb') as f:
        CurrentInfo=pickle.load(f)

    ScanX=CurrentInfo[key_X]
    ScanY=CurrentInfo[key_Y]

    #fast check for BCID
    #check if BCID exists in the first scanpoint of X scan
    checkscanpoint=ScanX[0][7]
    keyslist=checkscanpoint.keys()
    if BCID not in keyslist:
        print "Error in readCurrentsData: BCID=", BCID, " does not exist, exit program, check the config file"
        sys.exit()

    CurrentXB1,CurrentXB2,CurrentX=findCurrent(ScanX,lenX,BCID)
    CurrentYB1,CurrentYB2,CurrentY=findCurrent(ScanY,lenY,BCID)

    return BCID, CurrentXB1,CurrentXB2, CurrentYB1,CurrentYB2, CurrentX, CurrentY

##########
def readRatesData(ConfigInfo,key_X,key_Y,lenX,lenY):

    RatesFilePath=str(ConfigInfo['RateFilePath'])
    BCID=str(ConfigInfo['BCID'])
    with open(RatesFilePath,'rb') as f:
        RatesInfo=pickle.load(f)

    ScanX=RatesInfo[key_X]
    ScanY=RatesInfo[key_Y]

    #fast check for BCID
    #check if BCID exists in the first scanpoint of X scan
    checkscanpoint=ScanX[0][3][0]
    #print checkscanpoint
    keyslist=checkscanpoint.keys()
    if BCID not in keyslist:
        print "Error in readRatesData: BCID=", BCID, " does not exist, exit program, check the config file"
        sys.exit()

    RatesX,RatesErrX=findRates(ScanX,lenX,BCID)
    RatesY,RatesErrY=findRates(ScanY,lenY,BCID)

    return RatesX,RatesY,RatesErrX,RatesErrY

##########
def readBeamBeamData(ConfigInfo,BCID,key_X,key_Y,SPListX,SPListY):

    BeamBeamFilePath=str(ConfigInfo['BeamBeamFilePath'])
    with open(BeamBeamFilePath,'rb') as f:
        BeamBeamInfo=pickle.load(f)

    ScanX=BeamBeamInfo[key_X]
    ScanY=BeamBeamInfo[key_Y]

    BBCorrX=findBeamBeamCorr('X',ScanX,len(SPListX),BCID)
    BBCorrY=findBeamBeamCorr('Y',ScanY,len(SPListY),BCID)

    #apply BeamBeam correction
    corrSPListX=[a+b for a,b in zip(SPListX,BBCorrX)]
    corrSPListY=[a+b for a,b in zip(SPListY,BBCorrY)]

    return corrSPListX,corrSPListY

##########
def readFitResultsData(ConfigInfo,BCID):

    FitResultsFilePath=str(ConfigInfo['FitResultsFilePath'])
    Scanpair=ConfigInfo['Scanpair']

    with open(FitResultsFilePath,'rb') as f:
        FitResultsInfo=pickle.load(f)

    #read CapSigmas in mm
    CapSigmaX,MeanX=findCapSigma(str(Scanpair[0]),'X',FitResultsInfo,BCID)
    CapSigmaY,MeanY=findCapSigma(str(Scanpair[1]),'Y',FitResultsInfo,BCID)

    return CapSigmaX,CapSigmaY,MeanX,MeanY

########## normalized beam separation 
def normalizeBeamSeparation(SPList,CapSigma):

    Length=len(SPList)
    normSPList=[]
    for idx in range(Length):
        normSPList.append(math.sqrt(2.0)*SPList[idx]/CapSigma)

    return normSPList

##########
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

    return normBeamSep, DeltaBSXwrtBSX_Xscan, DeltaBSYwrtBSY_Xscan, DeltaBSXwrtBSX_Yscan, DeltaBSYwrtBSY_Yscan

########## define correction curves
def defineDynBetaCurves(Nsim,NX,NY,emitXsim,emitYsim,emitX,emitY,sim_DeltaBSXwrtBSX_Xscan,sim_DeltaBSYwrtBSY_Xscan,sim_DeltaBSXwrtBSX_Yscan,sim_DeltaBSYwrtBSY_Yscan,refidx):
    
    KX=NX/Nsim*math.sqrt(emitXsim)*(math.sqrt(emitXsim)+math.sqrt(emitYsim))/math.sqrt(emitX)/(math.sqrt(emitX)+math.sqrt(emitY))
    KY=NY/Nsim*math.sqrt(emitYsim)*(math.sqrt(emitXsim)+math.sqrt(emitYsim))/math.sqrt(emitY)/(math.sqrt(emitX)+math.sqrt(emitY))

    BSXrefwrtBSX0_Xscan=KX*sim_DeltaBSXwrtBSX_Xscan[refidx]+1.0
    BSYrefwrtBSY0_Xscan=KY*sim_DeltaBSYwrtBSY_Xscan[refidx]+1.0
    BSXrefwrtBSX0_Yscan=KX*sim_DeltaBSXwrtBSX_Yscan[refidx]+1.0
    BSYrefwrtBSY0_Yscan=KY*sim_DeltaBSYwrtBSY_Yscan[refidx]+1.0
   
    Length=len(sim_DeltaBSXwrtBSX_Xscan)
    BSXwrtBSXref_Xscan=[]
    BSYwrtBSYref_Xscan=[]
    BSXwrtBSXref_Yscan=[]
    BSYwrtBSYref_Yscan=[]

    for idx in range(Length):
        val=(KX*sim_DeltaBSXwrtBSX_Xscan[idx]+1.0)/BSXrefwrtBSX0_Xscan
        BSXwrtBSXref_Xscan.append(val)
        val=(KY*sim_DeltaBSYwrtBSY_Xscan[idx]+1.0)/BSYrefwrtBSY0_Xscan
        BSYwrtBSYref_Xscan.append(val)
        val=(KX*sim_DeltaBSXwrtBSX_Yscan[idx]+1.0)/BSXrefwrtBSX0_Yscan
        BSXwrtBSXref_Yscan.append(val)
        val=(KY*sim_DeltaBSYwrtBSY_Yscan[idx]+1.0)/BSYrefwrtBSY0_Yscan
        BSYwrtBSYref_Yscan.append(val)

    return BSXwrtBSXref_Xscan, BSYwrtBSYref_Xscan, BSXwrtBSXref_Yscan, BSYwrtBSYref_Yscan

########## incl. shift to zero value of the table
def interpolateDynBeta(SPList,baseSPList,baseDBList,Shift):

    maxval=max(baseSPList)
    interpolateDB=interp1d(baseSPList,baseDBList)

    Length=len(SPList)
    DynBeta=[]
    for idx in range(Length):
        coord=math.fabs(SPList[idx]-Shift)
        if coord<=maxval:
            val=interpolateDB(coord)
            val1=val.tolist()
            pair=(idx,val1)
            DynBeta.append(pair)
        else:
            print idx

    if len(DynBeta)<Length:
        print "Warning from interpolateDynBeta: there were points out of the interpolation range"

    return DynBeta
    
##########
def calcLumiCorrFactor(DynBeta1,DynBeta2,SPList):

#    print DynBeta1
#    print DynBeta2
    #fast check
    Length1=len(DynBeta1)
    Length2=len(DynBeta2)
    if Length1!=Length2:
        print "Error in calcLumiCorrFactor: exit program"
        sys.exit()
    for idx in range(Length1):
        db1=DynBeta1[idx]
        db2=DynBeta2[idx]
        if db1[0]!=db2[0]:
            print "Error in calcLumiCorrFactor: exit program"
            sys.exit()

    LumiCorrFactor=[]
    for idx in range(Length1):
        db1=DynBeta1[idx]
        db2=DynBeta2[idx]
        SPidx=db1[0]
        coord=SPList[SPidx]
        val1=1.0/db1[1]
        val=math.sqrt(db1[1]*db2[1])*math.exp(-0.25*coord*coord*(1.0-val1))
        coordidx=db1[0]
        pair=(coordidx,val)
        LumiCorrFactor.append(pair)

    return LumiCorrFactor

##########
def correctedLumi(Rates,RatesErr,CorrFactor,CurrentB1,CurrentB2,CoordList):

    Length=len(Rates)
    Length1=len(CorrFactor)
    if Length<Length1:
        print "Error in correctedLumi: exit program"
        sys.exit()

    print Length
    print Length1

    minidx=CorrFactor[0][0]
    maxidx=CorrFactor[Length1-1][0]

    # There could be extra scanpoints in Rates: at scan start and at the end
    corrRates=[]
    corrErr=[]
    Coord=[]
    k=0
    for idx in range(minidx,maxidx+1):
        factor=CorrFactor[k][1]
        val=Rates[idx]*factor/CurrentB1[idx]/CurrentB2[idx]*1E22

        print k, idx, factor, Rates[idx]/CurrentB1[idx]/CurrentB2[idx]*1E22, val

        corrRates.append(val)
        val=RatesErr[idx]*factor/CurrentB1[idx]/CurrentB2[idx]*1E22
        corrErr.append(val)
        Coord.append(CoordList[idx])
        k=k+1
    
    CoordErr=[0.0 for a in Coord]

    Coord=array("d",Coord)
    CoordErr=array("d",CoordErr)
    corrRates=array("d",corrRates)
    corrErr=array("d",corrErr)

    print minidx
    print maxidx

    Graph=r.TGraphErrors(Length1,Coord,corrRates,CoordErr,corrErr)
    
    return Graph

##################################################
###################### Main program ############

##### check for "output" directory
outdir='./DynBeta_light_results'
if not os.path.isdir(outdir):
    os.mkdir(outdir,0755)

##### load simulated table
#if base table is changed, this code should be overwritten from here -->

#normalized emittance in um*rad  
emitXsim=4.0
emitYsim=4.0
#intensity of opposing bunch, proton/bunch
Nsim=8.5E10

simtable=open(r"dynBetaCrctnTable_v1.0_22May13.txt","rt")
normBeamSep,ST_DeltaBSXwrtBSX_Xscan,ST_DeltaBSYwrtBSY_Xscan,ST_DeltaBSXwrtBSX_Yscan,ST_DeltaBSYwrtBSY_Yscan=readBaseTable(simtable)
simtable.close()

#<-- till here (may be, together with readBaseTable())

print "base table has been read" 

#####read and prepare vdm data

ConfigFile=sys.argv[1]

Config=open(ConfigFile)
ConfigInfo=json.load(Config)
Config.close()

Fill,BetaStar0,Energy,key_X,key_Y,uncorrSPListX,uncorrSPListY=readScanData(ConfigInfo)
gamma=Energy*1E3/938.272
LengthSPListX=len(uncorrSPListX)
LengthSPListY=len(uncorrSPListX)

BCID,CurrentXB1,CurrentXB2,CurrentYB1,CurrentYB2,CurrentX,CurrentY=readCurrentsData(ConfigInfo,key_X,key_Y,LengthSPListX,LengthSPListY)

RatesX,RatesY,RatesErrX,RatesErrY=readRatesData(ConfigInfo,key_X,key_Y,LengthSPListX,LengthSPListY)

corrSPListX,corrSPListY=readBeamBeamData(ConfigInfo,BCID,key_X,key_Y,uncorrSPListX,uncorrSPListY)

CapSigmaX,CapSigmaY,MeanX,MeanY=readFitResultsData(ConfigInfo,BCID)

normSPListX=normalizeBeamSeparation(corrSPListX,CapSigmaX)
normSPListY=normalizeBeamSeparation(corrSPListY,CapSigmaY)

print "vdM data has been read"

##### Auxiliary table

#normalized emittance
#CapSigmas are in mm => result in um*rad

emitX=gamma*CapSigmaX*CapSigmaX/2.0/BetaStar0
emitY=gamma*CapSigmaY*CapSigmaY/2.0/BetaStar0

# if reference point or base table is changed, check next lines. From here -->

refidx=normBeamSep.index(0.0)
BSXwrtBSXref_Xscan, BSYwrtBSYref_Xscan, BSXwrtBSXref_Yscan, BSYwrtBSYref_Yscan=defineDynBetaCurves(Nsim,CurrentX,CurrentY,emitXsim,emitYsim,emitX,emitY,ST_DeltaBSXwrtBSX_Xscan,ST_DeltaBSYwrtBSY_Xscan,ST_DeltaBSXwrtBSX_Yscan,ST_DeltaBSYwrtBSY_Yscan,refidx)
  
# <--till here
# BetaStar_wrt_reference_value at corrected scanpoints
BSXwrtBSXref_Xscan_SP=interpolateDynBeta(normSPListX,normBeamSep,BSXwrtBSXref_Xscan,math.sqrt(2.0)*MeanX/CapSigmaX)
BSYwrtBSYref_Xscan_SP=interpolateDynBeta(normSPListX,normBeamSep,BSYwrtBSYref_Xscan,math.sqrt(2.0)*MeanX/CapSigmaX)
BSXwrtBSXref_Yscan_SP=interpolateDynBeta(normSPListY,normBeamSep,BSXwrtBSXref_Yscan,math.sqrt(2.0)*MeanY/CapSigmaY)
BSYwrtBSYref_Yscan_SP=interpolateDynBeta(normSPListY,normBeamSep,BSYwrtBSYref_Yscan,math.sqrt(2.0)*MeanY/CapSigmaY)

LumiCorrFactorX=calcLumiCorrFactor(BSXwrtBSXref_Xscan_SP,BSYwrtBSYref_Xscan_SP,normSPListX)
LumiCorrFactorY=calcLumiCorrFactor(BSYwrtBSYref_Yscan_SP,BSXwrtBSXref_Yscan_SP,normSPListY)
TableLengthX=len(LumiCorrFactorX)
TableLengthY=len(LumiCorrFactorY)

GraphX=correctedLumi(RatesX,RatesErrX,LumiCorrFactorX,CurrentXB1,CurrentXB2,corrSPListX)
comps=key_X.split('_')
GraphX.SetName(comps[1]+"_X_"+str(BCID))
GraphX.SetTitle(comps[1]+"_X_"+str(BCID))
GraphX.SetMinimum(0.000001)

GraphY=correctedLumi(RatesY,RatesErrY,LumiCorrFactorY,CurrentYB1,CurrentYB2,corrSPListY)
comps=key_Y.split('_')
GraphY.SetName(comps[1]+"_Y_"+str(BCID))
GraphY.SetTitle(comps[1]+"_Y_"+str(BCID))
GraphY.SetMinimum(0.000001)

print "lumi correction has been calculated"

##### fit section

FitName = str(ConfigInfo['FitName'])
FitConfigFile = str(ConfigInfo['FitConfigFile'])
PlotsTempPath = ["./plotstmp/"]

FitConfig=open(FitConfigFile)
FitConfigInfo = json.load(FitConfig)
FitConfig.close()

# needs to be the same name as assumed in the fit function python files, where it is ./minuitlogtmp/Minuit.log
MinuitLogPath = './minuitlogtmp/'
MinuitLogFile = MinuitLogPath + 'Minuit.log'
if not os.path.isdir(MinuitLogPath):
    os.mkdir(MinuitLogPath, 0755)

# need to do this before each fitting loop
if os.path.isfile(MinuitLogFile):
    os.remove(MinuitLogFile)

showAvailableFits()
availableFits = FitManager.get_plugins(FitManager.FitProvider)

key = FitName + '_Fit'
if key not in availableFits:
    print "Fit " + FitName + " requested via json file does not exist, nothing to fit with, exit."
    sys.exit(1)

fitter = availableFits[key]()

FitLogFile = FitName +'.log'
fitlogfile = open(FitLogFile,'w') 

FunctionsX,FitX=fitter.doFit(GraphX, FitConfigInfo)
FunctionsY,FitY=fitter.doFit(GraphY, FitConfigInfo)
FitTable=fitter.table

##### Save and plot data

TableLength=len(normBeamSep)
restable={}
rescsv=[]

rescsv.append(["Fill","Energy[GeV]","BetaStar[m]","Scan_X","Scan_Y","BCID","norm_EmitX[um*rad]","norm_EmitY[um*rad]"])
rescsv.append([Fill,Energy,BetaStar0,key_X,key_Y,BCID,emitX,emitY])
rescsv.append(["Fit results after correction"])

restable["Fill"]=Fill
restable["Energy"]=Energy
restable["BetaStar"]=BetaStar0
restable["ScanpairXY"]=[key_X,key_Y]
restable["BCID"]=BCID
restable["EmittanceXY"]=[emitX,emitY]

restable["FitResults"]=[]
for entry in FitTable:
    print(entry)
    rescsv.append(entry)
    restable["FitResults"].append(entry)

rescsv.append(["Dynamic beta correction curves"])
rescsv.append(["normBeamSep","BSXwrtBSXref_Xscan", "BSYwrtBSYref_Xscan", "BSXwrtBSXref_Yscan", "BSYwrtBSYref_Yscan"])

restable["DBCaptions"]=["normBeamSep","BSXwrtBSXref_Xscan", "BSYwrtBSYref_Xscan", "BSXwrtBSXref_Yscan", "BSYwrtBSYref_Yscan"]
restable["DBTable"]=[]

for idx in range(TableLength):
    row=[normBeamSep[idx],BSXwrtBSXref_Xscan[idx], BSYwrtBSYref_Xscan[idx], BSXwrtBSXref_Yscan[idx], BSYwrtBSYref_Yscan[idx]]
    rescsv.append(row)
    restable["DBTable"].append(row)

rescsv.append(["Luminosity correction factor"])
rescsv.append(["BeamSeparation[mm]","LumiCorrFactor"])
restable["LCFCaptions"]=["BeamSeparation[mm]","LumiCorrFactor"]

restable["LCFTableX"]=[]
rescsv.append([key_X,"_X"])
for idx in range(TableLengthX):
    pair=LumiCorrFactorX[idx]
    SPidx=pair[0]
    coord=corrSPListX[SPidx]
    val=pair[1]
    row=[coord,val]
    rescsv.append(row)
    restable["LCFTableX"].append(row)

restable["LCFTableY"]=[]
rescsv.append([key_Y,"_Y"])
for idx in range(TableLengthY):
    pair=LumiCorrFactorY[idx]
    SPidx=pair[0]
    coord=corrSPListY[SPidx]
    val=pair[1]
    row=[coord,val]
    rescsv.append(row)
    restable["LCFTableY"].append(row)

csvfile=open(outdir+'/'+"DynamicBeta_light_"+str(Fill)+"_"+str(BCID)+"_"+key_X+"_"+key_Y+".csv","wb")
writer=csv.writer(csvfile)
writer.writerows(rescsv)
csvfile.close()

with open(outdir+'/'+"DynamicBeta_light_"+str(Fill)+"_"+str(BCID)+"_"+key_X+"_"+key_Y+".pkl","wb") as f:
    pickle.dump(restable,f)

canvas=r.TCanvas()
outpdf=outdir+'/'+"DynamicBeta_light_"+str(Fill)+"_"+str(BCID)+"_"+key_X+"_"+key_Y+".pdf"

gr_DBCurves=r.TMultiGraph()
gr_DBCurves.SetTitle("DynamicBetaCorrectionCurves_"+str(Fill)+"_"+str(BCID)+"_"+key_X+"_X_"+key_Y+"_Y;Normalized beam separation;Beta*_dyn/Beta*_ref")

gr_BSXwrtBSXref_Xscan=r.TGraph()
gr_BSYwrtBSYref_Xscan=r.TGraph()
gr_BSXwrtBSXref_Yscan=r.TGraph()
gr_BSYwrtBSYref_Yscan=r.TGraph()

for idx in range(TableLength):
    gr_BSXwrtBSXref_Xscan.SetPoint(idx,normBeamSep[idx],BSXwrtBSXref_Xscan[idx])
    gr_BSYwrtBSYref_Xscan.SetPoint(idx,normBeamSep[idx],BSYwrtBSYref_Xscan[idx])
    gr_BSXwrtBSXref_Yscan.SetPoint(idx,normBeamSep[idx],BSXwrtBSXref_Yscan[idx])
    gr_BSYwrtBSYref_Yscan.SetPoint(idx,normBeamSep[idx],BSYwrtBSYref_Yscan[idx])

gr_BSXwrtBSXref_Xscan.SetLineColor(2)
gr_BSXwrtBSXref_Xscan.SetLineWidth(3)
gr_BSXwrtBSXref_Xscan.SetTitle("B*_dynX/B*_refX__Xscan")

gr_BSYwrtBSYref_Xscan.SetLineColor(4)
gr_BSYwrtBSYref_Xscan.SetLineWidth(3)
gr_BSYwrtBSYref_Xscan.SetTitle("B*_dynY/B*_refY__Xscan")

gr_BSXwrtBSXref_Yscan.SetLineColor(6)
gr_BSXwrtBSXref_Yscan.SetLineWidth(3)
gr_BSXwrtBSXref_Yscan.SetTitle("B*_dynX/B*_refX__Yscan")

gr_BSYwrtBSYref_Yscan.SetLineColor(8)
gr_BSYwrtBSYref_Yscan.SetLineWidth(3)
gr_BSYwrtBSYref_Yscan.SetTitle("B*_dynY/B*_refY__Yscan")

gr_DBCurves.Add(gr_BSXwrtBSXref_Xscan)
gr_DBCurves.Add(gr_BSYwrtBSYref_Xscan)
gr_DBCurves.Add(gr_BSXwrtBSXref_Yscan)
gr_DBCurves.Add(gr_BSYwrtBSYref_Yscan)

gr_DBCurves.Draw("AC")
canvas.BuildLegend(0.65,0.2,0.85,0.4)

canvas.SaveAs(outpdf+'(')

gr_LCFactorX=r.TGraph()
gr_LCFactorX.SetMarkerStyle(8)
gr_LCFactorX.SetMarkerSize(0.4)
gr_LCFactorX.SetTitle("Lumi Correction Factor,"+str(Fill)+"_"+str(BCID)+"_"+key_X+"_X;Beam separation, mm;Rate_corr/Rate_meas")

for idx in range(TableLengthX):
    pair=LumiCorrFactorX[idx]
    SPidx=pair[0]
    coord=corrSPListX[SPidx]
    val=pair[1]   
    gr_LCFactorX.SetPoint(idx,coord,val)

gr_LCFactorY=r.TGraph()
gr_LCFactorY.SetMarkerStyle(8)
gr_LCFactorY.SetMarkerSize(0.4)
gr_LCFactorY.SetTitle("Lumi Correction Factor,"+str(Fill)+"_"+str(BCID)+"_"+key_Y+"_Y;Beam separation, mm;Rate_corr/Rate_meas")

for idx in range(TableLengthY):
    pair=LumiCorrFactorY[idx]
    SPidx=pair[0]
    coord=corrSPListY[SPidx]
    val=pair[1]
    gr_LCFactorY.SetPoint(idx,coord,val)

gr_LCFactorX.Draw("AP")
canvas.SaveAs(outpdf+'(')

gr_LCFactorY.Draw("AP")
canvas.SaveAs(outpdf+'(')

canvas.SaveAs(outpdf+']')

