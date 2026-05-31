@echo off
set "PYTHON_PATH_1=F:/0_MyProject/Anaconda/envs/MoviesV6/python.exe"
set "PYTHON_PATH_2=F:/0_MyProject/Anaconda/envs/MoviesV7/python.exe"


REM 系统启动
cd /d "F:/0_MyProject/KylinEcho"
start "pnpm_dev" cmd /k "pnpm dev"


REM electron启动
cd /d "F:\0_MyProject\KylinEcho\modules\SystemElectron"
start "npm_dev" cmd /k "npm run electron:serve"


REM 实时字幕生成
cd /d "F:\0_MyProject\KylinEcho\modules\RealtimeClient"
start "Realtime" cmd /k "%PYTHON_PATH_1% app.py"


REM 离线字幕生成
cd /d "F:\0_MyProject\KylinEcho\modules\OfflineSpeakersSubtitles"
start "Offline" cmd /k "%PYTHON_PATH_1% app.py"


REM 离线去噪
cd /d "F:\0_MyProject\KylinEcho\modules\AudioDenoising"
start "Audio" cmd /k "%PYTHON_PATH_1% app.py"


REM 硬字幕提取
cd /d "F:\0_MyProject\KylinEcho\modules\HardSubtitleExtraction"
start "HardSubtitle" cmd /k "%PYTHON_PATH_2% app.py"











