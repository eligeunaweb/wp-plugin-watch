# Metodología / Methodology

## Selección

Se consulta `query_plugins`, vista popular, ocho páginas de 250 resultados. Se filtran instalaciones publicadas >=10.000 y última actualización anterior en al menos 730 días al momento UTC de consulta. Se ordena por instalaciones descendentes y slug y se seleccionan los primeros veinte. `data/candidates.json` conserva la muestra inicial, hora y método; `watchlist.json` fija la lista seguida. Un plugin con actualizaciones posteriores permanece y cambia de estado. Nuevas incorporaciones se revisan manualmente.

La muestra puede cambiar entre páginas, no representa el directorio completo y puede omitir plugins cerrados o fuera de las primeras páginas. No se suman instalaciones como si fueran sitios únicos. Las cifras son las publicadas por la API, no una medida exacta. `tested` es una declaración de compatibilidad del autor, no una prueba nuestra.

## Estados y errores

- `no_updates_2y`: al menos 730 días sin actualización observada. No equivale a abandono o inseguridad.
- `updated_within_2y`: menos de 730 días. No garantiza mantenimiento futuro ni seguridad.
- `closed`: respuesta explícita de cierre; se recoge fecha y motivo público si existen.
- `not_found`: respuesta explícita de no encontrado. No inventa motivo de retirada.
- `check_status=error`: respuesta inválida o fuente inaccesible. Conserva el último dato válido y su `verified_at`, marca `checked_at` del intento fallido. Sin dato anterior, se muestra desconocido.

La respuesta de cierre/no encontrado puede carecer de instalaciones. Si existían, se mantienen con `metadata_observed_at` y marca histórica. `verified_at` solo se actualiza al recibir una respuesta válida. Los campos `changes` describen diferencias en la consulta actual; Git conserva las consultas anteriores. No hay historial anterior al inicio del proyecto. Un fallo de escritura no es una prueba de cierre. La escritura usa reemplazo por archivo; no se promete transacción de varios archivos ante un apagado. GitHub publica el conjunto en un único commit.

Se esperan hasta 20 segundos por petición; hasta tres intentos ante fallos de transporte, 429 y 5xx seleccionados, con pausas crecientes. Máximo 8 MiB por respuesta y una pausa de un segundo entre plugins. No se siguen redirecciones ni se ejecuta contenido de la API. El uso debe respetar las condiciones de WordPress.org; aumentar cobertura exige revisar carga y límites.

## English

Discovery samples eight popular-API pages of 250 entries. Candidates have >=10,000 published installs and >=730 days since the last update; the initial watchlist takes the first twenty sorted by installs and slug. It is not a complete census, an abandonment verdict or a vulnerability feed. Closed plugins may be absent from discovery. New candidates require review; renewed plugins stay tracked.

Explicit closure, explicit not-found and transport/validation failure are separate. Failed checks retain last valid metadata and verification date. Historical install counts on closed/not-found records are labeled and timestamped. Declared WordPress compatibility is not tested here. Current-run changes are recorded in JSON; Git provides longitudinal history from project inception. Counts do not represent distinct websites.

No plugin code is downloaded/executed. API data is rendered as escaped text and CSV formulas are neutralized. The script uses only Python's standard library. Metadata is attributed to WordPress.org, code is MIT; no rights to third-party code, names or artwork are implied. Dependencies/action pins and automated conclusions should be reviewed over time.
