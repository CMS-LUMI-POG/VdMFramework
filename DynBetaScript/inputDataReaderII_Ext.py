## Extended class to store vdm data; standard+BeamBeam+FitResults
import ROOT as r
import pickle
import math

class vdmInputData_Ext:

# class meant to hold relevant data
# to be instantiated per scan


    def __init__(self, scanNumber):

        self.scanNumber = scanNumber

# -->> from Scan file

        self.fill = 0
        self.date = ""
        self.run = 0
        self.inputDIPFile = ""
        self.scanTimeWindows = []
        self.betaStar = 0
        self.angle = 0
        self.offset = 0.0
        self.particleTypeB1 = ""
        self.particleTypeB2 = ""
        self.energyB1 = 0.0
        self.energyB2 = 0.0

        self.scanName = ""
        self.scanNamesAll = []

# scan points info table
        self.sp = {}
        self.nSP = 0

# per scan point
        self.tStart = []
        self.tStop = []
        self.displacement = []

# to allow for SP coordinates that vary with bcid
        self.spPerBX = {}

# -->> from Beam Current file

# currents info table
        self.curr = {}
    
# per scan point
        self.avrgDcctB1 = []
        self.avrgDcctB2 = []
        self.sumAvrgFbctB1 = []
        self.sumAvrgFbctB2 = []
        self.sumCollAvrgFbctB1 = []
        self.sumCollAvrgFbctB2 = []
        self.avrgFbctB1PerSP = []
        self.avrgFbctB2PerSP = []

# per BX
        self.avrgFbctB1 = []
        self.avrgFbctB2 = []
        self.avrgFbctB1PerBX = {}
        self.avrgFbctB2PerBX = {}

# BCID lists
        self.collidingBunches = []
        self.collidingBunchesPerSP=[]

# not all colliding bunches are used for all luminometers

        self.usedCollidingBunches = []

# -->> from Luminometer Data file

        self.luminometerDataSource = ""
        self.lum = {}
# per BX
        self.lumi = []
        self.lumiErr = []
        self.sumLumi = []
        self.sumLumiErr = []
        self.lumiPerBX = {}
        self.lumiErrPerBX = {}
# per scan point
        self.lumiPerSP = []
        self.lumiErrPerSP = []
        self.splumiPerBX={}

# --> from BeamBeamFile
        # file fragment for current scan
        self.bb={} 
        # BeamBeam correction per BX at scanpoints
        self.bbPerBX={}

# --> from FitResultsFile
        # file fragment for fit results
        self.fitres={}
        # data from fit results
        self.CapSigmaPerBX={}
        self.meanPerBX={}

# ---> simulated data
        # bb-corrected scanpoints
        self.corrspPerBX={}
        #averaged bunch current
        self.averCurrPerBX={}
        #normalized beam separation per BX
        self.normBeamSepPerBX={}
        #normalized bb corrected beam separation per BX
        self.normBeamSepPerBX_BBcorr={}
        #emittance per BX
        self.emitPerBX={}

    ####### -->> Scan_ data reading
    def GetScanInfo(self, fileName):

        table = {}
        with open(fileName, 'rb') as f:
            table = pickle.load(f)

        self.fill = table["Fill"]
        self.date = table["Date"]
        self.run = table["Run"]
        self.inputDIPFile = table["InputDIPFile"]
        self.scanTimeWindows = table["ScanTimeWindows"]
        self.betaStar = table["BetaStar"]
        self.angle = table["Angle"]
        self.particleTypeB1 = table["ParticleTypeB1"]
        self.particleTypeB2 = table["ParticleTypeB2"]
        self.energyB1 = table["EnergyB1"]
        self.energyB2 = table["EnergyB2"]

        self.scanNamesAll = table["ScanNames"]

        key = "Scan_" + str(self.scanNumber)
        self.scanName = table["ScanNames"][int(self.scanNumber) -1]
        self.offset = table["Offset"][int(self.scanNumber) -1]
        self.sp = table[key]

        self.tStart = [entry[3] for entry in self.sp] 
        self.tStop = [entry[4] for entry in self.sp] 
        self.displacement = [entry[5] for entry in self.sp] 
        self.nSP = len(self.displacement)

        return
    
    ####### -->> BeamCurrents_ data reading
    def GetBeamCurrentsInfo(self, fileName):

        table = {}
        with open(fileName, 'rb') as f:
            table = pickle.load(f)
        
        key = "Scan_" + str(self.scanNumber)
        self.curr = table[key]
 
