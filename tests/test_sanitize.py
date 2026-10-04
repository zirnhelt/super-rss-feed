"""No third-party feed content leaves the pipeline as active HTML or a dangerous link.

Every published feed goes out through write_feed(), which runs sanitize_feed();
these pin the payloads that must die there and the pipeline markup that must
survive it unchanged.
"""
import json
import sys
import types
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import sanitize as s
import super_rss_curator_json as m

HOSTILE_HTML = [
    '<script>alert(1)</script>',
    '<SCRIPT SRC=https://evil.test/x.js></SCRIPT>',
    '<img src=x onerror=alert(1)>',
    '<img src="https://ok.test/a.jpg" onerror="alert(1)">',
    '<a href="javascript:alert(1)">x</a>',
    '<a href="JaVaScRiPt:alert(1)">x</a>',
    '<a href="java\tscript:alert(1)">x</a>',
    '<a href=" javascript:alert(1)">x</a>',
    '<a href="&#106;avascript:alert(1)">x</a>',
    '<a href="data:text/html,<script>alert(1)</script>">x</a>',
    '<a href="vbscript:msgbox(1)">x</a>',
    '<svg onload=alert(1)><circle/></svg>',
    '<math><mi xlink:href="javascript:alert(1)">x</mi></math>',
    '<iframe src="https://evil.test"></iframe>',
    '<object data="https://evil.test/x.swf"></object><embed src="x">',
    '<form action="https://evil.test"><input name=q><button>go</button></form>',
    '<body onload=alert(1)>',
    '<div style="background:url(javascript:alert(1))">x</div>',
    '<div style="width: expression(alert(1))">x</div>',
    '<p style="position:fixed;top:0;left:0;z-index:9999">overlay</p>',
    '<noscript><p title="</noscript><img src=x onerror=alert(1)>"></noscript>',
    '<!--<img src=x onerror=alert(1)>-->',
    '<![CDATA[<script>alert(1)</script>]]>',
    '<style>body{display:none}</style>',
    '<base href="https://evil.test/">',
    '<meta http-equiv="refresh" content="0;url=javascript:alert(1)">',
    '<a href="https://ok.test" onmouseover="alert(1)">x</a>',
    '<img src="data:image/svg+xml;base64,PHN2ZyBvbmxvYWQ9YWxlcnQoMSk+">',
    '<p>unclosed <b>bold <script>alert(1)',
    '<<script>script>alert(1)<</script>/script>',
]

_ACTIVE = ('<script', 'onerror', 'onload', 'onmouseover', 'javascript:', 'vbscript:',
           'data:', 'expression(', 'url(', '<iframe', '<object', '<embed', '<form',
           '<svg', '<math', '<style', '<base', '<meta', '<noscript', 'position:', '<!--')


@pytest.mark.parametrize('payload', HOSTILE_HTML)
def test_hostile_markup_is_inert(payload):
    out = s.sanitize_html(payload).lower()
    for marker in _ACTIVE:
        assert marker not in out, (payload, out)


@pytest.mark.parametrize('payload', HOSTILE_HTML)
def test_sanitizing_is_idempotent(payload):
    once = s.sanitize_html(payload)
    assert s.sanitize_html(once) == once


def test_pipeline_badge_and_lead_image_survive_byte_for_byte():
    badge = m._make_score_badge(
        score=80, quality=80, relevance=80, local_score=0, content_type=None, tags=[],
        podcast_days=['monday'], article_url='https://news.test/a?b=1&c=2',
    )
    lead = m._lead_image_html('https://img.test/a.jpg')
    html = lead + badge + '<p>Body text.</p>'
    out = s.sanitize_html(html)
    assert f'style="{m._LEAD_IMAGE_STYLE}"' in out
    assert f'style="{m._BADGE_STYLE}"' in out
    assert 'style="color:#7b9fc4;text-decoration:none;"' in out
    assert 'review.html?url=https%3A%2F%2Fnews.test%2Fa%3Fb%3D1%26c%3D2' in out
    assert s.sanitize_html(out) == out


