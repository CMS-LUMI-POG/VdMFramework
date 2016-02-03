import CorrectionManager
import ROOT as r
import sys
import pickle
from vdmUtilities import *

class BeamBeam_Corr(CorrectionManager.CorrectionProvider):

    BBcorr = {}

    def GetCorr(self, fileName):

        table = {}
        with open(fileName, 'rb') as f:
            table = pickle.load(f)

        self.BBcorr = table 

        return


    def PrintCorr(self):

        print ""
        print "===="
        print "PrintBeamBeamCorr"
        print "Correction factors derived from fits to uncorrected distributions"
        print "Correction factors depend on scan number, scan point number and bcid"
        print "===="
        print ""


    def doCorr(self,inData,configFile):

        print "Correcting coordinates with beambeam correction factors"

        self.GetCorr(configFile)
        
        self.PrintCorr()

#put pdf in file with same location and name as correction file, just with ending pdf instead of pkl
        pdfName = configFile[:configFile.index(".pkl")] + ".pdf"
        canvas = r.TCanvas()
        canvas.SetGrid()
                    
# apply correction here to coordinate, then write back into entry, check if this really changes value in calling function

        for entry in inData:
            scanNumber = entry.scanNumber
            key = "Scan_"+str(scanNumber)
            
            corrPerSP  = self.BBcorr[key]        

            corrXPerSP = [{} for value in corrPerSP]
            corrYPerSP = [{} for value in corrPerSP]
            for value in corrPerSP:
                corrXPerSP[value[2]-1] = value[3]
                corrYPerSP[value[2]-1] = value[4]
                
            corrXPerBX = {bx:[] for bx in entry.collidingBunches}
            corrYPerBX = {bx:[] for bx in entry.collidingBunches}
            for bx in entry.collidingBunches:
                print bx
                try:
                    for j in range(entry.nSP):
                        valueX = corrXPerSP[j][str(bx)]
                        corrXPerBX[bx].append(valueX)
                        valueY = corrYPerSP[j][str(bx)]
                        corrYPerBX[bx].append(valueY)
                except:
                    print bx,"is missing; don't fill corr per bx"
            for index in entry.spPerBX:
                if 'X' in entry.scanName:
                    entry.spPerBX[index] = [a+b for a,b in zip(entry.spPerBX[index], corrXPerBX[index])]
                if 'Y' in entry.scanName:
                    entry.spPerBX[index] = [a+b for a,b in zip(entry.spPerBX[index], corrYPerBX[index])]                    

            for bx in entry.collidingBunches:
                histo = r.TGraph()
                histo.SetMarkerStyle(8)
                histo.SetMarkerSize(0.4)
                try:
                    for j in range(entry.nSP):
                        hidx = entry.scanName + "_"+str(bx)
                        htitle= "BeamBeam correction for " + str(hidx)
                        if 'X' in entry.scanName:
                            histo.SetPoint(j,entry.spPerBX[bx][j],corrXPerBX[bx][j]) 
                            histo.SetTitle(htitle)
                        if 'Y' in entry.scanName:
                            histo.SetPoint(j,entry.spPerBX[bx][j],corrYPerBX[bx][j]) 
                            histo.SetTitle(htitle)
                    histo.Draw("AP")
                    histo.GetXaxis().SetTitle('nominal displacement in mm')
                    histo.GetYaxis().SetTitle('correction from beam-beam in mm')
                    canvas.SaveAs(pdfName+'(')
                except:
                    print bx,"is missing; no BeamBeam corr."

        canvas.SaveAs(pdfName + ']')
                        
