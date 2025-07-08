@echo off
chcp 65001 >nul
echo ========================================
echo 티스토리 자동 포스터 실행
echo ========================================
echo.

:: 현재 디렉토리를 스크립트 위치로 변경
cd /d "C:\GitHubRepo\Blog-monetization-agent"

:: 가상환경 활성화
echo 가상환경을 활성화하는 중...
call venv\Scripts\activate.bat

:: 티스토리 셀레니움 포스터 실행 (자동 모드)
echo 티스토리 자동 포스터를 실행하는 중...
python src\posters\tistory_selenium_poster.py --auto

:: 완료 후 대기
echo.
echo ========================================
echo 실행 완료! 아무 키나 누르면 창이 닫힙니다.
echo ========================================
pause 