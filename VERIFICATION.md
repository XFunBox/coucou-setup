# Verificación — 2026-10-23 — botones de permisos

Versión **0.5.1-sendoa.5**. La vista interna del proveedor de chat conservaba la clase `on` al ocultar el panel padre. Su `pointer-events: auto` interceptaba clics destinados a la tarjeta de permisos. La visibilidad del chat ahora desactiva esa vista interna y la reactiva al abrirlo; las notificaciones repetidas de visibilidad no vuelven a renderizarla.

- Regresión de ciclo visible → aprobación → visible: falla antes del cambio y pasa después. Pasan los archivos de pruebas de chat, chat Codex, hooks y FSM, más la comprobación TypeScript.
- QA de navegador con componentes reales y puente simulado: tanto Permitir como Denegar llegan al receptor de prueba. La simulación no autoriza herramientas reales.
- Revisión independiente sin hallazgos accionables; comprobados ocultación, reapertura, cambios de modo y sincronizaciones repetidas. Parche final aplicado a upstream limpio: **62 archivos idénticos** y SHA-256 fijado.
- TypeScript/Vite y Tauri release compilados con la interfaz final; nueve pruebas Rust del adaptador correctas. Exportación y SHA-256 verificados.
- Instalación nativa .5: servicio activo/running y overlay layer-shell confirmados; hashes comparados tras el arranque. Ajustes, hooks y menú byte idénticos, autostart conservado. Copia previa con reversión preparada. La recepción de clics se verificó con el puente simulado; queda pendiente confirmación humana del botón nativo.
- Mantiene el filtro Guardian de .4. Sin cambios en el protocolo de permisos, confianza de hooks ni preferencias de seguridad.

# Verificación — 2026-10-23 — selector sin revisiones internas

Versión **0.5.1-sendoa.4**. El índice nativo incluye «Guardian review» junto a los chats del usuario. Su origen `subagent.other=guardian` se comprobó mediante metadatos SQLite en modo solo lectura. El índice JSONL carece de ese campo: el selector excluye el nombre interno reservado, sin distinguir mayúsculas ni espacios exteriores, después de deduplicar y antes del límite de 100 chats. No se excluyen otros títulos por contener la palabra guardian.

- Regresión del código Rust real: falla sin el filtro y pasa con él. Las **nueve pruebas del adaptador** pasan. Selector contra el índice nativo: **76 chats y cero Guardian review**, sin mostrar ni guardar títulos o mensajes.
- Parche aplicado a upstream limpio: **61 archivos idénticos** y SHA-256 fijado. Sintaxis Bash y revisión de espacios correctas. No se modifican el protocolo, envío/parada, interfaz ni dependencias; las verificaciones de .3 siguen documentadas abajo.
- Pruebas afectadas dentro de la aplicación Rust release: **nueve correctas**. TypeScript/Vite y Tauri release compilados; aplicación y relé .4 exportados y SHA-256 verificado. Se reutilizan las dependencias locales y la interfaz sin cambios.
- Instalación nativa: servicio activo/running, versión .4 y overlay layer-shell confirmados en registro. Binarios comparados después del arranque; ajustes, hooks y menú byte idénticos, autostart conservado. Copia previa con reversión preparada. No se han enviado mensajes ni modificado sesiones para esta corrección.

# Verificación — 2026-10-23 — chat compartido con Codex

Versión **0.5.1-sendoa.3**, sobre Linux 0.5.1 y las personalizaciones EVA-01 existentes.

