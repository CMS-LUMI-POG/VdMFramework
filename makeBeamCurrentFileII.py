import ROOT
import tables
import numpy as np
from scipy import stats
import pandas as pd

import json
import os

def sumCurrents(curr, bcidList):

    sumCurr = 0.0
    if curr:
        for bcid in bcidList:
            sumCurr = sumCurr + curr[str(bcid)]
    else: 
        print "Attention: No beam currents for time period of scan found in input files"
    
    return sumCurr


def checkFBCTcalib(table, CalibrateFBCTtoDCCT):

    h_ratioB1 = ROOT.TGraph()
    h_ratioB1.SetMarkerStyle(8)
    h_ratioB1.SetMarkerSize(0.4)
    h_ratioB1.SetTitle("SumFBCT/DCCT for B1, for scan "+str(table[0][1]))
    h_ratioB1.GetXaxis().SetTitle("Scan point number")
    h_ratioB1.GetYaxis().SetTitle("SumFBCT(active bunches)/DCCT")

    h_ratioB2 = ROOT.TGraph()
    h_ratioB2.SetMarkerStyle(8)
    h_ratioB2.SetMarkerSize(0.4)
    h_ratioB2.SetTitle("SumFBCT/DCCT for B2, for scan "+str(table[0][1]))
    h_ratioB2.GetXaxis().SetTitle("Scan point number")
    h_ratioB2.GetYaxis().SetTitle("SumFBCT(active bunches)/DCCT")


    for idx, entry in enumerate(table):
        h_ratioB1.SetPoint(idx, entry[2], entry[5]/entry[3])
        h_ratioB2.SetPoint(idx, entry[2], entry[6]/entry[4])


    h_ratioB1.Fit("pol0")
    h_ratioB2.Fit("pol0")

    fB1 = ROOT.TF1()
    fB2 = ROOT.TF1()
    fB1 = h_ratioB1.GetFunction("pol0")
    fB2 = h_ratioB2.GetFunction("pol0")

    corrB1 = fB1.GetParameter(0)
    corrB2 = fB2.GetParameter(0)

    if CalibrateFBCTtoDCCT == True:

        print "Applying FBCT to DCCT calibration"
        for idx, entry in enumerate(table):
            old1 = entry[7]
#            entry[7] = entry[5]/entry[3]*old1
            entry[7] = corrB1*old1
            old2 =  entry[8]
#            entry[8] = entry[6]/entry[4]*old2
            entry[8] = corrB2*old2

    return [h_ratioB1, h_ratioB2]


def getCurrents(datapath, scanpt):


#    print "beginning of getCurrents", scanpt
    filelist = os.listdir(datapath)

    beamts = []
    bx1data = []
    bx2data = []
    bx1df = pd.DataFrame()
    bx2df = pd.DataFrame()

    beam1data = []
    beam2data = [] 
    beam1df = pd.DataFrame()
    beam2df = pd.DataFrame()

    fbct1 = {}
    fbct2 = {}

    dcct1 = 0.0
    dcct2 = 0.0

    filledBunches1 = []
    filledBunches2 = []
    collBunches=[]

# omit very first nibble because it may not be fully contained in VdM scan
    tw = '(timestampsec >' + str(scanpt[0]) + ') & (timestampsec <=' +  str(scanpt[1]) + ')'
    print "tw", tw

    for file in filelist:
#        print file
        h5file = tables.open_file(datapath + "/" + file, 'r')
        beamtable = h5file.root.beam
        bunchlist1 = [r['bxconfig1'] for r in beamtable.where(tw)] 
        bunchlist2 = [r['bxconfig2'] for r in beamtable.where(tw)]        
        beamtslist = [r['timestampsec'] for r in beamtable.where(tw)]
        beamts = beamts + beamtslist

        if bunchlist1 and bunchlist2:
            collBunches  = np.nonzero(bunchlist1[0]*bunchlist2[0])[0].tolist()
            filledBunches1 = np.nonzero(bunchlist1[0])[0].tolist()
            filledBunches2 = np.nonzero(bunchlist2[0])[0].tolist()

# dcct, i.e. current per beam
            beam1list = [r['intensity1'] for r in beamtable.where(tw)]
            beam2list = [r['intensity2'] for r in beamtable.where(tw)]
            beam1data = beam1data + beam1list
            beam2data = beam2data + beam2list
# fbct, ie. current per bx 
            bx1list = [r['bxintensity1'] for r in beamtable.where(tw)]
            bx2list = [r['bxintensity2'] for r in beamtable.where(tw)]
# only consider nominally filled bunches
            bx1data = bx1data + (bx1list* bunchlist1[0]).tolist()
            bx2data = bx2data + (bx2list* bunchlist2[0]).tolist()

        h5file.close()

    beam1df = pd.DataFrame(beam1data)
    beam2df = pd.DataFrame(beam2data)
    
    bx1df = pd.DataFrame(bx1data)
    bx2df = pd.DataFrame(bx2data)

    if beam1df.empty or beam2df.empty or bx1df.empty or bx2df.empty:
        print "Attention, beam current df empty because timestamp window not contained in file"
    else:
        dcct1 = float(beam1df.mean())
        dcct2 = float(beam2df.mean())