# curr values for filled bunches per beam, first index SP, second index BCID
        self.avrgFbctB1PerSP = [{} for entry in self.curr]
        self.avrgFbctB2PerSP = [{} for entry in self.curr]
        for entry in self.curr:
            self.avrgFbctB1PerSP[int(entry[2])-1] = entry[7]
            self.avrgFbctB2PerSP[int(entry[2])-1] = entry[8]

        for index, value in enumerate(self.curr):
            self.avrgDcctB1.append(self.curr[index][3])
            self.avrgDcctB2.append(self.curr[index][4])
            self.sumAvrgFbctB1.append(self.curr[index][5])
            self.sumAvrgFbctB2.append(self.curr[index][6])

# BCID list, colliding bunches, for scanpoints
        self.collidingBunchesPerSP=[[] for a in range(self.nSP)]
        for i in range(self.nSP):
            BunchListB1PerSP=list(self.avrgFbctB1PerSP[i].keys())
            BunchListB2PerSP=list(self.avrgFbctB2PerSP[i].keys())
            CollidingBunchPerSP=[]
            for j in range(len(BunchListB1PerSP)):
                if BunchListB1PerSP[j] in BunchListB2PerSP:
                    if BunchListB1PerSP[j]!='sum':
                        CollidingBunchPerSP.append(BunchListB1PerSP[j])
            self.collidingBunchesPerSP[i]=CollidingBunchPerSP

# BCID list for the scan
        collidingBunchesForScan=[]
        for i in range(self.nSP):
            for j in range(len(self.collidingBunchesPerSP[i])):
                if self.collidingBunchesPerSP[i][j] not in collidingBunchesForScan:
                    collidingBunchesForScan.append(self.collidingBunchesPerSP[i][j])
        self.collidingBunches=collidingBunchesForScan

# natural order per BX for analysis: curr values only for colliding bunches
# first index BCID (for colliding bx only), second index SP
        self.avrgFbctB1 = [[] for a in range(len(self.collidingBunches))]
        self.avrgFbctB2 = [[] for a in range(len(self.collidingBunches))]
        spNumberPerBX=[[] for a in range(len(self.collidingBunches))]
        for i, bx in enumerate(self.collidingBunches):
            for j in range(self.nSP):
                try:
                  value = self.avrgFbctB1PerSP[j][str(bx)]
                  self.avrgFbctB1[i].append(value)
                  value = self.avrgFbctB2PerSP[j][str(bx)]
                  self.avrgFbctB2[i].append(value)                 
                except:
                  print "self.displacement is longer than avrgFbctBPerSP"
                else:
                  spNumberPerBX[i].append(self.displacement[j])
            self.avrgFbctB1PerBX[bx] = self.avrgFbctB1[i]
            self.avrgFbctB2PerBX[bx] = self.avrgFbctB2[i]
            self.spPerBX[bx]=spNumberPerBX[i]

        self.sumCollAvrgFbctB1 = [0.0 for a in range(self.nSP)]
        self.sumCollAvrgFbctB2 = [0.0 for a in range(self.nSP)]
        try:
            for j in range(len(self.displacement)):
                try:
                  self.sumCollAvrgFbctB1[j] = self.avrgFbctB1PerSP[j]['sum']
                  self.sumCollAvrgFbctB2[j] = self.avrgFbctB2PerSP[j]['sum']
                except:
                  print "self.displacement is longer than avrgFbctB1PerSP"
        except KeyError, e:
            print 'KeyError in inputDataReader- reason "%s"' % str(e)

        #print self.avrgFbctB1PerBX['1011']

        return

    ######## -->> rates_ data reading
    def GetLuminometerData(self, fileName):

        self.luminometerDataSource = fileName

        table = {}
        with open(fileName, 'rb') as f:
            table = pickle.load(f)

        key = "Scan_" + str(self.scanNumber)
        self.lum = table[key]
 
        self.lumiPerSP = [{} for entry in self.lum]
        self.lumiErrPerSP = [{} for entry in self.lum]
        for entry in self.lum:
            self.lumiPerSP[int(entry[2])-1] = entry[3][0]
            self.lumiErrPerSP[int(entry[2])-1] = entry[3][1]

# determine which of the colliding bunches are in fact used
# for HF should be identical to all colliding ones
# for PCC should only be subset, typically 5

        usedCollidingBunches=[]
        for i, bx in enumerate(self.collidingBunches):
            for j in range(self.nSP):
                try:
                    if str(bx) in self.lumiPerSP[j]:
                        if bx not in usedCollidingBunches:
                            usedCollidingBunches.append(bx)
                except:
                    print "in usedCollidingBunches: BCID ", bx, " is not filled at the scanpoint ", j
        self.usedCollidingBunches = usedCollidingBunches

