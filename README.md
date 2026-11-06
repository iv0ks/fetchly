# 📁 Fetchly

[![CI](https://github.com/iv0ks/fetchly/actions/workflows/ci.yml/badge.svg)](https://github.com/iv0ks/fetchly/actions/workflows/ci.yml)
[![Trivy](https://github.com/iv0ks/fetchly/actions/workflows/trivy.yml/badge.svg)](https://github.com/iv0ks/fetchly/actions/workflows/trivy.yml)
[![Release](https://github.com/iv0ks/fetchly/actions/workflows/release-please.yml/badge.svg)](https://github.com/iv0ks/fetchly/actions/workflows/release-please.yml)
[![GHCR](https://img.shields.io/badge/ghcr.io-iv0ks%2Ffetchly-blue?logo=docker)](https://github.com/iv0ks/fetchly/pkgs/container/fetchly)

> **Fetchly** is a tiny "personal document vault" — sign in, keep your files,
> download them whenever you need. At least, that's the pitch.

---

## ⚠️ Disclaimer — read this first

**Fetchly is an intentionally vulnerable application built for security
education.** It contains a deliberate [path traversal](https://owasp.org/www-community/attacks/Path_Traversal)
(CWE-22) flaw so you can practice finding and exploiting it in a safe,
controlled, local environment (for example with [Burp Suite](https://portswigger.net/burp)).

- ✅ Run it **locally**, against `localhost`, on infrastructure you own.
- ❌ Do **not** deploy it on a public/shared server.
- ❌ Do **not** reuse this code in real software.
- ❌ Do **not** use these techniques against systems you don't have explicit
  permission to test. Unauthorized testing is illegal.

This repository is part of a series of educational AppSec labs
(topic: [`appsec-lab`](https://github.com/topics/appsec-lab)).

---

## 🎯 The challenge

Fetchly serves your documents from a private vault directory. Your goal:

> **Read a file that lives _outside_ the vault — specifically, capture the
> flag stored in `lab/flag.txt`, one level above the served `storage/` dir.**

The flag has the format `FLAG{...}`.

| | |
|---|---|
| **Vulnerability** | Path Traversal (CWE-22) |
| **Difficulty** | ⭐ Level 1 — basic, no filtering |
| **Stack** | Python · Flask · gunicorn |
| **Entry point** | `GET /documents/download?doc=<filename>` |

### Hints

<details>
<summary>Hint 1</summary>
The dashboard downloads files by name. What is that name used for on the
server side? Watch the request in Burp.
</details>

<details>
<summary>Hint 2</summary>
The app serves files from a <code>storage/</code> directory. Directories have
parents. Classic traversal uses <code>../</code> sequences.
</details>

<details>
<summary>Hint 3</summary>
There is no input validation at all on this level. The flag is one directory
<em>above</em> <code>storage/</code>.
</details>

A full walkthrough lives in [docs/SOLUTION.md](docs/SOLUTION.md) (spoilers!).

---

## 🗂️ Project layout

```
fetchly/
├── app/                    # the application package (the bug lives here)
│   ├── main.py             # Flask app — vulnerable download endpoint
│   └── templates/
│       └── dashboard.html  # UI (kept out of the Python code)
├── lab/                    # everything specific to the challenge
│   ├── storage/            # decoy documents (the "allowed" directory)
│   └── flag.txt            # the target — lives OUTSIDE storage/ on purpose
├── docs/SOLUTION.md        # exploit writeup + the fix (spoilers)
├── .github/workflows/      # ci · trivy · release-please · publish (GHCR)
├── Dockerfile              # hardened multi-stage image
├── docker-compose.yml
├── pyproject.toml          # ruff + black config, packaging
└── requirements.txt
```

The clean split between `app/` (code) and `lab/` (challenge scenario) is
deliberate: it makes the vulnerable code easy to read and keeps the flag
physically outside the served directory, which is what makes traversal work.

---

## 🚀 Running the lab

### Option A — Docker Compose (recommended)

```bash
docker compose up --build
```

Then open <http://localhost:5000>.

### Option B — Pull the published image from GHCR

```bash
docker run --rm -p 5000:5000 ghcr.io/iv0ks/fetchly:latest
```

### Option C — Run directly with Python

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the app (the `app` package lives at the repo root). Either works:
flask --app app.main run --port 5000
# ...or with auto-reload while developing:
flask --app app.main run --port 5000 --debug
```

Then open <http://localhost:5000>.

> The app finds its lab data via the `LAB_DIR` env var, defaulting to the
> repo's `./lab` directory. Override it with `LAB_DIR=/path/to/lab` if needed.

---

## 🧰 About this repo (DevSecOps showcase)

Beyond the vulnerability, this repo is also a template for shipping a small
service with sane engineering practices:

- **Conventional Commits** enforced via **commitlint** (pre-commit hook).
- **pre-commit** suite: `ruff`, `black`, `gitleaks` (secret scanning),
  `hadolint` (Dockerfile lint), whitespace/EOF fixers.
- **CI** (`ci.yml`): lint + Docker build on every PR.
- **Trivy** (`trivy.yml`): filesystem + image CVE scanning, results uploaded
  to the GitHub **Security** tab as SARIF, plus a weekly scheduled scan.
- **release-please**: automated SemVer releases and changelog from commits.
- **GHCR publishing** (`publish.yml`): multi-tag image push with provenance
  and SBOM attestations, triggered on release.
- **Hardened container**: multi-stage build, non-root user, read-only root
  filesystem, dropped capabilities.

> 💡 **Teaching note:** Trivy scans for *known CVEs in dependencies and the
> base image*. It will **not** flag Fetchly's path traversal, because that is
> a **business-logic** flaw in our own code, not a vulnerable dependency.
> Catching that class of bug needs SAST / manual review / DAST — which is
> exactly what you're practicing here. Different tools, different coverage.

Set up the hooks locally with:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type commit-msg
pre-commit run --all-files
```

---

## 📄 License

[MIT](LICENSE) — see also [SECURITY.md](SECURITY.md).