def test_ordinary_article_markup_is_kept():
    html = ('<p class="lead">A <strong>dam</strong> <a href="https://bc.test/x" title="t">vote</a>.</p>'
            '<figure><img src="https://bc.test/i.jpg" alt="dam" width="600"><figcaption>Cap</figcaption></figure>'
            '<table><tr><td style="padding: 14px 16px; vertical-align: top;">cell</td></tr></table>'
            '<ul><li>one</li></ul><a href="mailto:editor@bc.test">mail</a>')
    out = s.sanitize_html(html)
    for kept in ('<strong>dam</strong>', 'href="https://bc.test/x"', 'src="https://bc.test/i.jpg"',
                 'alt="dam"', '<figcaption>Cap</figcaption>', 'padding:14px 16px;vertical-align:top;',
                 '<li>one</li>', 'href="mailto:editor@bc.test"'):
        assert kept in out, kept


def test_relative_links_resolve_against_the_article_not_dropped():
    html = '<img src="/images/a.webp"><a href="../tag/x">tag</a><a href="javascript:alert(1)">j</a>'
    out = s.sanitize_html(html, base_url='https://blog.test/2026/10/post/')
    assert 'src="https://blog.test/images/a.webp"' in out
    assert 'href="https://blog.test/2026/10/tag/x"' in out
    assert 'javascript' not in out
    item = s.sanitize_feed_item({'url': 'https://blog.test/p', 'content_html': '<img src="/a.jpg">'})
    assert item['content_html'] == '<img src="https://blog.test/a.jpg"/>'


def test_unknown_tags_keep_their_text_and_target_blank_gets_noopener():
    out = s.sanitize_html('<custom-card>inner</custom-card><a href="https://x.test" target="_blank">x</a>')
    assert 'inner' in out and 'custom-card' not in out
    assert 'rel="noopener noreferrer"' in out


@pytest.mark.parametrize('text, expected', [
    ('Smith & Sons win contract', 'Smith & Sons win contract'),
    ('Why 2 < 3 matters', 'Why 2 < 3 matters'),
    ('<b>Bold</b> headline', 'Bold headline'),
    ('Headline <script>alert(1)</script>', 'Headline'),
    ('<img src=x onerror=alert(1)>Headline', 'Headline'),
    # _clean_text decodes entities, so an encoded payload reaches summary as markup.
    ('Story <b>x</b> &lt;script&gt;alert(1)&lt;/script&gt;', 'Story x'),
    ('Tab\tand\x00null', 'Tab\tandnull'),
])
def test_plain_text_fields_carry_no_markup(text, expected):
    assert s.plain_text(text) == expected


@pytest.mark.parametrize('url, expected', [
    ('https://news.test/a?b=1', 'https://news.test/a?b=1'),
    ('http://news.test', 'http://news.test'),
    ('//cdn.test/i.jpg', 'https://cdn.test/i.jpg'),
    ('javascript:alert(1)', ''),
    ('JAVASCRIPT:alert(1)', ''),
    ('java\nscript:alert(1)', ''),
    ('\x01javascript:alert(1)', ''),
    ('data:image/png;base64,AAAA', ''),
    ('vbscript:x', ''),
    ('file:///etc/passwd', ''),
    ('/relative/path.jpg', ''),
    ('https://bank.test@evil.test/', ''),
    ('https://user:pw@news.test/', ''),
    ('https://news.test:99999/', ''),
    ('https://ne ws.test/', ''),
    ('https:///nohost', ''),
    ('', ''),
    (None, ''),
])
def test_safe_url(url, expected):
    assert s.safe_url(url) == expected


@pytest.mark.parametrize('url, public', [
    ('https://wltribune.com/news/x', True),
    ('http://8.8.8.8/', True),
    ('http://127.0.0.1/', False),
    ('http://127.1/', False),
    ('http://2130706433/', False),
    ('http://0x7f000001/', False),
    ('http://169.254.169.254/latest/meta-data/', False),
    ('http://10.1.2.3/', False),
    ('http://192.168.0.1/', False),
    ('http://[::1]/', False),
    ('http://[::ffff:127.0.0.1]/', False),
    ('http://localhost:8080/', False),
    ('http://localhost./', False),
    ('http://metadata.google.internal/', False),
    ('http://printer.local/', False),
    ('javascript:alert(1)', False),
])
def test_fetch_guard(url, public):
    assert s.is_public_http_url(url) is public


def _item(**over):
    item = {
        'id': 'https://news.test/a', 'url': 'https://news.test/a',
        'title': 'Title <script>alert(1)</script>',
        'content_html': '<p onclick="x()">Body</p><img src="javascript:alert(1)">',
        'summary': 'Sum <img src=x onerror=alert(1)>',
        '_excerpt': 'Ex',
        'date_published': '2026-10-01T00:00:00+00:00',
        'authors': [{'name': '<b>Outlet</b>', 'url': 'javascript:alert(1)'}],
        'image': 'javascript:alert(1)',
        '_apple_news_url': 'https://apple.news/Axxxxxxxxx',
        'tags': ['local-priority', '<i>x</i>'],
    }
    item.update(over)
    return item


