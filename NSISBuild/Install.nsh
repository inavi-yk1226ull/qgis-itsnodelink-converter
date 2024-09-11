RMDir /r "${PLUGIN_FOLDER}\${PRODUCT_FOLDER}"
RMDir /r "${PLUGIN_FOLDER}\${DELETE_FOLDER}"
SetOutPath "${PLUGIN_FOLDER}\${PRODUCT_FOLDER}"
SetOverwrite try
; nsi파일부터의 상대경로 ("*") 에서 시작,
; /x ".git" -> .git폴더 및 그 안의 내용은 포함하지 않는다.
; File /r /x "*.png" /x "*.yml" /x "*.exe" /x "*.ico" /x ".git" /x ".settings" /x ".gitignore" "${PACKING_FOLDER}\${PRODUCT_FOLDER}\*"
File /r /x ".gitmodules" /x "*.github" /x "README.md" /x "Test" /x "*.githooks" /x ".pre-commit-config.yaml" /x "pyproject.toml" /x "*.vscode" /x "*.env" /x "*.yml" /x "*.exe" /x "__pycache__" /x "*.ico" /x ".git" /x ".venv" /x ".settings" /x ".gitignore" "..\..\builds\*"
