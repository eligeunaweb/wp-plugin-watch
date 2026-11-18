# Instalación / Setup

## GitHub

1. Crear `eligeunaweb/wp-plugin-watch`, público, con rama predeterminada `main`. Publicar los archivos, incluidas `.github/workflows/` y `data/`.
2. En Actions, habilitar los workflows si GitHub lo solicita.
3. Abrir **Daily WordPress metadata → Run workflow → main**.
4. Verificar el resultado, el commit de datos del bot y `generated_at`/`verified_at` en `data/plugins.json`.
5. Comprobar al día siguiente una ejecución de tipo `schedule`. La primera ejecución manual prueba el flujo; no demuestra que ya haya sucedido una ejecución programada.

El workflow usa `GITHUB_TOKEN` con `contents: write` solo para el trabajo de actualización. No necesita token personal ni secrets. Políticas de organización, protección de rama o reglas que exijan PR pueden bloquear el push: en ese caso adaptar el flujo a PR con revisión; no saltarse las reglas. Los pushes del propio GITHUB_TOKEN normalmente no disparan otros workflows; por eso el actualizador ejecuta las pruebas antes de publicar.

La publicación del workflow o un cambio de watchlist en la rama predeterminada también dispara una actualización inicial. Esto permite comprobar la publicación del bot sin esperar al día siguiente; no se confunde ese evento `push` con una ejecución diaria `schedule`.

Horario: 06:23 UTC cada día; Madrid 07:23 en invierno / 08:23 en verano. No se garantiza puntualidad. GitHub puede desactivar la programación tras 60 días sin actividad; comprobar Actions periódicamente. Los commits diarios contienen observaciones reales con su fecha. Para pausar, **Actions → Daily WordPress metadata → Disable workflow**. No instala tareas en tu ordenador.

Si la ejecución termina en rojo, revisar el paso fallido. Un fallo de fuente mantiene datos anteriores, deja la incidencia en el JSON y devuelve error. Un fallo de permisos al publicar requiere corregir permisos, no falsear el resultado. Los avisos de GitHub dependen de las preferencias de notificaciones del propietario.

## Local / English

Install Python 3.11+ and Git. No `pip install` is required. From the repository directory run:

```console
python -m unittest discover -s tests -v
python watch.py refresh
```

Publish on the default branch, enable Actions, then manually run **Daily WordPress metadata** and inspect its result plus the bot's data commit. The daily schedule is 06:23 UTC and may be delayed. Confirm a later event with type `schedule`; a manual success is not proof of a scheduled run. Public-repository inactivity and organization policies may disable/block it.

The updater uses only the repository GITHUB_TOKEN with job-scoped write permission. Branch protection can prevent direct pushes; use a reviewed PR workflow instead of bypassing policy. Source errors preserve previous verified metadata, are committed visibly and make the run fail. Tests run inside the updater because GITHUB_TOKEN pushes generally do not trigger separate CI. Disable the daily workflow in Actions to pause it.

Sources: [schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [workflow disabling](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).

## Explorer / Explorador

- `python watch.py expand --pages 20 --min-installs 1000`: discover and add candidates (maximum 500 total; retain tracked entries).
- `python watch.py refresh`: fetch tracked metadata; generate JSON/CSV, both READMEs, category lists and `docs/index.html` together.
- `python watch.py render`: regenerate outputs from saved metadata without network requests. Does not advance verification dates.
- Open `docs/index.html` directly in a browser, even offline. On GitHub, download the raw HTML first; GitHub file previews cannot run JavaScript. The category Markdown lists work directly on GitHub.
- GitHub Pages: Settings → Pages → Build and deployment → Source → **GitHub Actions**. Enable this once as repository owner, then run **Publish explorer** on main (or re-run its failed setup job). No personal token or extra secret is needed.
- `Publish explorer` tests and renders the latest trusted main branch, stages only `index.html`, and deploys it with the official pinned Pages actions. It runs on site changes and after the daily metadata workflow completes, including recorded source errors. This `workflow_run` trigger also handles data commits made with GITHUB_TOKEN. It never checks out pull request code or downloads artifacts from the triggering run. If tests/build fail, the last successful deployed site stays online.

Abre `docs/index.html` en el navegador, incluso sin conexión. En GitHub descarga primero el archivo HTML: la vista de código no ejecuta filtros. Las listas `CATEGORIES.md` sí se navegan dentro de GitHub. Para alojarlo, el propietario debe seleccionar una vez **Settings → Pages → Source → GitHub Actions** y ejecutar **Publish explorer** en main. Después se publica automáticamente tras cambios del sitio y al terminar la actualización diaria, sin tokens personales. Si fallan las pruebas o el despliegue, permanece la última web publicada.

Browser checks (development only): install `pip install -r requirements-test.txt`, then `python -m playwright install chromium`, and run `python tests/browser_check.py`. Runtime/updater remain standard-library-only.