def test_feed_item_is_sanitized_field_by_field():
    item = s.sanitize_feed_item(_item())
    assert item['title'] == 'Title'
    assert item['summary'] == 'Sum'
    assert item['content_html'] == '<p>Body</p>'
    assert 'image' not in item
    assert item['_apple_news_url'] == 'https://apple.news/Axxxxxxxxx'
    # Read-backs index authors[0]['url'], so the key stays, emptied.
    assert item['authors'] == [{'name': 'Outlet', 'url': ''}]
    assert item['tags'] == ['local-priority', 'x']


@pytest.mark.parametrize('over', [
    {'url': 'javascript:alert(1)'},
    {'url': ''},
    {'url': 'https://apple.news/Axxxxxxxxx', 'external_url': 'data:text/html,x'},
    {'url': 'http://169.254.169.254/latest/meta-data/'},
    {'url': 'http://localhost:8080/admin'},
])
def test_item_with_an_unsafe_link_is_dropped(over):
    feed = {'items': [_item(**over), _item(id='https://news.test/b', url='https://news.test/b')]}
    s.sanitize_feed(feed)
    assert [i['url'] for i in feed['items']] == ['https://news.test/b']


def test_podcast_contract_keys_survive_sanitizing():
    item = {k: 'x' for k in m.PODCAST_FEED_CONTRACT['items']}
    item.update(url='https://news.test/a', authors=[{'name': 'Outlet', 'url': ''}])
    assert set(m.PODCAST_FEED_CONTRACT['items']) <= set(s.sanitize_feed_item(item))


# --- The writers ------------------------------------------------------------

def _article(link: str, image: str = 'https://img.test/a.jpg', **over) -> types.SimpleNamespace:
    art = types.SimpleNamespace(
        link=link, title='Council votes <script>alert(1)</script>',
        description='<p>Body <img src=x onerror=alert(1)></p>',
        source='Test Outlet', source_url='https://news.test',
        pub_date=datetime(2026, 10, 1, tzinfo=timezone.utc),
        score=70, quality=70, relevance=70, local=60, content_type=None, image=image,
    )
    for k, v in over.items():
        setattr(art, k, v)
    return art


