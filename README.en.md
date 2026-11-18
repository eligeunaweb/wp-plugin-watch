# WordPress Plugin Watch

[Español](README.md) · [Methodology](docs/METHODOLOGY.md) · [Setup](docs/SETUP.md)

**Widely installed WordPress plugins with maintenance signals worth reviewing.**
Public WordPress.org metadata, verifiable observation dates and reproducible daily updates. No AI, WordPress installation, API keys or third-party Python dependencies required.

The initial watchlist selects 20 candidates from the first 2,000 popular results with at least 10,000 published installations and 730 days without an update. This is a sample, not a directory census or a security/abandonment verdict. Plugins remain tracked after maintenance resumes. [Original candidate selection](data/candidates.json).

<!-- WATCH:START -->

Last run: **2026-11-18T13:13:19Z** · Errors: **0**

| Plugin | Installs¹ | Last updated | WP tested² | Status³ | Check |
|---|---:|---|---|---|---|
| [Health Check &amp; Troubleshooting](https://wordpress.org/plugins/health-check/) | 200000+ | 2024-07-25T21:43:00Z | 6.6.11 | No updates ≥730 days | OK |
| [YARPP – Yet Another Related Posts Plugin](https://wordpress.org/plugins/yet-another-related-posts-plugin/) | 100000+ | 2024-11-11T18:16:00Z | 6.7.11 | No updates ≥730 days | OK |
| [Disable REST API](https://wordpress.org/plugins/disable-json-api/) | 80000+ | 2023-09-14T00:26:00Z | 6.3.14 | No updates ≥730 days | OK |
| [Widget CSS Classes](https://wordpress.org/plugins/widget-css-classes/) | 80000+ | 2024-11-12T00:16:00Z | 6.7.11 | No updates ≥730 days | OK |
| [Facebook Chat Plugin – Live Chat Plugin for WordPress](https://wordpress.org/plugins/facebook-messenger-customer-chat/) | 70000+ | 2022-07-05T23:01:00Z | 5.9.20 | No updates ≥730 days | OK |
| [Heartbeat Control](https://wordpress.org/plugins/heartbeat-control/) | 70000+ | 2023-08-31T13:23:00Z | 6.3.14 | No updates ≥730 days | OK |
| [Fixed Widget and Sticky Elements for WordPress](https://wordpress.org/plugins/q2w3-fixed-widget/) | 70000+ | 2023-03-30T07:15:00Z | 6.2.15 | No updates ≥730 days | OK |
| [Add From Server](https://wordpress.org/plugins/add-from-server/) | 60000+ | 2020-12-11T07:32:00Z | 5.5.24 | No updates ≥730 days | OK |
| [Enhanced Media Library](https://wordpress.org/plugins/enhanced-media-library/) | 60000+ | 2024-07-15T14:07:00Z | 6.5.14 | No updates ≥730 days | OK |
| [Brazilian Market on WooCommerce](https://wordpress.org/plugins/woocommerce-extra-checkout-fields-for-brazil/) | 60000+ | 2024-02-17T19:14:00Z | 6.4.14 | No updates ≥730 days | OK |
| [Easy SSL Plugin for SAKURA Rental Server](https://wordpress.org/plugins/sakura-rs-wp-ssl/) | 50000+ | 2019-11-25T02:46:00Z | 5.3.27 | No updates ≥730 days | OK |
| [Disable Google Fonts](https://wordpress.org/plugins/disable-google-fonts/) | 30000+ | 2019-02-24T21:01:00Z | 5.1.28 | No updates ≥730 days | OK |
| [Export Media Library](https://wordpress.org/plugins/export-media-library/) | 30000+ | 2023-04-05T15:30:00Z | 6.2.15 | No updates ≥730 days | OK |
| [Scripts n Styles](https://wordpress.org/plugins/scripts-n-styles/) | 30000+ | 2023-06-06T19:13:00Z | 6.2.15 | No updates ≥730 days | OK |
| [Increase Maximum Upload File Size](https://wordpress.org/plugins/upload-max-file-size/) | 30000+ | 2023-08-14T06:49:00Z | 5.8.19 | No updates ≥730 days | OK |
| [Gutenberg Block Editor Toolkit – EditorsKit](https://wordpress.org/plugins/block-options/) | 20000+ | 2024-05-28T12:30:00Z | 6.5.14 | No updates ≥730 days | OK |
| [Change WordPress Login Logo](https://wordpress.org/plugins/change-login-logo/) | 20000+ | 2024-07-31T06:16:00Z | 6.6.11 | No updates ≥730 days | OK |
| [Hide Admin Notices](https://wordpress.org/plugins/hide-admin-notices/) | 20000+ | 2024-02-18T17:52:00Z | 6.4.14 | No updates ≥730 days | OK |
| [JetSticky For Elementor](https://wordpress.org/plugins/jetsticky-for-elementor/) | 20000+ | 2023-08-24T07:53:00Z | 6.3.14 | No updates ≥730 days | OK |
| [Material Design Icons for Page Builders](https://wordpress.org/plugins/material-design-icons-for-elementor/) | 20000+ | 2024-03-20T12:40:00Z | 6.5.14 | No updates ≥730 days | OK |

¹ WordPress.org published figures, not exact counts. Hist.: last known value, not current.
² Author declaration; compatibility has not been tested here.
³ Age or closure does not establish a vulnerability. This is not an “unsafe plugins” list.

Full metadata, verification dates and public closure reasons: [JSON](data/plugins.json) · [CSV](data/plugins.csv).

<!-- WATCH:END -->

## Usage

Python 3.11+ on Windows, Linux or macOS:

```console
python -m unittest discover -s tests -v
python watch.py refresh
python watch.py discover --pages 8
```

Discovery only writes candidates; it never changes the watchlist. Refresh generates Markdown, JSON and spreadsheet-safe CSV. Network failures retain last valid observations and exit with status 1. Explicit directory closure and not-found responses are distinct from connection errors. Previous installation counts on closed/not-found entries are historical, not current.

The workflow runs daily at **06:23 UTC** and supports manual dispatch. It must be installed on the default branch with Actions enabled; local files alone do not activate a schedule. GitHub may delay runs or disable schedules after 60 days without repository activity. Check Actions and data commits for evidence of execution.

The workflow commits only generated data/README files. Partial failures are published transparently and the run then fails. Tests and fresh validation precede publication; no credentials are needed for WordPress.org. API calls are bounded, paced and retried.

No vulnerability claims, automatic replacement recommendations, tested migrations or security patches are included. Those require separate evidence and human review. [Contributing](CONTRIBUTING.md).

Original code is MIT licensed. Metadata remains attributed to WordPress.org; plugin code, artwork and long descriptions are not redistributed. Independent project, not affiliated with WordPress.
