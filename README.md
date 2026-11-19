# Chrome Profiles — Alfred workflow

Open links, bookmarks and tabs in the Chrome profile you choose, instead of
whichever profile Chrome happened to use last.

## Usage

| Trigger | What it does |
|---|---|
| `cm [profile]` | Move the front Chrome tab to another profile: reopens it there and closes it here. |
| `co [url] [profile]` | Pick a profile for a URL. With no URL typed, the URL on the clipboard is used. |
| `cb <query>` | Search bookmarks from every profile. ↩ opens in the bookmark's own profile, ⌘↩ picks another. |
| `cp [profile]` | Open a new Chrome window in a profile. |
| Universal Action **Open in Chrome Profile…** | Same as `co`, for a selected URL or a clipboard-history entry. |

The workflow also has two unassigned Hotkey triggers, for `cm` and `co`.

## Install

```sh
python3 build.py                     # writes info.plist and Chrome-Profiles.alfredworkflow
open Chrome-Profiles.alfredworkflow  # import into Alfred
```

Requires Alfred with the Powerpack (built on Alfred 6), Google Chrome, and
`/usr/bin/python3` (installed with the Xcode Command Line Tools).

## Notes

- The first `cm` run asks for permission for Alfred to control Google Chrome.
- `cm` reloads the page in the new profile, so unsaved form input in the old tab is lost.
- `cp` always opens a new window; Chrome does not tell scripts which profile a window belongs to.
- Profiles are read from `~/Library/Application Support/Google/Chrome/Local State`.
  Set the `chrome_dir` / `chrome_app` environment variables in the workflow to
  point at a different Chromium-based browser.

## Layout

- `chrome.py` — all the logic: three Script Filters plus the open action.
- `build.py` — generates `info.plist` and packages the workflow.