# this is the natural order for analysis
        self.lumi = [[] for a in range(len(self.usedCollidingBunches))]
        self.lumiErr = [[] for a in range(len(self.usedCollidingBunches))]
        SPNumberPerBX=[[] for a in range(len(self.usedCollidingBunches))]
        for i, bx in enumerate(self.usedCollidingBunches):
            for j in range(self.nSP):
                try:
                    value = self.lumiPerSP[j][str(bx)]
                    self.lumi[i].append(value)
                    valueErr = self.lumiErrPerSP[j][str(bx)]
                    self.lumiErr[i].append(valueErr)
                except:
                    print "in GetLuminometerData: BCID ", bx, "is not filled at the scanpoint ", j
                else:
                    SPNumberPerBX[i].append(self.displacement[j])
            self.lumiPerBX[bx] = self.lumi[i]
            self.lumiErrPerBX[bx] = self.lumiErr[i]
            self.splumiPerBX[bx]=SPNumberPerBX[i]

        self.sumLumi = [0.0 for a in range(self.nSP)]
        self.sumLumiErr = [0.0 for a in range(self.nSP)]
        for j in range(self.nSP):
            try:
                self.sumLumi[j] = self.lumiPerSP[j]['sum'] 
                self.sumLumiErr[j] = self.lumiErrPerSP[j]['sum'] 
            except:
                print "in GetLuminometerData: BCID ", bx, "is not filled at the scanpoint ", j

        return

##### --> BeamBeam data reading
    def GetBeamBeamData(self, fileName):

        table = {}
        with open(fileName, 'rb') as f:
            table = pickle.load(f)

        key = "Scan_" + str(self.scanNumber)
        self.bb = table[key]

        bbCorr=[{} for idx in range(self.nSP)]
        for entry in self.bb:
            if 'X' in str(entry[1]):
                pos=3
            elif 'Y' in str(entry[1]):
                pos=4
            else:
                "something wrong in getBeamBeamData; exit program"
                sys.exit
            bbCorr[int(entry[2])-1]=entry[pos]

        self.bbPerBX={}
        bbCorrList=[[] for idx in range(len(self.usedCollidingBunches))]
        for i, bx in enumerate(self.usedCollidingBunches):
            for j in range(self.nSP):
                try:
                    value=bbCorr[j][str(bx)]
                    bbCorrList[i].append(value)
                except:
                     print "in getBeamBeamData: BCID ", bx, "does not exist at the scanpoint ". j
            self.bbPerBX[bx]=bbCorrList[i]

        #print key
        #print self.bbPerBX['1011']

        return

#### --> FitResults data reading
    def GetFitResults(self,fileName):

        with open(fileName,'rb') as f:
           table=pickle.load(f)

        captions=table[0]
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

        for entry in table:
            if (entry[0]==str(self.scanNumber)) and (str(entry[2])!='sum'):
                bcid=entry[2]
                self.CapSigmaPerBX[str(bcid)]=entry[idx1]
                self.meanPerBX[str(bcid)]=entry[idx2]

        #print self.CapSigmaPerBX['1011']

        return

### --> calculations within scan
### --> apply BeamBeam correction
    def applyBeamBeam(self):
      
        for i, bx in enumerate(self.usedCollidingBunches):
            if len(self.bbPerBX[bx])!=len(self.spPerBX[bx]):
                print "Error in applyBeamBeam, bx=", bx, " lengths are not equal, exit program"
                sys.exit(1)
            else:
                corrSPList=[a+b for a,b in zip(self.spPerBX[bx],self.bbPerBX[bx])]
                self.corrspPerBX[bx]=corrSPList

        #print self.corrspPerBX['1011']

        return

### --> calculate averaged current of bunch
    def averageCurrent(self):

        #the prescription from "W. Kozanecki, Updated implementation of the dynamic-b correction, LLCMWG meeting, 5 Aug 2013" is implemented
        #so, the average current is used as the intensity of opposite bunch

        for i, bx in enumerate(self.usedCollidingBunches):
            Length=len(self.spPerBX[bx])
            meanSPCurr=[]
            for idx in range(Length):
                cur1=self.avrgFbctB1PerBX[bx][idx]
                cur2=self.avrgFbctB2PerBX[bx][idx]
                meanSPCurr.append(0.5*(cur1+cur2))
            
            Current=0.0 
            for sp in range(Length):
                Current=Current+meanSPCurr[sp]

            Current=Current/Length
            self.averCurrPerBX[bx]=Current

        #print self.averCurrPerBX['1011']

        return

