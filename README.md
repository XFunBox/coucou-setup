# Coucou con Codex, GitHub y Spotify

Setup de **Coucou 0.5.0-sendoa.3** para Ubuntu/Debian amd64 y Windows x64. Descarga la fuente oficial 0.5.0, verifica su SHA-256 y aplica dos parches verificados: las personalizaciones Sendoa y la oficina de agentes. Linux compila en Docker; Windows utiliza su backend nativo y MSVC. No necesita las imágenes ni los binarios de otro equipo.

## Windows y oficina de agentes

Para Windows, consulta [WINDOWS.md](WINDOWS.md): `install.ps1 -DryRun` muestra el plan, `build.ps1 -PrepareOnly` prepara la fuente y `install.ps1` compila e instala para tu usuario. Requiere las herramientas de compilación indicadas; no las instala globalmente.

En ambos sistemas, abre **Coucou → Notch → Oficina de agentes**. La oficina representa las sesiones reales recibidas por los hooks, con escritorios, estados y subagentes cuando el agente proporciona su identificador. Seleccionar un escritorio abre sus detalles; una burbuja de pregunta abre su tarjeta real en la isla. La oficina vacía no inventa actividad. Respeta el teclado y la preferencia de movimiento reducido.

Las preguntas de Claude Code existentes se conservan. Para responder preguntas de opciones de **Codex**, inicia una sesión nueva con el puente incluido. En Linux:

```bash
~/.local/share/coucou-local/bin/coucou-codex --cwd "$PWD" --plan 'Revisa el proyecto y pregunta qué enfoque prefiero'
```

Requiere Coucou abierto, Node 22+ en PATH y Codex CLI autenticado. El puente usa `codex app-server`; no se conecta a chats ya abiertos de Codex Desktop. Permite preguntas de opciones y aprobaciones de comandos/archivos, con respuestas humanas correlacionadas y una cola compartida entre sesiones. También admite `--model`, `--codex` y `--hook` (ejecutable nativo o archivo JavaScript). No admite respuestas libres, preguntas secretas ni solicitudes de permisos adicionales `item/permissions/requestApproval`; una solicitud no compatible se devuelve con un error explícito, sin conceder permisos. No sustituye al CLI interactivo completo: cada invocación ejecuta un turno y conserva la conversación de Codex en su almacenamiento normal.

Los hooks de Codex ya instalados siguen funcionando con su mecanismo anterior de aprobaciones. El puente es la vía específica para las preguntas con opciones. Las comprobaciones ejecutadas y los límites están en [VERIFICATION.md](VERIFICATION.md).

Incluye:

- Autocierre corregido tras avisos consecutivos, manteniendo los avisos al terminar. Panel a 10 segundos, sonido desactivado y pantalla del cursor.
- GitHub: repositorios propios, últimos commits y pipelines de Actions en ejecución; enlaces a cada elemento y textos en español.
- Codex como agente principal, plan y límites, diez hooks y solicitudes de aprobación desde la isla, con respuesta explícita del usuario. Las herramientas MCP muestran sus parámetros cuando hace falta.
- Enlace opcional con Coucou para Android desde Settings → Android phone: desactivado por defecto, sin servidor escuchando hasta activarlo. Emparejamiento QR con certificado fijado, controles separados para detalles, preguntas, chat, diffs, uso y servicios; «Pair again» desconecta los móviles anteriores. El APK se obtiene o compila por separado y no se instala con este setup.
- Spotify o Spotifast/EVA-01 mediante MPRIS: se prefiere Spotifast si ambos están abiertos, los controles siguen al propietario activo y se reconoce el lanzador `eva-01-audio`. Muñeco de escritorio desactivado.
- Inicio automático y acceso del menú apuntando al **binario personalizado**, con copias previas y restauración.

## Clonar e instalar

Requiere una sesión gráfica de Ubuntu/Debian **x86_64/amd64**, Python 3, acceso a Internet y espacio para la compilación Docker. KDE Plasma con Wayland y layer-shell es el entorno comprobado. La primera compilación puede tardar varios minutos. No modifica la barra de tareas ni las pantallas.

```bash
git clone https://github.com/XFunBox/coucou-setup.git
cd coucou-setup
bash install.sh
```

El repositorio es público y se puede clonar por HTTPS sin iniciar sesión. Si tienes SSH configurado, también puedes usar `git@github.com:XFunBox/coucou-setup.git`.

El instalador solicita `sudo` para las dependencias de ejecución y compilación. Si falta Docker, instala `docker.io`; si tu usuario no puede acceder al daemon, solicita `sudo` para ejecutar Docker. Node y Rust se usan dentro del contenedor. Codex existente se reutiliza; la app de escritorio se detecta en `/usr/lib/chatgpt/resources/codex`. Si falta Codex, se descarga el CLI oficial 0.159.2 con SHA-256 fijado.

El perfil del setup para instalaciones nuevas fija autocierre a 10 segundos, chat OpenAI y pantalla del cursor. Tanto la instalación completa como `--configure-only` aplican ese perfil: las claves que contiene sustituyen sus valores actuales; las demás claves y los hooks ajenos se conservan. Si actualizas una instalación personalizada y quieres conservar todos sus ajustes, guarda la configuración y sustituye únicamente los binarios verificados; este setup no ofrece un modo de actualización solo de binarios.

