import pickle
import sys
import argparse
import ROOT
import math


parser = argparse.ArgumentParser(description='Compare the beam width as measured by two detectors')
parser.add_argument('--files', type=str, default="", help='The two filenames (comma-spearated)')
parser.add_argument('--names', type=str, default="", help="Names of the two detectors")
parser.add_argument('--label', type=str, default="", help="Label for output file")
parser.add_argument('--pccbcids', type=int, default=0, help="Use only PCC BCIDs (default 0)")

args = parser.parse_args()
ROOT.gROOT.SetBatch(ROOT.kTRUE)
try:
    args.names=args.names.split(",")
except:
    args.names=["1","2"]

filenames=args.files.split(",")
PCCBCIDs=['51','771','1631','2211','2674']

beamWidths={}

for filename in filenames:
    beamWidths[filename]={}
    file=open(filename)
    fits=pickle.load(file)
    
    capInd=fits[0].index('CapSigma')
    capErrInd=fits[0].index('CapSigmaErr')
    
    for fit in fits:
        if fit[0]=='Scan':
            continue
        if fit[2]=='sum':
            continue
        if args.pccbcids==0 or fit[2] in PCCBCIDs:
            beamWidths[filename][(fit[0],fit[1],fit[2])]=(float(fit[capInd]),float(fit[capErrInd]))
            #print fit[0],fit[1],fit[2],fit[capInd],fit[capErrInd]


can=ROOT.TCanvas("can","",1200,700)
can.Divide(2,1)

pullLabel="("+args.names[1]+"-"+args.names[0]+")/error"
systLabel="("+args.names[1]+"-"+args.names[0]+")/Average [in percent]"

pullDist=ROOT.TH1F("pullDist","Pull Distribution of #Sigma "+args.names[1]+"-"+args.names[0]+";Pull in beam width "+pullLabel,40,-5,5)
systError=ROOT.TH1F("systError","Systematic Error of #Sigma "+args.names[1]+"-"+args.names[0]+";"+systLabel,50,-3,3)

pullLEG=ROOT.TLegend(0.1,0.8,0.4,0.9)
pullLEG.SetFillColor(ROOT.kWhite)
systLEG=ROOT.TLegend(0.1,0.8,0.4,0.9)
systLEG.SetFillColor(ROOT.kWhite)

for scanKey in beamWidths[filenames[0]]:
    if scanKey in beamWidths[filenames[1]]:
        diff=beamWidths[filenames[1]][scanKey][0]-beamWidths[filenames[0]][scanKey][0]
        ave=0.5*(beamWidths[filenames[1]][scanKey][0]+beamWidths[filenames[0]][scanKey][0])
        error=math.sqrt(beamWidths[filenames[1]][scanKey][1]*beamWidths[filenames[1]][scanKey][1]+beamWidths[filenames[0]][scanKey][1]*beamWidths[filenames[0]][scanKey][1])+0.0001
        pullDist.Fill(diff/error)
        systError.Fill(diff*100/ave)
        print scanKey,beamWidths[filenames[1]][scanKey][0],beamWidths[filenames[0]][scanKey][0],diff*100/ave


can.cd(1)
systError.Draw()
systError.Fit("gaus")
systLEG.AddEntry(systError,"Mean:  "+str("{0:.3f}".format(systError.GetMean())),"l")
systLEG.AddEntry(systError,"RMS:   "+str("{0:.3f}".format(systError.GetRMS())),"l")
systLEG.Draw("same")
print systError.GetMean(),systError.GetRMS()

can.cd(2)
pullDist.Draw()
pullDist.Fit("gaus")
pullLEG.AddEntry(pullDist,"Mean:  "+str("{0:.3f}".format(pullDist.GetMean())),"l")
pullLEG.AddEntry(pullDist,"RMS:   "+str("{0:.3f}".format(pullDist.GetRMS())),"l")
pullLEG.Draw("same")
print pullDist.GetMean(),pullDist.GetRMS()

can.Update()


can.SaveAs("beamWidth_"+args.names[0]+"_"+args.names[1]+"_pccbcids"+str(args.pccbcids)+".png")
