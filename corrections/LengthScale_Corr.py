import CorrectionManager
import ROOT as r
import sys
import pickle
from vdmUtilities import *

class LengthScale_Corr(CorrectionManager.CorrectionProvider):

    LS_ScaleX =-999.
    LS_ScaleY =-999.
    LS_ScaleX1 = -999.
    LS_ScaleY1 = -999.
    LS_ScaleX2 = -999.
    LS_ScaleY2 = -999.

    SingleBeamScans = []

    def GetCorr(self, fileName):

        table = {}
        with open(fileName, 'rb') as f:
            table = pickle.load(f)

        self.LS_ScaleX = float(table["LS_ScaleX"])
        self.LS_ScaleY = float(table["LS_ScaleY"])
        self.LS_ScaleX1 = float(table["LS_ScaleX1"])
        self.LS_ScaleY1 = float(table["LS_ScaleY1"])
        self.LS_ScaleX2 = float(table["LS_ScaleX2"])
        self.LS_ScaleY2 = float(table["LS_ScaleY2"])

        self.SingleBeamScans = table["SingleBeamScans"]

        return


    def PrintCorr(self):

        print ""
        print "===="
        print "PrintLSCorr"
        print "LS_ScaleX ", self.LS_ScaleX
        print "LS_ScaleY ", self.LS_ScaleY
        print "LS_ScaleX1 ", self.LS_ScaleX1
        print "LS_ScaleY1 ", self.LS_ScaleY1
        print "LS_ScaleX2 ", self.LS_ScaleX2
        print "LS_ScaleY2 ", self.LS_ScaleY2
        print "===="
        if self.SingleBeamScans:
            print "PrintSingleBeamScans"
            for sbs in self.SingleBeamScans:
                print "Scan "+sbs[0]+": beam "+str(sbs[1])
            print "===="
        print ""


    def doCorr(self,inData,configFile):

        print "Scaling coordinates with lengthscale factors"

        self.GetCorr(configFile)

        self.PrintCorr()

    # apply correction here to coordinate, then write back into entry, check if this really changes value in calling function

        for entry in inData:
            correction = 1.0
            for sbs in self.SingleBeamScans:
                if sbs[0] in entry.scanName:
                    if 'X' in sbs[0] and sbs[1] == 1:
                        correction = self.LS_ScaleX1
                    elif 'Y' in sbs[0] and sbs[1] == 1:
                        correction = self.LS_ScaleY1
                    elif 'X' in sbs[0] and sbs[1] == 2:
                        correction = self.LS_ScaleX2
                    elif 'Y' in sbs[0] and sbs[1] == 2:
                        correction = self.LS_ScaleY2
                    else:
                        continue
                    break
            else:
                if 'X' in entry.scanName:
                    correction = self.LS_ScaleX
                elif 'Y' in entry.scanName:
                    correction = self.LS_ScaleY

            coord = entry.displacement
            coord_corr = [a*correction for a in coord]
            entry.displacement = coord_corr

            for bx in entry.collidingBunches:
                coordinates = entry.spPerBX[bx]
                coordinates_corrected = [a*correction for a in coordinates]
                entry.spPerBX[bx] = coordinates_corrected
