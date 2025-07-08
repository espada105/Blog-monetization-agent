# PowerShell script: Create desktop shortcuts

# Get desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")

# Script directory
$ScriptPath = "C:\GitHubRepo\Blog-monetization-agent"

Write-Host "Desktop Path: $DesktopPath" -ForegroundColor Green
Write-Host "Script Path: $ScriptPath" -ForegroundColor Green

# Create BBC News shortcut
$BBCShortcutPath = "$DesktopPath\BBC_News_Collector.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($BBCShortcutPath)
$Shortcut.TargetPath = "$ScriptPath\run_bbc_processor.bat"
$Shortcut.WorkingDirectory = $ScriptPath
$Shortcut.Description = "BBC News Collector and Blog Post Generator"
$Shortcut.Save()

Write-Host "BBC News shortcut created: $BBCShortcutPath" -ForegroundColor Green

# Create Tistory Poster shortcut
$TistoryShortcutPath = "$DesktopPath\Tistory_Auto_Poster.lnk"
$Shortcut2 = $WshShell.CreateShortcut($TistoryShortcutPath)
$Shortcut2.TargetPath = "$ScriptPath\run_tistory_poster.bat"
$Shortcut2.WorkingDirectory = $ScriptPath
$Shortcut2.Description = "Tistory Auto Poster"
$Shortcut2.Save()

Write-Host "Tistory Auto Poster shortcut created: $TistoryShortcutPath" -ForegroundColor Green

# Create Ollama Server shortcut
$OllamaShortcutPath = "$DesktopPath\Ollama_Server.lnk"
$Shortcut3 = $WshShell.CreateShortcut($OllamaShortcutPath)
$Shortcut3.TargetPath = "$ScriptPath\run_ollama_server.bat"
$Shortcut3.WorkingDirectory = $ScriptPath
$Shortcut3.Description = "Ollama LLM Server"
$Shortcut3.Save()

Write-Host "Ollama Server shortcut created: $OllamaShortcutPath" -ForegroundColor Green

Write-Host ""
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "Shortcuts created successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "The following shortcuts were created on desktop:" -ForegroundColor White
Write-Host "- BBC_News_Collector.lnk" -ForegroundColor Cyan
Write-Host "- Tistory_Auto_Poster.lnk" -ForegroundColor Cyan
Write-Host "- Ollama_Server.lnk" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor White
Read-Host 