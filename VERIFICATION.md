# Verificación — 2026-10-16

Versión final **0.5.0-sendoa.2**, base oficial Linux 0.5.0 `841a81ce1d75b65882b30139e6b716d0837dce30`. Dos cambios separados: primero la actualización principal a 0.5.0-sendoa.1, después Spotifast/EVA-01.

## Fuente y compilación

- Fuente, parche y versión fijados en `source-lock.json`; aplicación y reversión textual del parche comprobadas. Los paquetes externos de Cargo.lock conservan las versiones upstream.
- Compilación principal Docker completa con Node 22.23.3, Rust 1.99 y ALSA. Aplicación y relé release, TypeScript y Vite correctos.
- Principal: **403 Node, 26 GitHub Rust, 481 aplicación Rust y 34 relé**, sin fallos; seis pruebas upstream ignoradas por necesitar modelos o bus privado. Instalador: **10 Python**; sintaxis Bash y `git diff --check` correctos.
- Spotifast: **406 Node, 482 aplicación Rust y 34 relé**, sin fallos; 10 ignoradas en la pasada general. **Cinco pruebas MPRIS adicionales ejecutadas con éxito en un bus D-Bus privado**, incluidas las ignoradas que corresponden a Spotify/Spotifast. La prueba de reconexión se repitió además diez veces sin fallos. Se corrigió su sincronización para esperar los eventos asíncronos con un plazo máximo. Los modelos de voz y el portal de escritorio no se prueban aquí.
- La segunda compilación reutiliza la imagen principal y sus cachés de dependencias; vuelve a ejecutar Node, Rust, MPRIS privado y Tauri con el código .2. El Dockerfile del repositorio conserva la receta completa desde las imágenes públicas. No se repitió una segunda compilación desde cero.
- SHA-256 de aplicación/relé comprobados antes de cada instalación y después de cada arranque. `ldd` sin bibliotecas ausentes en este Ubuntu. Revisión independiente, hallazgos corregidos y regresiones ejecutadas.

## Funciones conservadas e integración

- Se mantienen autocierre, repositorios/commits/pipelines GitHub y aprobaciones Codex/MCP. Traducciones propias fusionadas dentro de `strings`, sin perder las nuevas entradas upstream.
- En Linux el relé hermano del ejecutable personalizado tiene prioridad sobre el de un paquete oficial antiguo; en Windows se conserva el orden previo.
- Spotifast tiene preferencia MPRIS si ambos clientes están abiertos; señales y controles siguen al propietario seleccionado. Pruebas de desaparición, reconexión, señales ajenas, lectura obsoleta y lanzadores EVA-01/Spotify realizadas en el contenedor.
- Regresión de interfaz: el nombre Spotifast/EVA-01 identifica el reposo y el acceso al reproductor; las canciones y los anuncios conservan su título.

## Instalación real y conservación

- Instaladas y arrancadas ambas fases, sustituyendo solo la aplicación y las dos copias del relé. Copias previas y reversión preparadas. Servicio final `active/running`, versión nueva y overlay layer-shell en el registro.
- Ajustes existentes conservados y hooks Codex/acceso del menú idénticos byte a byte en ambas fases. La migración upstream del autostart mantiene el ejecutable y añade `--autostart`. No se aplica el perfil base del instalador.
- Sesión real: reproductor seleccionado `org.mpris.MediaPlayer2.spotifast`, confirmado en log `True`; metadatos disponibles `True`. Solo se consultan nombres y propiedades, sin guardar canciones ni enviar controles de reproducción.
- Eventos de hooks posteriores al arranque observados: `True`.
- No se cambian credenciales, confianza de hooks, Spotifast, pantallas ni barra de tareas. El paquete oficial permanece instalado.

## Límites

No se verificaron visualmente la ventana nativa, una nueva aprobación humana ni clics de control sobre el reproductor real. Los controles se prueban con servidores MPRIS simulados en bus privado. No se descargaron modelos ni se probaron micrófono/dictado/notas de llamadas, emparejamiento Android o instalación apt en un equipo limpio. Voz y enlace Android conservan sus ajustes existentes; el setup no los activa automáticamente.

Resultados y rutas de reversión del equipo registrados en las notas de contexto Coucou. Los binarios y copias locales están excluidos de Git.
