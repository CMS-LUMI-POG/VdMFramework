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
parser.add_argument("--plotlabel",  default="2016  (13TeV)", help="Label for the upper right.  Default:  2016  (13TeV)")
args=parser.parse_args()



ROOT.gROOT.SetBatch(ROOT.kTRUE)

file=open(args.filename)
fits=pickle.load(file)

xsecInd=fits[0].index('xsec')
xsecErrInd=fits[0].index('xsecErr')

BCIDs=["644",'1215','2269','2389','2589']
scans=["1_2","4_3","5_6","7_8","9_10"]

BCIDs=['41', '281', '872', '1783', '2063']
scans=["1_2","4_3","5_6","7_8","9_10"]

if args.allbcids !=0:
    for fit in fits:
        if fit[2] not in BCIDs:
            BCIDs.append(fit[2])
    BCIDs.sort()
    
    


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
    if fit[0] != "5_6" and fit[2] != "sum": #5_6 was a bad one at 13tev
    #if fit[0] != "1_2" and fit[0] != "4_3" and fit[2] != "sum":
        try:
            #if float(fit[xsecInd])<0:
            print fit[0],fit[1],int(fit[2]),fit[xsecInd],fit[xsecErrInd]
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
            xsecs[0].append(thisXsec)
            xsecs[1].append(thisXsecErr)
            xsecs[2].append(1./(xsecs[1][-1]*xsecs[1][-1]))
            #print iScan,offset
            xsecsPerScan[fit[0]][0].append(thisXsec)
            xsecsPerScan[fit[0]][1].append(thisXsecErr)
            #xsecsPerScan[fit[0]][0].append(float(fit[xsecInd]))
            #xsecsPerScan[fit[0]][1].append(float(fit[xsecErrInd]))
            xsecsPerScan[fit[0]][2].append(1/(xsecsPerScan[fit[0]][1][-1]*xsecsPerScan[fit[0]][1][-1]))
            xsecsPerBCID[fit[2]][0].append(thisXsec)
            xsecsPerBCID[fit[2]][1].append(thisXsecErr)
            #xsecsPerBCID[fit[2]][0].append(float(fit[xsecInd]))
            #xsecsPerBCID[fit[2]][1].append(float(fit[xsecErrInd]))
            xsecsPerBCID[fit[2]][2].append(1/(xsecsPerScan[fit[0]][1][-1]*xsecsPerScan[fit[0]][1][-1]))
            iScan=scans.index(fit[0])
            offset=(BCIDs.index(fit[2])- len(BCIDs)/2)*(0.85*(len(BCIDs)>15)+0.5*(len(BCIDs)<16))/float(len(BCIDs))
            graphs[fit[2]].SetPoint(iScan,iScan+offset+1,thisXsec)
            graphs[fit[2]].SetPointError(iScan,0,thisXsecErr)
            
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
leg=ROOT.TLegend(0.7,0.15,0.9,0.43)
leg.SetBorderSize(0)
leg.SetFillColor(0)
for bcid in BCIDs:
    multigraph.Add(graphs[bcid])
    leg.AddEntry(graphs[bcid],"BX = "+bcid,"p")


text=ROOT.TLatex(0.72,0.88,args.plotlabel)
text.SetNDC()
text.SetTextFont(62)
text.SetTextSize(0.05)
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

