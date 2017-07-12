import pickle, csv, sys, json, os
import ROOT as r
from vdmUtilities import setupDirStructure
from makeScanFileII import doMakeScanFile
from dataPrepII.makeRateFile import doMakeRateFile
from dataPrepII_PCC.makePCCRateFile import doMakePCCRateFile
from makeBeamCurrentFileII import doMakeBeamCurrentFile
from dataPrep_corr.makeBeamBeamFile import doMakeBeamBeamFile
from dataPrep_corr.makeGhostsFile import doMakeGhostsFile
from dataPrep_corr.makeSatellitesFile import doMakeSatellitesFile
from dataPrep_corr.makeLengthScaleFile import doMakeLengthScaleFile
from makeGraphsFileII import doMakeGraphsFile
from makeGraphs2D import doMakeGraphs2D
from vdmFitterII import doRunVdmFitter

r.gROOT.SetBatch(r.kTRUE)

ConfigFile = sys.argv[1]

Config=open(ConfigFile)
ConfigInfo = json.load(Config)
Config.close()


Fill = str(ConfigInfo['Fill'])
Date = str(ConfigInfo['Date'])
Luminometer = str(ConfigInfo['Luminometer'])
AnalysisDir = str(ConfigInfo['AnalysisDir'])    

Corr = ConfigInfo['Corr']

makeScanFile = False
makeScanFile = ConfigInfo['makeScanFile']

makeRateFile = False
makeRateFile = ConfigInfo['makeRateFile']

makeBeamCurrentFile = False
makeBeamCurrentFile = ConfigInfo['makeBeamCurrentFile']

makeBeamBeamFile = False
makeBeamBeamFile =  ConfigInfo['makeBeamBeamFile']

makeGhostsFile =  False
makeGhostsFile =  ConfigInfo['makeGhostsFile']

makeSatellitesFile = False
makeSatellitesFile = ConfigInfo['makeSatellitesFile'] 

makeLengthScaleFile = False
makeLengthScaleFile = ConfigInfo['makeLengthScaleFile']

makeGraphsFile = False
makeGraphsFile = ConfigInfo['makeGraphsFile']

makeGraphs2D = False
makeGraphs2D = ConfigInfo['makeGraphs2D']

runVdmFitter = False
runVdmFitter = ConfigInfo['runVdmFitter']

print ""
print "Running with this config info:"
print "Fill ", Fill
print "Date ", Date
print "Luminometer ", Luminometer
print "AnalysisDir ", AnalysisDir
print "Corrections ", Corr
print "makeScanFile ", makeScanFile
print "makeBeamCurrentFile ", makeBeamCurrentFile
print "makeGraphsFile ", makeGraphsFile
print "runVdmFitter ", runVdmFitter

print ""
setupDirStructure(AnalysisDir, Luminometer, Corr)
print ""

if makeScanFile == True:

    makeScanFileConfig = ConfigInfo['makeScanFileConfig']
    
    print "Running makeScanFile with config info:"
    for key in makeScanFileConfig:
        print key, makeScanFileConfig[key]
    print ""

    makeScanFileConfig['Fill'] = Fill
    makeScanFileConfig['Date'] = Date

    OutputSubDir = str(makeScanFileConfig['OutputSubDir'])    
    outpath = './' + AnalysisDir + '/'+ OutputSubDir 

    table = {}
    csvtable = []

    table, csvtable = doMakeScanFile(makeScanFileConfig)

    csvfile = open(outpath+'/Scan_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(outpath+'/Scan_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)


if makeRateFile == True:

    makeRateFileConfig = ConfigInfo['makeRateFileConfig']
    makeRateFileConfig['Fill'] = Fill
    makeRateFileConfig['AnalysisDir'] = AnalysisDir

    print "Running makeRateFile with config info:"
    for key in makeRateFileConfig:
        print key, makeRateFileConfig[key]
    print ""

    OutputSubDir = AnalysisDir + "/" + str(makeRateFileConfig['OutputSubDir'])

    table = {}
    csvtable = []

    if Luminometer=='PCC':
        table, csvtable = doMakePCCRateFile(makeRateFileConfig)
    else:
        table, csvtable = doMakeRateFile(makeRateFileConfig)

    csvfile = open(OutputSubDir+'/Rates_'+ Luminometer + '_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(OutputSubDir+'/Rates_' + Luminometer +  '_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)
            

