@echo off
echo ============================================
echo   CronoScore - Generando ejecutable (.exe)
echo ============================================
echo.

python -m PyInstaller ^
    --name CronoScore ^
    --onefile ^
    --windowed ^
    --add-data "app.html;." ^
    --add-data "apis_config.json;." ^
    --add-data "valid_emails.txt;." ^
    --add-data "invalid_emails.txt;." ^
    --clean ^
    app.py

echo.
if exist dist\CronoScore.exe (
    echo ============================================
    echo   LISTO! El ejecutable esta en:
    echo   dist\CronoScore.exe
    echo ============================================
    echo.
    echo Para distribuirlo, copia estos archivos:
    echo   - dist\CronoScore.exe
    echo   - apis_config.json  (configuracion de APIs)
    echo   - valid_emails.txt   (emails validos)
    echo   - invalid_emails.txt (emails invalidos)
) else (
    echo ERROR: No se pudo generar el ejecutable.
    echo Revisa los errores arriba.
)

pause
