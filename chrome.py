#!/usr/bin/python3
"""Alfred workflow backend: open URLs, bookmarks and tabs in a chosen Chrome profile.

Subcommands
  bookmarks            Script Filter: every bookmark in every profile (Alfred filters).
  open-in [query]      Script Filter: pick a profile for a URL.
                       query = "<url> [profile filter]"; with no URL the clipboard is used.
  move-tab             Script Filter: pick a profile to move the front Chrome tab to.
  profiles             Script Filter: pick a profile to open a new window in.
  open                 Action: open $url in $profile; closes tab $tab_id if set.
                       With no $url, opens a new window in $profile.
"""
import json
import os
import re
import subprocess
import sys

# Both can be overridden with environment variables, which the tests rely on.
CHROME_DIR = os.environ.get("chrome_dir") or os.path.expanduser(
    "~/Library/Application Support/Google/Chrome"
)
CHROME_APP = os.environ.get("chrome_app") or "Google Chrome"

URL_RE = re.compile(r"^[a-z][a-z0-9+.-]*://\S+$", re.I)
DOMAIN_RE = re.compile(r"^(localhost|[\w-]+(\.[\w-]+)+)(:\d+)?([/?#]\S*)?$", re.I)


def emit(items):
    # ASCII-escaped on purpose: the output is then valid whatever locale or
    # encoding the script happens to be started with.
    json.dump({"items": items}, sys.stdout)


def message(title, subtitle=""):
    return {"title": title, "subtitle": subtitle, "valid": False}


def natural_key(text):
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", text)]


def load_profiles():
    """Return [{dir, name, email, icon}] for every Chrome profile."""
    with open(os.path.join(CHROME_DIR, "Local State"), encoding="utf-8") as f:
        cache = json.load(f).get("profile", {}).get("info_cache", {})
    profiles = []
    for directory in sorted(cache, key=natural_key):
        info = cache[directory]
        picture = os.path.join(
            CHROME_DIR, directory, info.get("gaia_picture_file_name") or "-"
        )
        profiles.append(
            {
                "dir": directory,
                "name": info.get("name") or directory,
                "email": info.get("user_name") or "",
                "icon": picture if os.path.isfile(picture) else None,
            }
        )
    return profiles


def profiles_or_error():
    try:
        profiles = load_profiles()
    except OSError as err:
        emit(
            [
                message(
                    "Can't read Chrome profiles",
                    "%s — check Alfred's access in System Settings › Privacy & Security"
                    % err.strerror,
                )
            ]
        )
        sys.exit(0)
    if not profiles:
        emit([message("No Chrome profiles found", CHROME_DIR)])
        sys.exit(0)
    return profiles


def with_icon(item, profile):
    if profile["icon"]:
        item["icon"] = {"path": profile["icon"]}
    return item


def normalize_url(text):
    """Return a URL if text looks like one, else None."""
    text = (text or "").strip()
    if URL_RE.match(text):
        return text
    if DOMAIN_RE.match(text):
        return "https://" + text
    return None


def profile_items(profiles, url, title_fmt, extra_vars=None, needle=""):
    needle = needle.lower().strip()
    items = []
    for p in profiles:
        haystack = ("%s %s %s" % (p["name"], p["email"], p["dir"])).lower()
        if needle and not all(word in haystack for word in needle.split()):
            continue
        variables = {"url": url, "profile": p["dir"]}
        variables.update(extra_vars or {})
        items.append(
            with_icon(
                {
                    "title": title_fmt % p["name"],
                    "subtitle": " · ".join(
                        x for x in (p["email"], url or "New window") if x
                    ),
                    "arg": url or p["dir"],
                    "match": haystack,
                    "variables": variables,
                },
                p,
            )
        )
    return items or [message("No profile matches “%s”" % needle)]


# --- Script Filters ---------------------------------------------------------


def cmd_bookmarks():
    items = []

    def walk(node, path, profile):
        if node.get("type") == "url":
            url = node.get("url", "")
            if url.startswith("javascript:"):
                return
            name = node.get("name") or url
            items.append(
                with_icon(
                    {
                        "title": name,
                        "subtitle": " · ".join(
                            x for x in (profile["name"], "/".join(path), url) if x
                        ),
                        "arg": url,
                        "match": " ".join(
                            [name, re.sub(r"[^\w]+", " ", url), profile["name"]]
                            + path
                        ),
                        "variables": {"url": url, "profile": profile["dir"]},
                        "mods": {
                            "cmd": {
                                "subtitle": "Choose a different profile for this bookmark…",
                                "arg": url,
                            }
                        },
                        "text": {"copy": url, "largetype": url},
                    },
                    profile,
                )
            )
        for child in node.get("children", []):
            walk(child, path + [node["name"]] if node.get("name") else path, profile)

    for profile in profiles_or_error():
        try:
            with open(
                os.path.join(CHROME_DIR, profile["dir"], "Bookmarks"), encoding="utf-8"
            ) as f:
                roots = json.load(f).get("roots", {})
        except (OSError, ValueError):
            continue
        for root in roots.values():
            if isinstance(root, dict):
                walk(root, [], profile)
    emit(items or [message("No bookmarks found in any Chrome profile")])


