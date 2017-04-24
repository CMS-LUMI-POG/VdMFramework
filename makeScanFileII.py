import sys
import os

import tables
import pandas as pd
import numpy as np

import ROOT

def doMakeScanFile(ConfigInfo):

    Date = str(ConfigInfo['Date'])
    Fill = str(ConfigInfo['Fill'])
    InputDIPFile = str(ConfigInfo['InputDIPFile'])
    InputCentralPath = str(ConfigInfo['InputCentralPath'])
    ScanNames= ConfigInfo['ScanNames']
    ScanTimeWindows= ConfigInfo['ScanTimeWindows']
    BetaStar = str(ConfigInfo['BetaStar'])
    Angle = str(ConfigInfo['Angle'])
    Offset = ConfigInfo['Offset']
    ParticleTypeB1 = str(ConfigInfo['ParticleTypeB1'])
    ParticleTypeB2 = str(ConfigInfo['ParticleTypeB2'])
    EnergyB1 = str(ConfigInfo['EnergyB1'])
    EnergyB2 = str(ConfigInfo['EnergyB2'])

    print ""
    print "Making scan file for scan during fill ", Fill
    print "Scans fell into time periods: "
    for entry in ScanTimeWindows:
        print "From ", pd.to_datetime(entry[0], unit = 's'), " to ",   pd.to_datetime(entry[1], unit = 's')  
    print ""
    

    if len(ScanNames) != len(ScanTimeWindows):
        print "Attention: number of scan names and number of scan time windows inconsistent. Exit program."
        sys.exit(1)

    if len(ScanNames) != len(Offset):
        print "Attention: number of scan names and number of offset values inconsistent. Exit program."
        sys.exit(1)


    df = pd.read_csv(InputDIPFile)

# sanity checks

    columnsList = ['fill', 'run', 'ls', 'nb', 'sec', 'msec', 'acqflag', 'step', 'beam', 'ip', 'scanstatus', 'plane', 'progress', 'nominal_separation', 'read_nominal_B1sepPlane', 'read_nominal_B1xingPlane', 'read_nominal_B2sepPlane', 'read_nominal_B2xingPlane', 'set_nominal_B1sepPlane', 'set_nominal_B1xingPlane', 'set_nominal_B2sepPlane', 'set_nominal_B2xingPlane', 'bpm_5LDOROS_B1Names', 'bpm_5LDOROS_B1hPos', 'bpm_5LDOROS_B1vPos,bpm_5LDOROS_B1hErr', 'bpm_5LDOROS_B1vErr,bpm_5RDOROS_B1Names', 'bpm_5RDOROS_B1hPos', 'bpm_5RDOROS_B1vPos', 'bpm_5RDOROS_B1hErr', 'bpm_5RDOROS_B1vErr', 'bpm_5LDOROS_B2Names', 'bpm_5LDOROS_B2hPos', 'bpm_5LDOROS_B2vPos', 'bpm_5LDOROS_B2hErr', 'bpm_5LDOROS_B2vErr', 'bpm_5RDOROS_B2Names', 'bpm_5RDOROS_B2hPos', 'bpm_5RDOROS_B2vPos', 'bpm_5RDOROS_B2hErr', 'bpm_5RDOROS_B2vErr', 'atlas_totInst', 'nominal_separation_plane']

    extractedList = df.columns.values.tolist()
    if('nominal_separation_plane' in extractedList):
        print "nominal_separation_plane in extractedList: this column is used"
    else:
        print "nominal_separation_plane not in extractedList: plane column is used"

    #if not (columnsList == extractedList):
       # print "Attention: First line in dip csv file not as expected, check file integrity. Exit program."
        #sys.exit(1)

    FillfromDip = df['fill'][0]

    if (Fill != str(FillfromDip)):
            print("Mismatch between fill info from dip and from config file. Exit program.")
            sys.exit(1)
    
# check that there is only one fill number in file

    fillfromDipmean = df['fill'].mean()
    if not (float(FillfromDip) == fillfromDipmean):
        print "Attention: Fill number in first row of dip csv file ", FillfromDip, " and mean of the fill number over all rows in the file ", fillfromDipmean, " are different. Check file integrity. Exit program."
        sys.exit(1)

    run = df['run'][0]

# check that there is only one run number in file

    runfromDipmean = df['run'].mean()
    if not (float(run) == runfromDipmean):
        print "Attention: There appears to be more than one run number in the dip file. Is this intentional ?"
        print "List of all runs in dip file: ", df['run'].drop_duplicates().tolist()

    #fill=int(Fill)

    scan = [ [] for entry in ScanNames]
    Run = [0 for entry in ScanNames]
    for i, scanName in enumerate(ScanNames):
        print "Now at scan", scanName
        timeWindow = [ScanTimeWindows[i][0], ScanTimeWindows[i][1]]

# get scan point info from dip file

        dfPreSelect = df[(df.sec >= timeWindow[0]) & (df.sec <= timeWindow[1]) & (df.ip == 32) & (df.acqflag == 1) & (df.scanstatus == 'ACQUIRING') & (df.step != 9999)]

        if('nominal_separation_plane' in extractedList):
            SeparationPlane=dfPreSelect.nominal_separation_plane
        else:
            SeparationPlane=dfPreSelect.plane

