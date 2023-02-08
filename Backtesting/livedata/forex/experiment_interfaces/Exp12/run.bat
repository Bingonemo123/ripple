@echo off
if not "%1" == "max" start /MAX cmd /c %0 max & exit/b

:: here comes the rest of your batch-file
python PackageMain.py pause
