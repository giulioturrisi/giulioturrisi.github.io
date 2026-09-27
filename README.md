# Giulio Turrisi

Alternative academic design on branch `design/oriolo-style`, inspired by https://www.diag.uniroma1.it/oriolo/. Plain HTML and CSS with no build step, custom JavaScript, or external fonts. The Videos page embeds the five newest published videos from the Research playlist using privacy-enhanced YouTube players.

## Preview locally

```sh
python3 -m http.server 8000
```

Open http://localhost:8000.

## Edit

- `index.html`: single-page site with Bio sketch, Research, Teaching, Software, and Videos. The `profile-bio`, `publications`, and `latest-videos` marker blocks are generated; keep manual edits outside them.
- `research/`, `teaching/`, `repositories/`, `videos/`: redirects to the corresponding homepage sections.
- `data/publications.json`: ten latest publications from Scholar, in publication-date order.
- `scripts/update_publications.py`: fetches and renders Scholar publications; `--render-only` uses the saved data without accessing Scholar.
- `scripts/update_bio.py`: synchronizes the biography from `giulioturrisi/giulioturrisi`, branch `master`. Markdown formatting and links are rendered; the `Contact:` and `Other sites:` lines are omitted because contacts are already beside the photo. Install `scripts/requirements.txt`, then run `python3 scripts/update_bio.py` to refresh locally.
- `scripts/update_videos.py`: refreshes the generated video section from the public YouTube playlist feed, without an API key. Run with `python3 scripts/update_videos.py`.
- `style-diag.css`: shared layout, with a white background in all system themes.
- `images/profile.png`: original profile photo.
- `profile-readme.md`: source README snapshot, updated by the biography sync script.

## Branch preview

This design is isolated on `design/oriolo-style`; `master` keeps the previous design. Preview locally using the command above. The deployment job only runs on `main` or `master`, including manual dispatches, so preview branches cannot replace the live site. Biography and video synchronization markers are preserved.

## GitHub Pages

Select **Settings → Pages → Build and deployment → Source → GitHub Actions**. The Pages workflow refreshes the biography and videos on push, every 48 hours, and on manual dispatch, then deploys the static site. A daily check at 00:23 UTC allows scheduled deployment on alternating UTC days, keeping the 48-hour cadence across month boundaries. Scheduled runs start after the workflow reaches the default branch; GitHub may delay schedules or disable them after prolonged repository inactivity. If the biography cannot be fetched or is invalid, the workflow warns and publishes the checked-in biography. If the video feed fails validation or cannot be fetched, the workflow warns and publishes the checked-in video snapshot. The `.nojekyll` file disables Jekyll processing. Paths assume this repository is served at the domain root, https://giulioturrisi.github.io/.

The layout follows the reference’s full-width white page, compact Verdana typography, blue underlined links, blue section titles, and horizontal rules. A photo and academic contact block sit above the navigation. The implementation uses original HTML and CSS and adapts to narrow screens.

The public YouTube playlist feed can be limited to 15 entries. The current playlist has 13 entries; if it grows beyond the feed limit, full-playlist retrieval should replace the feed to guarantee the newest five across every item.

Biography and video updates are included in the deployed Pages artifact without committing those changes. The separate publication workflow commits only `data/publications.json`. Edit and commit the profile README on GitHub to change the source biography.

This branch uses a separate `style-diag.css` stylesheet with page-relative URLs so previews cannot reuse the previous design’s cached `/style.css`.

## Weekly Scholar synchronization

`publications.yml` runs every Monday at 06:41 UTC, or manually, on `main`/`master`. It fetches the public Scholar profile with `sortby=pubdate`, keeps the first ten unique papers, and preserves Scholar's ordering within each year. This is publication recency, never citation count. The public list supplies years rather than exact dates, so the renderer does not invent day/month values.

On success, the workflow commits changed publication data. A `workflow_run` trigger then deploys Pages from the updated branch (bot commits alone do not trigger push workflows). Every regular Pages build also renders the saved publications, so the 48-hour bio/video updates preserve the latest weekly papers. If Scholar blocks access, returns a CAPTCHA, or changes its markup, the refresh fails without overwriting saved data; existing publications remain available. No API key or anti-bot bypass is used.

The five latest research videos appear as small players in one horizontal, scrollable row. Teaching retains its existing TODO until course information is added.

The tab icon is `images/favicon-robot.svg`, a vector recreation of the supplied robotic-arm reference. Profile links use local Simple Icons assets in `images/icons/` with their CC0 license included.

## Weekly software list

The Software section shows the six most-starred repositories from the public list https://github.com/stars/giulioturrisi/lists/mystuff. `scripts/update_software.py` reads the list (following pagination), gets exact star counts and descriptions from GitHub's public repository API, and sorts by stars descending, then repository name for ties. No unrelated starred repositories are included.

`.github/workflows/software.yml` runs every Monday at 07:17 UTC, or manually, on `main`/`master`. It uses the automatic `github.token` for API rate limits; no personal token or extra secret is required. The list must stay public. The workflow commits only `data/software.json`; a successful completion triggers Pages to render the saved data. Unavailable or malformed responses fail without replacing the last valid list.

Refresh locally with `python3 scripts/update_software.py` (an optional `GH_TOKEN` raises the API rate limit), or render saved data with `python3 scripts/update_software.py --render-only`. The home section between `software` markers is generated. Scheduled workflows become active after integration into the default branch.
