import ROOT as r

import tables
import numpy as np
from scipy import stats
import pandas as pd

import json
import os



def getRates(datapath, rateTable , collBunches,scanpt):

#    print "beginning of getCurrents", scanpt
    filelist = os.listdir(datapath)

    beamts = []
    bxdata = []
    avgdata = []
    bxdf = pd.DataFrame()
    avgdf = pd.DataFrame()

    rates = {}
    ratesErr = {}

# omit very first nibble because it may not be fully contained in VdM scan
    tw = '(timestampsec >' + str(scanpt[0]) + ') & (timestampsec <=' +  str(scanpt[1]) + ')'
#    print "tw", tw

    for file in filelist:
#        print file
        h5file = tables.open_file(datapath + "/" + file, 'r')
        if rateTable == "hflumi":
            beamtable = h5file.root.hflumi
        if rateTable == "bcm1flumi":
            beamtable = h5file.root.bcm1flumi
        if rateTable == "pltlumizero":
            beamtable = h5file.root.pltlumizero
        if rateTable == "pltlumi":
            beamtable = h5file.root.pltlumi
# sum over all bx
        avglist = [r['avgraw'] for r in beamtable.where(tw)]
        if avglist:
            avgdata = avgdata + avglist
# rates per bx 
        bxlist = [r['bxraw'] for r in beamtable.where(tw)]

        if bxlist:
## only consider nominally filled bunches
#            helper = np.zeros_like(bxlist)
#            for entry in collBunches:
#                helper[0][entry-1] =1.

#            bxdata = bxdata + (bxlist* helper[0]).tolist()
            bxdata = bxdata + bxlist

        h5file.close()


#    print "avgdata", avgdata
    bxdf = pd.DataFrame(bxdata)
#    print "bxdf", bxdf

    avgdf = pd.DataFrame(avgdata)

    if bxdf.empty:
        print "Attention, rates bxdf empty because timestamp window not contained in file"
    else:
        for idx, bcid in enumerate(collBunches):
            rates[str(bcid)] = bxdf[bcid-1].mean()
            ratesErr[str(bcid)] = stats.sem(bxdf[bcid-1])
    if avgdf.empty:
        print "Attention, rates avgdf empty because timestamp window not contained in file"
    else:
        rates['sum'] = avgdf[0].mean()
        ratesErr['sum'] = stats.sem(avgdf[0])

    return [rates, ratesErr]


def doMakeRateFile(ConfigInfo):
    
    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    InputScanFile = AnalysisDir + "/" + str(ConfigInfo['InputScanFile'])
    InputLumiDir = str(ConfigInfo['InputLumiDir'])
    RateTable = str(ConfigInfo['RateTable'])


    import pickle
    with open(InputScanFile, 'rb') as f:
        scanInfo = pickle.load(f)

    Fill = scanInfo["Fill"]     
    ScanNames = scanInfo["ScanNames"]     
    CollidingBunches = scanInfo["CollidingBunches"]

    csvtable = []
    csvtable.append(["ScanNumber, ScanNames, ScanPointNumber, Rates per bx, RateErr per bx"])

    table = {}


    for i in range(len(ScanNames)):
        key = "Scan_" + str(i+1)
        scanpoints = scanInfo[key]
        table["Scan_" + str(i+1)]=[]
        csvtable.append([str(key)] )
        for j, sp in enumerate(scanpoints):
            rates = getRates(InputLumiDir, RateTable , CollidingBunches, sp[3:])
# check against avrgraw
#            sumRate = 0.
#            sumRateErr = 0.
#            for key in rate:
#                sumRate = sumRate+ rate[key]
#            for key in rateErr:
#                sumRateErr = sumRateErr + (rateErr[key]/rate[key])**2
#            sumRateErr = math.sqrt(sumRateErr)
#            print "Scan point", j, sp
            row = [i+1, str(ScanNames[i]), j+1, rates]
            table["Scan_" + str(i+1)].append(row)
            csvtable.append(row[:3])
            helper1= row[3][0]
            csvtable.append([helper1])
            helper2 = row[3][1]
            csvtable.append([helper2])


    return table, csvtable


if __name__ == '__main__':

    import sys, json, pickle

    # read config file
    ConfigFile = sys.argv[1]

    Config=open(ConfigFile)
    ConfigInfo = json.load(Config)
    Config.close()

    Luminometer = str(ConfigInfo['Luminometer'])
    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    OutputSubDir = AnalysisDir + "/" + str(ConfigInfo['OutputSubDir'])

    InputScanFile = './' + AnalysisDir + '/' + str(ConfigInfo['InputScanFile'])
    with open(InputScanFile, 'rb') as f:
        scanInfo = pickle.load(f)

    Fill = scanInfo["Fill"]     

    table = {}
    csvtable = []

    table, csvtable = doMakeRateFile(ConfigInfo)

    import csv
    csvfile = open(OutputSubDir+'/Rates_'+str(Luminometer)+'_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(OutputSubDir+'/Rates_'+str(Luminometer)+'_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)
            





