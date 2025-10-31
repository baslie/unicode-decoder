@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: Устанавливаем UTF-8 кодировку для корректного отображения кириллицы
set PYTHONIOENCODING=utf-8

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════
echo   Unicode/Escape Sequence Decoder
echo   Декодирование escape-последовательностей в текстовых файлах
echo ═══════════════════════════════════════════════════════════════════════
echo.

:: Проверяем наличие Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Пожалуйста, установите Python с официального сайта: https://www.python.org/
    echo.
    pause
    exit /b 1
)

:: Запускаем скрипт декодирования
echo Запуск обработки...
echo.
python unicode_decoder.py

:: Проверяем код возврата
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Скрипт завершился с ошибкой!
    echo.
) else (
    echo.
    echo [УСПЕХ] Все файлы обработаны успешно!
    echo.
)

echo Нажмите любую клавишу для выхода...
pause > nul
