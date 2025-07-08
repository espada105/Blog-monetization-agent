@echo off
chcp 65001 >nul
echo ========================================
echo Ollama 서버 실행
echo ========================================
echo.

:: 현재 디렉토리를 스크립트 위치로 변경
cd /d "C:\GitHubRepo\Blog-monetization-agent"

:: 가상환경 활성화
echo 가상환경을 활성화하는 중...
call venv\Scripts\activate.bat

:: Ollama 서버 실행
echo Ollama 서버를 실행하는 중...
echo 서버가 실행되면 Ctrl+C를 눌러서 종료할 수 있습니다.
echo.
ollama serve

:: 완료 후 대기
echo.
echo ========================================
echo Ollama 서버가 종료되었습니다.
echo ========================================
pause 