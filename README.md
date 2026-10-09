# Coucou con Codex, GitHub y Spotify

Instalación reproducible de mi configuración de Coucou en Linux. Perfil exportado el 9 de octubre de 2026: Coucou 0.3.0, Codex como agente principal, GitHub y Spotify, sonido desactivado y autocierre del panel a los 10 segundos. Usa la pantalla del cursor y arranca al iniciar sesión. El muñeco de escritorio está desactivado.

## Clonar e instalar

Ubuntu/Debian de 64 bits (amd64), Python 3 y una sesión gráfica. KDE Plasma con Wayland y layer-shell es el entorno comprobado. No modifica la barra de tareas ni la configuración de pantallas.

```bash
git clone https://github.com/XFunBox/coucou-setup.git
cd coucou-setup
bash install.sh
```

Como el repositorio es privado, GitHub pedirá autenticación al clonar. Si tienes acceso SSH configurado, también puedes usar `git@github.com:XFunBox/coucou-setup.git`.

El instalador solicita `sudo` únicamente para instalar el paquete de Coucou y sus dependencias. Verifica los SHA-256 publicados de Coucou 0.3.0 y Codex CLI 0.159.2. Si ya tienes Codex, reutiliza su ejecutable; si tienes la app de escritorio, crea un enlace a su ejecutable; en un equipo sin Codex descarga el CLI oficial para tu usuario. Conserva los otros hooks, guarda copias antes de aplicar ajustes y reinicia solo Coucou.

Para ver el plan sin modificar nada:

```bash
bash install.sh --dry-run
```

Si los programas ya están instalados:

```bash
bash install.sh --configure-only
```

## Autenticación del equipo nuevo

Los ajustes quedan preparados, pero las cuentas se autentican en cada equipo:

1. Abre Codex y entra con tu cuenta ChatGPT; desde terminal puedes ejecutar `~/.local/bin/codex login` si se instaló ahí. Si se reutilizó otro ejecutable, usa `codex login` desde su ruta habitual.
2. En Codex, abre `/hooks`, revisa las entradas de Coucou y autorízalas. El instalador no copia la confianza de otro equipo ni evita esa revisión. Abre una conversación nueva para comprobar los eventos.
3. En Coucou → Settings → Integrations → GitHub, introduce un token personal con lectura de Pull requests, Commit statuses y Actions en los repositorios que elijas. Se guarda en el llavero local, no en este repositorio.
4. Abre Spotify para que su tarjeta detecte el reproductor local mediante MPRIS.

La tarjeta Codex recibe actividad y puede mostrar límites de uso. El chat propio de Coucou es una conversación aparte: no permite enviar mensajes a un chat existente de Codex. El perfil conserva Anthropic como proveedor del chat; para usarlo requiere su propia clave, que tampoco se distribuye.

## Copias y comprobación

Las copias están en `~/.local/share/coucou-setup/backups/FECHA/` y conservan las rutas relativas al directorio personal. `manifest.json` indica qué archivos existían antes. Para deshacer, cierra Coucou, restaura los archivos anteriores que necesites y vuelve a abrirlo. No se eliminan archivos automáticamente; comprueba los cambios locales posteriores antes de restaurar.

```bash
python3 -m unittest -v test_install.py
tail -n 20 ~/.local/share/coucou/coucou.log
```

Pruebas automáticas: fusión de hooks ajenos, repetición sin duplicados, rutas con espacios, rechazo de JSON inesperado, copias y conservación de ajustes locales. El perfil se aplicó en un directorio temporal durante la preparación; no se ha probado una instalación completa de apt en un equipo limpio.

El perfil público del instalador contiene preferencias, no credenciales, sesiones, proyectos ni historiales. Los indicadores de instalación de Claude Code se conservan localmente; no se instala su integración.

## Procedencia

- [Coucou Linux 0.3.0](https://github.com/Louis-CFM/coucou/releases/tag/linux-v0.3.0) y [documentación de sus integraciones](https://github.com/Louis-CFM/coucou/blob/linux-v0.3.0/windows/README.md).
- [Codex CLI 0.159.2](https://github.com/openai/codex/releases/tag/rust-v0.159.2).
- [Hooks de Codex y revisión de confianza](https://learn.chatgpt.com/docs/hooks).

Este repositorio contiene el instalador y las preferencias. Descarga los programas oficiales, sin redistribuir sus binarios ni modificar su código.
