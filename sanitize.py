"""Make third-party content inert before this pipeline publishes it.

Every feed item carries text, markup and URLs taken from someone else's RSS
feed, search result or web page. Feed readers, review.html, index.html and the
podcast all consume them, and not every consumer escapes what it reads. So the
writer guarantees it once, at the exit (see ``write_feed`` in
super_rss_curator_json.py):

* URLs are http(s) with a real host and no embedded credentials. A link may
  also be ``mailto:``. Anything else (``javascript:``, ``data:``, a relative
  path) is removed; an item whose own link is unsafe is dropped.
* Plain-text fields (title, summary, excerpt, author name, tags) carry no
  markup. They are stripped, not entity-escaped, because JSON Feed text is
  rendered as text and escaping would show ``&amp;`` in every reader.
* ``content_html`` keeps an allowlist of tags and attributes. Script-capable
  elements go with their contents, unknown tags are unwrapped to their text,
  and inline styles keep only layout and typography declarations.

``is_public_http_url`` is the separate guard for the pipeline's own outbound
fetches of article pages, whose bodies are republished as excerpts and images.
"""
import ipaddress
import re
import socket
from typing import Any, Dict, Iterable, Optional, Union
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from bs4.element import PreformattedString

WEB_SCHEMES = frozenset({'http', 'https'})
LINK_SCHEMES = WEB_SCHEMES | {'mailto'}

# C0 controls and DEL. Browsers delete tab and newline from inside a URL, so
# "java\tscript:" runs as javascript:; reject rather than normalize.
_URL_CONTROL = re.compile(r'[\x00-\x1f\x7f]')
_BAD_HOST_CHARS = re.compile(r'[\s<>"\'`\\{}|^%]')

# Hostnames that only resolve inside a private network.
_PRIVATE_HOSTS = ('localhost', '.localhost', '.local', '.internal', '.lan',
                  '.home.arpa', '.intranet')

# Text controls other than tab, newline and carriage return.
_TEXT_CONTROL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
_TAG_LIKE = re.compile(r'<[A-Za-z/!?]')

# Removed together with everything inside them.
_DROP_WITH_CONTENT = frozenset({
    'script', 'style', 'iframe', 'frame', 'frameset', 'object', 'embed', 'applet',
    'form', 'input', 'button', 'select', 'option', 'textarea', 'link', 'meta',
    'base', 'svg', 'math', 'template', 'noscript', 'audio', 'video', 'source',
    'track', 'canvas', 'portal', 'title', 'head', 'xml',
})

_ALLOWED_TAGS = frozenset({
    'a', 'abbr', 'article', 'b', 'blockquote', 'br', 'caption', 'cite', 'code',
    'dd', 'del', 'div', 'dl', 'dt', 'em', 'figcaption', 'figure', 'font',
    'footer', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'i', 'img',
    'ins', 'kbd', 'li', 'mark', 'ol', 'p', 'pre', 'q', 's', 'section', 'small',
    'span', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
    'thead', 'time', 'tr', 'u', 'ul',
})

# No id or name: they clobber DOM globals in a page that renders the content.
_GLOBAL_ATTRS = frozenset({'class', 'dir', 'lang', 'style', 'title'})
_TAG_ATTRS = {
    'a': frozenset({'href', 'hreflang', 'rel', 'target'}),
    'img': frozenset({'alt', 'height', 'src', 'width'}),
    'font': frozenset({'color', 'face', 'size'}),
    'td': frozenset({'align', 'colspan', 'rowspan', 'valign'}),
    'th': frozenset({'align', 'colspan', 'rowspan', 'scope', 'valign'}),
    'ol': frozenset({'start', 'type'}),
    'time': frozenset({'datetime'}),
    'blockquote': frozenset({'cite'}),
    'q': frozenset({'cite'}),
}
_URL_ATTRS = {'href': LINK_SCHEMES, 'src': WEB_SCHEMES, 'cite': WEB_SCHEMES}

