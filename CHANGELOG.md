# Cambios

## 0.4.0-sendoa.1 — 2026-10-14

- Actualización al commit oficial Linux 0.4.0 `e1b2cfdfd684a312fc0d7db26be97d6269615a31`, con fuente y parche verificados por SHA-256.
- Se conservan autocierre, repositorios/commits/pipelines GitHub y aprobaciones Codex/MCP.
- Se fusionan las traducciones personalizadas con todas las traducciones nuevas de upstream.
- Nuevo enlace opcional a Coucou para Android, desactivado por defecto. QR y certificado fijado, controles separados de datos y reinicio del emparejamiento; el setup no compila ni instala el APK.
- Aviso upstream sobre la necesidad del CLI Claude Code para su medidor de límites, y actualización de workflows oficiales.
- Se incluyen la atribución y licencia MIT del enlace al móvil. Node 22.23.3 y Rust 1.99 se mantienen para la compilación.

## 0.3.0-sendoa.2 — 2026-10-09

- El setup compila la versión personalizada desde el commit oficial fijado y un parche verificable. Incluye el Dockerfile completo, sin depender de imágenes locales previas.
- El inicio automático y el acceso del menú ejecutan `~/.local/share/coucou-local/bin/coucou`.
- El autocierre se vuelve a programar cuando llegan avisos consecutivos con el cursor fuera.
- GitHub muestra repositorios personales, últimos commits y Actions en ejecución, con enlaces y mensajes de acceso parcial.
- Las solicitudes de Codex muestran parámetros de herramientas MCP cuando no hay un comando sencillo y mantienen la decisión mediante clic explícito.
- Se conservan los ajustes del perfil actual, incluidos GitHub, Spotify y OpenAI como proveedor del chat independiente de Coucou.
- Copias de binarios, relé, ajustes, hooks y accesos; restauración automática ante fallos al aplicar y script de restauración manual.
- Antes de aplicar se comprueban versión, origen, parche y hashes. No se distribuyen credenciales ni confianza de hooks.
