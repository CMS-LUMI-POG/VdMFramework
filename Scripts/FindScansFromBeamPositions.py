import sys
import argparse

parser = argparse.ArgumentParser(description='Find scan windows for vdm scans from beam positions')
parser.add_argument('-i', '--filename', default="", help="Input file")
parser.add_argument('-r', '--runs', default="", help="Runs to look for (default:  no filter")

args = parser.parse_args()


if args.filename=="":
    print "No file name given... I quit."
    sys.exit(-1)

if args.runs!="":
    args.runs=args.runs.split(",")
    print "args.runs",args.runs

beamPositionFile=open(args.filename)

beamPositionLines=beamPositionFile.readlines()

stdFirstLine="fill,run,ls,nb,sec,msec,acqflag,step,beam,ip,scanstatus,plane,progress,nominal_separation,read_nominal_B1sepPlane,read_nominal_B1xingPlane,read_nominal_B2sepPlane,read_nominal_B2xingPlane,set_nominal_B1sepPlane,set_nominal_B1xingPlane,set_nominal_B2sepPlane,set_nominal_B2xingPlane,bpm_5LDOROS_B1Names,bpm_5LDOROS_B1hPos,bpm_5LDOROS_B1vPos,bpm_5LDOROS_B1hErr,bpm_5LDOROS_B1vErr,bpm_5RDOROS_B1Names,bpm_5RDOROS_B1hPos,bpm_5RDOROS_B1vPos,bpm_5RDOROS_B1hErr,bpm_5RDOROS_B1vErr,bpm_5LDOROS_B2Names,bpm_5LDOROS_B2hPos,bpm_5LDOROS_B2vPos,bpm_5LDOROS_B2hErr,bpm_5LDOROS_B2vErr,bpm_5RDOROS_B2Names,bpm_5RDOROS_B2hPos,bpm_5RDOROS_B2vPos,bpm_5RDOROS_B2hErr,bpm_5RDOROS_B2vErr,atlas_totInst,nominal_separation_plane"
fieldKey=[]
items=beamPositionLines[0].split(",")
if items[0] is "fill":
    fieldKey=items
    beamPositionLines.pop(0)
else:
    #assume may 2016 format
    fieldKey=stdFirstLine.split(",")

print fieldKey

scanPoints={} # number --> dx, dy, start, stop

if 'set_nominal_B2xingPlane' in fieldKey:
    print "set_nominal_B2xingPlane in fieldKey"

iScanPoint=0
curX=0
curY=0
for line in beamPositionLines:
    items=line.split(",")
    #if items[fieldKey.index('nominal_separation_plane')]  is 'NONE':
    #    continue
    try:
        if args.runs!="":
            if items[fieldKey.index('run')] not in args.runs:
                continue
        dx=float(items[fieldKey.index('set_nominal_B2xingPlane')])-float(items[fieldKey.index('set_nominal_B1xingPlane')])
        dy=float(items[fieldKey.index('set_nominal_B2sepPlane')])-float(items[fieldKey.index('set_nominal_B1sepPlane')])
        if dx==0 and dy==0:
            continue
        elif abs(dx)<1.e-10 and dy==0:
            continue
        elif dx==0 and abs(dy)<1.e-10:
            continue

        if len(scanPoints.keys())==0:
            scanPoints[iScanPoint]=[dx,dy,int(items[fieldKey.index('sec')]),-1]
            curX=dx
            curY=dy
        # is new scan?
        if curX!=dx or curY!=dy: 
            iScanPoint=iScanPoint+1
            scanPoints[iScanPoint]=[dx,dy,int(items[fieldKey.index('sec')]),-1]
            curX=dx
            curY=dy
        else:
            scanPoints[iScanPoint][3]=int(items[fieldKey.index('sec')])
    except:
        print "fail",line

print iScanPoint
scans={}
iScan=0
lastTime=0
for scanPoint in range(iScanPoint):
    print scanPoint,scanPoints[scanPoint]
    if len(scans.keys())==0:
        print "no keys, insert one"
        if scanPoints[scanPoint][0]==0:
            scans[iScan]=["Y",scanPoints[scanPoint][2],scanPoints[scanPoint][3]]
        if scanPoints[scanPoint][1]==0:
            scans[iScan]=["X",scanPoints[scanPoint][2],scanPoints[scanPoint][3]]
    else:
        newScan=False
        if scans[iScan][0]=="Y" and scanPoints[scanPoint][1]==0:
            print "Y scan ends... X begins"
            newScan=True
        elif scans[iScan][0]=="X" and scanPoints[scanPoint][0]==0:
            print "X scan ends... Y begins"
            newScan=True
        elif int(scanPoints[scanPoint][2])-lastTime>100:
            print "It's been awhile"
            newScan=True

        if newScan:
            scans[iScan][2]=lastTime
            iScan=iScan+1
            if scanPoints[scanPoint][0]==0:
                scans[iScan]=["Y",scanPoints[scanPoint][2],scanPoints[scanPoint][3]]
            if scanPoints[scanPoint][1]==0:
                scans[iScan]=["X",scanPoints[scanPoint][2],scanPoints[scanPoint][3]]
    
    lastTime=int(scanPoints[scanPoint][3])

scans[iScan][2]=lastTime
iScan=iScan+1

for scan in range(iScan):
    duration=scans[scan][2]-scans[scan][1]
    print scan,scans[scan],duration,"seconds",
    if duration<700:
        print "short?"
    else:
        print
