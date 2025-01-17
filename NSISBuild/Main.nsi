; 플러그인 경로
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"

;------------------------------------------------------------------------------
; Include 

  !include "MUI2.nsh"
  Unicode true

;------------------------------------------------------------------------------
; Product Configuration

  !include "ProductInfo.nsh"
  Name "${PRODUCT_NAME}"
  BrandingText "My Company"

;------------------------------------------------------------------------------
; Install Options

  RequestExecutionLevel user
  !define PLUGIN_FOLDER  "$APPDATA\QGIS\QGIS3\profiles\default\python\plugins"
  InstallDir "${PLUGIN_FOLDER}\${PRODUCT_FOLDER}"
  OutFile "${PRODUCT_KEY}Setup_v${PRODUCT_VERSION}.exe"  

;------------------------------------------------------------------------------
; Set Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH
  !insertmacro MUI_LANGUAGE "Korean"

;------------------------------------------------------------------------------
; Installer Sections

  Section "Dummy Section" SecDummy
 
  ;----------------------------------------------------------------------------
  ; Set Install Files
  
    !include "install.nsh" 
  

  SectionEnd
