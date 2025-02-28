@echo off
echo ===========================================
echo  Instalando TradeSim en Windows (sin Docker)
echo ===========================================

:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado. Descárgalo en https://www.python.org/downloads/
    exit /b 1
)

:: Crear y activar el entorno virtual
echo [INFO] Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate

:: Instalar dependencias
echo [INFO] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

:: Crear directorio de la base de datos si no existe
if not exist "data" mkdir data

:: Inicializar la base de datos
echo [INFO] Inicializando la base de datos...
python scripts\init_db.py

:: Ejecutar la aplicación
echo [INFO] Ejecutando TradeSim...
python -m reflex run --env dev

pause