def cmd_open_in(query):
    profiles = profiles_or_error()
    first, _, rest = query.strip().partition(" ")
    url = normalize_url(first)
    needle = rest
    if not url:
        # No URL typed: fall back to the clipboard and treat the query as a filter.
        needle = query
        try:
            # Ask for UTF-8 explicitly: without a locale, pbpaste turns
            # non-ASCII characters into "?".
            clip = subprocess.run(
                ["pbpaste"],
                capture_output=True,
                timeout=2,
                env=dict(os.environ, LC_ALL="en_US.UTF-8"),
            ).stdout.decode("utf-8", "replace")
        except (OSError, subprocess.SubprocessError):
            clip = ""
        url = normalize_url(clip)
    if not url:
        emit([message("No URL to open", "Type a URL after the keyword, or copy one first")])
        return
    emit(profile_items(profiles, url, "Open in %s", needle=needle))


def cmd_profiles():
    emit(profile_items(profiles_or_error(), "", "Open Chrome as %s"))


FRONT_TAB_SCRIPT = """
tell application "%s"
    if not running then return ""
    if (count of windows) is 0 then return ""
    set t to active tab of front window
    return (id of t as text) & linefeed & (URL of t) & linefeed & (title of t)
end tell
"""

CLOSE_TAB_SCRIPT = """
tell application "%s"
    repeat with w in windows
        repeat with t in tabs of w
            if (id of t as text) is "%s" then
                close t
                return
            end if
        end repeat
    end repeat
end tell
"""


def osascript(source):
    # osascript always writes UTF-8, so decode it as such regardless of locale.
    return subprocess.run(
        ["osascript", "-e", source],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


def cmd_move_tab():
    profiles = profiles_or_error()
    try:
        result = osascript(FRONT_TAB_SCRIPT % CHROME_APP)
    except subprocess.TimeoutExpired:
        # Usually the macOS prompt asking to let Alfred control the browser.
        emit([message("%s did not answer" % CHROME_APP, "Allow the permission prompt if one is showing, then try again")])
        return
    parts = result.stdout.rstrip("\n").split("\n", 2)
    if result.returncode != 0:
        if "-1743" in result.stderr:
            emit(
                [
                    message(
                        "Alfred is not allowed to control %s" % CHROME_APP,
                        "Turn it on in System Settings › Privacy & Security › Automation",
                    )
                ]
            )
        else:
            emit([message("Can't talk to %s" % CHROME_APP, result.stderr.strip())])
        return
    if len(parts) < 2 or not parts[1]:
        emit([message("No Chrome tab to move", "Chrome has no open window")])
        return
    tab_id, url = parts[0], parts[1]
    title = parts[2] if len(parts) > 2 and parts[2] else url
    items = profile_items(profiles, url, "Move tab to %s", {"tab_id": tab_id})
    for item in items:
        item["subtitle"] = "%s · %s" % (title, url)
    emit(items)


# --- Action -----------------------------------------------------------------


def cmd_open():
    url = os.environ.get("url", "")
    profile = os.environ.get("profile", "")
    tab_id = os.environ.get("tab_id", "")
    if not profile:
        sys.exit("missing profile")
    command = ["open", "-na", CHROME_APP, "--args", "--profile-directory=" + profile]
    if url:
        command.append(url)
    subprocess.run(command, check=True)
    if url and tab_id.isdigit():
        try:
            osascript(CLOSE_TAB_SCRIPT % (CHROME_APP, tab_id))
        except subprocess.TimeoutExpired:
            pass  # The page is already open in the new profile; leave the old tab.


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    query = sys.argv[2] if len(sys.argv) > 2 else ""
    if command == "bookmarks":
        cmd_bookmarks()
    elif command == "open-in":
        cmd_open_in(query)
    elif command == "move-tab":
        cmd_move_tab()
    elif command == "profiles":
        cmd_profiles()
    elif command == "open":
        cmd_open()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
