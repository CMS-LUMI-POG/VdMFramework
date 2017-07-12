import pickle
import sys
import numpy
import ROOT
import math
import argparse



parser=argparse.ArgumentParser()
#parser.add_argument("-h", "--help", help="Display this message.")
parser.add_argument("-f", "--filename", default="",  help="Filename")
parser.add_argument("-u", "--units", default="Barn", help="Barn, mB, uB (Default:  Barn)")
parser.add_argument("-l", "--label", default="PCC",  help="Label for file (Default:  PCC)")
parser.add_argument("-r", "--range", default="",  help="Range for y-axis of plots (Default:  none)")
parser.add_argument("-a", "--allbcids", default=0,  help="Use all bcids (Default:  0)")
parser.add_argument("--plotlabel",  default="2016  (13 TeV)", help="Label for the upper right.  Default:  2016  (13 TeV)")
args=parser.parse_args()



ROOT.gROOT.SetBatch(ROOT.kTRUE)

file=open(args.filename)
fits=pickle.load(file)

xsecInd=fits[0].index('xsec')
xsecErrInd=fits[0].index('xsecErr')

BCIDs=[]
if '5 TeV' in args.plotlabel:
    BCIDs=["644",'1215','2269','2389','2589']

if '13 TeV' in args.plotlabel:
    BCIDs=['41', '281', '872', '1783', '2063']

if args.allbcids !=0:
    BCIDs=[]
    for fit in fits:
        try:
            thisBCID=int(fit[2])
            if thisBCID not in BCIDs:
                BCIDs.append(thisBCID)
        except:
            print fit[2],"is not a valid integer/BCID."
    BCIDs.sort()
    

scans=[]
for fit in fits:
    if fit[0] not in scans:
        scans.append(fit[0])
scans.sort()
    


xsecs=[[],[],[]]
xsecsPerScan={}
for scan in scans:
    xsecsPerScan[scan]=[[],[],[]] #val, error, weight

xsecsPerBCID={}
for bcid in BCIDs:
    xsecsPerBCID[bcid]=[[],[],[]] #val, error, weight

graphs={}
colors=[1,633,417,601,617]
iColor=0
for bcid in BCIDs:
    graphs[bcid]=ROOT.TGraphErrors(5)
    graphs[bcid].SetMarkerColor(colors[iColor%len(colors)]+iColor/len(colors))
    graphs[bcid].SetLineColor(colors[iColor%len(colors)]+iColor/len(colors))
    graphs[bcid].SetMarkerStyle(20)
    iColor=(iColor+1)

for fit in fits:
    #if  fit[2] != "sum": #5_6 was a bad one at 13tev
    if fit[0] != "5_6" and fit[2] != "sum": #5_6 was a bad one at 13tev
    #if fit[0] != "1_2" and fit[0] != "4_3" and fit[2] != "sum":
        try:
            #if float(fit[xsecInd])<0:
            print fit[0],fit[1],int(fit[2]),fit[xsecInd],fit[xsecErrInd]
            scanPair=fit[0]
            BCID=int(fit[2])
            if float(fit[xsecErrInd])<1.0:
                continue
            #print scans.index(fit[0]),BCIDs.index(fit[2])
            #thisXsec=1.011*float(fit[xsecInd])/1e6
            if args.units=="mB":
                thisXsec=float(fit[xsecInd])/1e3
                thisXsecErr=float(fit[xsecErrInd])/1e3
            elif args.units=="Barn":
                thisXsec=float(fit[xsecInd])/1e6
                thisXsecErr=float(fit[xsecErrInd])/1e6
            elif args.units=="uB":
                thisXsec=float(fit[xsecInd])
                thisXsecErr=float(fit[xsecErrInd])

            if thisXsecErr/thisXsec<0.003:
                thisXsecErr=thisXsec*0.003

            thisXsec=thisXsec*1.008

            xsecs[0].append(thisXsec)
            xsecs[1].append(thisXsecErr)
            xsecs[2].append(1./(xsecs[1][-1]*xsecs[1][-1]))
            #print iScan,offset
            xsecsPerScan[scanPair][0].append(thisXsec)
            xsecsPerScan[scanPair][1].append(thisXsecErr)
            xsecsPerScan[scanPair][2].append(1/(xsecsPerScan[scanPair][1][-1]*xsecsPerScan[scanPair][1][-1]))
            xsecsPerBCID[BCID][0].append(thisXsec)
            xsecsPerBCID[BCID][1].append(thisXsecErr)
            xsecsPerBCID[BCID][2].append(1/(xsecsPerScan[scanPair][1][-1]*xsecsPerScan[scanPair][1][-1]))
            iScan=scans.index(scanPair)
            offset=(BCIDs.index(BCID)- len(BCIDs)/2)*(0.85*(len(BCIDs)>15)+0.5*(len(BCIDs)<16))/float(len(BCIDs))
            graphs[BCID].SetPoint(iScan,iScan+offset+1,thisXsec)
            graphs[BCID].SetPointError(iScan,0,thisXsecErr)
            
        except:
            #print "not doing this"
            pass

