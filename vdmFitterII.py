import FitManager
import SG_Fit
import SGConst_Fit
import DG_Fit
import DGConst_Fit
import SimCapSigma_PCCAndVtx_Fit
import GSupGConst_Fit
import DG_2D_Fit
from vdmUtilities import showAvailableFits
from vdmUtilities import orderedIntKeysFirst

import sys
import json
import pickle
import os
import ROOT as r

def doRunVdmFitter(Fill, FitName, InputGraphsFiles, OutputDir, PlotsTempPath, FitConfigInfo):

    showAvailableFits()
    
    availableFits = FitManager.get_plugins(FitManager.FitProvider)

    key = FitName + '_Fit'
    if key not in availableFits:
        print "Fit " + FitName + " requested via json file does not exist, nothing to fit with, exit."
        sys.exit(1)

    fitter = availableFits[FitName+'_Fit']()

    FitLogFile = OutputDir + FitName +'.log'
    fitlogfile = open(FitLogFile,'w') 
    sysstdout = sys.stdout
    sys.stdout = fitlogfile
    sysstderr = sys.stderr
    sys.stderr = fitlogfile

# temporarily: move graphs files over from forTmpStorage directory
#list = os.listdir('./forTmpStorage/')
#import shutil
#for element in list:
#    shutil.copy('./forTmpStorage/'+element, InputDataDir)

# for 2D fits

    if '_2D' in FitName:

# test that when 2D fit function is requested, the graph file used is also a 2D one
        if not '2D' in InputGraphsFiles:
            print "--?? You selected a 2D fitting function, but chose as input a graphs file without the \"2D\" in its name"
            print "??--"
            print " "
            sys.exit(1)

    for graphFile in InputGraphsFiles:
        if not os.path.isfile(graphFile):        
            print "--?? Input data file ", graphFile ," does not exist"
            print "??--"
            print " "
            sys.exit(1)
        if (not any('VTX' in graph for graph in InputGraphsFiles) and len(InputGraphsFiles)>1):
            print "--?? Input data file ", graphFile ," does not correspond to Vertex file"
            print "??--"
            print " "
            sys.exit(1)

    graphsAll_dict = {}
    graphsAll_list = []
    resultsAll = {}

    for graphFile in InputGraphsFiles:
        print " "
        print "Now open input graphs file: ", graphFile
        infile = open(graphFile, 'rb')
        graphsAll_dict = pickle.load(infile)
        infile.close()
        graphsAll_list.append(graphsAll_dict)

# if input file is 2D graphs file, also open the corresponding 1D graph file
    if '_2D' in FitName:
        fileName1D = InputGraphsFile.replace("graphs2D", "graphs")
        infile1D = open(fileName1D, 'rb')
        graphs1D = pickle.load(infile1D)



# first loop over scan numbers

    orderedKeyList=[]
    if (len(InputGraphsFiles)==1):
     for keyAll in sorted(graphsAll_dict.keys()):
        graphs = {}
        results = {}
        graphs = graphsAll_dict[keyAll]
        if '_2D' in FitName:
            keyX = "Scan_" + keyAll.split("_")[1]
            keyY = "Scan_" + keyAll.split("_")[2]
            graphsX = graphs1D[keyX] 
            graphsY = graphs1D[keyY] 


# order keys in natural order, i.e. from smallest BCID to largest

# determine which of the bcid among those with collisions are indeed represented with a TGraphErrors() in the input graphs file
# need to do this because PCC uses only subset of 5 bcids of all possible bcids with collisions

        for key in orderedIntKeysFirst(graphs.keys()):
            print "------>>>>"
            print "Now fitting BCID ", key
            graph = graphs[key]
            if '_2D' in FitName:
                result = fitter.doFit2D(graph, graphsX[key], graphsY[key], FitConfigInfo)
                for entry in result:
                    print ">>", result, type(result)
                results[key] = result
                functions = result[0]
                canvas = fitter.doPlot2D(graphsX[key], graphsY[key], functions, Fill)
            else:    
                result = fitter.doFit(graph, FitConfigInfo)
                results[key] = result
                functions = result[0]
                canvas = fitter.doPlot(graph, functions, Fill, PlotsTempPath[0])

     resultsAll[keyAll] = results
     table = [fitter.table]
     sys.stdout = sysstdout
     sys.stderr = sysstderr
     fitlogfile.close()

     return resultsAll, table
    else: #Sim Fit
     for (keyAll1,keyAll2) in sorted(zip(graphsAll_list[0].keys(), graphsAll_list[1].keys())):
         graphs  = {}
         graphs1 = {}
         graphs2 = {}
         results = {}

         graphs1 = graphsAll_list[0][keyAll1]
         graphs2 = graphsAll_list[1][keyAll1]
        
         ds = [graphs1, graphs2]
         for k in graphs1.iterkeys():
             graphs[k] = list(graphs[k] for graphs in ds)
# order keys in natural order, i.e. from smallest BCID to largest

# determine which of the bcid among those with collisions are indeed represented with a TGraphErrors() in the input graphs file
# need to do this because PCC uses only subset of 5 bcids of all possible bcids with collisions
         for key in orderedIntKeysFirst(graphs.keys()):
            print "------>>>>"
            print "Now fitting BCID ", key
            result = fitter.doFit(graphs[key], FitConfigInfo)
            results[key] = result
            functions = result[0]
            canvas = fitter.doPlot(graphs[key][0], functions[:4], Fill, PlotsTempPath[0]) 
            canvas = fitter.doPlot(graphs[key][1], functions[4:], Fill, PlotsTempPath[1])
     sys.stdout = sysstdout
     sys.stderr = sysstderr
     fitlogfile.close()
     table = [fitter.table_Luminometer1, fitter.table_Luminometer2]
     return resultsAll, table 