# attention: LHC bcid's start at 1, not at 0
        ## FIXME SUPER HACKED
        ## In 4266 BCID 2674 is 3% too low in FBCT
        for idx, bcid in enumerate(filledBunches1):
            if bcid+1==2674:
                fbct1[str(bcid+1)] = 1.03*bx1df[bcid].mean()
            else:
                fbct1[str(bcid+1)] = bx1df[bcid].mean()
        for idx, bcid in enumerate(filledBunches2):
            if bcid==2674:
                fbct2[str(bcid+1)] = 1.03*bx2df[bcid].mean()
            else:
                fbct2[str(bcid+1)] = bx2df[bcid].mean()

    return dcct1, dcct2, fbct1, fbct2



def doMakeBeamCurrentFile(ConfigInfo):

    import csv, pickle

    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    InputCentralPath = str(ConfigInfo['InputCentralPath'])
    InputScanFile = './' + AnalysisDir + '/' + str(ConfigInfo['InputScanFile'])
    OutputSubDir = str(ConfigInfo['OutputSubDir'])

    outpath = './' + AnalysisDir + '/' + OutputSubDir 

    CalibrateFBCTtoDCCT = False
    CalibrateFBCTtoDCCT = str(ConfigInfo['CalibrateFBCTtoDCCT'])

    with open(InputScanFile, 'rb') as f:
        scanInfo = pickle.load(f)

    Fill = scanInfo["Fill"]     
    ScanNames = scanInfo["ScanNames"]     
    
    CollidingBunches = scanInfo["CollidingBunches"]
    FilledBunchesB1 = scanInfo["FilledBunchesB1"]
    FilledBunchesB2 = scanInfo["FilledBunchesB2"]

    table = {}
    csvtable = []
#    csvtable.append(["ScanNumber, ScanNames, ScanPointNumber, avrgdcct1, avrgdcct2, sum(avrgfbctB1), sum(avrgfbctB2), sumColl(avrgfbct1), sumColl(avrgfbct2), fbct1 per Bx, fbct2 per BX"])
    csvtable.append(["ScanNumber, ScanNames, ScanPointNumber, avrgdcct1, avrgdcct2, sum(avrgfbctB1), sum(avrgfbctB2), fbct1 per Bx, fbct2 per BX"])

    for i in range(len(ScanNames)):
        key = "Scan_" + str(i+1)
        scanpoints = scanInfo[key]
        table["Scan_" + str(i+1)]=[]
        csvtable.append([str(key)] )
        for j, sp in enumerate(scanpoints):
            avrgdcct1, avrgdcct2, avrgfbct1, avrgfbct2 = getCurrents(InputCentralPath, sp[3:])
# todo: implement correcting FBCT values in case CalibrateFBCTtoDCCT =True in json

#Sums over all filled bunches
            sumavrgfbct1 = sumCurrents(avrgfbct1, FilledBunchesB1) 
            sumavrgfbct2 = sumCurrents(avrgfbct2, FilledBunchesB2) 
#Sums over all colliding bunches
            sumCollavrgfbct1 = sumCurrents(avrgfbct1, CollidingBunches) 
            sumCollavrgfbct2 = sumCurrents(avrgfbct2, CollidingBunches) 
            avrgfbct1['sum'] = sumCollavrgfbct1
            avrgfbct2['sum'] = sumCollavrgfbct2

            print "Scan point", j, sp
#            row = [i+1, str(ScanNames[i]), j+1, avrgdcct1, avrgdcct2, sumavrgfbct1, sumavrgfbct2, sumCollavrgfbct1, sumCollavrgfbct2, avrgfbct1, avrgfbct2
            row = [i+1, str(ScanNames[i]), j+1, avrgdcct1, avrgdcct2, sumavrgfbct1, sumavrgfbct2, avrgfbct1, avrgfbct2]
            table["Scan_" + str(i+1)].append(row)
            csvtable.append(row)



    canvas = ROOT.TCanvas()

    ROOT.gStyle.SetOptFit(111)
    ROOT.gStyle.SetOptStat(0)

    h_ratioB1 = ROOT.TGraph()
    h_ratioB2 = ROOT.TGraph()

    outpdf = outpath+'/checkFBCTcalib_'+str(Fill)+'.pdf'
    for i in range(len(ScanNames)):
        key = "Scan_" + str(i+1)
        [h_ratioB1, h_ratioB2] = checkFBCTcalib(table[key], CalibrateFBCTtoDCCT)
        h_ratioB1.Draw("AP")
        canvas.SaveAs(outpdf + '(')
        h_ratioB2.Draw("AP")
        canvas.SaveAs(outpdf + '(')

    canvas.SaveAs(outpdf + ']')

    return table, csvtable



if __name__ == '__main__':

    import pickle, csv, sys, json

    ConfigFile = sys.argv[1]

    Config=open(ConfigFile)
    ConfigInfo = json.load(Config)
    Config.close()

    AnalysisDir = str(ConfigInfo["AnalysisDir"])
    OutputSubDir = str(ConfigInfo["OutputSubDir"])


    InputScanFile = './' + AnalysisDir + '/' + str(ConfigInfo['InputScanFile'])
    with open(InputScanFile, 'rb') as f:
        scanInfo = pickle.load(f)

    Fill = scanInfo["Fill"]     

    table = {}
    csvtable = []

    table, csvtable = doMakeBeamCurrentFile(ConfigInfo)
    
    outpath = AnalysisDir + '/' + OutputSubDir

    csvfile = open(outpath+'/BeamCurrents_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(outpath+'/BeamCurrents_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)
            
