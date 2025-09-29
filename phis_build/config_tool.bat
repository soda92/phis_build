@echo off
chcp 65001 > nul
setlocal

:: =================================================================
:: --- 1. 配置区域 ---
:: =================================================================


SET "APP_PYZ=app.pyz"

SET "HOSPITAL_NAME={hospital_name}"
SET "TASK_NAME={task_name}"

:: =================================================================
:: --- 请勿修改以下内容 ---
:: =================================================================

:: -- 动态查找 Python 环境 --
SET "PYTHON_EXE="
SET "PYTHON_PATH="

:: -- 1. 优先查找新版安装程序（嵌入式Python）的注册表项 --
:: -- 注意：这里的 "数字员工平台" 必须与 NSIS 脚本中的 PRODUCT_NAME 一致 --
FOR /F "tokens=2*" %%A IN ('REG QUERY "HKLM\SOFTWARE\数字员工平台" /v "PythonPath" 2^>nul') DO (
    SET "PYTHON_PATH=%%B"
)
IF DEFINED PYTHON_PATH (
    IF EXIST "%PYTHON_PATH%\python.exe" (
        SET "PYTHON_EXE=%PYTHON_PATH%\python.exe"
        GOTO PythonFound
    )
)

:: -- 2. 如果没找到，则查找旧版（系统级）Python 的注册表项 --
FOR /F "tokens=2*" %%A IN ('REG QUERY "HKLM\SOFTWARE\Python\PythonCore\3.8\InstallPath" /ve 2^>nul') DO (
    SET "PYTHON_PATH=%%B"
)
IF DEFINED PYTHON_PATH (
    IF EXIST "%PYTHON_PATH%\python.exe" (
        SET "PYTHON_EXE=%PYTHON_PATH%\python.exe"
        GOTO PythonFound
    )
)

:PythonFound
:: 构建所需文件的完整路径
SET "PYZ_PATH=%~dp0%APP_PYZ%"

:: 检查 Python 依赖是否存在
IF NOT EXIST "%PYTHON_EXE%" (
    echo.
    echo "错误：未找到 Python 环境!"
    echo "所需的数字员工运行环境未正确安装。"
    echo.
    echo "请先运行主安装程序 (数字员工平台.exe)。"
    echo.
    pause
    exit /b 1
)

:: -- 组装参数 --
:: -- 你可以在这里修改参数的格式，例如 --user, --task-id 等 --
SET "ARGS=--launch-config-tool"

:: -- 启动应用程序并传递参数 --
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