# make sure that preselected df contains at most one X (=CROSSING) and one Y (=SEPARATION) scan

        justonescan = False
        if len(dfPreSelect[SeparationPlane == "CROSSING"].index.tolist()) == 0:
            justonescan = True
        if len(dfPreSelect[SeparationPlane == "SEPARATION"].index.tolist()) == 0:
            justonescan = True

        if not(justonescan):
            minIndexX = dfPreSelect[SeparationPlane == "CROSSING"].index.min()
            maxIndexX = dfPreSelect[SeparationPlane == "CROSSING"].index.max()
            minIndexY = dfPreSelect[SeparationPlane == "SEPARATION"].index.min()
            maxIndexY = dfPreSelect[SeparationPlane == "SEPARATION"].index.max()
            if (minIndexX < minIndexY and maxIndexX > maxIndexY) or (minIndexX > minIndexY and maxIndexX < maxIndexY):
                print "Attention: Time search window given in config file contains more than one X and one Y scan, do not know how to handle this. Exit program"
                sys.exit(1)

        nomSep = []
        dfSP = pd.DataFrame()
        if ("X" in scanName):
            dfSP = dfPreSelect[SeparationPlane == "CROSSING"]           
        if ("Y" in scanName):
            dfSP = dfPreSelect[SeparationPlane == "SEPARATION"]

# cut off zero separation points at very beginning and very end of scan            
        
        firstnonzeroIdx = dfSP.index[dfSP['nominal_separation'].nonzero()[0]][0]
        lastnonzeroIdx = dfSP.index[dfSP['nominal_separation'].nonzero()[0]][-1]

        nomSep = dfSP['nominal_separation'][range(firstnonzeroIdx, lastnonzeroIdx+1)].dropna().drop_duplicates().tolist()

        run = dfSP['run'].drop_duplicates().tolist()[0]

        if len(nomSep) == 0:
            print "Attention: Cannot get nominal separations. Exit program."
            sys.exit(1)
    
# determine time window that goes with each separation

        for idx, entry in enumerate(nomSep):
            DFsingleSP = dfSP[dfSP.nominal_separation == entry]['sec'][range(firstnonzeroIdx, lastnonzeroIdx+1)]
            tstart = DFsingleSP.min() 
            tstop = DFsingleSP.max() 
            relDis = round(entry, 6)
            SP = [idx+1, tstart, tstop, relDis]

            scan[i].append(SP)
            Run[i] = run

    table = {}

    table["Fill"] = Fill
    table["Date"] = Date
    table["Run"] = Run
    table["InputDIPFile"] = InputDIPFile
    table["ScanNames"] = ScanNames
    table["ScanTimeWindows"] = ScanTimeWindows 
    table["BetaStar"] = BetaStar
    table["Angle"] = Angle
    table["Offset"] = Offset
    table["ParticleTypeB1"] = ParticleTypeB1
    table["ParticleTypeB2"] = ParticleTypeB2
    table["EnergyB1"] = EnergyB1
    table["EnergyB2"] = EnergyB2

    csvtable = []

    csvtable.append(["Fill", Fill])
    csvtable.append(["Date", Date])
    csvtable.append(["Run", Run])
    csvtable.append(["InputDIPFile", InputDIPFile])
    csvtable.append(["ScanNames", ScanNames])
    csvtable.append(["ScanTimeWindows",ScanTimeWindows ])
    csvtable.append(["BetaStar",BetaStar ])
    csvtable.append(["Angle",Angle ])
    csvtable.append(["Offset",Offset ])
    csvtable.append(["ParticleTypeB1",ParticleTypeB1 ])
    csvtable.append(["ParticleTypeB2", ParticleTypeB2])
    csvtable.append(["EnergyB1",EnergyB1 ])
    csvtable.append(["EnergyB2", EnergyB2])
    csvtable.append(["scan number", "scan type", "scan points: number, tStart, tStop, relative displacement"])

    for i, scanName in enumerate(ScanNames):
        table["Scan_" + str(i+1)]=[]
        csvtable.append(["Scan_" + str(i+1)] )
        for j in range(len(scan[i])):
            row = [i+1, scanName]
            row.append(j+1)
            row.append(scan[i][j][1])
            row.append(scan[i][j][2])
            row.append(scan[i][j][3])
            csvtable.append(row)
            table["Scan_" + str(i+1)].append(row)

    return table, csvtable



if __name__ == '__main__':

    import pickle, csv, sys, json

    ConfigFile = sys.argv[1]

    Config=open(ConfigFile)
    ConfigInfo = json.load(Config)
    Config.close()

    Fill = str(ConfigInfo['Fill'])
    AnalysisDir = str(ConfigInfo['AnalysisDir'])    
    OutputSubDir = str(ConfigInfo['OutputSubDir'])    

    outpath = './' + AnalysisDir + '/'+ OutputSubDir 

    import os
    dirlist = ['./'+AnalysisDir, outpath]
    for entry in dirlist:
        if not os.path.isdir(entry):
            print "Make directory ", entry
            os.mkdir(entry, 0755 )
            
    table = {}
    csvtable = []

    table, csvtable = doMakeScanFile(ConfigInfo)

    csvfile = open(outpath+'/Scan_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()


    with open(outpath+'/Scan_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)