- Integración experimental con el IPC privado local del escritorio Codex 26.928.31416 / backend 0.159.2: selección explícita, historial canónico con actividad reciente, envío único y parada con el identificador del turno mostrado. En el chat de prueba autorizado se verificaron lectura, respuesta y parada mediante IPC y el adaptador Rust antes de la interrupción del equipo; no se repiten envíos durante la recuperación.
- Pruebas de recuperación: **444 pruebas Node** pasan en el contenedor final (31 archivos pasan también con el Node local). Rust release: **516 pruebas de la aplicación y 34 del relé**, sin fallos; 11 ignoradas en la ejecución general. **Cinco MPRIS** ejecutadas aparte con bus privado, correctas. También pasan las **10 Python** del instalador, sintaxis Bash y revisión de espacios.
- Una revisión independiente detectó que un rechazo de parada suspendía las actualizaciones. Se corrigió y se comprobó primero la regresión fallida y después su éxito: se reanuda la lectura, sin repetir acciones. Si un envío queda sin confirmar, conserva el borrador y el aviso después de actualizar el estado.
- Parche aplicado a la fuente canónica limpia: **61 archivos idénticos** a la fuente final. SHA-256 fijado en `source-lock.json`.
- QA visual previa al apagado con componentes reales y datos simulados en Chrome; captura conservada. Las regresiones de apertura/autocierre y del chat se comprueban con DOM simulado. No se presenta como una inspección visual completa de la ventana nativa KDE.

- TypeScript/Vite y Tauri release compilados con la interfaz final. Instalación real Ubuntu/KDE: servicio activo y ejecutándose, versión .3 y overlay layer-shell confirmados en registro, hashes de binarios verificados y `ldd` sin dependencias ausentes. Ajustes, hooks y entrada del menú byte idénticos; inicio automático conserva su comando. Copia previa y reversión preparadas.
- El binario instalado lee por IPC el chat de prueba correcto: **34 mensajes**, turno activo, sin decisiones pendientes y sin truncación en esa comprobación. La consulta fue de solo lectura y el informe conserva únicamente recuentos y estados.

La compilación local reutiliza dependencias y cachés de Docker; la receta pública conserva su construcción desde imágenes base. No se repitió una construcción sin cachés. Se mantiene el chat propio de Coucou y su configuración. El IPC es privado y puede cambiar con Codex; las aprobaciones se responden en la app. Las pruebas que requieren modelos/portal, micrófono, Android y controles sobre un reproductor real quedan fuera de esta validación.

# Verificación — 2026-10-21 — EVA-01

Versión **0.5.1-sendoa.2**, sobre la misma base Linux 0.5.1. Tema compartido en isla, Hub, ajustes y módulos, Mochi normal verde EVA y estados coordinados. Conserva colores personalizados e integraciones.

- **440 pruebas Node** correctas; TypeScript, Vite y Tauri release compilados. Contraste mínimo sobre superficies base: texto secundario 6,31:1 y error 4,79:1.
- Parche completo aplicado a upstream limpio: **57 archivos idénticos** a la fuente compilada; SHA-256 fijado en source-lock.json.
- QA con componentes reales y datos simulados en Chrome: sala expandida, detalle y plegado, reloj oculto con estado de agentes, Hub, ajustes y selector de módulos. Capturas revisadas y cero errores JavaScript.
- Instalación local verificada: servicio active/running, versión .2 y overlay layer-shell confirmados en registro. SHA-256 y bibliotecas comprobados antes de instalar; hashes comprobados tras arrancar. Ajustes, hooks y menú byte idénticos; copia previa con reversión preparada.

Compilación con dependencias y cachés previas. Las suites Rust/MPRIS documentadas en .1 se conservan sin repetición para este cambio visual. La QA visual corresponde a Chrome; el arranque nativo KDE se verificó mediante servicio y registro. Sin cambios en paneles ni pantallas. Binarios, copias y registros locales excluidos de Git.

# Verificación — 2026-10-21 — Linux 0.5.1

Versión **0.5.1-sendoa.1**, base oficial `9fe1773296cb857f223acedfd41b2842afc7dcac` (linux-v0.5.1). Conserva las personalizaciones de 0.5.0-sendoa.5.

