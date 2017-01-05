##Basic Git Instructions

0. Create your own fork of CMS-LUMI-POG/VdMFramework (upper right)  

1. Check out the group's version of the tools (easiest way to keep in sync)  
    `git clone https://github.com/CMS-LUMI-POG/VdMFramework`

2. Step 1 clones only the master BRANCH of the CMS-LUMI-POG/VdMFramework (from now on origin). To fetch all the BRANCHES of the origin, 
   `git fetch origin`
   You can see the list of all BRANCHes with
   `git branch -a`

3. It is recommnened at this stage to checkout a new local branch in which you start to develop/edit files. This is done with
   `git checkout -b LOCAL_BRANCHNAME origin/REMOTE_BRANCHNAME`
   The name of LOCAL_BRANCHNAME could be whatever. For the list of available remote (and local) branches, you can simply type `git branch -a`.

4. Now, if you want to further release the local changes, the following steps (5-9) have to be done. Make a remote to your fork 
   `git remote add YOURGITUSERNAME http://github.com/YOURGITUSERNAME/VdMFramework`

5. Make sure that your remote repositoty has been added
    `git remote -v'

6. Make the first push to YOUR remote repository (fork).  To do this, it is necessary at least one file to have been edited/added. Check in your edited/created file(s) and commit with a descriptive comment 
   ```
    git add file1 file2  
    git commit -am "file1 and file2 are changed because..." 
   ```	  
7. Now, it is time to push the LOCAL_BRANCHNAME to YOUR fork.
    `git push YOURGITUSERNAME LOCAL_BRANCHNAME`
    It is also possible to give to the remote repository a different name with
     `git push YOURGITUSERNAME LOCAL_BRANCHNAME:NEW_BRANCHNAME`
8. If step 8 fails, i.e. if git complains with 
  "error: The requested URL returned error: 403 Forbidden while accessing https://github.com/YOURGITUSERNAME/VdMFramework.git/info/refs
  fatal: HTTP request failed"

  then simply add in the .git/config file the line:
  ` pushurl = git@github.com:YOURGITUSERNAME/VdMFramework.git `
  in the part of [remote "YOURGITUSERNAME"].

9. Make a pull request (PR) with your changes. The easiest way is to do it interactively on your github web interface
  
  a) Go to YOUR VdMFramework repository, i.e. https://github.com/YOURGITUSERNAME/VdMFramework
  
  b) You will see the indication 'New pull request' within the green context; you can click on it
  
  c) In the new screen of 'Comparing changes' there would be four instances, i.e. (BASE FORK, BASE) and (HEAD FORK, COMPARE)
  
  d) Select as BASE FORK "CMS-LUMI-POG/VdMFramework" and BASE "master"
  
  e) Select as HEAD FORK "YOURGITUSERNAME/VdMFramework" and COMPARE the branch name that you want to create the pull request for, e.g. the branch that it was created during steps 5-9
  
  f) An automatic message will be created. There should be 'Able to merge. These branches can be automatically merged.' If not the changes that you are trying to push cannot be automatically adapted. Furhter work will be needed, so for that case better communicate with Chris/Jakob on how to proceed
  
  g) If step g has been successful, simply leave a comment if you think the description you added during step 7 (in the commit command) is not sufficient, and then push 
  `Create pull request`
  
  h) Not yet finalized! Someone has to review and merge into CMS-LUMI-POG's "master", before you see your nice work be released. Stay tuned and follow the discussion on the pull request page



##Framework Instructions

Migrated from
 ```	 