# Layout and typography only: nothing that positions over the reader's own UI
# (position, z-index, transform) or loads anything (url(), image-set()).
_CSS_PROPERTIES = frozenset({
    'background', 'background-color', 'border', 'border-bottom', 'border-collapse',
    'border-color', 'border-left', 'border-radius', 'border-right', 'border-spacing',
    'border-style', 'border-top', 'border-width', 'clear', 'color', 'display',
    'float', 'font', 'font-family', 'font-size', 'font-style', 'font-weight',
    'height', 'letter-spacing', 'line-height', 'list-style', 'list-style-type',
    'margin', 'margin-bottom', 'margin-left', 'margin-right', 'margin-top',
    'max-height', 'max-width', 'min-height', 'min-width', 'object-fit', 'padding',
    'padding-bottom', 'padding-left', 'padding-right', 'padding-top', 'text-align',
    'text-decoration', 'text-indent', 'text-transform', 'vertical-align',
    'white-space', 'width',
})
_CSS_UNSAFE = re.compile(
    r'[\\<>@]|/\*|url\s*\(|src\s*\(|image-set|expression|script|behavior|binding',
    re.IGNORECASE,
)

# Text fields of a JSON Feed item, plus the podcast contract's excerpt.
_ITEM_TEXT_FIELDS = ('title', 'summary', 'content_text', '_excerpt')
# Optional URL fields: removed when unsafe.
_ITEM_OPTIONAL_URLS = ('image', 'banner_image', '_apple_news_url')


def safe_url(url: Any, schemes: Iterable[str] = WEB_SCHEMES) -> str:
    """Return ``url`` if it is an absolute URL in ``schemes`` with a sane host, else ''.

    A protocol-relative ``//host/path`` (common in og:image tags) is returned
    as https. Credentials in the authority (``https://bank.com@evil.test``) are
    a phishing shape, never an article, and are rejected.
    """
    if not isinstance(url, str):
        return ''
    url = url.strip()
    if not url or _URL_CONTROL.search(url):
        return ''
    if url.startswith('//'):
        url = 'https:' + url
    try:
        parts = urlsplit(url)
        scheme = parts.scheme.lower()
        if scheme not in schemes:
            return ''
        if scheme == 'mailto':
            return url
        host = parts.hostname
        _ = parts.port  # raises ValueError on a malformed port
    except ValueError:
        return ''
    if not host or _BAD_HOST_CHARS.search(host):
        return ''
    if parts.username is not None or parts.password is not None:
        return ''
    return url


