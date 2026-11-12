# Fetchly: Solution / Walkthrough

![CWE-22](https://img.shields.io/badge/CWE--22-Path%20Traversal-red?style=flat-square)
![Python](https://img.shields.io/badge/Python-Flask-blue?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Lab-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

**Fetchly is an intentionally vulnerable application built for security education.** It contains a deliberate [path traversal](https://owasp.org/www-community/attacks/Path_Traversal)
(CWE-22) flaw so you can practice finding and exploiting it in a safe and controlled environment.

<br>

> [!WARNING]
> This page gives away the payload and the flag. If you want to solve it yourself, start with the non-spoiler **[Learning Guide](GUIDE.md)** and come back here to check your work.

<br>

## 📚 What you'll get from this page

The [Learning Guide](GUIDE.md) covers *what* path traversal is and *how* to
approach the lab. This page is the spoiler half: the confirmed exploit, the
flag, and — most importantly — the **why** behind the bug and its fix. By the
end you should be able to:

- Read a snippet of file-serving code and point to the exact vulnerable line.
- Craft and send the exploit by hand, understanding every character of it.
- Explain **why** each fix works — and why some "obvious" fixes don't.

> **One-line recap** (full version in the [GUIDE](GUIDE.md)): path traversal
> happens when an app builds a file path from user input and trusts it to stay
> inside the intended folder. `../` walks out; nothing here stops it.

If you only want the payload, jump to [Exploitation](#-exploitation) — but the
real value is in the *why*.

<br>

## 🐛 The vulnerability

The `app/routes.py` builds the file path like this:

```python
name = request.args.get("name", "")           # attacker controls this
documents_dir = current_app.config["DOCUMENTS_DIR"]

target_path = os.path.join(documents_dir, name)   # the vulnerable line

if not os.path.isfile(target_path):
    return render_error(404, f"Document not found: {name}")

return send_file(target_path, as_attachment=False)
```

Walk through it the way the computer does:

1. `name` comes **straight from the query string** — fully attacker-controlled.
2. `os.path.join(documents_dir, name)` glues them together. Crucially,
   `os.path.join` does **not** sanitise anything: it keeps `..` segments intact
   (and if `name` were an absolute path, it would even discard `documents_dir`
   entirely).
3. The code checks that the file *exists* (`isfile`) — but never that it lives
   **inside** `documents_dir`.
4. `send_file` opens whatever path it was handed and streams it back.

The missing step is the other half of #3: a **boundary check**. That single
absent check is the entire vulnerability — the "filename → file read" sink the
[GUIDE](GUIDE.md) trains you to recognise.

> **Why `os.path.join` and not something safer?** Because `join` is the obvious,
> natural way to combine a folder and a filename, and it *looks* harmless. That
> is exactly why this bug is so common: the dangerous code looks like ordinary,
> reasonable code.

<br>

## 💥 Exploitation

**The intended request** — what the app expects:

```
GET /docs?name=welcome.txt
```

Resolves to `docs/welcome.txt`. Boring. Working as designed.

**The exploit** — escape `docs/` to read the flag sitting one level up:

```
GET /docs?name=../flag.txt
```

Here `os.path.join("docs", "../flag.txt")` resolves to `flag.txt` at the parent
level — outside the vault. Let's send it.

With `curl`:

```bash
curl --path-as-is "http://localhost:5000/docs?name=../flag.txt"
```

> **Why `--path-as-is`?** By default curl is "helpful" and normalises `../` away
> *before* the request leaves your machine, so the server would never see the
> traversal. `--path-as-is` tells curl to send your path byte-for-byte. Browsers
> and some proxies do the same normalisation — this is a common reason a payload
> "works in Repeater but not in the browser."

Expected output:

```
FLAG{FETCHLY_UNLOCKED_THE_VAULT}
```

> **Where does the flag come from?** It is **not** in the repo on purpose — it is
> baked into the Docker image at build time at `/app/flag.txt`, one level above
> `docs/` (see the `Dockerfile`). You have to actually exploit the traversal
> against the running container to read it; you can't just grep the source.

<br>

## 🚀 Going further

Because there is **no filtering at all**, the escape doesn't stop at the flag.
You can keep climbing to read files anywhere the app's user can reach:

```
GET /docs?name=../../../../etc/passwd
```

The extra `../` segments are harmless once you're already at the filesystem
root (`/`) — `..` from `/` is still `/` — so "too many" is a safe way to be sure
you reached the top. This is the classic quick confirmation that a traversal is
real.

> Inside the hardened container this reads the *container's* `/etc/passwd`, not
> your host's, and the app runs as a non-root user — so the blast radius is
> deliberately small. That containment is exactly why we run labs in Docker:
> you get to practise a real exploit without putting your own machine at risk.

<br>

## 🛠️ Doing it in Burp Suite

Prefer a proxy-driven workflow? This mirrors how you'd find and confirm the bug
in a real engagement:

1. Proxy your browser through Burp and load <http://localhost:5000>.
2. Click **Download** on any document — capture the request in
   **Proxy > HTTP history**. Notice the filename lands in `?name=`.
3. Send it to **Repeater** and re-send the original value to get a **baseline**
   response you can compare against.
4. Change `name` to `../flag.txt` and send. Compare against the baseline — a
   different body with the flag confirms the escape.
5. (Optional) Fuzz the parameter with **Intruder** using a path-traversal
   wordlist (e.g. from [SecLists](https://github.com/danielmiessler/SecLists))
   to see how an automated scanner would discover this.

> Keep an eye on whether Burp re-encodes or normalises the path. If a payload
> that works in `curl --path-as-is` fails in Repeater, encoding/normalisation is
> usually the culprit — toggle Repeater's URL-encoding and inspect the raw
> request.

<br>

## 🛡️ The fix

The correct implementation **resolves** the path to its real, canonical form and
then **verifies** it still lives inside the allowed base directory before
serving anything:

```python
import os
from flask import abort, send_file

def safe_path(base_dir: str, user_supplied: str) -> str:
    # realpath() collapses '..' and resolves symlinks, giving the true
    # destination the OS would actually open.
    full = os.path.realpath(os.path.join(base_dir, user_supplied))
    base = os.path.realpath(base_dir)

    # The boundary check: the resolved path must sit inside base_dir.
    # commonpath([full, base]) == base means "full starts at base".
    if os.path.commonpath([full, base]) != base:
        abort(403)
    return full
```

Why this works, step by step:

- **Resolve before you trust.** `os.path.realpath` collapses every `..` *and*
  follows symlinks, so you check the path the OS will *actually* open — not the
  string the user typed.
- **Compare canonical paths.** Both sides go through `realpath`, so you're
  comparing apples to apples.
- **Fail closed.** If the resolved path isn't under `base`, return `403` and
  serve nothing. Deny by default.

### ⚠️ Tempting fixes that *don't* work

Part of learning is knowing which "fixes" are traps:

- **Blocking the literal string `..`** (e.g. `if ".." in name: reject`).
  Attackers bypass this with URL-encoding (`%2e%2e`), double-encoding
  (`%252e`), or OS-specific separators. Blacklisting strings is a losing game.
- **A single `name.replace("..", "")`.** Overlapping sequences defeat it:
  `....//` becomes `../` *after* the replace runs. One-pass filtering is almost
  always bypassable.
- **Checking the string before resolving it.** Symlinks and odd encodings mean
  the string you inspected isn't the file you open. Always resolve *first*, then
  check.

### ✅ Even better: don't build paths from user input at all

The most robust designs sidestep the whole problem:

- **Opaque IDs.** Serve files by a server-side ID (`/docs?id=42`) mapped to a
  real path in a lookup table. The user never names a file, so there's nothing
  to traverse.
- **Allow-list.** Accept only filenames you explicitly know
  (`if name not in LISTED_DOCUMENTS: abort(404)`).
- **Use a vetted helper.** Flask's
  [`send_from_directory`](https://flask.palletsprojects.com/en/latest/api/#flask.send_from_directory)
  performs the safe-join boundary check for you. Reaching for a battle-tested
  helper beats hand-rolling path logic every time.

<br>

## 🎓 Key takeaways

If you remember five things from this lab, make it these:

1. **The sink is "user input → file path → file read."** Train your eye to spot
   it anywhere.
2. **`os.path.join` doesn't protect you.** It's string glue, not a security
   boundary.
3. **Resolve, then check.** Canonicalise the path (`realpath`) *before* you
   validate it, and fail closed if it escapes the base directory.
4. **Blacklists lose.** Don't filter bad strings; constrain to known-good inputs
   (allow-list / opaque IDs) or lean on a vetted helper.
5. **Defence in depth matters.** Running as a non-root user in a container
   didn't *fix* the bug, but it dramatically limited what the exploit could
   reach.


That's Level 1 — the baseline, no defences. Later levels in the series layer on
(broken) defences for you to bypass. Head back to the **[Learning Guide](GUIDE.md)**
for the method, or the **[README](README.md)** for the lab setup.
