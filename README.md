# Giulio Turrisi

Alternative academic design on branch `design/oriolo-style`, inspired by https://www.diag.uniroma1.it/oriolo/. Plain HTML and CSS with no build step, custom JavaScript, or external fonts. The Videos page embeds the five newest published videos from the Research playlist using privacy-enhanced YouTube players.

## Preview locally

```sh
python3 -m http.server 8000
```

Open http://localhost:8000.

## Edit

- `index.html`: photo and biography from the GitHub profile README. Only the content between `profile-bio` markers is generated; keep manual edits outside it.
- `research/index.html`: redirects to Google Scholar; Research navigation links open Scholar directly.
- `teaching/index.html`: teaching and learning resources.
- `repositories/index.html`: selected projects.
- `videos/index.html`: five individual videos, ordered by publication date (not playlist position or last update).
- `scripts/update_bio.py`: synchronizes the biography from `giulioturrisi/giulioturrisi`, branch `master`. Markdown formatting and links are rendered; the `Contact:` and `Other sites:` lines are omitted because contacts are already beside the photo. Install `scripts/requirements.txt`, then run `python3 scripts/update_bio.py` to refresh locally.
- `scripts/update_videos.py`: refreshes the generated video section from the public YouTube playlist feed, without an API key. Run with `python3 scripts/update_videos.py`.
- `style-oriolo.css`: shared layout, with a white background in all system themes.
- `images/profile.png`: original profile photo.
- `profile-readme.md`: source README snapshot, updated by the biography sync script.

## Branch preview

This design is isolated on `design/oriolo-style`; `master` keeps the previous design. Preview locally using the command above. The deployment job only runs on `main` or `master`, including manual dispatches, so preview branches cannot replace the live site. Biography and video synchronization markers are preserved.

## GitHub Pages

Select **Settings → Pages → Build and deployment → Source → GitHub Actions**. The Pages workflow refreshes the biography and videos on push, every 48 hours, and on manual dispatch, then deploys the static site. A daily check at 00:23 UTC allows scheduled deployment on alternating UTC days, keeping the 48-hour cadence across month boundaries. Scheduled runs start after the workflow reaches the default branch; GitHub may delay schedules or disable them after prolonged repository inactivity. If the biography cannot be fetched or is invalid, the workflow warns and publishes the checked-in biography. If the video feed fails validation or cannot be fetched, the workflow warns and publishes the checked-in video snapshot. The `.nojekyll` file disables Jekyll processing. Paths assume this repository is served at the domain root, https://giulioturrisi.github.io/.

The layout follows the reference’s full-width white page, compact Verdana typography, blue underlined links, blue section titles, and horizontal rules. A photo and academic contact block sit above the navigation. The implementation uses original HTML and CSS and adapts to narrow screens.

The public YouTube playlist feed can be limited to 15 entries. The current playlist has 13 entries; if it grows beyond the feed limit, full-playlist retrieval should replace the feed to guarantee the newest five across every item.

Biography and video updates are included in the deployed Pages artifact; the workflow does not commit generated changes back to this repository. Edit and commit the profile README on GitHub to change the source biography.

This branch uses a separate `style-oriolo.css` stylesheet with page-relative URLs so previews cannot reuse the previous design’s cached `/style.css`.
