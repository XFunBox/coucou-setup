# Windows nativo

Requisitos de compilación: Windows x64, Python 3.11+, Git, Node 22+, Rust MSVC y Visual Studio C++ Build Tools con Windows SDK. Utiliza una consola **x64 Native Tools / Developer PowerShell** para que `cl.exe` esté en PATH. La aplicación necesita Microsoft Edge WebView2 Runtime. Los scripts no instalan herramientas globales ni requieren administrador.

```powershell
# Solo leer configuración y comprobar hashes del código/parches, sin descargar/escribir:
.\install.ps1 -DryRun
# Preparar código oficial verificado sin compilar:
.\build.ps1 -PrepareOnly
# Compilar portátil, verificar y aplicar configuración del usuario:
.\install.ps1
# Compilar sin configurar usuario:
.\install.ps1 -BuildOnly
# Configurar utilizando .build/release-windows ya compilado y verificado:
.\install.ps1 -ConfigureOnly
```

`-Python C:\ruta\python.exe` permite seleccionar Python. `build.ps1 -Archive RUTA` acepta una descarga local cuyo SHA-256 debe coincidir con `source-lock.json`. `-Bundle` añade instaladores NSIS/MSI al build portátil. Preparar conserva `.build/source-windows-VERSION`; para repetir utiliza otra copia del repositorio o mueve esa carpeta. También se conserva una exportación existente en `.build/release-windows` y se rechaza sobrescribirla.

La instalación usa `%LOCALAPPDATA%\Coucou-local\bin`, `%LOCALAPPDATA%\Coucou\bin\coucou-hook.exe`, `%APPDATA%\Coucou\settings.json` y `%USERPROFILE%\.codex\hooks.json`. Conserva hooks ajenos y ajustes locales; no modifica credenciales ni confianza de Codex. Crea un lanzador VBScript en el menú Inicio (requiere Windows Script Host/VBScript). El inicio de sesión lo controla la opción de autostart de Coucou: se registra al abrir la aplicación por primera vez y se puede desactivar desde sus ajustes. No copia configuraciones Linux ni establece `PATH` global. Actualmente se rechaza AppData redirigido fuera del directorio personal para mantener la restauración limitada a ese perfil.

Con Coucou abierto, lanza una sesión nueva con el puente desde PowerShell:

```powershell
& "$env:LOCALAPPDATA\Coucou-local\bin\coucou-codex.cmd" --cwd C:\mi\proyecto --codex C:\ruta\codex.exe 'Revisa este proyecto'
```

El puente necesita Node 22+ en PATH y un ejecutable nativo o entrada JavaScript de Codex (`codex.exe` o `codex.js`, no el wrapper npm `codex.cmd`). Usa `--model MODELO --plan` para turnos de planificación capaces de pedir opciones; no conecta conversaciones ya abiertas de la app. Los argumentos son los del puente (`--cwd`, `--codex`, `--model`, `--plan` y texto de la petición), no los argumentos generales de `codex`.

Las copias fechadas se guardan en `%LOCALAPPDATA%\Coucou-setup\backups`. Con Coucou cerrado y sus procesos `coucou-hook.exe` terminados:

```powershell
python restore.py 'C:\ruta\al\backup' --dry-run
python restore.py 'C:\ruta\al\backup'
```

La restauración incluye binarios, ajustes, hooks, accesos y puente si se instaló. Comprueba rutas y presencia de todas las copias antes de escribir. Si falla una escritura durante la instalación, intenta restaurar todos los archivos de la copia automáticamente; un archivo bloqueado no impide restaurar los demás y se informa del error y de la copia a conservar. `.build/release-windows` incluye versión, procedencia fijada, licencias, versiones de herramientas y sumas SHA-256; no contiene un ejecutable firmado por Microsoft.
