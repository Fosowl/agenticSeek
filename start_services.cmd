@echo off

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker daemon is not running or inaccessible.
    echo Please ensure Docker Desktop is running.
    exit /b 1
)

REM Check if docker-compose.yml exists
if not exist docker-compose.yml (
    echo Error: docker-compose.yml not found in the current directory.
    exit /b 1
)

REM Check and download Chrome bundle if not present
echo Checking Chrome bundle...
if not exist chrome_bundle\chrome136 (
    echo Chrome bundle not found. Downloading...
    if not exist chrome_bundle mkdir chrome_bundle
    curl -L https://github.com/tcsenpai/agenticSeek/releases/download/utility/chrome136.zip -o %TEMP%\chrome136.zip
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to download Chrome bundle
        exit /b 1
    )
    powershell -Command "Expand-Archive -Path '%TEMP%\chrome136.zip' -DestinationPath 'chrome_bundle' -Force"
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to extract Chrome bundle
        exit /b 1
    )
    del %TEMP%\chrome136.zip
    echo Chrome bundle downloaded and extracted successfully
) else (
    echo Chrome bundle already exists
)

REM Stop only containers in our project's network
echo Stopping project containers...
docker-compose down

REM Start Ollama in the background
echo Starting Ollama...
start /B ollama serve

REM First start python-env
echo Starting python-env service...
docker-compose up -d python-env
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to start python-env container.
    exit /b 1
)

REM Wait for python-env to be healthy
echo Waiting for python-env to be ready...
set /a count=0
:wait_loop
docker inspect -f "{{.State.Running}}" python-env | findstr "true" >nul
if %ERRORLEVEL% neq 0 (
    set /a count+=1
    if %count% gtr 30 (
        echo Error: python-env failed to start properly after 30 seconds
        docker-compose logs python-env
        exit /b 1
    )
    timeout /t 1 /nobreak >nul
    goto wait_loop
)

echo python-env is ready!

REM Now start the rest of the services
echo Starting remaining services...
docker-compose up
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to start containers. Check Docker logs with 'docker compose logs'.
    echo Possible fixes: Ensure Docker Desktop is running or check if port 8080 is free.
    exit /b 1
)

timeout /t 10 /nobreak >nul