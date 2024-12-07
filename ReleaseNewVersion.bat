@echo off

:: Set the root directory to the directory where the batch file is located
set "root=%~dp0"

:: Remove trailing backslash for consistency (optional)
set "root=%root:~0,-1%"

:: Execute PyInstaller with the specified parameters
:: "--hidden-import requests" allows functions in config to use the `requests` library (1 MiB addition)
:: "hidden-import 3c22db458360489351e4__mypyc" this import is needed because PyInstaller cannot analyze imports in binary extensions
:: The tomli module and its submodules are stubborn
:: https://github.com/orgs/pyinstaller/discussions/7999#discussioncomment-7250690
pyinstaller --name "RobloxCore" ^
            --onefile "%root%\src\_main.py" ^
            -p "%root%\src" ^
            --console ^
            --workpath "%root%\PyInstallerWork" ^
            --distpath "%root%" ^
            --icon "%root%\src\Icon.ico" ^
            --specpath "%root%\PyInstallerWork\Spec" ^
            --hidden-import requests ^
            --hidden-import 3c22db458360489351e4__mypyc ^
            --hidden-import tomli ^
            --collect-submodules tomli

echo PyInstaller build completed!
pause
