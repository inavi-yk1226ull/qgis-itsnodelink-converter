import os

## distutils : python 모듈 배포를 위한 유틸리티
from distutils.core import setup  # # 배포를 위한 setup 함수
from distutils.extension import Extension  # # setup 스크립트에서 단일 c/c++ 확장 모듈을 정의하는 클래스

from Cython.Build import (  # # .py or .pyx 파일을 가져와 C/C++ 파일로 컴파일하고, C/C++ 파일을 Python에서 직접 가져올 수 있는 확장 모듈로 컴파일
    cythonize,
)

## cmd 명령어 : python D:\test\setup_new.py build_ext -b ..
## build_ext : build C/C++ and Cython extensions (compile/link to build directory)
## -b :  directory for compiled extension modules

current_path = os.path.realpath(__file__)
current_dir = os.path.dirname(current_path)
current_package_dir = os.path.dirname(current_dir)

package_path = current_package_dir
module_name = os.path.basename(os.path.normpath(package_path))
os.chdir(package_path)

ext_modules = []

## 경로 내 __init__.py / resources.py를 제외하고 모든 py 파일을 가져온다.
for parent, dirnames, filenames in os.walk(os.getcwd()):
    for fn in filenames:
        if fn.lower().endswith(".py") and fn != "__init__.py" and fn != "resources.py":
            idx = parent.find("iQ_ItsNodeLinkViewer")
            path = parent[idx:].replace("\\", ".")

            file_ext_idx = fn.find(".py")
            filename_noext = fn[0:file_ext_idx]

            ext = Extension(path + "." + filename_noext, [parent + "/" + fn])
            ## Extentsion(c/c++ 확장 모듈 명칭 / 소스 코드 경로)
            ## [parent+"/"+fn]를 컴파일하고, path+'.'+filename_noext 이름으로 확장 모듈을 생성.
            ## ex)
            ##  1번째 argument : iQ_HDMapEditor.iQ_HDMapEditor 이름으로 c/c++ 확장 모듈을 생성하는데,
            ##  2번째 argument : D:\test\iQ_HDMapEditor\iQ_HDMapEditor.py를 컴파일하겠다.
            ext_modules.append(ext)

setup(
    name="iQ_ItsNodeLinkViewer",  ## 패키지할 이름
    # cmdclass = {'build_ext': build_ext}, ## 패키징할 빌드 프로세스 지정
    # ##Cython의 build_ext 모듈 (c파일 제작 후, c 컴파일러로 빌드하여 pyd까지 생성)
    # ext_modules = ext_modules ## 빌드할 Python 확장 모듈의 목록
    ext_modules=cythonize(ext_modules, language_level="3"),
)