def _ip_literal(host: str) -> Optional[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
    """The address a host names directly, including inet_aton forms like 127.1."""
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        pass
    if re.fullmatch(r'[0-9a-fx.]+', host):
        try:
            return ipaddress.ip_address(socket.inet_aton(host))
        except OSError:
            pass
    return None


def is_public_http_url(url: Any) -> bool:
    """True if the pipeline may fetch ``url``: http(s), and not a private address.

    Article and image URLs come from third-party feeds, and the pages they
    point at are republished as excerpts and images. A link to a loopback,
    link-local (cloud metadata) or private address would publish whatever the
    runner can reach there. This checks the literal host only; it does not
    resolve DNS (see docs/decisions/sources.md).
    """
    url = safe_url(url)
    if not url:
        return False
    host = (urlsplit(url).hostname or '').rstrip('.')
    if not host or host == 'localhost' or host.endswith(_PRIVATE_HOSTS):
        return False
    address = _ip_literal(host)
    return address is None or address.is_global


def plain_text(value: Any) -> str:
    """Return ``value`` with any markup removed, for a field rendered as text.

    Text without anything tag-shaped passes through unchanged, so ordinary
    headlines (including ``&`` and ``2 < 3``) are untouched. Markup is parsed
    and dropped; the loop catches entity-encoded markup that the first parse
    decodes into live markup (``&lt;script&gt;``).
    """
    if value is None:
        return ''
    text = _TEXT_CONTROL.sub('', str(value))
    for _ in range(3):
        if not _TAG_LIKE.search(text):
            return text
        soup = BeautifulSoup(text, 'html.parser')
        for node in soup.find_all(_DROP_WITH_CONTENT):
            node.decompose()
        text = ' '.join(soup.get_text(' ').split())
    return _TAG_LIKE.sub(lambda m: m.group(0)[1:], text)


def _safe_style(style: Any) -> str:
    """Keep the allowlisted, inert declarations of an inline style."""
    kept = []
    for declaration in str(style).split(';'):
        prop, sep, value = declaration.partition(':')
        prop, value = prop.strip().lower(), value.strip()
        if sep and value and prop in _CSS_PROPERTIES and not _CSS_UNSAFE.search(value):
            kept.append(f'{prop}:{value};')
    return ''.join(kept)


def sanitize_html(html: Any, base_url: str = '') -> str:
    """Reduce an HTML fragment to inert markup: allowlisted tags, attributes and URLs.

    Relative links and images are resolved against ``base_url`` (the article's
    own URL), as readers do, rather than dropped. Idempotent, so retained
    items can pass through it on every run.
    """
    if not html:
        return ''
    html = _TEXT_CONTROL.sub('', str(html))
    if '<' not in html:
        return html
    soup = BeautifulSoup(html, 'html.parser')

    # Comments, CDATA, doctypes and processing instructions.
    for node in soup.find_all(string=lambda s: isinstance(s, PreformattedString)):
        node.extract()
    for tag in soup.find_all(_DROP_WITH_CONTENT):
        if not tag.decomposed:
            tag.decompose()

    for tag in soup.find_all(True):
        if tag.decomposed:
            continue
        if tag.name not in _ALLOWED_TAGS:
            tag.unwrap()
            continue
        allowed = _GLOBAL_ATTRS | _TAG_ATTRS.get(tag.name, frozenset())
        for name in list(tag.attrs):
            value = tag.attrs[name]
            if name not in allowed:
                del tag.attrs[name]
            elif name in _URL_ATTRS:
                if base_url and isinstance(value, str):
                    value = urljoin(base_url, value.strip())
                url = safe_url(value, _URL_ATTRS[name])
                if url:
                    tag.attrs[name] = url
                else:
                    del tag.attrs[name]
            elif name == 'style':
                style = _safe_style(value)
                if style:
                    tag.attrs[name] = style
                else:
                    del tag.attrs[name]
        if tag.name == 'img' and not tag.get('src'):
            tag.decompose()
        elif tag.name == 'a' and tag.get('target'):
            tag.attrs['rel'] = ['noopener', 'noreferrer']
    # Removing an element can leave whitespace that bs4 collapses on its next
    # parse; reparse once so the result is a fixed point.
    return str(BeautifulSoup(str(soup), 'html.parser'))


def sanitize_feed_item(item: Dict) -> Optional[Dict]:
    """Sanitize one JSON Feed item in place; None if its own link is unsafe or private.

    Keys are only ever rewritten, never removed, except the optional URL
    fields, so the podcast feed contract and every read-back keep working.
    """
    url = safe_url(item.get('url'))
    # external_url holds the publisher URL whenever url is an Apple News link.
    source = safe_url(item.get('external_url') or url)
    # No article lives at a private address, and the podcast fetches these links.
    if not (is_public_http_url(url) and is_public_http_url(source)):
        return None
    for key in _ITEM_TEXT_FIELDS:
        if isinstance(item.get(key), str):
            item[key] = plain_text(item[key])
    if 'content_html' in item:
        item['content_html'] = sanitize_html(item['content_html'], base_url=source)
    for key in _ITEM_OPTIONAL_URLS:
        if key in item:
            safe = safe_url(item[key]) if is_public_http_url(item[key]) else ''
            if safe:
                item[key] = safe
            else:
                del item[key]
    for author in item.get('authors') or []:
        if isinstance(author, dict):
            if 'name' in author:
                author['name'] = plain_text(author['name'])
            if 'url' in author:
                author['url'] = safe_url(author['url'])
    if isinstance(item.get('tags'), list):
        item['tags'] = [plain_text(tag) for tag in item['tags']]
    return item


def sanitize_feed(feed: Dict, label: str = '') -> Dict:
    """Sanitize every item of a JSON Feed dict in place and return it."""
    items = feed.get('items') or []
    kept = [clean for clean in (sanitize_feed_item(item) for item in items) if clean]
    if len(kept) < len(items):
        print(f"🧹 {label or 'feed'}: dropped {len(items) - len(kept)} item(s) with an unsafe link")
    feed['items'] = kept
    return feed
