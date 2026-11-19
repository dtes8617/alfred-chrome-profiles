#!/usr/bin/python3
"""Generate info.plist and package Chrome-Profiles.alfredworkflow."""
import os
import plistlib
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = "1.2.0"
PACKAGED_FILES = ("info.plist", "chrome.py", "icon.png")
CMD = 1048576  # connection modifier bit for ⌘

BOOKMARKS, OPEN_IN, MOVE_TAB, PROFILES = (
    "SF-BOOKMARKS", "SF-OPEN-IN", "SF-MOVE-TAB", "SF-PROFILES",
)
OPEN = "ACT-OPEN"
UA, HOTKEY_MOVE, HOTKEY_OPEN_IN = "UA-OPEN-IN", "HK-MOVE-TAB", "HK-OPEN-IN"

# Keywords are Workflow Configuration fields, so users change them in
# "Configure Workflow…" instead of editing the objects.
# (variable, default, label, description)
KEYWORDS = [
    ("keyword_bookmarks", "chb", "Bookmarks Keyword",
     "Search the bookmarks of every profile."),
    ("keyword_open_in", "cho", "Open URL Keyword",
     "Open a typed or copied URL in the profile you pick."),
    ("keyword_move_tab", "chm", "Move Tab Keyword",
     "Move the frontmost tab to another profile."),
    ("keyword_profiles", "chp", "Open Profile Keyword",
     "Open a new window in a profile."),
]


def script_filter(uid, keyword_variable, title, subtext, command, alfred_filters):
    return {
        "uid": uid,
        "type": "alfred.workflow.input.scriptfilter",
        "version": 3,
        "config": {
            "alfredfiltersresults": alfred_filters,
            "alfredfiltersresultsmatchmode": 2,  # Word matching - Any order
            "argumenttreatemptyqueryasnil": False,
            "argumenttrimmode": 0,
            "argumenttype": 1,  # argument optional
            "escaping": 0,
            "keyword": "{var:%s}" % keyword_variable,
            "queuedelaycustom": 3,
            "queuedelayimmediatelyinitially": True,
            "queuedelaymode": 0,
            "queuemode": 2,
            "runningsubtext": "Loading…",
            "script": '/usr/bin/python3 chrome.py %s "$1"' % command,
            "scriptargtype": 1,
            "scriptfile": "",
            "subtext": subtext,
            "title": title,
            "type": 0,
            "withspace": True,
        },
    }


def hotkey(uid):
    return {
        "uid": uid,
        "type": "alfred.workflow.trigger.hotkey",
        "version": 2,
        "config": {
            "action": 0,
            "argument": 0,
            "focusedappvariable": False,
            "focusedappvariablename": "",
            "hotkey": 0,
            "hotmod": 0,
            "hotstring": "",
            "leftcursor": False,
            "modsmode": 0,
            "relatedAppsMode": 0,
        },
    }


def conn(dest, modifiers=0, subtext=""):
    return {
        "destinationuid": dest,
        "modifiers": modifiers,
        "modifiersubtext": subtext,
        "vitoclose": False,
    }


objects = [
    script_filter(
        BOOKMARKS, "keyword_bookmarks", "Search Chrome bookmarks",
        "Bookmarks from every profile",
        "bookmarks", True,
    ),
    script_filter(
        OPEN_IN, "keyword_open_in", "Open URL in a Chrome profile",
        "Type a URL, or leave it out to use the one on your clipboard",
        "open-in", False,
    ),
    script_filter(
        MOVE_TAB, "keyword_move_tab", "Move the frontmost Chrome tab to a profile",
        "Reopens the page in the profile you pick and closes the original tab",
        "move-tab", True,
    ),
    script_filter(
        PROFILES, "keyword_profiles", "Open a Chrome profile",
        "Opens a new window in the profile you pick",
        "profiles", True,
    ),
    {
        "uid": UA,
        "type": "alfred.workflow.trigger.universalaction",
        "version": 1,
        "config": {
            "acceptsfiles": False,
            "acceptsmulti": 0,
            "acceptstext": True,
            "acceptsurls": True,
            "name": "Open in Chrome Profile…",
        },
    },
    hotkey(HOTKEY_MOVE),
    hotkey(HOTKEY_OPEN_IN),
    {
        "uid": OPEN,
        "type": "alfred.workflow.action.script",
        "version": 2,
        "config": {
            "concurrently": False,
            "escaping": 0,
            "script": "/usr/bin/python3 chrome.py open",
            "scriptargtype": 1,
            "scriptfile": "",
            "type": 0,
        },
    },
]

connections = {
    BOOKMARKS: [conn(OPEN), conn(OPEN_IN, CMD, "Choose another profile…")],
    OPEN_IN: [conn(OPEN)],
    MOVE_TAB: [conn(OPEN)],
    PROFILES: [conn(OPEN)],
    UA: [conn(OPEN_IN)],
    HOTKEY_MOVE: [conn(MOVE_TAB)],
    HOTKEY_OPEN_IN: [conn(OPEN_IN)],
}

uidata = {
    HOTKEY_MOVE: {"xpos": 40, "ypos": 40, "note": "Move the frontmost tab"},
    MOVE_TAB: {"xpos": 260, "ypos": 40},
    BOOKMARKS: {"xpos": 260, "ypos": 190},
    HOTKEY_OPEN_IN: {"xpos": 40, "ypos": 340, "note": "Open the copied URL"},
    UA: {"xpos": 40, "ypos": 480},
    OPEN_IN: {"xpos": 260, "ypos": 400},
    PROFILES: {"xpos": 260, "ypos": 560},
    OPEN: {"xpos": 520, "ypos": 190},
}

user_configuration = [
    {
        "type": "textfield",
        "variable": variable,
        "label": label,
        "description": description,
        "config": {
            "default": default,
            "placeholder": default,
            "required": True,
            "trim": True,
        },
    }
    for variable, default, label, description in KEYWORDS
]

# Shown in Alfred as "About this Workflow"; follows the Alfred Gallery style guide.
README = """## Usage

Search the bookmarks of all your Google Chrome profiles via the `chb` keyword.

* <kbd>↩︎</kbd> Open in the bookmark's own profile.
* <kbd>⌘</kbd><kbd>↩︎</kbd> Choose another profile.

Open a URL in a specific profile via the `cho` keyword. Type the URL, or leave it out to use the one on your clipboard. Add part of a profile's name or email to narrow the list.

Alternatively, open a selected URL in a specific profile via the Universal Action.

Move the frontmost tab to another profile via the `chm` keyword. The page reopens in the profile you pick and the original tab closes.

Open a new Google Chrome window in a specific profile via the `chp` keyword.

Configure the Hotkeys as shortcuts to move the frontmost tab and to open the copied URL."""

info = {
    "bundleid": "com.dtes8617.chrome-profiles",
    "category": "Internet",
    "connections": connections,
    "createdby": "dtes8617",
    "description": "Open links, bookmarks and tabs in the Chrome profile you choose",
    "disabled": False,
    "name": "Chrome Profiles",
    "objects": objects,
    "readme": README,
    "uidata": uidata,
    "userconfigurationconfig": user_configuration,
    "version": VERSION,
    "webaddress": "https://github.com/dtes8617/alfred-chrome-profiles",
}


def main():
    with open(os.path.join(HERE, "info.plist"), "wb") as f:
        plistlib.dump(info, f)

    out = os.path.join(HERE, "Chrome-Profiles.alfredworkflow")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in PACKAGED_FILES:
            z.write(os.path.join(HERE, name), name)
    print(out)


if __name__ == "__main__":
    main()
