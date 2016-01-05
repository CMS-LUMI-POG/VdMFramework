##Basic Git Instructions

0. Create your own fork of CMS-LUMI-POG/VdMFramework (upper right)  
1. Check out the group's version of the tools (easiest way to keep in sync)  
  a) git clone https://github.com/CMS-LUMI-POG/VdMFramework  
2. Make a remote to your fork  
  a) git remote add YOURGITUSERNAME http://github.com/YOURGITUSERNAME/DataCert  
3. Check in your edited files  
  a) git add file1 file2  
  b) git commit -m "file1 and file2 are changed because..."  
4. push to YOUR fork in a BRANCH  
  a) git checkout -b update-whatiam-date  
  b) git push YOURGITUSERNAME update-whatiam-date  
5. Make a pull request (PR) with your changes update-newcurrents-data  
  a) at https://github.com/CMS-LUMI-POG/VdMFramework  
  b) let someone review and merge into CMS-LUMI-POG's "master"  
6. Keep your master in syne with CMS-LUMI-POG/VdMFramework's master  
  a) git checkout master  
  b) git push YOURGITUSERNAME master  



##Framework Instructions
To be continued...


Migrated from
svn co svn+ssh://username@svn.cern.ch/reps/VdMframework/work/Monika
on December 14th, 2015
