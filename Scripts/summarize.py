import pickle
import sys

filename=sys.argv[1]
file=open(filename)
fits=pickle.load(file)

capInd=fits[0].index('CapSigma')
capErrInd=fits[0].index('CapSigmaErr')

PCCBCIDs=['51','771','1631','2211','2674']

for fit in fits:
    if fit[2] in PCCBCIDs:
        print fit[0],fit[1],fit[2],fit[capInd],fit[capErrInd]
