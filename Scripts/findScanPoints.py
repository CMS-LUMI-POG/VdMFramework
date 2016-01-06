import sys

beamSepFileName=sys.argv[1]
beamSepFile=open(beamSepFileName)

fields=["fill","run","ls","nb","sec","msec","acqflag","step","beam","ip","scanstatus","plane","progress","nominal_separation","read_nominal_B1sepPlane","read_nominal_B1xingPlane","read_nominal_B2sepPlane","read_nominal_B2xingPlane","set_nominal_B1sepPlane","set_nominal_B1xingPlane","set_nominal_B2sepPlane","set_nominal_B2xingPlane"]

lines=beamSepFile.readlines()

dataDict={} #time stamp ("sec") is the key

for line in lines:
    items=line.split(",")
    dataDict[int(items[4])]={}
    iItem=0
    for item in items:
        dataDict[int(items[4])][fields[iItem]]=item
        iItem=iItem+1


scanPoints={} #scan point to [step, xsep, ysep, start, stop]

#time order
timeStamps=dataDict.keys()
timeStamps.sort()

iStep=0
for timeStamp in timeStamps:
    thisStep=int(dataDict[timeStamp]["step"])
    if thisStep>0 and thisStep!=9999:
        if scanPoints.has_key(iStep):
            if thisStep!=scanPoints[iStep][0]:
                iStep=iStep+1
        
        if not scanPoints.has_key(iStep):
            scanPoints[iStep]=[int(dataDict[timeStamp]["step"]),float(dataDict[timeStamp]["set_nominal_B1sepPlane"]),float(dataDict[timeStamp]["set_nominal_B1xingPlane"]),int(dataDict[timeStamp]["sec"]),-99]
        
        if thisStep==scanPoints[iStep][0]:
            scanPoints[iStep][4]=timeStamp


sortedSteps=scanPoints.keys()
sortedSteps.sort()

for step in sortedSteps:
    print step, scanPoints[step]
        


