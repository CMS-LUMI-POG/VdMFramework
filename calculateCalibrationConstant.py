import sys, json, csv, pickle
import luminometers
from vdmUtilities import makeCorrString
from fitResultReader import fitResultReader

# [in Hz]
LHC_revolution_frequency =  11245

import math
pi = math.pi

class XsecCalculationOptions:

    class LuminometerOptions:
        LuminometerTypes = ("HF", "PCC", "Vtx", "BCM1F", "PLT")
        WhatIsMeasured = ("CountsPerTime","Counts")
        NormalizationGraphs = ("None", "CurrentProduct")
        OldNormalizationAvailable = ("Yes", "No")

    class FormulaOptions:
        FormulaToUse = ("1D-Gaussian-like", "2D-like", "numerical-Integration")


def xsecFormula_1DGaussianLike(CapSigmaX, CapSigmaY, peakX, peakY):

# units, want visible cross section in microbarn !
    CapSigmaX[0] =CapSigmaX[0]*1000
    CapSigmaX[1] =CapSigmaX[1]*1000
    CapSigmaY[0] =CapSigmaY[0]*1000
    CapSigmaY[1] =CapSigmaY[1]*1000

# with approximation peakX ~ peakY ~ 0.5(peakX+peakY)
    xsec =  pi * CapSigmaX[0] * CapSigmaY[0] * (peakX[0] + peakY[0])
    xsecErr = ( CapSigmaX[1]*CapSigmaX[1]/CapSigmaX[0]/CapSigmaX[0] + \
                CapSigmaY[1]*CapSigmaY[1]/CapSigmaY[0]/CapSigmaY[0] + \
                (peakX[1]*peakX[1] + peakY[1]*peakY[1])/(peakX[0]+peakY[0])/(peakX[0]+peakY[0]))
    xsecErr = math.sqrt(xsecErr) * xsec

    return xsec, xsecErr

def xsecFormula_2DLike(fitResult):

    return xsec

def xsecFormula_numericalIntegration(fitFunc):    

    return xsec



if __name__ == '__main__':

# check that options chosen in json do actually exist

# if non-standard luminometer chosen, check that all options provided are allowed, i.e. are in LuminometerOptions

# either use xsec as returned by function, for "Counts", or xsec/LHC_frequency, for "CountsPerTime"


    configFile = sys.argv[1]

    config=open(configFile)
    ConfigInfo = json.load(config)
    config.close()

    Fill = ConfigInfo['Fill']
    AnalysisDir = ConfigInfo['AnalysisDir']
    Luminometer = ConfigInfo['Luminometer']
    Corr = ConfigInfo['Corr']
    InputFitResultsFile = ConfigInfo['InputFitResultsFile']
    fit = InputFitResultsFile.strip("FitResults.pkl")

    corrFull = makeCorrString(Corr)
    InputFitResultsFile = AnalysisDir + "/" + Luminometer + "/results/" + corrFull + "/" + InputFitResultsFile 
    OutputDir = './' + AnalysisDir + '/' + Luminometer + '/results/' + corrFull + '/'
    
    predefinedTypes = XsecCalculationOptions.LuminometerOptions.LuminometerTypes
    
    from luminometers import *

    oldNormAvailable = False

    WhatIsMeasured = ConfigInfo['LuminometerSettings']['WhatIsMeasured']
    NormalizationGraphs = ConfigInfo['LuminometerSettings']['NormalizationGraphs']
    OldNormAvailable = ConfigInfo['LuminometerSettings']['OldNormAvailable']

    if Luminometer in predefinedTypes:
        defaults = LuminometerDefaults(Luminometer)
        if WhatIsMeasured == "default":
            WhatIsMeasured = defaults.WhatIsMeasured
        if NormalizationGraphs== "default":
            NormalizationGraphs = defaults.NormalizationGraphs
        if OldNormAvailable == "default":
            OldNormAvailable = defaults.OldNormAvailable
        print "defaults ", WhatIsMeasured, NormalizationGraphs, OldNormAvailable

    Total_inel_Xsec = ConfigInfo['Total_inel_Xsec']

    if OldNormAvailable:
        oldNormalization = ConfigInfo['OldNormalization']

        if oldNormalization < 0:
            print "Value of old normalization from json makes no sense, is negative, hence assume no old normalization available"
            OldNormAvailable = False

#            print "OldNormAvailable, oldNormalization", OldNormAvailable, oldNormalization

    FormulaToUse = ConfigInfo['FormulaToUse']
    Scanpairs = ConfigInfo['Scanpairs']

    fitResult = fitResultReader(InputFitResultsFile)
    
    CapSigmaDict = fitResult.getFitParam("CapSigma")
#    CapSigmaDict = fitResult.getFitParam("sigma")
#    print CapSigmaDict["Scan_1"]["1040"]
    CapSigmaErrDict = fitResult.getFitParam("CapSigmaErr")
