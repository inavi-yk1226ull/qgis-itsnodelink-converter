"& python -m compileall"
COPY ./ ../packing/ -Recurse
CD  ../packing/iQgis_21_NodeLinkChecker
RD .git -Recurse -Force
RD .gitignore -Recurse -Force
RD .idea -Recurse -Force
RD logging.log -Recurse -Force
RD pyrcc.cmd -Recurse -Force

# 메인 pyc
CD __pycache__
Get-ChildItem *.pyc -Recurse | Rename-Item -NewName { $_.Name -replace ".cpython-37.pyc", '.pyc' }
RD resources.pyc
RD __init__.pyc
MV *.pyc ../
CD ..
Get-ChildItem *.pyc | ForEach-Object { $remove = $_.Name -replace ".pyc", '.py' ; RD $remove; }
RD __pycache__

# 로그인 모듈 pyc
CD login/LoginModule/Account
CD __pycache__
Get-ChildItem *.pyc -Recurse | Rename-Item -NewName { $_.Name -replace ".cpython-37.pyc", '.pyc' }
MV *.pyc ../
CD ..
Get-ChildItem *.pyc | ForEach-Object { $remove = $_.Name -replace ".pyc", '.py' ; RD $remove; }
RD __pycache__
CD ..
CD __pycache__
Get-ChildItem *.pyc -Recurse | Rename-Item -NewName { $_.Name -replace ".cpython-37.pyc", '.pyc' }
MV *.pyc ../
CD ..
Get-ChildItem *.pyc | ForEach-Object { $remove = $_.Name -replace ".pyc", '.py' ; RD $remove; }
RD __pycache__
CD ..
CD __pycache__
Get-ChildItem *.pyc -Recurse | Rename-Item -NewName { $_.Name -replace ".cpython-37.pyc", '.pyc' }
MV *.pyc ../
CD ..
Get-ChildItem *.pyc | ForEach-Object { $remove = $_.Name -replace ".pyc", '.py' ; RD $remove; }
RD __pycache__
CD ..

CD C:\Users\inavi\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\iQgis_21_NodeLinkChecker
