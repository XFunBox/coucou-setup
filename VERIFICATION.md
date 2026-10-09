# Verificación — 2026-10-09

Preparación local de la versión **0.3.0-sendoa.2**:

- Descarga nueva del archivo oficial fijado por commit y SHA-256; aplicación del parche completo en un árbol Git aislado.
- `bash build.sh` completado con el Dockerfile de este repositorio y sus imágenes públicas de Node 22.23.3 y Rust 1.99; no se usaron las imágenes privadas de compilaciones anteriores.
- 123 pruebas Node y 26 pruebas Rust del código personalizado pasan.
- TypeScript, Vite, aplicación y relé Rust release compilados correctamente; sumas de los dos binarios comprobadas al exportar.
- 10 pruebas del instalador pasan: conservación de hooks y ajustes, ausencia de duplicados, accesos, copias, restauración y rechazo de datos inesperados.
- Perfil y binarios recién compilados aplicados a un directorio personal temporal con espacios; accesos validados con `desktop-file-validate`. Dependencias de ambos binarios presentes en Ubuntu del equipo.
- Restauración probada en un directorio temporal. La instalación real del usuario no se modificó.
- Sintaxis Bash y `--dry-run` correctos; parche completo, SHA-256 coincidente y revisión textual de credenciales sin coincidencias.

No se ha hecho una instalación completa de apt y autenticación en un equipo limpio. Las cuentas, el token GitHub y la confianza de hooks deben configurarse en cada equipo como explica el README. Las pruebas de la tarjeta de aprobaciones incluyen un clic humano comprobado previamente en Coucou, con un comando ficticio que no se ejecutó.

Los binarios y archivos descargados se generan en `.build/` y no se incluyen en Git. Esta actualización se prepara localmente para que el usuario la publique.
