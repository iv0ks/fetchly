# Fetchly: Learning Guide

![CWE-22](https://img.shields.io/badge/CWE--22-Path%20Traversal-red?style=flat-square)
![Python](https://img.shields.io/badge/Python-Flask-blue?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Lab-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

**Fetchly is an intentionally vulnerable application built for security education.** It contains a deliberate [path traversal](https://owasp.org/www-community/attacks/Path_Traversal)
(CWE-22) flaw so you can practice finding and exploiting it in a safe and controlled environment.

<br>

> [!TIP]
> A guided, **non-spoiler** path to solving this lab. It teaches the *method*, not the answer — the exact winning payload and the flag stay in [SOLUTION.md](SOLUTION.md).

<br>

## 🧬 What path traversal is

Here is the whole idea in one sentence:

> **Path traversal happens when an app builds a file path out of user input and
> then trusts that path to stay where it's supposed to.**

A web app usually wants to serve files from *one* folder — here, `docs/`. The
intended deal is: "give me a filename, I'll give you that file *from this
folder*." The catch is that the folder boundary is a **convention**, not a
**rule** the code enforces. Filesystems understand `..` as "go up one level", so
a filename like `../something.txt` is a perfectly valid instruction to leave the
folder. If nobody checks for it, the app obeys.

Think of `docs/` as a room and the filename as directions. "`welcome.txt`" means
"the welcome file in this room." "`../something`" means "step out the door, then
grab a file in the hallway." The app was only ever meant to serve things *in the
room* — but it never locked the door.

That "filename → file read" shape is the **sink** you're training your eye to
spot. Once you can recognise it on sight, you can find this bug in seconds.

> Want the deeper background — history, variants, encoding tricks, and the full
> manual-testing workflow with **Burp Suite** and **OWASP ZAP**? Read the shared
> **[Path Traversal field guide](https://github.com/iv0ks/appsec-labs/blob/main/docs/path-traversal.md)**.
> This lab is a hands-on application of it.

<br>

## 🎓 What this level teaches

**Level 1 — no defence at all.** Fetchly is the baseline of the series: the
download endpoint takes a user-supplied filename and joins it onto the documents
directory with **zero validation**. There is no filter to bypass — the goal is
to *recognise* the raw shape of the vulnerability and confirm it end to end,
before the later levels start adding (broken) defences.

- **Entry point:** `GET /docs?name=<name>`
- **The broken defence:** none — the filename is trusted verbatim.
- **Served directory:** `docs/` · **target:** a file one level above it.

## 🪧 How to approach it

1. Browse the dashboard through your proxy and download a legitimate document.
   Capture the request and note the `name` parameter.
2. Send it to Repeater / Request Editor and re-send the known-good value to get
   your **baseline** response — the thing you'll compare every attempt against.
3. Since nothing is filtered, ask yourself: what is the simplest way to point
   the filename *up* and out of `docs/`? Change `name` accordingly and watch the
   response.
4. Confirm the escape by reading the challenge target outside the served
   directory. Keep the path **as-is** so `../` is not normalised away before it
   is sent (`curl --path-as-is`, or edit the raw request in your proxy).

## 🕵️‍♂️ Going further

With no filter, the endpoint will read anything the app user can — try climbing
several levels to reach files elsewhere on the container filesystem. This is why
the labs run as a non-root user inside Docker: the bug is real, but the blast
radius is contained on purpose.

## 🤔 Why it matters

A no-filter traversal is rare in mature code but extremely common in quick
internal tools, admin panels and legacy endpoints. Learning to spot the
"filename → file read" sink instantly is the foundation for every later level.

---

When you have captured the flag (or want to check the fix and the *why* behind
it), continue to **[SOLVE → SOLUTION.md](SOLUTION.md)**.
