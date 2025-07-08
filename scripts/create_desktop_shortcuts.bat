@echo off
chcp 65001 >nul
echo ========================================
echo 바탕화면 바로가기 생성
echo ========================================
echo.

:: 바탕화면 경로 가져오기
for /f "tokens=2*" %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set "DESKTOP=%%b"

echo 바탕화면 경로: %DESKTOP%

:: 바로가기 파일들을 바탕화면으로 복사
echo BBC 뉴스 수집 바로가기 생성 중...
copy "BBC_뉴스_수집.lnk" "%DESKTOP%\BBC_뉴스_수집.lnk"

echo 티스토리 자동포스팅 바로가기 생성 중...
copy "티스토리_자동포스팅.lnk" "%DESKTOP%\티스토리_자동포스팅.lnk"

echo.
echo ========================================
echo 바로가기 생성 완료!
echo ========================================
echo 바탕화면에 다음 바로가기들이 생성되었습니다:
echo - BBC_뉴스_수집.lnk
echo - 티스토리_자동포스팅.lnk
echo.
echo 아무 키나 누르면 창이 닫힙니다.
pause 