# Hao Zhang · Fudan University

Bilingual (English / 中文) homepage for Hao Zhang's group, served by GitHub Pages.
Content was taken from the [Fudan faculty page](https://optics.fudan.edu.cn/2a/11/c39771a469521/page.htm).

## Updating content

All content lives in two files:

- `data/profile.json`: biography, awards, student honors, members, alumni, research areas, teaching, contact
- `data/publications.json`: selected papers and the full publication list

After editing, regenerate the HTML and commit everything, including the generated pages:

```bash
python3 build.py
git add -A && git commit -m "Update content" && git push
```

`build.py` needs only the Python 3 standard library. English pages are written to the repository
root and Chinese pages to `zh/`.

Notes:

- Group news (papers, talks, …) go in `news`, student honors in `honors` (newest first) in `profile.json`.
  The home page merges both and shows the six most recent; the Member page timeline shows `honors` only.
- Publication ids (`J148`, `C9`, …) are used as anchors and by the research page's
  representative-paper lists, so keep existing ids stable when adding papers.
- Paper figures are in `images/papers/`; reference them with the `figure` field.
- Set `site_url` in `profile.json` (e.g. `https://<user>.github.io`) to emit canonical links, a sitemap and robots.txt.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>.

The Poppins font is licensed under the SIL Open Font License (`assets/fonts/OFL.txt`).