def test_published_json_and_rss_carry_no_active_content(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    articles = [
        _article('https://news.test/a', image='javascript:alert(1)'),
        _article('javascript:alert(document.domain)'),
    ]
    m.generate_json_feed(articles, 'local', 'feed-local.json')

    feed = json.loads((tmp_path / 'feed-local.json').read_text(encoding='utf-8'))
    assert [i['url'] for i in feed['items']] == ['https://news.test/a']
    raw = (tmp_path / 'feed-local.json').read_text(encoding='utf-8').lower()
    for marker in ('<script', 'onerror', 'javascript:'):
        assert marker not in raw

    rss = (tmp_path / 'feed-local.xml').read_text(encoding='utf-8')
    ET.fromstring(rss.encode('utf-8'))  # still well-formed
    for marker in ('<script', 'onerror', 'javascript:'):
        assert marker not in rss.lower()


def test_retained_items_do_not_stack_a_new_image_every_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    m.generate_json_feed([_article('https://news.test/a', description='<p>Body</p>')],
                         'local', 'feed-local.json')
    for _ in range(3):
        item = json.loads((tmp_path / 'feed-local.json').read_text(encoding='utf-8'))['items'][0]
        retained = _article(item['url'], description=m._strip_generated_prefix(item['content_html']))
        m.generate_json_feed([retained], 'local', 'feed-local.json')
    item = json.loads((tmp_path / 'feed-local.json').read_text(encoding='utf-8'))['items'][0]
    assert item['content_html'].count('<img') == 1
    assert item['content_html'].endswith('<p>Body</p>')


def test_strip_prefix_heals_already_stacked_items_and_leaves_article_text_alone():
    lead = m._lead_image_html('https://img.test/a.jpg')
    badge = m._make_score_badge(80, 80, 80, 0, None, [], podcast_days=['friday'],
                                article_url='https://news.test/a')
    body = '<p><img src="https://news.test/inline.jpg"/> Article</p>'
    stacked = (lead + badge) * 3 + body
    assert m._strip_generated_prefix(stacked) == body
    assert m._strip_generated_prefix(s.sanitize_html(stacked)) == s.sanitize_html(body)
    assert m._strip_generated_prefix(body) == body


# --- The fetchers -------------------------------------------------------------

class _Resp:
    def __init__(self, url, status=200, location=None, cookies=None):
        self.url = url
        self.status_code = status
        self.headers = {'location': location} if location else {}
        self.is_redirect = location is not None
        self.cookies = cookies or {}
        self.text = '<html><head><meta property="og:image" content="https://img.test/a.jpg"></head>' \
                    '<body><article>' + 'Internal secret text. ' * 10 + '</article></body></html>'
        self.content = self.text.encode()

    def raise_for_status(self):
        pass

    def close(self):
        pass


# What each test hostname resolves to; anything else does not resolve.
_DNS = {'news.test': '93.184.216.34', 'img.test': '93.184.216.35', 'cdn.test': '93.184.216.36',
        'rebind.test': '169.254.169.254', 'lan.test': '192.168.1.10', 'mixed.test': ['93.184.216.34', '10.0.0.5'],
        'v6.test': '::1'}


class _Calls(list):
    """URLs requested, plus ``routes``: URL -> canned response factory."""
    def __init__(self):
        super().__init__()
        self.routes = {}


@pytest.fixture
def web(monkeypatch):
    """Stub DNS and the network; returns the list of URLs actually requested."""
    import requests

    def getaddrinfo(host, *a, **k):
        if host not in _DNS:
            raise s.socket.gaierror('no such host')
        ips = _DNS[host] if isinstance(_DNS[host], list) else [_DNS[host]]
        return [(None, None, None, '', (ip, 0)) for ip in ips]
    monkeypatch.setattr(s.socket, 'getaddrinfo', getaddrinfo)

    calls = _Calls()

    def get(url, **kwargs):
        assert kwargs.get('allow_redirects') is False, 'redirects must be followed hop by hop'
        calls.append(url)
        return calls.routes.get(url, lambda: _Resp(url))()
    monkeypatch.setattr(requests, 'get', get)
    return calls


@pytest.mark.parametrize('target', ['http://169.254.169.254/latest/meta-data/', 'http://localhost/admin',
                                    'http://rebind.test/latest/meta-data/', 'https://lan.test/admin',
                                    'https://mixed.test/a', 'https://v6.test/', 'https://nxdomain.test/'])
def test_private_targets_are_never_fetched(web, target):
    import fetch_images
    assert m._fetch_article_excerpt(target) == ''
    assert m._fetch_url_bytes(target) is None
    assert fetch_images.fetch_page_metadata(target)['image'] is None
    assert fetch_images.fetch_page_title(target) is None
    assert web == []


@pytest.mark.parametrize('hop', ['http://169.254.169.254/latest/meta-data/', 'http://rebind.test/x',
                                 'https://lan.test/router', 'file:///etc/passwd'])
def test_a_redirect_hop_into_a_private_address_is_never_requested(web, hop):
    import fetch_images
    web.routes['https://news.test/a'] = lambda: _Resp('https://news.test/a', 302, location=hop)
    assert m._fetch_article_excerpt('https://news.test/a') == ''
    assert fetch_images.fetch_page_metadata('https://news.test/a')['image'] is None
    assert set(web) == {'https://news.test/a'}


def test_a_public_redirect_chain_is_followed(web):
    import fetch_images
    web.routes['https://news.test/a'] = lambda: _Resp('https://news.test/a', 301, location='/b')
    web.routes['https://news.test/b'] = lambda: _Resp('https://news.test/b', 302, location='https://cdn.test/a')
    assert fetch_images.fetch_page_metadata('https://news.test/a')['image'] == 'https://img.test/a.jpg'
    assert web == ['https://news.test/a', 'https://news.test/b', 'https://cdn.test/a']


def test_a_redirect_loop_gives_up(web):
    web.routes['https://news.test/a'] = lambda: _Resp('https://news.test/a', 302, location='https://news.test/a')
    assert s.get_public('https://news.test/a') is None
    assert len(web) == s.MAX_REDIRECTS + 1


def test_a_public_page_is_still_read(web):
    import fetch_images
    assert m._fetch_article_excerpt('https://news.test/a').startswith('Internal secret text.')
    assert fetch_images.fetch_page_metadata('https://news.test/a')['image'] == 'https://img.test/a.jpg'
    assert m._fetch_url_bytes('https://news.test/feed')