if __name__ == '__main__':


    ConfigFile = sys.argv[1]

    Config=open(ConfigFile)
    ConfigInfo = json.load(Config)
    Config.close()


    Fill = str(ConfigInfo['Fill'])
    Luminometer = str(ConfigInfo['Luminometer'])
    Corr = ConfigInfo['Corr']
    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    FitName = str(ConfigInfo['FitName'])
    FitConfigFile = str(ConfigInfo['FitConfigFile'])
    PlotsTempPath = ConfigInfo['PlotsTempPath']

    corrFull = ""
    for entry in Corr:
        corrFull = corrFull + '_' + str(entry)

    if corrFull[:1] == '_':
        corrFull = corrFull[1:]

    if  not corrFull:
        corrFull = "noCorr"

    InputGraphsFiles = []
    OutputDirs = []
    
    if 'InputGraphsFile' in vdmFitterConfig:
        InputGraphsFile = AnalysisDir + '/' + Luminometer + '/' + vdmFitterConfig['InputGraphsFile']
        InputGraphsFiles.append(InputGraphsFile)
    else:
        defaultGraphsFile = 'graphs' + '/' + 'graphs_' + Fill + '_' + corrFull + '.pkl'
        InputGraphsFile = AnalysisDir + '/' + Luminometer + '/' +  defaultGraphsFile
        InputGraphsFiles.append(InputGraphsFile)

    OutputDir = './' + AnalysisDir + '/' + Luminometer + '/results/' + corrFull + '/'
    OutputDirs.append(OutputDir)

    if 'Sim' in FitConfigFile:
        if 'InputSimGraphsFile' in vdmFitterConfig:
            InputSimGraphsFile = AnalysisDir + '/' + 'VTX' + '/' + vdmFitterConfig['InputSimGraphsFile']
            InputGraphsFiles.append(InputSimGraphsFile)
        else:
            defaultSimGraphsFile = 'graphs' + '/' + 'graphs_' + Fill + '_' + corrFull + '.pkl'
            InputSimGraphsFile = AnalysisDir + '/' + 'VTX' + '/' +  defaultSimGraphsFile
            InputGraphsFiles.append(InputSimGraphsFile)
        OutputDir = './' + AnalysisDir + '/' + 'VTX' + '/results/' + corrFull + '/'
        OutputDirs.append(OutputDir)
            
    for OutputDir in OutputDirs:
        if not os.path.isdir(OutputDir):
            print "Requested output directory ", OutputDir , " does not exist."
            print "Please check if input for chosen corrections is available."
            sys.exit(1)

    print " "
    print "ATTENTION: Output will be written into ", OutputDirs[0]
    print "Please check there for log files."

    print " "

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

# needs to be the same name as assumed in vdmUtilities, where it is ./plotstmp
    for path in PlotsTempPath:
        if not os.path.isdir(path[0]):
            os.makedirs(path, 0755)
        else:
            filelist = os.listdir(path[0])
            for element in filelist:
                if ('ps' or 'root') in element:
                    os.remove(path[0]+element)

    resultsAll = {}
    table = []

    resultsAll, table = doRunVdmFitter(Fill, FitName, InputGraphsFiles, OutputDirs[0], PlotsTempPath, FitConfigInfo)

    for key in resultsAll:
        print "keyResutsAll", key

    for (i,OutputDir) in enumerate(OutputDirs):
        outResults ='./'+ OutputDir + '/'+FitName+'_FitResults.pkl'
        outFile = open(outResults, 'wb')
        pickle.dump(table[i], outFile)
        outFile.close()

        csvfile = open('./'+ OutputDir + '/'+FitName+'_FitResults.csv', 'wb')
        writer = csv.writer(csvfile)
        writer.writerows(table[i])
        csvfile.close()
    
        outResults ='./'+ OutputDir + '/'+FitName+'_Functions.pkl'
        outFile = open(outResults, 'wb')
        pickle.dump(resultsAll, outFile)
        outFile.close()

    outFileMinuit = './'+OutputDirs[0] + '/'+FitName+'_Minuit.log'
    os.rename(MinuitLogFile, outFileMinuit)

    output_FittedGraphs = dict(zip(OutputDirs,PlotsTempPath))
    for OutputDir in output_FittedGraphs:
        outPdf = './'+OutputDir + '/'+FitName+'_FittedGraphs.pdf'
        PlotsPath = output_FittedGraphs[OutputDir][0]
        filelist = os.listdir(PlotsPath)
        merge =-999.
        for element in filelist:
            if element.find(".ps") > 0:
                merge = +1.
        if merge > 0:
            os.system("gs -dNOPAUSE -sDEVICE=pdfwrite -dBATCH -sOutputFile="+outPdf+" " + PlotsPath+"/*.ps")

        outRoot = './'+OutputDir + '/'+FitName+'_FittedGraphs.root'
        if os.path.isfile(outRoot):
            os.remove(outRoot)
        merge =-999.
        for element in filelist:
            if element.find(".root") > 0:
                merge = +1.
        if merge > 0:
            os.system("hadd " + outRoot + "  " + PlotsPath + "*.root")



    