- Fuente oficial y parche fijados por SHA-256. Parche aplicado sobre el archivo canónico limpio: 44 archivos modificados idénticos byte a byte a la fuente compilada. Versiones npm, Cargo y Tauri coordinadas.
- Se conservan Codex/límites/hooks/aprobaciones/MCP, monitor y sala EVA-01 opcional, plegado de 0,6 s, apertura habitual, GitHub, Spotifast/MPRIS y autocierre. Módulos propios del monitor/sala sin cambios frente a .5.
- Updater optativo exclusivo del fork `XFunBox/coucou-setup`, tags `vX.Y.Z-sendoa.N`, revisión numérica y URL exacta del fork. Linux abre la release; no instala automáticamente. Dos casos mínimos con funciones extraídas del código real fallan en upstream y pasan con el arreglo; suite unitaria Rust valida también selección de release.
- Reloj compacto optativo con prioridad para el estado de agentes. Traducciones propias fusionadas con el catálogo nuevo sin pérdida de claves upstream; alemán/turco completados.
- Dockerfile actualizado con los archivos Apple que requieren las nuevas pruebas de registro de idiomas. La prueba de zona de retorno usa los límites del lienzo nativo personalizado de 960 × 540. `npm test` habilita la transformación TypeScript que necesita la prueba del reloj.

Pruebas: **440 Node, 26 Rust GitHub, 508 unitarias Rust de la aplicación, 34 del hook y 5 MPRIS con bus privado correctas**. Las 11 ignoradas de la ejecución general incluyen esas 5 MPRIS ejecutadas aparte. También pasan 10 Python del instalador, sintaxis Bash y revisión de espacios. TypeScript/Vite y Tauri release compilados correctamente. No se han ejecutado doc-tests Rust. `npm audit` informa un paquete afectado: Vite 6.4.3, dependencia de desarrollo; conserva el lock upstream, sin actualización automática. El servidor de QA se limita a loopback y se elimina tras la comprobación.

QA con componentes reales en Chrome y datos simulados: sala 880 × 480, ficha de subagente, plegado a 288 × 32, cero puestos ocultos y cero errores JavaScript. Reloj opcional oculto cuando hay estado de agentes (opacidad 0). Capturas y métricas guardadas en el scratch del chat.

Instalación real: servicio active/running, versión **0.5.1-sendoa.1** y overlay layer-shell confirmados en el registro. SHA-256 de los dos ejecutables y `ldd` comprobados antes de instalar; hashes comprobados tras el arranque. Valores de ajustes existentes conservados; archivo de ajustes byte idéntico: True. Hooks y menú byte idénticos; inicio automático conserva el ejecutable. Copia previa con reversión preparada: `/home/sendoa/.local/share/coucou-local/backups/upgrade-0.5.1-sendoa.1-20261021-133023`. Sin cambios en paneles ni pantallas.

Lectura real del monitor con el binario instalado: 3 agentes, con aviso `bounded_history` por el límite de historial; no se presenta como árbol completo. Un reproductor MPRIS disponible en el bus de usuario, sin accionar controles.

La compilación local reutiliza la imagen y cachés de dependencias previas; se ejecutan las suites con la fuente nueva. La receta pública Docker conserva su construcción desde imágenes base. No se ha repetido una construcción sin cachés. Las pruebas ignoradas que necesitan modelos/portal no se presentan como verificadas; tampoco se han probado micrófono/dictado, Android, controles sobre un reproductor real ni una nueva aprobación humana. La QA visual descrita corresponde a Chrome, no a una inspección completa de la ventana nativa en KDE.

No se publica esta versión en el remoto como parte de esta actualización local. Los binarios y copias de seguridad quedan fuera de Git.


# Verificación — 2026-10-21 · apertura habitual

Versión **0.5.0-sendoa.5**. Cambio acotado: al abrir la isla se muestra la vista habitual, mientras la oficina sigue accesible desde «Sala de agentes».

- Regresiones de apertura, teclado y retirada de avisos adaptadas al comportamiento solicitado. **415 pruebas Node**, TypeScript/Vite y Tauri release correctos. Preguntas y aprobaciones conservan su prioridad.
- Parche aplicado a fuente limpia y 39 archivos cotejados byte a byte. SHA-256 y ldd comprobados. Servicio real active/running, versión .5 y overlay layer-shell confirmados en log; ajustes byte idénticos, hooks/menú conservados y copia previa preparada.
- El parser y el diseño de la sala no cambian: se conserva la verificación .4 de abajo, sin repetir sus pruebas Rust o QA visual. No se ha inspeccionado visualmente la ventana nativa.

# Verificación — 2026-10-21 · monitor de subagentes

