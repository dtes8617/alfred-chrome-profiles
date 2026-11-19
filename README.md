# Chrome Profiles — Alfred workflow

<img src="icon.png" width="96" alt="">

Open links, bookmarks and tabs in the Google Chrome profile you choose,
instead of whichever profile Chrome happened to use last.

## Install

Download `Chrome-Profiles.alfredworkflow` from the
[latest release](https://github.com/dtes8617/alfred-chrome-profiles/releases/latest)
and open it.

Requires [Alfred](https://www.alfredapp.com) with the Powerpack, Google Chrome,
and `/usr/bin/python3`, which macOS provides once the Xcode Command Line Tools
are installed (`xcode-select --install`).

## Usage

Search the bookmarks of all your Google Chrome profiles via the `chb` keyword.

* <kbd>↩︎</kbd> Open in the bookmark's own profile.
* <kbd>⌘</kbd><kbd>↩︎</kbd> Choose another profile.

Open a URL in a specific profile via the `cho` keyword. Type the URL, or leave
it out to use the one on your clipboard. Add part of a profile's name or email
to narrow the list.

Alternatively, open a selected URL in a specific profile via the Universal
Action.

Move the frontmost tab to another profile via the `chm` keyword. The page
reopens in the profile you pick and the original tab closes.

Open a new Google Chrome window in a specific profile via the `chp` keyword.

Configure the Hotkeys as shortcuts to move the frontmost tab and to open the
copied URL.

## Configuration

All four keywords can be changed in the workflow's configuration
(**Configure Workflow…** in Alfred Preferences).

## Good to know

- The first time you move a tab, macOS asks whether Alfred may control Google
  Chrome. Moving a tab needs that permission; the other features do not.
- Moving a tab reloads the page in the new profile, so unsaved form input in
  the original tab is lost.
- Opening a profile always opens a new window. Chrome does not tell scripts
  which profile a window belongs to, so an existing window cannot be focused.
- Everything runs on your Mac. The workflow reads Chrome's `Local State` and
  `Bookmarks` files and sends nothing anywhere.

## Development

- `chrome.py` holds all the logic: four Script Filters and the open action.
- `build.py` generates `info.plist` and packages the workflow:

  ```sh
  python3 build.py
  open Chrome-Profiles.alfredworkflow
  ```
