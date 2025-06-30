@echo off
echo ========================================
echo    Threads 크롤러 설치 스크립트
echo ========================================
echo.

echo Python이 설치되어 있는지 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python을 설치해주세요.
    pause
    exit /b 1
)

echo ✅ Python이 설치되어 있습니다.
python --version

echo.
echo 필요한 패키지를 설치 중...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 패키지 설치 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo ✅ 설치가 완료되었습니다!
echo.
echo 사용 방법:
echo 1. python threads_crawler.py     (Selenium 버전)
echo 2. python simple_threads_crawler.py (간단한 버전)
echo.
pause 