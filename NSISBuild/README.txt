설치 파일 제작 방법

1. release.ps1 내 $project_path / $build_path 지정
$project_path : 프로젝트 경로
$build_path : build 파일이 복사될 경로

2. release.ps1 powershell 실행

3. NSISBuild 폴더 내 'iQ_HDMapEditorSetup_v0.9.0.exe' 패키지 생성 확인

참고)
- 로컬 pc 내 NSIS가 설치되어 있어야함.
　NSIS Path : C:\Program Files (x86)\NSIS\makensis.exe

- python 3.7.X로 제작 시, release_py37.ps1을 실행하며 Python37이 설치되어 있어야 함.
　Python 3.7 Path : C:\Program Files\Python37\python

- unable to find vcvarsall.bat 오류 확인 시 C++ 빌드 개발 도구 설치
  23.05.09 기준 Visual Studio 2022 / MSVC v143 빌드 도구 설치
