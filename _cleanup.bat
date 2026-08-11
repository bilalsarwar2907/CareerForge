@echo off
cd /d C:\Users\biges\CareerForge
del _git_push.bat
git add -A
git commit -m "chore: remove temp scripts"
git push
(goto) 2>nul & del "%~f0"
