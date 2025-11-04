!define APP_NAME            "Fido2 Key Manager"
!define APP_DIR             "Fido2Manager"
!define COMP_NAME           "jamkar20"
!define VERSION             "1.0.0.0"
!define DESCRIPTION         "Cross-Platform Fido2 Key Management"
!define COPYRIGHT           "Jamal Kargar"
!define ProjectLocation     "${__filedir__}\.."
!define INSTALLER_NAME      "${ProjectLocation}\package\Fido2Manager_${VERSION}.exe"
!define MAIN_APP_EXE        "Fido2KeyManager.exe"
!define MAIN_APP_LNK        "Fido2KeyManager.lnk"
!define INSTALL_TYPE        "SetShellVarContext current"
!define INSTALL_DIR         "$PROGRAMFILES\${APP_DIR}"
!define REG_ROOT            "HKLM"
!define REG_APP_PATH        "Software\Microsoft\Windows\CurrentVersion\App Paths\${MAIN_APP_EXE}"
!define UNINSTALL_PATH      "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

######################################################################

VIProductVersion                        "${VERSION}"
VIAddVersionKey     "ProductName"       "${APP_NAME}"
VIAddVersionKey     "CompanyName"       "${COMP_NAME}"
VIAddVersionKey     "LegalCopyright"    "${COPYRIGHT}"
VIAddVersionKey     "FileDescription"   "${DESCRIPTION}"
VIAddVersionKey     "FileVersion"       "${VERSION}"

######################################################################

Unicode True
SetCompressor           ZLIB
Name                    "${APP_NAME}"
Caption                 "${APP_NAME}"
OutFile                 "${INSTALLER_NAME}"
BrandingText            "${APP_NAME}"
InstallDirRegKey        "${REG_ROOT}" "${REG_APP_PATH}" ""
InstallDir              "$PROGRAMFILES\${APP_DIR}"

######################################################################

RequestExecutionLevel admin

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

!define MUI_ICON "${ProjectLocation}\logo.ico"
!define MUI_UNICON "${ProjectLocation}\logo.ico"
!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

######################################################################

Section "Main Program"
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    
    File "${ProjectLocation}\dist\Fido2KeyManager.exe"
    
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    WriteRegStr HKLM "${UNINSTALL_PATH}"    "DisplayName"       "${APP_NAME}"
    WriteRegStr HKLM "${UNINSTALL_PATH}"    "UninstallString"   '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "${UNINSTALL_PATH}"    "DisplayIcon"       '"$INSTDIR\${MAIN_APP_EXE}"'
    WriteRegStr HKLM "${UNINSTALL_PATH}"    "Publisher"         "${COMP_NAME}"
    WriteRegStr HKLM "${UNINSTALL_PATH}"    "DisplayVersion"    "${VERSION}"
    WriteRegStr HKLM "${REG_APP_PATH}"      ""                  "$INSTDIR\${MAIN_APP_EXE}"
    
    CreateShortCut "$DESKTOP\${MAIN_APP_LNK}" "$INSTDIR\${MAIN_APP_EXE}"
    
    CreateDirectory "$SMPROGRAMS\${APP_DIR}"
    CreateShortCut  "$SMPROGRAMS\${APP_DIR}\${MAIN_APP_LNK}"    "$INSTDIR\${MAIN_APP_EXE}"
    CreateShortCut  "$SMPROGRAMS\${APP_DIR}\Uninstall.lnk"      "$INSTDIR\Uninstall.exe"
SectionEnd

######################################################################

Section "Uninstall"
    Delete "$INSTDIR\${MAIN_APP_EXE}"
    Delete "$INSTDIR\Uninstall.exe"
    
    Delete "$DESKTOP\${MAIN_APP_LNK}"
    
    Delete "$SMPROGRAMS\${APP_DIR}\*.*"
    RMDir "$SMPROGRAMS\${APP_DIR}"
    
    RMDir "$INSTDIR"
    
    DeleteRegKey HKLM "${UNINSTALL_PATH}"
    DeleteRegKey HKLM "${REG_APP_PATH}"
SectionEnd