svn co svn+ssh://username@svn.cern.ch/reps/VdMframework/work/Monika
 ```
on December 14th, 2015.

Here, there are some (slightly outdated) illustrated instructions:

```
https://indico.cern.ch/event/433686/attachments/1126803/1609016/Tutorial_VdM_July2015.pdf
```

****Running the Driver****

The framework is centrally steered by the `vdmDriverII.py`. What you are running and in which order is defined by passing a json file to the driver.  The user by editing such a .json file can enanble/dissable with boolean flags the functionality of the driver.

For our example, we take here the `4634_Configs/vdmDriverII_Config_PCC_4634.json`, meant for the LHC fill 4634 and using the Pixel Cluster Counting (PCC) luminometer. Currently *no parsing* is available, thus the user has to *open* and *edit* the .json file with an editor. 

More specifically, the  vdmDriverII.py can handle the macros below (with the order currently listed in vdmDriverII_Config_PCC_4634.json ):

a) makeScanFileII.py

b) dataPrepII_PCC/makePCCRateFile.py; this is specific to the luminometer handled by the .json file 

c) makeBeamCurrentFileII.py

d) for this iteration we ignore the makeBeamBeamFile till makeLengthScaleFile part (FIXME)

e) makeGraphsFileII.py

f) makeGraphs2D.py 

h) vdmFitterII.py

Note that the driver can handle all functionalities above at once, i.e. set all booleans to true, but for the time being it is *recommended* to enable its feautres separarely, as explained in the following.

0th order edit in the  4634_Configs/vdmDriverII_Config_PCC_4634.json file is to place *everywhere* your lxplus initials, e.g.  

```
/g/gkrintir → your lxplus initiials

```

The driver then runs with: 

```
 python vdmDriverII.py 4634_Configs/vdmDriverII_Config_PCC_4634.json
```

Let us assume a version of vdmDriverII_Config_PCC_4634.json in which the driver is enabled to run sequentially, step by step, starting from step *a* (in the list described above). i.e. `"makeScanFile": true` and false everywhere. For step *a* make sure *before* you run the driver to execute on your terminal:

```
eosmount ~/tempeos
```

Also, please make sure that the `"BetaStar"`, `"Angle"`, `"EnergyB1"` and `"EnergyB1"` parameters have been correctly set up. Info can be found on `https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillReport`. Once step *a* is done, the output is stored in 
```
Fill4634_Nov192015/cond/Scan_4634.*, with *=csv, pkl. 
```

Moving now to step *b*, i.e. `"makeRateFile": true` and false everywherethe, the input file for making the rate file can be found in `/afs/cern.ch/user/g/gkrintir/public/ForMassimo/ZeroBias2.root` (*FIXME*). To note that this .root file is the ouput of the `VdMPrep/makeVdMMiniTree.py` macro in the `CMS-LUMI-POG/PCCTools` repository.
 
Now, i.e. after having executed with `"makeRateFile": true`, you should see the output stored in  
```
Fill4634_Nov192015/LuminometerData/Rates_PCC_4634.*, *=csv, pkl. 
```

The next step is to create the graph file, which will be the input of the subsequent fit step. To do this, dissable the “makeScanFile” and "makeRateFile", and enable `"makeGraphsFile": true`. The output of this step is stored in 
```
Fill4634_Nov192015/PCC/graphs/graphs_4634_noCorr.*, * = pkl, root 
```

And now the fitting step! Again, disable "makeGraphsFile",  and enable `"runVdmFitter": true`. The output of this step is stored in 
```
Fill4634_Nov192015/PCC/results/noCorr/ and plotstmp/ (just under the VdMFramework/ directory).
```

Note that if you have selected as `"FitName" : "SimCapSigma_PCCAndVtx"`, i.e. the option for a simultaneous fit, in the `4634_Configs/vdmDriverII_Config_PCC_4634.json` configuration file, then the output is seprately stored under
```
Fill4634_Nov192015/PCC/results/noCorr/ and plotstmp/1/ (just under the VdMFramework/ directory).
```

and

```
Fill4634_Nov192015/TrkVtx/results/noCorr/ and plotstmp/2 (just under the VdMFramework/ directory).
```

The `"PlotsTempPath":` argument inside the `4634_Configs/vdmDriverII_Config_PCC_4634.json` configuration file are configurable and user is free to change them.


You are done! What is left is simply to illustrate the fitting results. 

****Plot the results****

This is a *two* step process, i.e. 

1) `python calculateCalibrationConstant.py 4634_Configs/calculateCalibrationConstant_Config_PCC_4634.json`

This will create and store the output in 
```
Fill4634_Nov192015/PCC/results/noCorr/LumiCalibration_PCC_DGConst_4634.*, *=csv, pkl. 
```

2) Run

`python Scripts/summarizeXSEC.py Fill4634_Nov192015/PCC/results/noCorr/LumiCalibration_PCC_DGConst_4634.pkl`

and the plots will be stored under the VdMFramework/ directory as 
```
xsecs_PCC.png, xsecsPerBCID_PCC.png, and xsecsPerScan_PCC.png
```
along with their .C source files for further editing, if needed.



