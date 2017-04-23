if [ "$1" = "Timber" ]
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_85swan3/x86_64-slc6-gcc49-opt/setup.sh
    export PYTHONPATH=${PWD}:$PYTHONPATH
    export PYTHONPATH=${PWD}/fits:$PYTHONPATH
    export PYTHONPATH=${PWD}/corrections:$PYTHONPATH
    export VDMPATH=${PWD}
    export PATH=/afs/cern.ch/cms/lumi/brilconda-1.0.3/bin:$PATH
else
    export ROOTSYS=/afs/cern.ch/cms/lumi/brilconda-1.1.7/root
    export PATH=$ROOTSYS/bin:$PATH
    export LD_LIBRARY_PATH=/afs/cern.ch/cms/lumi/brilconda-1.1.7/root/lib
    export PYTHONPATH=/afs/cern.ch/cms/lumi/brilconda-1.1.7/root/lib
    export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH
    export PYTHONPATH=${PWD}:$PYTHONPATH
    export PYTHONPATH=${PWD}/fits:$PYTHONPATH
    export PYTHONPATH=${PWD}/corrections:$PYTHONPATH
    export VDMPATH=${PWD}
    export PATH=/afs/cern.ch/cms/lumi/brilconda-1.1.7/bin:$PATH
    #source /afs/cern.ch/cms/lumi/brilconda-1.1.7/root/bin/thisroot.sh
fi
echo "Is your username listed in remote list?"
echo
git remote -v
echo
echo "If not, do 'git remote add YOURGITUSERNAME git@github.com:YOURGITUSERNAME/VdMFramework.git'."
