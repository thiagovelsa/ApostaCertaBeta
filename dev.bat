@echo off
title Palpite Mestre - Dev Server
color 0A

echo ========================================
echo    PALPITE MESTRE - DEV SERVER
echo ========================================
echo.

:: Portas utilizadas
set FRONTEND_PORT=5173
set BACKEND_PORT=8000

:: Encerrar processos nas portas
echo [1/3] Encerrando processos nas portas...
call :kill_port %FRONTEND_PORT% "Frontend"
call :kill_port 5174 "Frontend Alt"
call :kill_port 5175 "Frontend Alt2"
call :kill_port %BACKEND_PORT% "Backend"
echo.

:: Iniciar Backend
echo [2/3] Iniciando Backend (FastAPI) na porta %BACKEND_PORT%...
cd /d "%~dp0backend"
start "Palpite Mestre - Backend" cmd /k "call .venv\Scripts\activate 2>nul & uvicorn app.main:app --reload --port %BACKEND_PORT%"
cd /d "%~dp0"
echo       Backend iniciado.
echo.

:: Iniciar Frontend
echo [3/3] Iniciando Frontend (Vite) na porta %FRONTEND_PORT%...
cd /d "%~dp0frontend"
start "Palpite Mestre - Frontend" cmd /k "npm run dev -- --port %FRONTEND_PORT% --strictPort"
cd /d "%~dp0"
echo       Frontend iniciado.
echo.

echo ========================================
echo    SERVIDORES INICIADOS!
echo ========================================
echo.
echo    Frontend: http://localhost:%FRONTEND_PORT%
echo    Backend:  http://localhost:%BACKEND_PORT%
echo    API Docs: http://localhost:%BACKEND_PORT%/docs
echo.
echo    Pressione qualquer tecla para fechar...
pause >nul
goto :eof

:kill_port
set PORT=%~1
set LABEL=%~2
set FOUND=0
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
        set FOUND=1
        echo       Encerrando PID %%a na porta %PORT% (%LABEL%)
        taskkill /F /PID %%a >nul 2>&1
    )
)
if %FOUND%==0 (
    echo       Porta %PORT% livre.
)
:: Verifica se ainda esta em uso
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
        echo [AVISO] Porta %PORT% ainda em uso ^(PID %%a^). Continuando mesmo assim...
    )
)
exit /b 0
