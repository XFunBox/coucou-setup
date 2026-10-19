# Windows y oficina de agentes

## Objetivo
Extender el setup personal de Coucou a Windows nativo y ofrecer en Linux y Windows una oficina opcional que represente sesiones reales y permita abrir sus preguntas y aprobaciones.

## Diseño aprobado en conversación
- Reutilizar el backend Windows upstream; añadir instalación/configuración con verificación de procedencia y restauración, sin reemplazar herramientas del equipo.
- Conservar la isla y añadir una página Oficina al Hub con gráficos originales, estados reales y navegación accesible.
- Identificar sesiones y subagentes por separado sin alterar el catálogo existente de integraciones.
- Para preguntas Codex, usar un puente explícito que inicia una sesión mediante app-server y devuelve respuestas estructuradas. No atribuir a este puente control de conversaciones Desktop existentes.
- Mantener el parche Sendoa original e incorporar un segundo parche verificado para estas capacidades en ambas compilaciones.

## Plan de ejecución
1. Windows: pruebas de rutas con espacios, fusión hooks, backups/restauración y procedencia; implementar build/install y configuración nativos. Responsable: windows_setup.
2. Sesiones y preguntas: pruebas de dos sesiones, subagentes, correlación y protocolo de preguntas; implementar estado de oficina y puente Codex. Responsable: sessions_codex.
3. Oficina: vista Hub conectada por eventos a la isla; estados vacíos, teclado y movimiento reducido; probar render/modelo y compilación TypeScript. Responsable: office_ui.
4. Integración: generar desktop.patch desde fuente verificada, actualizar hashes y aplicar ambos parches en Linux; comprobar preparación limpia, tests frontend, tests setup Windows, checks Linux en CI. Responsable: principal.
5. Entrega: documentar comandos, límites verificados y comprobaciones pendientes; rama y PR de revisión sin fusionar ni instalar en la sesión del usuario.

## Validación
- Python unittest para configuración y procedencia; no tocar perfil real del usuario.
- Node test runner para hooks, oficina y puente con app-server de prueba sin inferencia de pago.
- tsc --noEmit y Vite build.
- Preparación de fuente limpia con ambas verificaciones SHA256.
- CI Linux/Windows para la diferencia de plataformas. La compilación nativa necesita toolchain MSVC/Rust en Windows y librerías gráficas en Linux.
