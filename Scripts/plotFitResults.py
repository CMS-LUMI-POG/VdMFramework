from fitResultReader import fitResultReader
import ROOT as r
import sys, json
from vdmUtilities import makeCorrString

r.gROOT.SetBatch(r.kTRUE)

def addXsecPlots(description, paramName, param, paramErr, ouFileName):


    noScanPairs = len(param)

    canvas = r.TCanvas()

    marker = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
    color = [2,3,4,6,7,2,3,4,6,7]

    plot = r.TGraphErrors()
    plot.SetMarkerStyle(8)
    plot.SetMarkerSize(0.4)
    plot.SetTitle(description + " " + paramName)
    plot.GetXaxis().SetTitle('Scan number')
    plot.GetYaxis().SetTitle(paramName)
    
    i = 0
    scanpairno = 0
    scanpairList = []
    for scanpair in sorted(param):
        scanpairList.append(scanpair)
        scanpairno = scanpairno + 1
        for bcid in param[scanpair]:
            try:
                value = int(bcid)
            except: TypeError
            else:
                plot.SetPoint(i, scanpairno, param[scanpair][bcid])
                i = i+1


    plot.GetXaxis().SetTitle('Scanpair')
    plot.GetYaxis().SetTitle(paramName)
    plot.Draw("AP")
    canvas.SaveAs(outFileName +'(')

    max = plot.GetHistogram().GetMaximum()
    min = plot.GetHistogram().GetMinimum()
    max = max*1.1
    min = min*0.9

    plot_byBX=[r.TGraphErrors() for i in range(noScanPairs)]

    scanpairno = 0
    for scanpair in sorted(param):
        scanpairno= scanpairno + 1
        i = 0
        for bcid in param[scanpair]:
            try:
                value = int(bcid)
            except: TypeError
            else:
                plot_byBX[int(scanpairno)-1].SetPoint(i, int(bcid), param[scanpair][bcid])
                plot_byBX[int(scanpairno)-1].SetPointError(i, 0.0, paramErr[scanpair][bcid])
                i = i+1


    plot_byBX[0].SetMaximum(max)
    plot_byBX[0].SetMinimum(min)
    plot_byBX[0].SetMarkerColor(color[0])        
    plot_byBX[0].SetMarkerStyle(marker[0])
    plot_byBX[0].SetMarkerSize(0.4)
    
    plot_byBX[0].SetTitle(description + " " + paramName + " scan pair " + scanpairList[0])
    plot_byBX[0].GetXaxis().SetTitle('BCID')
    plot_byBX[0].GetYaxis().SetTitle(paramName)
    plot_byBX[0].Draw("AP")
    for i in range(1,noScanPairs):
        plot_byBX[i].SetTitle(description + " " + paramName +" scan pair " + scanpairList[i])
        plot_byBX[i].SetMarkerColor(color[i])        
        plot_byBX[i].SetMarkerStyle(marker[i])
        plot_byBX[i].SetMarkerSize(0.4)
        plot_byBX[i].Draw("P")
            
    canvas.BuildLegend(0.65,0.8,0.95,0.95,"")
    plot_byBX[0].SetTitle(description + " " + paramName)
    canvas.SaveAs(outFileName +'(')




def addPlots(description, paramName, param, paramErr, ouFileName):

    noScans = len(param)

    canvas = r.TCanvas()

    marker = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
    color = [2,3,4,6,7,2,3,4,6,7]

    plot = r.TGraphErrors()
    plot.SetMarkerStyle(8)
    plot.SetMarkerSize(0.4)
    plot.SetTitle(description + " " + paramName)
    plot.GetXaxis().SetTitle('Scan number')
    plot.GetYaxis().SetTitle(paramName)

