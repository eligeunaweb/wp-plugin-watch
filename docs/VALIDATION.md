# Validación / Validation

Fecha de los últimos datos: 2026-11-18T12:29:55Z.

- Python 3.12.9, Windows: 16 pruebas unitarias/integración de archivos ejecutadas, todas correctas, sin omisiones.
- Consulta real de ocho páginas populares (hasta 2.000 plugins): 39 candidatos con los criterios documentados.
- Dos ciclos reales de actualización de la selección de 20 plugins: ambos sin errores. El segundo devolvió 0 cambios de metadatos; cambió la fecha de observación.
- La API real de un plugin cerrado y de un slug inexistente se consultó al preparar los validadores. Se distingue cierre de no encontrado; los tests verifican preservación ante fallos, reintentos y respuestas inválidas.
- Pruebas de CSV/HTML, Unicode, esquemas, renovación del mantenimiento, error parcial, límites de respuesta, redirecciones y escritura de archivos.
- El primer ensayo local de archivos falló por permisos del TEMP del sandbox. Se repitió con TEMP/TMP en una carpeta permitida, sin modificar las comprobaciones. Se corrigió además el cierre de un archivo del propio test.
- La primera exploración alcanzó el límite de respuesta porque los campos booleanos se codificaban como texto false. Se corrigieron a 0/1; se mantuvo el límite de 8 MiB y la exploración terminó correctamente.

## Pendiente de ejecución externa

Los workflows para Windows/Linux/macOS y actualización diaria están preparados, pero todavía no se han ejecutado en GitHub. Falta crear/publicar el repositorio; el conector de esta sesión no permite crear repositorios nuevos. No afirmar que la automatización está activa hasta comprobar Actions y el commit del bot. Una primera ejecución por push o manual no prueba una ejecución schedule futura.

No se han auditado vulnerabilidades de los plugins ni se han probado migraciones, compatibilidad con WordPress/PHP o parches. Las alternativas/migraciones siguen fuera de esta entrega del monitor. No hay dependencias Python de terceros.

## English

Executed locally on Windows/Python 3.12.9: all 16 tests passed. Two live refreshes of 20 plugins succeeded. Discovery sampled eight popular pages and found 39 qualifying candidates. Error recovery, strict response handling, historical counts, CSV/HTML safety and file generation were exercised. GitHub CI and scheduled execution are pending publication; configuration is not proof of execution. No plugin security audit, WordPress compatibility or migration testing is claimed.