### --> normalize Beam Separation
    def normalizeBeamSeparation(self):

        for i,bx in enumerate(self.usedCollidingBunches):
            Length=len(self.spPerBX[bx])
            CapSigma=self.CapSigmaPerBX[bx]
            normSPList=[]
            normSPList_corr=[]
            for idx in range(Length):
                coord=self.spPerBX[bx][idx]
                normSPList.append(math.sqrt(2.0)*coord/CapSigma)
                coord=self.corrspPerBX[bx][idx]
                normSPList_corr.append(math.sqrt(2.0)*coord/CapSigma)
            self.normBeamSepPerBX[bx]=normSPList
            self.normBeamSepPerBX_BBcorr[bx]=normSPList_corr

        #print self.CapSigmaPerBX['1011']
        #print self.normBeamSepPerBX['1032']
        #print self.normBeamSepPerBX_BBcorr['1032']


        return

### --> Emittance estimation
    def calculateEmittance(self):
        
        # for protons only; beams of equal energy, energy in GeV
        gamma=float(self.energyB1)*1E3/938.272
        bStar=float(self.betaStar)
        for i,bx in enumerate(self.usedCollidingBunches):
            self.emitPerBX[bx]=gamma*self.CapSigmaPerBX[bx]*self.CapSigmaPerBX[bx]/2.0/bStar

        #print self.emitPerBX['1011']
        return
        


    ####### -->> Print Info functions    
    def PrintScanInfo(self):

        print ""
        print "===="
        print "PrintScanInfo"
        print "fill", self.fill
        print "date", self.date
        print "run", self.run
        print "inputDIPFile", self.inputDIPFile
        print "scanName", self.scanName
        print "scanNamesAll", self.scanNamesAll
        print "scanTimeWindows", self.scanTimeWindows
        print "betaStar", self.betaStar
        print "angle", self.angle
        print "particleTypeB1", self.particleTypeB1
        print "particleTypeB2", self.particleTypeB2
        print "scanNumber", self.scanNumber
        print "complete ScanPoint info table", self.sp
        print "tStart", self.tStart
        print "tStop", self.tStop
        print "displacement", self.displacement
        print "SP coordinates, which may vary with BX", self.spPerBX
        

    def PrintBeamCurrentsInfo(self):
        
        print ""
        print" ===="
        print "PrintBeamCurrentsInfo"
        print "collidingBunches", self.collidingBunches 
        print "complete current info table", self.curr
        print "avrgDcctB1 per SP", self.avrgDcctB1
        print "avrgDcctB2 per SP", self.avrgDcctB2
        print "sumAvrgFbctB1 per SP", self.sumAvrgFbctB1
        print "sumAvrgFbctB2 per SP", self.sumAvrgFbctB2
        print "avrgFbctB1 per SP", self.avrgFbctB1PerSP
        print "avrgFbctB2 per SP", self.avrgFbctB2PerSP
        print "avrgFbctB1 per BX", self.avrgFbctB1
        print "avrgFbctB2 per BX", self.avrgFbctB2
        print "avrgFbctB1 per BX", self.avrgFbctB1PerBX
        print "avrgFbctB2 per BX", self.avrgFbctB2PerBX


    def PrintLuminometerData(self):

        print self.lum

        print ""
        print" ===="
        print "PrintLuminometerData"
        print "LuminometerDataSource", self.luminometerDataSource
        print "usedCollidingBunches", self.usedCollidingBunches
        print "complete Luminometer Rate info", self.lum
        for idx, val in enumerate(self.lumiPerSP, start=1):
            print "For SP ", idx, " Luminometer Rates for each BX ", val
        for idx, val in enumerate(self.lumiErrPerSP, start=1):
            print "For SP ", idx, " Luminometer Rates Errors for each BX ", val
        for idx, val in enumerate(self.lumi):
            print "For BX index ", idx, " Luminometer Rates for each SP ", val
        for idx, val in enumerate(self.lumiErr):
            print "For BX index ", idx, " Luminometer Rates Errors for each SP ", val
        print "SumLumi over all bx, per SP ", self.sumLumi 
        print "SumLumiErr over all bx, per SP ", self.sumLumiErr 