#print numpy.mean(xsecs[0])
#print numpy.std(xsecs[0])
# FIXME x-y correlation by hand!
overallxsec=numpy.ma.average(xsecs[0],weights=xsecs[2])
sumofweights=0
for weight in xsecs[2]:
    sumofweights=sumofweights+weight
totalError=1/math.sqrt(sumofweights)
print overallxsec,totalError
print "Mean,RMS",numpy.ma.average(xsecs[0]),numpy.ma.std(xsecs[0])



graphPerScan=ROOT.TGraphErrors()
graphPerScan.SetTitle(";Scan Pair;#sigma_{Vis} ("+args.units+")")
graphPerScan.SetMarkerColor(417)
graphPerScan.SetMarkerStyle(20)

iPoint=0
for fit in xsecsPerScan:
    print fit,
    # FIXME x-y correlation by hand!
    average=numpy.ma.average(xsecsPerScan[fit][0],weights=xsecsPerScan[fit][2])
    sumofweights=0
    for weight in xsecsPerScan[fit][2]:
        sumofweights=sumofweights+weight
    if sumofweights==0:
        continue
    totalError=1/math.sqrt(sumofweights)
    print average,totalError
    graphPerScan.SetPoint(iPoint,scans.index(fit)+1,average)
    graphPerScan.SetPointError(iPoint,0,totalError)
    iPoint=iPoint+1


graphPerBCID=ROOT.TGraphErrors()
graphPerBCID.SetTitle(";BCID;#sigma_{Vis} ("+args.units+")")
graphPerBCID.SetMarkerColor(417)
graphPerBCID.SetMarkerStyle(20)

iPoint=0
for fit in xsecsPerBCID:
    print fit,
    # FIXME x-y correlation by hand!
    average=numpy.ma.average(xsecsPerBCID[fit][0],weights=xsecsPerBCID[fit][2])
    sumofweights=0
    for weight in xsecsPerBCID[fit][2]:
        sumofweights=sumofweights+weight
    if sumofweights==0:
        continue
    totalError=1/math.sqrt(sumofweights)
    print average,totalError
    graphPerBCID.SetPoint(iPoint,int(fit),average)
    graphPerBCID.SetPointError(iPoint,0,totalError)
    iPoint=iPoint+1



multigraph=ROOT.TMultiGraph()
multigraph.SetTitle(";Scan Pair;#sigma_{Vis} ("+args.units+")")
leg=ROOT.TLegend(0.45,0.15,0.65,0.43)
leg.SetBorderSize(0)
leg.SetFillColor(0)
for bcid in BCIDs:
    multigraph.Add(graphs[bcid])
    leg.AddEntry(graphs[bcid],"BX = "+str(bcid),"p")


text=ROOT.TLatex(0.93,0.88,args.plotlabel)
text.SetNDC()
text.SetTextFont(62)
text.SetTextSize(0.05)
text.SetTextAlign(31)
text2=ROOT.TLatex(0.15,0.88,"CMS #bf{#scale[0.75]{#it{Preliminary}}}")
text2.SetNDC()
text2.SetTextSize(0.05)
text2.SetTextFont(62)

can=ROOT.TCanvas("can","",800,600)
multigraph.Draw("AP")
if args.range!="":
    multigraph.SetMinimum(float(args.range.split(",")[0]))
    multigraph.SetMaximum(float(args.range.split(",")[1]))
multigraph.GetXaxis().SetRangeUser(0.5,5.5)
multigraph.GetXaxis().SetNdivisions(6)
#multigraph.GetYaxis().SetNdivisions(20)
text.Draw("same")
text2.Draw("same")
leg.Draw("same")
can.Update()
can.SaveAs("xsecs_"+args.label+".png")
can.SaveAs("xsecs_"+args.label+".C")

graphPerBCID.GetXaxis().SetNdivisions(11)
graphPerBCID.Draw("AP")
text.Draw("same")
text2.Draw("same")
can.Update()
can.SaveAs("xsecsPerBCID_"+args.label+".png")
can.SaveAs("xsecsPerBCID_"+args.label+".C")

graphPerScan.Draw("AP")
text.Draw("same")
text2.Draw("same")
can.Update()
can.SaveAs("xsecsPerScan_"+args.label+".png")
can.SaveAs("xsecsPerScan_"+args.label+".C")

