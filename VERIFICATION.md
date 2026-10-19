# Verificación 0.5.0-sendoa.3 — 2026-10-19

Implementación Windows y oficina de agentes preparada a partir de la misma fuente fijada, conservando el parche Sendoa original y añadiendo `patches/desktop.patch` con SHA-256 propio.

## Comprobaciones de esta versión

- **431 pruebas Node pasan**: regresiones existentes, sesiones/subagentes, oficina, navegación y localización, cola entre procesos, cancelación y preguntas/aprobaciones Codex.
- **11 pruebas Python Windows pasan**, incluidas ejecución real de PowerShell, dry-run sin escrituras, opciones incompatibles, ida/vuelta UTF-8 a un ejecutable de prueba, rutas con espacios y caracteres especiales, fusión de hooks, instalación/restauración aisladas y rollback ante un archivo bloqueado.
- TypeScript y compilación Vite correctos. La oficina utiliza el renderizador real del Hub; los tests DOM comprueban texto seguro, contexto por sesión, foco y liberación de listeners.
- El E2E del puente inicia procesos separados de App Server y relé de prueba: valida el protocolo fijado de Codex, solicita una opción, devuelve la respuesta al request original y observa la continuación. No ejecuta inferencia ni sustituye una prueba con un agente autenticado.
- Fuente original verificada y aplicación de ambos parches desde cero correctas; todos los archivos resultantes cambiados coinciden byte a byte con la fuente de trabajo. Preparación probada también con `core.autocrlf=true` global.
- `install.ps1` y `build.ps1` analizados por PowerShell sin errores. El sandbox local bloquea el arranque de Git Bash, por lo que la sintaxis Bash y las regresiones Linux se ejecutan mediante CI.
- Revisiones independientes corrigieron mezcla de contextos entre sesiones, rollback parcial, enum de sandbox de Codex, pérdida de `--cwd` y doble ACK de una solicitud encolada.

## Comprobaciones pendientes

El equipo de desarrollo no tiene Rust/MSVC. La compilación nativa Windows y las pruebas Rust del relé están configuradas en `.github/workflows/desktop.yml`, junto con las comprobaciones Linux. Consulta el resultado de Actions para el commit que vayas a utilizar; la presencia del workflow no acredita una compilación exitosa.

No se ha instalado ni iniciado esta versión en el perfil real del usuario, ni se ha verificado visualmente el escritorio nativo Windows/Linux. El navegador de comprobación no pudo acceder al servidor local. No se probaron reproducción multimedia real, voz ni Android en esta versión. Las pruebas e instalación aisladas no contienen credenciales.

El puente crea sesiones Codex propias, de un turno por invocación: no intercepta chats Desktop existentes. Solo admite preguntas con opciones y aprobaciones de comandos/archivos; texto libre, preguntas secretas y permisos adicionales requieren otro cliente. Las solicitudes caducadas/no compatibles no conceden permisos. Los subagentes aparecen únicamente si el origen envía identificadores concretos; no se deducen de texto libre.

---

# Verificación histórica 0.5.0-sendoa.2 — 2026-10-16

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
