@echo off
pyinstaller.exe -y --onefile WantedPushCrawler.spec
if exist "HelloList.txt" (
	copy "HelloList.txt" .\dist\WantedPushCrawler
)
if exist "PublicList.txt" (
	copy "PublicList.txt" .\dist\WantedPushCrawler
)
if exist "WantList.txt" (
	copy "WantList.txt" .\dist\WantedPushCrawler
)