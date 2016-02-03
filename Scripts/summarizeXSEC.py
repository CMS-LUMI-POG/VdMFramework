import pickle
import sys
import numpy
import ROOT
import math

filename=sys.argv[1]
file=open(filename)
fits=pickle.load(file)

xsecInd=fits[0].index('xsec')
xsecErrInd=fits[0].index('xsecErr')

PCCBCIDs=["51",'771','1631','2211','2674']
scans=["1_2","4_3","5_6","7_8","9_10"]

xsecs=[[],[],[]]
xsecsPerScan={}
for scan in scans:
    xsecsPerScan[scan]=[[],[],[]] #val, error, weight

xsecsPerBCID={}
for bcid in PCCBCIDs:
    xsecsPerBCID[bcid]=[[],[],[]] #val, error, weight

graphs={}
colors=[1,633,417,601,617]
iColor=0
for bcid in PCCBCIDs:
    graphs[bcid]=ROOT.TGraphErrors(5)
    graphs[bcid].SetMarkerColor(colors[iColor])
    graphs[bcid].SetLineColor(colors[iColor])
    graphs[bcid].SetMarkerStyle(20)
    iColor=iColor+1

for fit in fits:
    if fit[0] != "5_6" and fit[2] != "sum":
    #if fit[2] != "sum":
        try:
            #if float(fit[xsecInd])<0:
            print fit[0],fit[1],int(fit[2]),fit[xsecInd],fit[xsecErrInd]
            if float(fit[xsecErrInd])<1.0:
                continue
            #print scans.index(fit[0]),PCCBCIDs.index(fit[2])
            xsecs[0].append(float(fit[xsecInd]))
            xsecs[1].append(float(fit[xsecErrInd]))
            xsecs[2].append(1./(xsecs[1][-1]*xsecs[1][-1]))
            #print iScan,offset
            #xsecsPerScan[fit[0]][0].append(float(fit[xsecInd])/1e6)
            #xsecsPerScan[fit[0]][1].append(float(fit[xsecErrInd])/1e6)
            xsecsPerScan[fit[0]][0].append(float(fit[xsecInd]))
            xsecsPerScan[fit[0]][1].append(float(fit[xsecErrInd]))
            xsecsPerScan[fit[0]][2].append(1/(xsecsPerScan[fit[0]][1][-1]*xsecsPerScan[fit[0]][1][-1]))
            #xsecsPerBCID[fit[2]][0].append(float(fit[xsecInd])/1e6)
            #xsecsPerBCID[fit[2]][1].append(float(fit[xsecErrInd])/1e6)
            xsecsPerBCID[fit[2]][0].append(float(fit[xsecInd]))
            xsecsPerBCID[fit[2]][1].append(float(fit[xsecErrInd]))
            xsecsPerBCID[fit[2]][2].append(1/(xsecsPerScan[fit[0]][1][-1]*xsecsPerScan[fit[0]][1][-1]))
            iScan=scans.index(fit[0])
            offset=(PCCBCIDs.index(fit[2])-2)*0.05
            graphs[fit[2]].SetPoint(iScan,iScan+offset+1,float(fit[xsecInd])/1e6)
            graphs[fit[2]].SetPointError(iScan,0,float(fit[xsecErrInd])/1e6)
            
        except:
            #print "not doing this"
            pass

#print numpy.mean(xsecs[0])
#print numpy.std(xsecs[0])
print numpy.ma.average(xsecs[0],weights=xsecs[2])
sumofweights=0
for weight in xsecs[2]:
    sumofweights=sumofweights+weight
totalError=1/math.sqrt(sumofweights)
print totalError


sys.exit(0)

graphPerScan=ROOT.TGraphErrors()
graphPerScan.SetTitle(";Scan Pair;Weighted Average #sigma_{Vis} [Barn]")
graphPerScan.SetMarkerColor(417)
graphPerScan.SetMarkerStyle(20)

iPoint=0
for fit in xsecsPerScan:
    print fit,
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
graphPerBCID.SetTitle(";BCID;Weighted Average #sigma_{Vis} [Barn]")
graphPerBCID.SetMarkerColor(417)
graphPerBCID.SetMarkerStyle(20)

iPoint=0
for fit in xsecsPerBCID:
    print fit,
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
multigraph.SetTitle(";Scan Pair;#sigma_{Vis} [Barn]")
leg=ROOT.TLegend(0.4,0.15,0.6,0.35)
leg.SetBorderSize(0)
leg.SetFillColor(0)
for bcid in PCCBCIDs:
    multigraph.Add(graphs[bcid])
    leg.AddEntry(graphs[bcid],"BX = "+bcid,"p")



can=ROOT.TCanvas("can","",800,600)
multigraph.Draw("AP")
multigraph.SetMinimum(8.85)
multigraph.SetMaximum(9.1)
multigraph.GetXaxis().SetRangeUser(0.5,5.5)
leg.Draw("same")
can.Update()
can.SaveAs("xsecs_PCC.png")
raw_input()

graphPerBCID.Draw("AP")
can.Update()
can.SaveAs("xsecsPerBCID_PCC.png")
raw_input()

graphPerScan.Draw("AP")
can.Update()
can.SaveAs("xsecsPerScan_PCC.png")
raw_input()

