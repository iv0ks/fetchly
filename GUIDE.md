# Fetchly — Learning Guide

> A guided, **non-spoiler** path to solving this lab. It teaches the *method*,
> not the answer — the exact winning payload and the flag stay in
> [SOLUTION.md](SOLUTION.md).

## Before you start

Read the shared **[Path Traversal field guide](https://github.com/iv0ks/appsec-labs/blob/main/docs/path-traversal.md)**
first. It covers what path traversal (CWE-22) is, why it appears, and the manual
testing workflow with **Burp Suite** and **OWASP ZAP**. This guide assumes it.

## What this level teaches

**Level 1 — no defence at all.** Fetchly is the baseline: the download endpoint
takes a user-supplied filename and joins it onto the documents directory with
**zero validation**. There is no filter to bypass — the goal is to *recognise*
the raw shape of the vulnerability and confirm it end to end before the later
levels start adding (broken) defences.

- **Entry point:** `GET /docs?name=<name>`
- **The broken defence:** none — the filename is trusted verbatim.
- **Served directory:** `docs/` · **target:** a file one level above it.

## How to approach it

1. Browse the dashboard through your proxy and download a legitimate document.
   Capture the request and note the `name` parameter.
2. Send it to Repeater / Request Editor and re-send the known-good value to get
   your baseline response.
3. Since nothing is filtered, ask yourself: what is the simplest way to point
   the filename *up* and out of `docs/`? Change `name` accordingly and watch the
   response.
4. Confirm the escape by reading the challenge target outside the served
   directory. Keep the path **as-is** so `../` is not normalised away before it
   is sent (`curl --path-as-is`, or edit the raw request in your proxy).

## Going further

With no filter, the endpoint will read anything the app user can — try climbing
several levels to reach files elsewhere on the container filesystem. This is why
the labs run as a non-root user inside Docker.

## Why it matters

A no-filter traversal is rare in mature code but extremely common in quick
internal tools, admin panels and legacy endpoints. Learning to spot the
"filename → file read" sink instantly is the foundation for every later level.

When you have captured the flag (or want to check the fix), read
[SOLUTION.md](SOLUTION.md).
