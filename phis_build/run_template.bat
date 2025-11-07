
@echo off
chcp 65001 > nul

@echo off
setlocal

:: Digital Worker RPA Platform - Runner Template
:: Version: {VERSION}

:: --- Dynamic Argument Placeholder ---
SET "ARGS={ARGS}"

:: =================================================================
:: --- Environment Discovery (Do Not Modify) ---
:: =================================================================

SET "APP_PYZ=app.pyz"
SET "PYTHON_EXE="
SET "PYTHON_PATH="
SET "PLATFORM_VERSION_REQUIRED=1.8"

:: -- 1. Check for the installed platform version from the registry --
FOR /F "tokens=2*" %%A IN ('REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\数字员工平台" /v "DisplayVersion" 2^>nul') DO (
    SET "PLATFORM_VERSION_INSTALLED=%%B"
)

IF NOT DEFINED PLATFORM_VERSION_INSTALLED (
    echo.
    echo 错误：未找到“数字员工平台”的安装信息。
    echo.
    echo "请先运行主安装程序 (数字员工平台.exe)。"
    echo.
    pause
    exit /b 1
)

:: -- Basic version comparison --
IF "%PLATFORM_VERSION_INSTALLED%" LSS "%PLATFORM_VERSION_REQUIRED%" (
    echo.
    echo 错误：数字员工平台版本过低。
    echo   已安装版本: %PLATFORM_VERSION_INSTALLED%
    echo   所需最低版本: %PLATFORM_VERSION_REQUIRED%
    echo.
    echo 请运行最新的安装程序进行升级。
    echo.
    pause
    exit /b 1
)

:: -- 2. Find Python executable path from the registry --
FOR /F "tokens=2*" %%A IN ('REG QUERY "HKLM\SOFTWARE\数字员工平台" /v "PythonPath" 2^>nul') DO (
    SET "PYTHON_PATH=%%B"
)

IF DEFINED PYTHON_PATH (
    IF EXIST "%PYTHON_PATH%\python.exe" (
        SET "PYTHON_EXE=%PYTHON_PATH%\python.exe"
        GOTO PythonFound
    )
)

:PythonNotFound
echo.
echo 错误：未找到与“数字员工平台”关联的 Python 环境!
echo 请尝试重新运行安装程序进行修复。
echo.
pause
exit /b 1

:PythonFound
SET "PYZ_PATH=%~dp0%APP_PYZ%"

IF NOT EXIST "%PYZ_PATH%" (
    echo.
    echo "错误：未找到应用程序核心文件 (%APP_PYZ%)。"
    echo 应用程序可能已损坏，请尝试重新安装。
    echo.
    pause
    exit /b 1
)

:: =================================================================
:: --- Application Execution --- 
:: =================================================================

echo -- 正在启动应用程序...
echo -- 使用 Python: %PYTHON_EXE%
echo -- 传递参数: %ARGS%
echo.
echo --- Python 脚本输出开始 ---
"%PYTHON_EXE%" "%PYZ_PATH%" %ARGS%
echo --- Python 脚本输出结束 ---
echo.
pause
exit /b 0