if makeBeamCurrentFile == True:

    makeBeamCurrentFileConfig = ConfigInfo['makeBeamCurrentFileConfig']
    makeBeamCurrentFileConfig['AnalysisDir'] = AnalysisDir

    print "Running makeBeamCurrentFile with config info:"
    for key in makeBeamCurrentFileConfig:
        print key, makeBeamCurrentFileConfig[key]
    print ""

    OutputSubDir = str(makeBeamCurrentFileConfig['OutputSubDir'])
    outpath = './' + AnalysisDir + '/' + OutputSubDir 

    InputScanFile = './' + AnalysisDir + '/' + str(makeBeamCurrentFileConfig['InputScanFile'])
    with open(InputScanFile, 'rb') as f:
        scanInfo = pickle.load(f)

    Fill = scanInfo["Fill"]     

    table = {}
    csvtable = []

    table, csvtable = doMakeBeamCurrentFile(makeBeamCurrentFileConfig)
    
    csvfile = open(outpath+'/BeamCurrents_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(outpath+'/BeamCurrents_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)


if makeBeamBeamFile == True:

    makeBeamBeamFileConfig = ConfigInfo['makeBeamBeamFileConfig']

    print "Running makeBeamBeamFile with config info:"
    for key in makeBeamBeamFileConfig:
        print key, makeBeamBeamFileConfig[key]
    print ""

    makeBeamBeamFileConfig['AnalysisDir'] = AnalysisDir
    makeBeamBeamFileConfig['Fill'] =  Fill
    makeBeamBeamFileConfig['Luminometer'] =  Luminometer

    OutputDir = AnalysisDir +'/'+makeBeamBeamFileConfig['OutputSubDir']

    table = {}
    csvtable = []
    table, csvtable = doMakeBeamBeamFile(makeBeamBeamFileConfig)

    csvfile = open(OutputDir+'/BeamBeam_' + Luminometer + '_' + str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(OutputDir+'/BeamBeam_'+ Luminometer + '_' +str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)




if makeGhostsFile == True:
    
    makeGhostsFileConfig = ConfigInfo['makeGhostsFileConfig']

    print "Running makeGhostsFile with config info:"
    for key in makeGhostsFileConfig:
        print key, makeGhostsFileConfig[key]
    print ""

    makeGhostsFileConfig['AnalysisDir'] = AnalysisDir
    makeGhostsFileConfig['Fill'] = Fill

    OutputDir = AnalysisDir +'/'+ makeGhostsFileConfig['OutputSubDir']

    table = {}
    csvtable = []
    table, csvtable = doMakeGhostsFile(makeGhostsFileConfig)

    csvfile = open(OutputDir+'/Ghosts_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(OutputDir+'/Ghosts_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)


if makeSatellitesFile == True:
    
    makeSatellitesFileConfig = ConfigInfo['makeSatellitesFileConfig']

    print "Running makeSatellitesFile with config info:"
    for key in makeSatellitesFileConfig:
        print key, makeSatellitesFileConfig[key]
    print ""

    makeSatellitesFileConfig['AnalysisDir'] = AnalysisDir
    makeSatellitesFileConfig['Fill'] = Fill

    OutputDir = AnalysisDir +'/'+ makeSatellitesFileConfig['OutputSubDir']

    table = {}
    csvtable = []
    table, csvtable = doMakeSatellitesFile(makeSatellitesFileConfig)

    csvfile = open(OutputDir+'/Satellites_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(OutputDir+'/Satellites_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)


if makeLengthScaleFile == True:
    
    makeLengthScaleFileConfig = ConfigInfo['makeLengthScaleFileConfig']

    print "Running makeLengthScaleFile with config info:"
    for key in makeLengthScaleFileConfig:
        print key, makeLengthScaleFileConfig[key]
    print ""

    makeLengthScaleFileConfig['AnalysisDir'] = AnalysisDir
    makeLengthScaleFileConfig['Fill'] = Fill

    OutputDir = AnalysisDir +'/'+ makeLengthScaleFileConfig['OutputSubDir']

    table = {}
    csvtable = []
    table, csvtable = doMakeLengthScaleFile(makeLengthScaleFileConfig)

    csvfile = open(OutputDir+'/LengthScale_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(OutputDir+'/LengthScale_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)


if makeGraphsFile == True:

    makeGraphsFileConfig = ConfigInfo['makeGraphsFileConfig']

    print "Running makeGraphsFile with config info:"
    for key in makeGraphsFileConfig:
        print key, makeGraphsFileConfig[key]
    print ""

    makeGraphsFileConfig['AnalysisDir'] = AnalysisDir
    makeGraphsFileConfig['Luminometer'] = Luminometer
    makeGraphsFileConfig['Fill'] = Fill
    makeGraphsFileConfig['Corr'] = Corr

    graphsListAll = {}

    corrFull, graphsListAll = doMakeGraphsFile(makeGraphsFileConfig)

    OutputSubDir = str(makeGraphsFileConfig['OutputSubDir'])
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


if makeGraphs2D == True:

    makeGraphs2DConfig = ConfigInfo['makeGraphs2DConfig']

    print "Running makeGraphs2D with config info:"
    for key in makeGraphs2DConfig:
        print key, makeGraphs2DConfig[key]
    print ""

    makeGraphs2DConfig['AnalysisDir'] = AnalysisDir
    makeGraphs2DConfig['Luminometer'] = Luminometer
    makeGraphs2DConfig['Fill'] = Fill
    makeGraphs2DConfig['Corr'] = Corr

    graphs2DListAll = {}

    corrFull, graphs2DListAll = doMakeGraphs2D(makeGraphs2DConfig)

    InOutSubDir = makeGraphs2DConfig['InOutSubDir']
    outputDir = AnalysisDir + '/' + Luminometer + '/' + InOutSubDir + '/'

#2D graph file should be called graphs2D_<n>_<corrFull>.pkl
    GraphFile2D = outputDir + 'graphs2D_' + Fill + corrFull + '.pkl'

    file2D = open(GraphFile2D, 'wb')
    pickle.dump(graphs2DListAll, file2D)
    file2D.close()


if runVdmFitter == True:

    vdmFitterConfig = ConfigInfo['vdmFitterConfig']

    print "Running runVdmFitter with config info:"
    for key in vdmFitterConfig:
        print key, vdmFitterConfig[key]
    print ""

    vdmFitterConfig['AnalysisDir'] = AnalysisDir
    vdmFitterConfig['Luminometer'] = Luminometer
    vdmFitterConfig['Fill'] = Fill
    vdmFitterConfig['Corr'] = Corr

    FitName = vdmFitterConfig['FitName']
    FitConfigFile = vdmFitterConfig['FitConfigFile']
    PlotsTempPath = [["./plotstmp/"]]

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
        if (corrFull not in InputGraphsFile):
            raw_input("InputGraphsFile extension different than the Correction to be applied!!; Press ENTER to continue.")
        InputGraphsFiles.append(InputGraphsFile)
    else:
        defaultGraphsFile = 'graphs' + '/' + 'graphs_' + Fill + '_' + corrFull + '.pkl'
        InputGraphsFile = AnalysisDir + '/' + Luminometer + '/' +  defaultGraphsFile
        InputGraphsFiles.append(InputGraphsFile)

    OutputDir = './' + AnalysisDir + '/' + Luminometer + '/results/' + corrFull + '/'
    OutputDirs.append(OutputDir)
    
    if 'Sim' in FitConfigFile:
        PlotsTempPath = vdmFitterConfig['PlotsTempPath']
        FitPartner    = vdmFitterConfig['FitPartner']
        if 'InputSimGraphsFile' in vdmFitterConfig:
            InputSimGraphsFile = AnalysisDir + '/' + FitPartner + '/' + vdmFitterConfig['InputSimGraphsFile']
            InputGraphsFiles.append(InputSimGraphsFile)
        else:
            defaultSimGraphsFile = 'graphs' + '/' + 'graphs_' + Fill + '_' + corrFull + '.pkl'
            InputSimGraphsFile = AnalysisDir + '/' + FitPartner + '/' +  defaultSimGraphsFile
            InputGraphsFiles.append(InputSimGraphsFile)
        OutputDir = './' + AnalysisDir + '/' + FitPartner + '/results/' + corrFull + '/'
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
            os.makedirs(path[0], 0755)
        else:
            filelist = os.listdir(path[0])
            for element in filelist:
                if ('ps' or 'root') in element:
                    os.remove(path[0]+element)

    resultsAll = {}
    table = []

    resultsAll, table = doRunVdmFitter(Fill, FitName, InputGraphsFiles, OutputDirs[0], PlotsTempPath, FitConfigInfo)

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


