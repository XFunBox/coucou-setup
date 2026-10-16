# Verificación — 2026-10-16

Actualización principal a **0.5.0-sendoa.1**, base oficial Linux 0.5.0 `841a81ce1d75b65882b30139e6b716d0837dce30`. La integración Spotifast se reserva para un commit posterior.

## Fuente y compilación

- Fuente, parche y versión fijados en `source-lock.json`; parche aplicado y reversión textual comprobada. Los paquetes externos de Cargo.lock conservan las versiones de upstream.
- Docker completo con Node 22.23.3 y Rust 1.99: dependencias de audio incluidas, aplicación y relé release compilados. TypeScript y Vite correctos.
- Node: **403/403**. GitHub Rust: **26/26**. Workspace Rust release: **481 de aplicación y 34 de relé**, sin fallos; seis pruebas upstream ignoradas que requieren modelos o un bus privado. Python instalador: **10/10**. Sintaxis Bash y `git diff --check` correctos.
- SHA-256 de los dos binarios comprobados antes de instalar y después del arranque. `ldd` sin bibliotecas ausentes en este Ubuntu.
- Se conservan autocierre, repositorios/commits/pipelines y aprobaciones Codex/MCP; traducciones propias fusionadas dentro de `strings`, manteniendo el catálogo nuevo. Revisión independiente y correcciones verificadas con la suite.
- En Linux se prioriza el relé hermano del ejecutable personalizado sobre el recurso de un paquete oficial antiguo. En Windows se mantiene el orden anterior.

## Instalación real

- Sustitución exclusiva de aplicación y dos copias del relé, con copia de seguridad previa. Reinicio de `app-Coucou@autostart.service`; servicio activo, log con versión nueva y overlay layer-shell.
- Todos los valores existentes de ajustes conservados; hooks Codex y acceso del menú idénticos byte a byte. La migración upstream del inicio automático solo añade `--autostart` al mismo ejecutable. No se aplica el perfil base del instalador.
- No se cambian credenciales, confianza de hooks, pantallas ni barra de tareas. La instalación oficial permanece.

## Límites

No se verificaron visualmente la ventana nativa ni una nueva aprobación humana. No se descargaron modelos ni probaron micrófono, dictado, notas de llamadas, emparejamiento Android o una instalación apt en un equipo limpio. Las funciones de voz y el enlace Android conservan sus valores existentes; el setup no los activa automáticamente. Spotify mantiene aquí la implementación previa; Spotifast se prueba por separado.

Los resultados y la ruta de reversión de este equipo se registran en la nota de contexto Coucou. Los binarios y las copias locales se excluyen de Git.
