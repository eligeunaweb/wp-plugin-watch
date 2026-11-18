# Validación / Validation

Fecha de los últimos datos: 2026-11-18T12:29:55Z.

- Python 3.12.9, Windows: 16 pruebas unitarias/integración de archivos ejecutadas, todas correctas, sin omisiones.
- Consulta real de ocho páginas populares (hasta 2.000 plugins): 39 candidatos con los criterios documentados.
- Dos ciclos reales de actualización de la selección de 20 plugins: ambos sin errores. El segundo devolvió 0 cambios de metadatos; cambió la fecha de observación.
- La API real de un plugin cerrado y de un slug inexistente se consultó al preparar los validadores. Se distingue cierre de no encontrado; los tests verifican preservación ante fallos, reintentos y respuestas inválidas.
- Pruebas de CSV/HTML, Unicode, esquemas, renovación del mantenimiento, error parcial, límites de respuesta, redirecciones y escritura de archivos.
- El primer ensayo local de archivos falló por permisos del TEMP del sandbox. Se repitió con TEMP/TMP en una carpeta permitida, sin modificar las comprobaciones. Se corrigió además el cierre de un archivo del propio test.
- La primera exploración alcanzó el límite de respuesta porque los campos booleanos se codificaban como texto false. Se corrigieron a 0/1; se mantuvo el límite de 8 MiB y la exploración terminó correctamente.

## Verificación en GitHub — 2026-11-18

Repositorio publicado en https://github.com/eligeunaweb/wp-plugin-watch. Los 16 tests pasaron en Windows, Linux y macOS: https://github.com/eligeunaweb/wp-plugin-watch/actions/runs/44311485332 . La primera actualización real de GitHub Actions consultó 20 plugins sin errores y publicó el commit 6ead220f22ee4377be5d8e4bb479c8d420b09d8d: https://github.com/eligeunaweb/wp-plugin-watch/actions/runs/44311485458 . Ambos workflows figuran active. La programación diaria es 06:23 UTC. Esta primera ejecución se disparó por push; todavía no ha ocurrido la primera ejecución de tipo schedule. Código probado: 53cc56e2cf08a0eb5e17150b67fe8db13d6dadff; el commit del bot solo modifica datos y tablas generadas.

No se han auditado vulnerabilidades de los plugins ni se han probado migraciones, compatibilidad con WordPress/PHP o parches. Las alternativas/migraciones siguen fuera de esta entrega del monitor. No hay dependencias Python de terceros.

## English

Executed locally on Windows/Python 3.12.9: all 16 tests passed. Two live refreshes of 20 plugins succeeded. Discovery sampled eight popular pages and found 39 qualifying candidates. Error recovery, strict response handling, historical counts, CSV/HTML safety and file generation were exercised. GitHub CI passed all 16 tests on Windows/Linux/macOS. The active daily workflow completed an initial push-triggered live refresh and published bot commit 6ead220f22ee4377be5d8e4bb479c8d420b09d8d. Daily scheduling is configured for 06:23 UTC; the first schedule-triggered run has not occurred yet. Run links and exact tested code revision are above. No plugin security audit, WordPress compatibility or migration testing is claimed.