#    CapSigmaErrDict = fitResult.getFitParam("sigmaErr")
#    print CapSigmaErrDict["Scan_1"]["1040"]
    peakDict = fitResult.getFitParam("peak")
#    peakDict = fitResult.getFitParam("Amp")
    peakErrDict = fitResult.getFitParam("peakErr")
#    peakErrDict = fitResult.getFitParam("AmpErr")

    fitstatusDict = fitResult.getFitParam("fitStatus")
    chi2Dict = fitResult.getFitParam("chi2")
        
    table =[]
    csvtable = []
    csvtable.append(["XscanNumber_YscanNumber","Type", "BCID", "xsec", "xsecErr", "normChange", "normChangeErr"] )
    table.append(["XscanNumber_YscanNumber","Type", "BCID", "xsec", "xsecErr", "normChange", "normChangeErr"] )

    for entry in Scanpairs:

        XscanNumber = entry[0]
        YscanNumber = entry[1]
        XYbxlist=[]

        from collections import defaultdict

        xsec = defaultdict(float)
        xsecErr = defaultdict(float)
        xsecDict = defaultdict(dict)
        xsecErrDict = defaultdict(dict)
        XscanID = 'Scan_'+str(XscanNumber)
        YscanID = 'Scan_'+str(YscanNumber)
        XY_ID = 'Scan_'+str(XscanNumber) + '_'+str(YscanNumber)

#        csvtable.append([XY_ID])

#        print "CapSigmaDict[XscanID] for " + XscanID
#        print CapSigmaDict[XscanID]

        for bx in CapSigmaDict[XscanID]:
            if bx in CapSigmaDict[YscanID]:
                XYbxlist.append(bx)

#        print len(CapSigmaDict[XscanID])
#        print len(CapSigmaDict[YscanID])
#        print len(XYbxlist)
#        print "XYbxlist: ", XYbxlist

        for bx in XYbxlist:
            considerInMean = True
            print "now at bx", bx
            CapSigmaX = [CapSigmaDict[XscanID][bx], CapSigmaErrDict[XscanID][bx]]
            CapSigmaY = [CapSigmaDict[YscanID][bx], CapSigmaErrDict[YscanID][bx]]
            peakX = [peakDict[XscanID][bx], peakErrDict[XscanID][bx]]
            peakY = [peakDict[YscanID][bx], peakErrDict[YscanID][bx]]

# need to replace with something that takes FormulaToUse as argument and applies selected formula
            if FormulaToUse == "1D-Gaussian-like":
                value, err = xsecFormula_1DGaussianLike(CapSigmaX, CapSigmaY, peakX, peakY)
                if WhatIsMeasured == "CountsPerTime":
                    value =  value/LHC_revolution_frequency
                    err = err/LHC_revolution_frequency
                xsec[bx] =  value
                xsecErr[bx] = err
#                print "bx, [CapSigmaX, CapSigmaXErr],[CapSigmaY, CapSigmaYErr], [peakX, peakXErr], [peakY, peakYErr], xsec, xsecErr"
#                print ">>>>", bx, CapSigmaX, CapSigmaY, peakX, peakY, xsec[bx], xsecErr[bx]
                if fitstatusDict[XscanID][bx] >0:
                    print "fitstatus Xscan for bx", bx, fitstatusDict[XscanID][bx]
                if fitstatusDict[YscanID][bx] >0:
                    print "fitstatus Yscan for bx", bx, fitstatusDict[YscanID][bx]
                ## FIXME I hacked it 
                ###if chi2Dict[XscanID][bx] >100:
                ###    print "chi2 Xscan for bx", bx, chi2Dict[XscanID][bx]
                ###    considerInMean = False
                ###if chi2Dict[YscanID][bx] >100:
                ###    print "chi2 Yscan for bx", bx, chi2Dict[YscanID][bx]
                ###    considerInMean = False

#                printall(bx, CapSigmaX, CapSigmaY, peakX, peakY, xsec[bx], xsecErr[bx])



            normChange = -999. 
            normChangeErr = -999.

            if OldNormAvailable:
                normChange = LHC_revolution_frequency/xsec[bx] * 1/oldNormalization
                normChangeErr = normChange*xsecErr[bx]/xsec[bx]
            
            row = [str(XscanNumber)+"_"+str(YscanNumber), "XY", bx, xsec[bx], xsecErr[bx], normChange, normChangeErr]
            if considerInMean:
                table.append(row)
                csvtable.append(row)
            else:
                print "bcid ", bx, " excluded because chi2 value too high: ", chi2Dict[XscanID][bx], chi2Dict[YscanID][bx]

# need to name output file such that fit function name in file name


    csvfile = open(OutputDir+'/LumiCalibration_'+ Luminometer+ '_'+ fit + str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()


    with open(OutputDir+'/LumiCalibration_'+ Luminometer+ '_'+ fit + str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)

        