La aplicación oficial, si existe, se conserva. La versión compilada se instala para tu usuario en `~/.local/share/coucou-local/bin/`. El setup no se ha probado mediante una instalación completa de apt en un equipo limpio.

```bash
# Ver el plan sin descargar, instalar ni modificar nada:
bash install.sh --dry-run

# Compilar y comprobar, sin tocar la configuración ni cerrar Coucou:
bash install.sh --build-only

# Aplicar la compilación y el perfil base que ya existan en .build/release:
bash install.sh --configure-only
```

`--configure-only` verifica versión, fuente, parche y hashes antes de cerrar Coucou o cambiar archivos. No acepta una compilación antigua ni usa `/usr/bin/coucou` como sustituto.

## Autenticación y aprobaciones

Las preferencias se preparan automáticamente; las cuentas se autentican en cada equipo:

1. Entra en Codex con tu cuenta ChatGPT (`codex login`, o abre su app).
2. Revisa y autoriza los hooks de Coucou desde `/hooks`. No se copia la confianza de otro equipo. Abre un chat nuevo para comprobar los eventos.
3. Selecciona **Pedir aprobación / Ask for approval** en Codex para recibir las solicitudes que requieran tu decisión. En Coucou puedes pulsar **Permitir** o rechazar. La tarjeta no aprueba automáticamente ni todas las herramientas requieren aprobación. La prueba realizada fue controlada: el clic humano devolvió `allow` y el comando mostrado no se ejecutó.
4. En Coucou → Settings → Integrations → GitHub, introduce un token granular con acceso a tus repositorios y permisos **de lectura**: Contents, Actions, Commit statuses, Pull requests y Metadata. Estos permisos no se conceden desde el instalador. El token se guarda en el llavero del equipo.
5. Abre Spotifast/EVA-01 Audio o Spotify para que la tarjeta detecte el reproductor. La tarjeta conserva el título de la canción y la etiqueta de anuncio; en reposo identifica el reproductor.

GitHub lista hasta 500 repositorios propios, hasta veinte commits recientes de los diez repositorios con actividad más reciente y Actions `in_progress` de los repositorios listados no archivados. Los errores de acceso se indican como datos parciales. Se renueva cada cinco minutos sin ejecuciones activas y cada minuto con ejecuciones, adaptándose a cuentas grandes; abrir la sección y refrescar también permite actualizar.

El chat propio de Coucou es independiente de los chats de Codex. El perfil base del setup usa OpenAI para ese chat y requiere su propia clave de API; iniciar sesión en Codex no configura esa clave. No se incluyen credenciales, sesiones, historial ni confianza de hooks.

La base 0.5.0 incorpora el hub, dictado Flow y notas de voz. El setup no activa la escucha ni descarga modelos de voz automáticamente. Al arrancar, upstream migra el acceso de inicio de sesión para añadir `--autostart` y mantener oculto el hub al entrar.

## Copias y deshacer

Antes de escribir, el setup guarda ajustes, hooks, accesos y los binarios anteriores en:

```text
~/.local/share/coucou-setup/backups/FECHA/
```

`manifest.json` distingue archivos previos de los creados. Si la aplicación de archivos falla, se intenta restaurar esa copia. Para deshacer después, cierra Coucou desde su icono, elige la copia adecuada y revisa primero:

```bash
python3 restore.py ~/.local/share/coucou-setup/backups/FECHA --dry-run
python3 restore.py ~/.local/share/coucou-setup/backups/FECHA
```

La restauración recupera los archivos anteriores y elimina los que esa instalación creó. Ten en cuenta los cambios locales hechos después de la copia. Abre Coucou desde el acceso restaurado o al iniciar sesión.

## Fuente y compilación

`source-lock.json` fija el commit oficial, la suma del archivo fuente, la suma del parche y las versiones de las imágenes de Node/Rust. El Dockerfile instala las dependencias, ejecuta las regresiones y compila aplicación y relé. Las pruebas de integración MPRIS usan `dbus-run-session` dentro del contenedor, sin acceder al bus ni a los reproductores de tu sesión. Los paquetes npm y la aplicación Rust usan los lockfiles del código fuente.

```bash
# Solo preparar la fuente verificada y aplicar el parche:
bash build.sh --prepare-only

# Compilar directamente, con Docker y las herramientas ya disponibles:
bash build.sh

# Comprobar el instalador sin tocar tu configuración:
python3 -m unittest -v test_install.py
bash -n install.sh build.sh
```

Los resultados están en `.build/release/`, que Git ignora. No se suben binarios, archivos fuente descargados, credenciales ni imágenes Docker. El parche incluye el código de las mejoras, sus regresiones y las versiones de los lockfiles. `LICENSE` conserva la licencia MIT del código de Coucou y `LICENSE-ANDROID` la del enlace al móvil, de Rhytam Biswas; `LICENSE-ASSETS.md` recoge las condiciones del autor para nombre y recursos. El instalador descarga los recursos originales para la compilación personal.

Procedencia:

Resultados y límites de las pruebas: [VERIFICATION.md](VERIFICATION.md).

- [Código base oficial de Coucou](https://github.com/Louis-CFM/coucou/tree/841a81ce1d75b65882b30139e6b716d0837dce30).
- [Codex CLI 0.159.2](https://github.com/openai/codex/releases/tag/rust-v0.159.2).
- [Hooks de Codex](https://learn.chatgpt.com/docs/hooks).
