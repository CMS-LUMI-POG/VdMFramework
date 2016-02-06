import pickle
import sys
import argparse
import ROOT
import math
import numpy
#ROOT.gROOT.SetBatch(ROOT.kTRUE)

parser = argparse.ArgumentParser(description='Compare the beam width as measured by two detectors')
parser.add_argument('--files', type=str, default="", help='The two filenames (comma-spearated)')
parser.add_argument('--names', type=str, default="", help="Names of the two detectors")
parser.add_argument('--label', type=str, default="", help="Label for output file")
parser.add_argument('--pccbcids', type=int, default=0, help="Use only PCC BCIDs (default 0)")

args = parser.parse_args()
filenames=args.files.split(",")
try:
    args.names=args.names.split(",")
except:
    iCount=1
    args.names=[]
    for filename in filenames:
        args.names.append(str(iCount))
        iCount=iCount+1

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
    file.close()
pulls={}
commonKeys=beamWidths[filenames[0]]
iCount=0
for filename in beamWidths:
    pulls[filename]=ROOT.TH1F("Pull_"+args.names[iCount],"Pull_"+args.names[iCount],50,-5,5)
    newCommonKeys=[]
    for key in beamWidths[filename]:
        if key in commonKeys:
            newCommonKeys.append(key)
    commonKeys=newCommonKeys
    iCount=iCount+1

stdDev=ROOT.TH1F("stdDev",";Standard deviation in percent;",20,0,1)

for key in commonKeys:
    values=[]
    for filename in beamWidths:
        values.append(beamWidths[filename][key][0])
    #print key
    #print values
    #print numpy.mean(values)
    #print numpy.std(values)
    mean=numpy.mean(values)
    std=numpy.std(values)
    stdDev.Fill(std*100/mean)

    iCount=0
    for filename in beamWidths:
        fitError=beamWidths[filename][key][1]
        error=math.sqrt(std*std+fitError*fitError)
        pulls[filename].Fill((values[iCount]-mean)/error)
        iCount=iCount+1




can=ROOT.TCanvas("can","",700,700)
for filename in beamWidths:
    pulls[filename].Draw()
    can.Update()
    raw_input()

stdDev.Draw()
can.Update()
print stdDev.GetMean(),stdDev.GetRMS()
raw_input()

