# WordPress Plugin Watch

[English](README.en.md) · [Metodología](docs/METHODOLOGY.md) · [Instalación y GitHub Actions](docs/SETUP.md)

**Plugins con muchas instalaciones y señales de mantenimiento que merece la pena revisar.**
Datos de WordPress.org, fechas verificables y actualización diaria reproducible. No necesita IA, WordPress instalado, claves de API ni dependencias de Python externas.

La selección inicial incluye 20 candidatos de una muestra de los primeros 2.000 resultados populares: al menos 10.000 instalaciones publicadas y 730 días sin actualizaciones. No es un censo del directorio ni un dictamen de abandono o seguridad. Los plugins permanecen en seguimiento aunque vuelvan a actualizarse. [Selección original y otros candidatos](data/candidates.json).

<!-- WATCH:START -->

Última consulta: **2026-11-18T12:29:55Z** · Errores: **0**

| Plugin | Instalaciones¹ | Última actualización | WP probado² | Estado³ | Consulta |
|---|---:|---|---|---|---|
| [Health Check &amp; Troubleshooting](https://wordpress.org/plugins/health-check/) | 200000+ | 2024-07-25T21:43:00Z | 6.6.11 | Sin actualizar ≥730 días | OK |
| [YARPP – Yet Another Related Posts Plugin](https://wordpress.org/plugins/yet-another-related-posts-plugin/) | 100000+ | 2024-11-11T18:16:00Z | 6.7.11 | Sin actualizar ≥730 días | OK |
| [Disable REST API](https://wordpress.org/plugins/disable-json-api/) | 80000+ | 2023-09-14T00:26:00Z | 6.3.14 | Sin actualizar ≥730 días | OK |
| [Widget CSS Classes](https://wordpress.org/plugins/widget-css-classes/) | 80000+ | 2024-11-12T00:16:00Z | 6.7.11 | Sin actualizar ≥730 días | OK |
| [Facebook Chat Plugin – Live Chat Plugin for WordPress](https://wordpress.org/plugins/facebook-messenger-customer-chat/) | 70000+ | 2022-07-05T23:01:00Z | 5.9.20 | Sin actualizar ≥730 días | OK |
| [Heartbeat Control](https://wordpress.org/plugins/heartbeat-control/) | 70000+ | 2023-08-31T13:23:00Z | 6.3.14 | Sin actualizar ≥730 días | OK |
| [Fixed Widget and Sticky Elements for WordPress](https://wordpress.org/plugins/q2w3-fixed-widget/) | 70000+ | 2023-03-30T07:15:00Z | 6.2.15 | Sin actualizar ≥730 días | OK |
| [Add From Server](https://wordpress.org/plugins/add-from-server/) | 60000+ | 2020-12-11T07:32:00Z | 5.5.24 | Sin actualizar ≥730 días | OK |
| [Enhanced Media Library](https://wordpress.org/plugins/enhanced-media-library/) | 60000+ | 2024-07-15T14:07:00Z | 6.5.14 | Sin actualizar ≥730 días | OK |
| [Brazilian Market on WooCommerce](https://wordpress.org/plugins/woocommerce-extra-checkout-fields-for-brazil/) | 60000+ | 2024-02-17T19:14:00Z | 6.4.14 | Sin actualizar ≥730 días | OK |
| [Easy SSL Plugin for SAKURA Rental Server](https://wordpress.org/plugins/sakura-rs-wp-ssl/) | 50000+ | 2019-11-25T02:46:00Z | 5.3.27 | Sin actualizar ≥730 días | OK |
| [Disable Google Fonts](https://wordpress.org/plugins/disable-google-fonts/) | 30000+ | 2019-02-24T21:01:00Z | 5.1.28 | Sin actualizar ≥730 días | OK |
| [Export Media Library](https://wordpress.org/plugins/export-media-library/) | 30000+ | 2023-04-05T15:30:00Z | 6.2.15 | Sin actualizar ≥730 días | OK |
| [Scripts n Styles](https://wordpress.org/plugins/scripts-n-styles/) | 30000+ | 2023-06-06T19:13:00Z | 6.2.15 | Sin actualizar ≥730 días | OK |
| [Increase Maximum Upload File Size](https://wordpress.org/plugins/upload-max-file-size/) | 30000+ | 2023-08-14T06:49:00Z | 5.8.19 | Sin actualizar ≥730 días | OK |
| [Gutenberg Block Editor Toolkit – EditorsKit](https://wordpress.org/plugins/block-options/) | 20000+ | 2024-05-28T12:30:00Z | 6.5.14 | Sin actualizar ≥730 días | OK |
| [Change WordPress Login Logo](https://wordpress.org/plugins/change-login-logo/) | 20000+ | 2024-07-31T06:16:00Z | 6.6.11 | Sin actualizar ≥730 días | OK |
| [Hide Admin Notices](https://wordpress.org/plugins/hide-admin-notices/) | 20000+ | 2024-02-18T17:52:00Z | 6.4.14 | Sin actualizar ≥730 días | OK |
| [JetSticky For Elementor](https://wordpress.org/plugins/jetsticky-for-elementor/) | 20000+ | 2023-08-24T07:53:00Z | 6.3.14 | Sin actualizar ≥730 días | OK |
| [Material Design Icons for Page Builders](https://wordpress.org/plugins/material-design-icons-for-elementor/) | 20000+ | 2024-03-20T12:40:00Z | 6.5.14 | Sin actualizar ≥730 días | OK |

¹ Cifras publicadas por WordPress.org, no conteos exactos. Hist.: último valor conocido, no actual.
² Declaración del autor; no hemos probado esa compatibilidad.
³ Antigüedad o cierre no demuestran una vulnerabilidad. No es una lista de plugins «inseguros».

Datos completos, fechas de verificación y motivos públicos de cierre: [JSON](data/plugins.json) · [CSV](data/plugins.csv).

<!-- WATCH:END -->

## Qué hace

- Consulta únicamente la API pública de WordPress.org, con pausas, límites y reintentos.
- Distingue plugin cerrado, no encontrado y consulta fallida. Conserva datos válidos ante errores.
- Publica Markdown, JSON y CSV; neutraliza HTML y fórmulas de hojas de cálculo.
- Conserva cambios mediante el historial de Git y muestra diferencias en el JSON de cada ejecución.
- Programa una consulta diaria a las **06:23 UTC** (07:23 invierno / 08:23 verano en Madrid), además de ejecución manual.

**El workflow debe estar publicado en la rama predeterminada y habilitado para que exista actualización diaria.** Tener el archivo local no activa GitHub Actions. La página Actions y el último commit de datos permiten comprobarlo. GitHub puede retrasar ejecuciones y desactivar programaciones tras 60 días sin actividad.

## Ejecutar

Python 3.11 o superior, en Windows, Linux o macOS:

```console
python -m unittest discover -s tests -v
python watch.py refresh
```

Para descubrir candidatos sin cambiar la lista seguida:

```console
python watch.py discover --pages 8
```

Un error de consulta produce salida 1, mantiene el último dato válido y deja el error visible. El workflow conserva esos resultados y termina en rojo para no ocultar el fallo.

## Qué NO se automatiza

No se declara un plugin vulnerable por su antigüedad. No se recomiendan sustituciones automáticamente ni se cambian webs. Este repositorio no publica todavía migraciones probadas ni parches de seguridad. Para añadirlos se requieren pruebas en una instalación controlada, fuentes y revisión humana. [Cómo contribuir](CONTRIBUTING.md).

## Fuentes y licencia

- [WordPress Plugins API](https://developer.wordpress.org/reference/functions/plugins_api/)
- [Avisos del directorio](https://developer.wordpress.org/plugins/wordpress-org/alerts-and-warnings/)
- [Programación de GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

Código original: MIT. Los metadatos proceden de WordPress.org y conservan su procedencia; no se redistribuye código de plugins, imágenes o descripciones extensas. WordPress es una marca de sus titulares; proyecto independiente, sin afiliación.
