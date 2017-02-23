import sys, json, pickle, csv

def doMakeLengthScaleFile(ConfigInfo):

    table = {}
    csvtable = []

    FillLS = ConfigInfo["FillLS"]
    InputDataDir = str(ConfigInfo['InputDataDir'])

    if 'SingleBeamScans' in ConfigInfo:
        SingleBeamScans = ConfigInfo['SingleBeamScans']
    else:
        SingleBeamScans = []
    table['SingleBeamScans'] = SingleBeamScans

# get correction factors

    LSValuesFile = InputDataDir + '/LengthScale_' + FillLS + '.json'
    LSConfigInfo = open(LSValuesFile)
    LSValues =json.load(LSConfigInfo)
    LSConfigInfo.close()

    LS_ScaleX = LSValues['LS_ScaleX']
    LS_ScaleY = LSValues['LS_ScaleY']
    if 'LS_ScaleX1' in LSValues:
        LS_ScaleX1 = LSValues['LS_ScaleX1']
    else:
        LS_ScaleX1 = LS_ScaleX
    if 'LS_ScaleY1' in LSValues:
        LS_ScaleY1 = LSValues['LS_ScaleY1']
    else:
        LS_ScaleY1 = LS_ScaleY
    if 'LS_ScaleX2' in LSValues:
        LS_ScaleX2 = LSValues['LS_ScaleX2']
    else:
        LS_ScaleX2 = LS_ScaleX
    if 'LS_ScaleY2' in LSValues:
        LS_ScaleY2 = LSValues['LS_ScaleY2']
    else:
        LS_ScaleY2 = LS_ScaleY

    table['LS_ScaleX'] = LS_ScaleX
    table['LS_ScaleY'] = LS_ScaleY
    table['LS_ScaleX1'] = LS_ScaleX1
    table['LS_ScaleY1'] = LS_ScaleY1
    table['LS_ScaleX2'] = LS_ScaleX2
    table['LS_ScaleY2'] = LS_ScaleY2

    for entry in table:
        csvtable.append([entry])
        csvtable.append([table[entry]])

    return table, csvtable



if __name__ == '__main__':

# read config file
    ConfigFile = sys.argv[1]

    Config=open(ConfigFile)
    ConfigInfo = json.load(Config)
    Config.close()

    Fill = ConfigInfo["Fill"]
    AnalysisDir = ConfigInfo["AnalysisDir"]
    OutputDir = AnalysisDir +'/'+ConfigInfo["OutputSubDir"]


    table = {}
    csvtable = []
    table, csvtable = doMakeLengthScaleFile(ConfigInfo)

    csvfile = open(OutputDir+'/LengthScale_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()


    with open(OutputDir+'/LengthScale_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)
