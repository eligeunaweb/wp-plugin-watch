# Contribuir / Contributing

Propón cambios mediante pull request. Para incorporar un plugin, indica su slug oficial, fuente, fecha e instalaciones publicadas; explica por qué merece seguimiento. No cambies watchlist.json desde la actualización automática. No presentes antigüedad como vulnerabilidad ni una consulta fallida como cierre.

Los scripts automáticos solo cambian metadatos objetivos. Una alternativa necesita revisión funcional; una migración necesita versiones exactas, copia de seguridad, pasos reproducibles, pruebas antes/después y limitaciones. Una vulnerabilidad necesita un aviso público identificable y versiones afectadas. No publiques datos privados ni pruebas contra sitios ajenos.

Before a PR: `python -m unittest discover -s tests -v`. Changes to workflows/updater require human review. Data-only corrections must include their source and observation date. New alternatives, migration guides and security claims require independent evidence; they are never inferred from update age. Keep Spanish and English documentation aligned.
