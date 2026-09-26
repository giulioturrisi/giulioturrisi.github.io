# Giulio Turrisi

Minimal academic website with a layout inspired by https://cmastalli.github.io/. Plain HTML and CSS with no build step or custom JavaScript. Roboto is loaded from Google Fonts. The Videos page embeds the five newest published videos from the Research playlist using privacy-enhanced YouTube players.

## Preview locally

```sh
python3 -m http.server 8000
```

Open http://localhost:8000.

## Edit

- `index.html`: photo and biography from the GitHub profile README.
- `research/index.html`: redirects to Google Scholar; Research navigation links open Scholar directly.
- `teaching/index.html`: teaching and learning resources.
- `repositories/index.html`: selected projects.
- `videos/index.html`: five individual videos, ordered by publication date (not playlist position or last update).
- `scripts/update_videos.py`: refreshes the generated video section from the public YouTube playlist feed, without an API key. Run with `python3 scripts/update_videos.py`.
- `style.css`: shared layout, with a white background in all system themes.
- `images/profile.png`: original profile photo.
- `profile-readme.md`: source biography, copied from https://github.com/giulioturrisi/giulioturrisi on 2026-09-26. This is a snapshot; update the homepage manually when changing it.

## GitHub Pages

Select **Settings → Pages → Build and deployment → Source → GitHub Actions**. The Pages workflow refreshes videos on push, every 48 hours, and on manual dispatch, then deploys the static site. A daily check at 00:23 UTC allows scheduled deployment on alternating UTC days, keeping the 48-hour cadence across month boundaries. Scheduled runs start after the workflow reaches the default branch; GitHub may delay schedules or disable them after prolonged repository inactivity. If the feed fails validation or cannot be fetched, the workflow warns and publishes the checked-in video snapshot. The `.nojekyll` file disables Jekyll processing. Paths assume this repository is served at the domain root, https://giulioturrisi.github.io/.

The layout is inspired by https://cmastalli.github.io/, with the same 750px content width, white background, Roboto typography, blue links, and single-column layout. The implementation uses original HTML and CSS.

The public YouTube playlist feed can be limited to 15 entries. The current playlist has 13 entries; if it grows beyond the feed limit, full-playlist retrieval should replace the feed to guarantee the newest five across every item.
