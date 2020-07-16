
pyinstaller --clean --onedir --noconfirm ^
    --distpath windows/ ^
    --workpath windows/build ^
    --specpath windows ^
    --name search_youtube ^
    search_youtube.py