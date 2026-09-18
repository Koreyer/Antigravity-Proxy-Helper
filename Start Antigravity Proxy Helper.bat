@echo off
chcp 65001 >nul
cd /d "%~dp0"

if exist "%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe" (
  start "" "%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe" "antigravity_proxy_helper.py"
  exit /b
)
if exist "%ProgramFiles%\Python314\pythonw.exe" (
  start "" "%ProgramFiles%\Python314\pythonw.exe" "antigravity_proxy_helper.py"
  exit /b
)
where pyw >nul 2>nul && (start "" pyw "antigravity_proxy_helper.py" & exit /b)
where pythonw >nul 2>nul && (start "" pythonw "antigravity_proxy_helper.py" & exit /b)
start "" python "antigravity_proxy_helper.py"
