# Cambios

## 0.3.0-sendoa.2 — 2026-10-09

- El setup compila la versión personalizada desde el commit oficial fijado y un parche verificable. Incluye el Dockerfile completo, sin depender de imágenes locales previas.
- El inicio automático y el acceso del menú ejecutan `~/.local/share/coucou-local/bin/coucou`.
- El autocierre se vuelve a programar cuando llegan avisos consecutivos con el cursor fuera.
- GitHub muestra repositorios personales, últimos commits y Actions en ejecución, con enlaces y mensajes de acceso parcial.
- Las solicitudes de Codex muestran parámetros de herramientas MCP cuando no hay un comando sencillo y mantienen la decisión mediante clic explícito.
- Se conservan los ajustes del perfil actual, incluidos GitHub, Spotify y OpenAI como proveedor del chat independiente de Coucou.
- Copias de binarios, relé, ajustes, hooks y accesos; restauración automática ante fallos al aplicar y script de restauración manual.
- Antes de aplicar se comprueban versión, origen, parche y hashes. No se distribuyen credenciales ni confianza de hooks.