#        XorY = scan[scan.keys()[0]]

    i = 0
    for scan in param:
        scanno= int(scan.strip("Scan_"))
        for bcid in param[scan]:
            try:
                value = int(bcid)
            except: TypeError
            else:
                plot.SetPoint(i, scanno, param[scan][bcid])
                i = i+1

    plot.GetXaxis().SetTitle('Scan')
    plot.GetYaxis().SetTitle(paramName)
    plot.Draw("AP")
    canvas.SaveAs(outFileName +'(')

    max = plot.GetHistogram().GetMaximum()
    min = plot.GetHistogram().GetMinimum()

    plot_byBX=[r.TGraphErrors() for i in range(noScans)]

    for scan in param:
        scanno= int(scan.strip("Scan_"))
        i = 0
        for bcid in param[scan]:
            try:
                value = int(bcid)
            except: TypeError
            else:
                plot_byBX[int(scanno)-1].SetPoint(i, int(bcid), param[scan][bcid])
                plot_byBX[int(scanno)-1].SetPointError(i, 0.0, paramErr[scan][bcid])
                i = i+1

    plot_byBX[0].SetMaximum(max*1.1)
    plot_byBX[0].SetMinimum(min)
    plot_byBX[0].SetMarkerColor(color[0])        
    plot_byBX[0].SetMarkerStyle(marker[0])
    plot_byBX[0].SetMarkerSize(0.4)
    
    plot_byBX[0].SetTitle(description + " " + paramName + " Scan  1")
    plot_byBX[0].GetXaxis().SetTitle('BCID')
    plot_byBX[0].GetYaxis().SetTitle(paramName)
    plot_byBX[0].Draw("AP")
    for i in range(1,noScans):
        plot_byBX[i].SetTitle(description + " " + paramName +" " + " Scan " +str(i+1))
        plot_byBX[i].SetMarkerColor(color[i])        
        plot_byBX[i].SetMarkerStyle(marker[i])
        plot_byBX[i].SetMarkerSize(0.4)
        plot_byBX[i].Draw("P")
            
    canvas.BuildLegend(0.65,0.8,0.95,0.95,"")
    plot_byBX[0].SetTitle(description + " " + paramName)
    canvas.SaveAs(outFileName +'(')



if __name__ == '__main__':

    configFile = sys.argv[1]

    config=open(configFile)
    ConfigInfo = json.load(config)
    config.close()

    Fill = ConfigInfo['Fill']
    AnalysisDir = ConfigInfo['AnalysisDir']
    Luminometer = ConfigInfo['Luminometer']
    Corr = ConfigInfo['Corr']
    FitName = ConfigInfo['FitName']
    InputFitResultsFile = ConfigInfo['InputFitResultsFile']

    corrFull = makeCorrString(Corr)
    InputFitResultsFile = AnalysisDir + "/" + Luminometer + "/results/" + corrFull + "/" + InputFitResultsFile 

    InputXsecResultsFile = AnalysisDir + "/" + Luminometer + "/results/" + corrFull + "/" + 'LumiCalibration_'+ Luminometer+ '_'+ FitName + "_" + str(Fill)+'.pkl'

    outFileName = AnalysisDir + "/" + Luminometer + "/results/" + corrFull + "/plots_"+FitName+"_"+Fill+".pdf"

    fitResult = fitResultReader(InputFitResultsFile)
    xsecResult = fitResultReader(InputXsecResultsFile)

    description = Fill + " " + Luminometer + " " + FitName

# special treatment for xsec plot where the result is per scan _pair_

    paramName = "xsec"
    paramErrName = "xsecErr"
    param = xsecResult.getFitParam(paramName)
    paramErr = xsecResult.getFitParam(paramErrName)
    addXsecPlots(description, paramName, param, paramErr, outFileName) 

# Fit function parameters come in pairs of: value, valueErr
# Hand over value, valuerErr dictionaries to plotAll
# For other parameters, e.g. fit status, chi2, ndf, put them in separate list, for which pseudo error dictionary is provided where all errrors are set to 0.0
# First find out where block of fit function parameters with their errors is
    paramlist = fitResult.fitParamNames[3:]
    lasterridx = 0
    for idx, entry in enumerate(paramlist):
        if "Err" in entry:
            lasterridx = idx
    fitlist = paramlist[:(lasterridx+1)]
    otherlist = paramlist[(lasterridx+1):]
    
# pair fit function parameters with their errors
    fiterrpairs = zip(fitlist[0::2], fitlist[1::2])

    for entry in fiterrpairs:
        value = entry[0]
        err = entry[1]
        paramName = value
        param = fitResult.getFitParam(value)
        paramErr = fitResult.getFitParam(err)
        canvas = r.TCanvas()
        addPlots(description, paramName, param, paramErr, outFileName) 

    import copy
    for entry in otherlist:
        paramName = entry
        param = fitResult.getFitParam(paramName)
        paramErr = copy.deepcopy(param)
        for a in paramErr:
            for b in paramErr[a]:
                paramErr[a][b] = 0.0
        addPlots(description, paramName, param, paramErr, outFileName) 


# chi/ndof plot

    paramName = "chi2/ndof"
    chi2 = fitResult.getFitParam("chi2")
    ndof = fitResult.getFitParam("ndof")
    for a in chi2:
        for b in chi2[a]:
            num = chi2[a][b]
            denom = ndof[a][b]
            param[a][b] = num/denom
    paramErr = copy.deepcopy(param)
    for a in paramErr:
        for b in paramErr[a]:
            paramErr[a][b] = 0.0
    addPlots(description, paramName, param, paramErr, outFileName) 


    canvas = r.TCanvas()
    canvas.SaveAs(outFileName +']')
