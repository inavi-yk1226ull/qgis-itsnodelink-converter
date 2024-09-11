$currentScriptPath = $PSScriptRoot

$project_path = Split-Path -Path $currentScriptPath -Parent
$build_path = "D:\plugin_build\builds"

$NSISbuild_path = $build_path + "\NSISBuild"
$cython_buildresult_path_proj = $project_path + "\build"
$cython_buildresult_path = $build_path + "\build"
$setupfile_path = $project_path + "\NSISBuild\setup.py"
$nsisfile_path = $project_path + "\NSISBuild\Main.nsi"

$initfile_path = $project_path + "\__init__.py"
$resourcefile_path = $project_path + "\resources.py"
$allfile = $project_path + "\*"

Write-Output "Start remove c file"
Get-ChildItem -Path $project_path -Recurse -Include *.c | ForEach-Object {
    Remove-Item $_.FullName; }

Write-Output "Start remove pyd"
Get-ChildItem -Path $project_path -Recurse -Include *.pyd | ForEach-Object {
    Remove-Item $_.FullName; }

# SetUpTool로 distutils 대체 -from python 3.12
Write-Output "Start Install setuptools"
& python -m pip install setuptools

Write-Output "Start Install cython"
& python -m pip install cython

Write-Output "Start Try to cython"
& python $setupfile_path build_ext -b ..

Get-ChildItem -Path $project_path -Include *.cp312-win_amd64.pyd -Recurse | ForEach-Object {
    $pyName = $_.FullName -replace ".cp312-win_amd64.pyd", ".pyd";
    Rename-Item $_.FullName $pyName; }

if (Test-Path $build_path) {
    Remove-Item $build_path -Recurse -Force
}

mkdir $build_path
Copy-Item $allfile $build_path -Recurse

Get-ChildItem -Path $build_path -Recurse -Include *.bat, *.puml, *.c, *.py, *.pyc | ForEach-Object {
    Remove-Item $_.FullName; }

Remove-Item $NSISbuild_path -Recurse
Remove-Item $cython_buildresult_path -Recurse

Copy-Item $initfile_path $build_path -recurse
Copy-Item $resourcefile_path $build_path -recurse

Start-Process -Wait -FilePath "C:\Program Files (x86)\NSIS\makensis.exe" $nsisfile_path

Remove-Item $cython_buildresult_path_proj -Recurse

Write-Output "Start remove c file"
Get-ChildItem -Path $project_path -Recurse -Include *.c | ForEach-Object {
    Remove-Item $_.FullName; }

Write-Output "Start remove pyd"
Get-ChildItem -Path $project_path -Recurse -Include *.pyd | ForEach-Object {
    Remove-Item $_.FullName; }

Read-Host -Prompt "Press Enter to exit"
