# Verificación — 2026-10-14

Actualización local a **0.4.0-sendoa.1**, basada en el tag oficial `linux-v0.4.0`, que apunta directamente al commit `e1b2cfdfd684a312fc0d7db26be97d6269615a31`.

- Fuente descargada por commit; archivo y parche fijados por SHA-256 en `source-lock.json`. El parche completo se aplica en un árbol Git aislado durante `build.sh`.
- Se mantienen las imágenes públicas Node 22.23.3 y Rust 1.99.
- 175 pruebas Node pasan: GitHub, dashboard personalizado, hooks/aprobaciones MCP, autocierre/FSM, traducciones y controles del enlace Android, chat y relé.
- 26 pruebas Rust del código GitHub pasan.
- 10 pruebas Python del instalador pasan: preservación de hooks ajenos, copias, restauración y rechazo de datos inesperados. Usan directorios temporales y fallos simulados; no instalan en el directorio personal real.
- Sintaxis de `install.sh` y `build.sh`, `--dry-run` y coherencia del SHA del parche comprobados.
- Las 346 entradas de traducción upstream se conservan idénticas; las diez etiquetas GitHub propias se completan en los nueve idiomas traducidos de la aplicación.
- `bash build.sh` completado con Docker: TypeScript, Vite y los binarios release de aplicación y relé compilados. Exportación en `.build/release/`, versión `0.4.0-sendoa.1`, lock y SHA-256 de ambos binarios comprobados.
- Ambos binarios son ELF x86-64; `ldd` resuelve todas sus dependencias en el Ubuntu del equipo. Esto comprueba el enlace dinámico, no el arranque de la interfaz.
- Revisión independiente del repositorio completada sin hallazgos; `git diff --check` correcto.

La primera ejecución detectó que la prueba i18n necesitaba el catálogo Mac dentro del contenedor y que las etiquetas personalizadas solo tenían traducción española. Se añadió el catálogo al Dockerfile y se completaron esas traducciones; las 175 pruebas pasan en la ejecución posterior.

Las pruebas Android anteriores usan el DOM y el puente Tauri simulados del proyecto. No se ha compilado un APK, emparejado un móvil ni comprobado una aprobación real desde Android. El enlace sigue desactivado por defecto en upstream; el setup no lo activa.

En este equipo se realizó una actualización de solo binarios con copia y reinicio controlado del servicio de usuario. La aplicación activa registra `Coucou 0.4.0-sendoa.1 started`, overlay layer-shell, servicio `active/running` y eventos reales PreToolUse/PostToolUse tras reiniciar. Ajustes, hooks y accesos del menú/inicio automático son idénticos byte a byte a los anteriores; no se aplicó el perfil base ni se tocaron credenciales, pantallas o barra de tareas. Se preparó reversión de los binarios anteriores.

`--configure-only` e instalación completa aplican las claves de `settings.json` (10 segundos, OpenAI y pantalla del cursor); conservar todos los ajustes de una instalación personalizada requiere una actualización de solo binarios como la anterior.

Al arrancar junto a un paquete oficial instalado, Coucou puede copiar su relé de `/usr/lib/Coucou/` a la ruta estable de hooks antes de buscar el relé junto al binario personalizado. En este equipo ocurrió así: el código fuente del relé de la base 0.3.0 y de 0.4.0 es idéntico, y su compatibilidad se comprobó mediante eventos reales; el binario personalizado nuevo y el relé compilado siguen en `coucou-local/bin/`. El paquete oficial no se modificó.

No se hizo inspección visual independiente de la ventana nativa ni una nueva aprobación humana con esta versión. La corrección del autocierre y la representación de aprobaciones están cubiertas por regresiones; la prueba real anterior del clic humano se distingue debajo.

No se ha hecho una instalación completa de apt ni autenticación en un equipo limpio. La prueba histórica del 09/10 de aprobaciones fue un clic humano que devolvió `allow` para un comando ficticio que no se ejecutó; no constituye una nueva prueba de la versión 0.4.0. Las cuentas, permisos GitHub y confianza de hooks se configuran en cada equipo según README.

Los binarios y la fuente descargada se generan en `.build/`, ignorado por Git. El repositorio incluye atribución MIT de Louis Raillé y del enlace Android de Rhytam Biswas, y las condiciones de nombre y recursos en `LICENSE-ASSETS.md`.
