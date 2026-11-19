#!/usr/bin/python3
"""Generate info.plist and package Chrome-Profiles.alfredworkflow."""
import os
import plistlib
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
CMD, ALT = 1048576, 524288

BOOKMARKS, OPEN_IN, MOVE_TAB, OPEN = "SF-BOOKMARKS", "SF-OPEN-IN", "SF-MOVE-TAB", "ACT-OPEN"
PROFILES = "SF-PROFILES"
UA, HOTKEY_MOVE, HOTKEY_OPEN_IN = "UA-OPEN-IN", "HK-MOVE-TAB", "HK-OPEN-IN"


def script_filter(uid, keyword, title, subtext, command, alfred_filters, argtype):
    return {
        "uid": uid,
        "type": "alfred.workflow.input.scriptfilter",
        "version": 3,
        "config": {
            "alfredfiltersresults": alfred_filters,
            "alfredfiltersresultsmatchmode": 2,  # word-based, any order
            "argumenttreatemptyqueryasnil": False,
            "argumenttrimmode": 0,
            "argumenttype": argtype,  # 0 required, 1 optional
            "escaping": 0,
            "keyword": keyword,
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
        BOOKMARKS, "cb", "Chrome bookmarks",
        "Search bookmarks across all profiles (⌘↩ to pick another profile)",
        "bookmarks", True, 1,
    ),
    script_filter(
        OPEN_IN, "co", "Open URL in Chrome profile…",
        "co [url] [profile] — uses the clipboard when no URL is typed",
        "open-in", False, 1,
    ),
    script_filter(
        MOVE_TAB, "cm", "Move current Chrome tab to profile…",
        "Reopen the front tab in another profile and close it here",
        "move-tab", True, 1,
    ),
    script_filter(
        PROFILES, "cp", "Open Chrome profile…",
        "Open a new Chrome window in the profile you pick",
        "profiles", True, 1,
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
    BOOKMARKS: [conn(OPEN), conn(OPEN_IN, CMD, "Choose a different profile…")],
    OPEN_IN: [conn(OPEN)],
    MOVE_TAB: [conn(OPEN)],
    PROFILES: [conn(OPEN)],
    UA: [conn(OPEN_IN)],
    HOTKEY_MOVE: [conn(MOVE_TAB)],
    HOTKEY_OPEN_IN: [conn(OPEN_IN)],
}

uidata = {
    HOTKEY_MOVE: {"xpos": 40, "ypos": 40, "note": "Set a hotkey: move front tab"},
    MOVE_TAB: {"xpos": 260, "ypos": 40},
    BOOKMARKS: {"xpos": 260, "ypos": 190},
    HOTKEY_OPEN_IN: {"xpos": 40, "ypos": 340, "note": "Set a hotkey: open clipboard URL"},
    UA: {"xpos": 40, "ypos": 480},
    OPEN_IN: {"xpos": 260, "ypos": 400},
    PROFILES: {"xpos": 260, "ypos": 560},
    OPEN: {"xpos": 520, "ypos": 190},
}

README = """Open links, bookmarks and tabs in the Chrome profile you choose.

• cb <query> — search bookmarks from every profile. ↩ opens in the bookmark's own profile, ⌘↩ lets you pick another.
• co [url] [profile] — pick a profile for a URL. With no URL, the clipboard is used.
• cm [profile] — move the front Chrome tab to another profile (reopens it there, closes it here).
• cp [profile] — open a new Chrome window in the profile you pick.
• Universal Action “Open in Chrome Profile…” — works on any selected URL/text or clipboard-history entry.
• Two empty Hotkey triggers are included for cm and co — double-click them to assign keys.

The first cm run asks for permission for Alfred to control Google Chrome."""

info = {
    "bundleid": "com.dtes8617.chrome-profiles",
    "category": "Internet",
    "connections": connections,
    "createdby": "",
    "description": "Open links, bookmarks and tabs in the right Chrome profile",
    "disabled": False,
    "name": "Chrome Profiles",
    "objects": objects,
    "readme": README,
    "uidata": uidata,
    "userconfigurationconfig": [],
    "version": "1.1.0",
    "webaddress": "",
}

with open(os.path.join(HERE, "info.plist"), "wb") as f:
    plistlib.dump(info, f)

out = os.path.join(HERE, "Chrome-Profiles.alfredworkflow")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name in ("info.plist", "chrome.py"):
        z.write(os.path.join(HERE, name), name)
print(out)