Versión **0.5.0-sendoa.4**, sobre la misma base oficial Linux 0.5.0.

- **415 pruebas Node**, **10 pruebas Rust del monitor** y **10 Python del instalador** correctas; una prueba Rust de lectura de sesiones reales permanece ignorada en la suite aislada. TypeScript, Vite, Tauri release, sintaxis Bash y revisión de espacios correctos. La compilación local reutiliza dependencias y cachés de .3; se conserva la receta Docker completa del setup.
- Parche aplicado a fuente limpia, **40 archivos** comparados byte a byte y SHA-256 fijado. SHA-256 de binarios y `ldd` comprobados antes de instalar, hashes comprobados después del arranque.
- Parser incremental acotado, aislamiento de chats, jerarquía, guardianes excluidos, líneas parciales, truncación, privacidad y cadenas de padres incompletas/cíclicas cubiertos. Consulta JSON del binario final contra registros reales: árbol de este chat con **3 agentes**; comprobados principal y dos subagentes conocidos. No se devuelve contenido de mensajes ni argumentos/resultados de herramientas.
- Revisión independiente: prioridad visual de preguntas/permisos y clics tras cambiar entre hooks y monitor corregidos, con regresiones verificadas. Los metadatos se mantienen separados del chat/enlace al móvil.
- QA con componentes reales en Chrome y datos simulados: sala **880 × 480**, ficha de subagente, plegado a **288 × 32** al sacar el cursor, cero puestos ocultos y cero errores JavaScript. Pin explícito y retardo de 0,6 s cubiertos por pruebas. No se ha inspeccionado visualmente la ventana nativa.
- Instalación real: servicio `active/running`, versión .4 y overlay layer-shell confirmados en log. Valores de ajustes existentes conservados; hooks y menú idénticos. Copia previa y reversión preparadas. No se modifican paneles ni pantallas.
- Los estados proceden de registros locales de Codex, cuyo formato puede cambiar. Una lectura incompleta se indica como desconocida y se señala la actividad antigua; no se afirma un heartbeat de procesos ni un nuevo canal de respuestas a preguntas Codex. El árbol usa el ID del hook (resolviendo hijos validados hacia la raíz) o la raíz modificada más recientemente.

# Verificación — 2026-10-21

Versión **0.5.0-sendoa.3**, sobre la misma base oficial Linux 0.5.0. El cambio de esta versión está en la interfaz; no modifica la lógica Rust de servicios o hooks.

- **409 pruebas Node** correctas en la fuente final, incluidas las regresiones de filtrado, traducciones, navegación y liberación de personajes al plegar. **10 pruebas Python** del instalador, sintaxis Bash y revisión de espacios correctas.
- El parche se aplica a la fuente original limpia; sus 29 archivos resultantes coinciden byte a byte con la fuente de trabajo. SHA-256 fijado en `source-lock.json`.
- Vista previa con los componentes reales de la isla en Chrome: cuatro puestos, uno, sala vacía, navegación a detalle y vuelta a sala; sin errores JavaScript. Los datos de esa vista son simulados. Revisión independiente y corrección del ciclo de vida de los personajes ocultos.
- Compilación Tauri release, TypeScript y Vite correctos. SHA-256 de aplicación y relés verificados antes y después del arranque; `ldd` sin bibliotecas ausentes. Servicio real `active/running`, versión .3 y overlay layer-shell confirmados en el registro. Ajustes existentes conservados y hooks/acceso del menú idénticos. Copia previa y reversión preparadas. No se ha comprobado visualmente la ventana nativa: la QA visual corresponde a Chrome.
- Compacto verificado con estado visible y cero puestos ocultos; sin errores JavaScript.
- La sala representa agentes registrados; no inventa subagentes internos de Codex. Las preguntas y aprobaciones conservan sus canales previos. No se afirma un nuevo canal bidireccional de preguntas de esta app Codex.
- Se conserva la receta Docker completa del setup; la compilación local reutiliza dependencias de la imagen .2. Las suites Rust/MPRIS de .2 que se describen abajo no se repiten para este cambio de interfaz.

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
