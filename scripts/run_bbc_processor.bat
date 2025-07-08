@echo off
chcp 65001 >nul
echo ========================================
echo BBC 뉴스 프로세서 실행
echo ========================================
echo.

:: 현재 디렉토리를 스크립트 위치로 변경
cd /d "C:\GitHubRepo\Blog-monetization-agent"

:: 가상환경 활성화
echo 가상환경을 활성화하는 중...
call venv\Scripts\activate.bat

:: BBC 뉴스 프로세서 실행
echo BBC 뉴스 프로세서를 실행하는 중...
python src\core\bbc_news_processor.py

:: 완료 후 대기
echo.
echo ========================================
echo 실행 완료! 아무 키나 누르면 창이 닫힙니다.
echo ========================================
pause 