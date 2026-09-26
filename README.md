# Giulio Turrisi

Minimal academic website with a layout inspired by https://cmastalli.github.io/. Plain HTML and CSS, no build step, JavaScript or tracking. Roboto is loaded from Google Fonts.

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
- `style.css`: shared layout, with a white background in all system themes.
- `images/profile.png`: original profile photo.
- `profile-readme.md`: source biography, copied from https://github.com/giulioturrisi/giulioturrisi on 2026-09-26. This is a snapshot; update the homepage manually when changing it.

## GitHub Pages

Publish from the repository root using GitHub Pages “Deploy from a branch”. The `.nojekyll` file disables Jekyll processing. Paths assume this repository is served at the domain root, https://giulioturrisi.github.io/.

The layout is inspired by https://cmastalli.github.io/, with the same 750px content width, white background, Roboto typography, blue links, and single-column layout. The implementation uses original HTML and CSS.
