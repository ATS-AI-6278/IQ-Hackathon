@echo off
echo ==============================================================================
echo   VERID - DIGITAL PRODUCT PASSPORT PLATFORM (iQOO Hackathon 2026)
echo   Starting all 3 services in one terminal (AI Engine, API Gateway, Web App)...
echo ==============================================================================
echo.
call pnpm dev:all
pause
