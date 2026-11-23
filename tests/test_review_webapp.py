"""review.html is an installable web app: manifest, service worker and icons must stay wired."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp"


def test_manifest_is_installable() -> None:
    manifest = json.loads((WEBAPP / "manifest.webmanifest").read_text())
    assert manifest["display"] == "standalone"
    assert manifest["start_url"] == "./review.html"
    sizes = {(i["sizes"], i["purpose"]) for i in manifest["icons"]}
    assert {("192x192", "any"), ("512x512", "any"), ("512x512", "maskable")} <= sizes
    for icon in manifest["icons"]:
        assert (WEBAPP / icon["src"]).is_file(), icon["src"]


def test_page_links_manifest_and_registers_worker() -> None:
    html = (ROOT / "review.html").read_text()
    assert 'rel="manifest" href="manifest.webmanifest"' in html
    assert "serviceWorker.register('review-sw.js'" in html
    assert (WEBAPP / "review-sw.js").is_file()
    assert (WEBAPP / "icons" / "apple-touch-icon.png").is_file()


def test_worker_never_intercepts_cross_origin() -> None:
    worker = (WEBAPP / "review-sw.js").read_text()
    assert "url.origin !== self.location.origin" in worker


def test_both_deploys_stage_the_webapp() -> None:
    for name in ("deploy-static.yml", "generate-feed.yml"):
        assert "cp -r webapp/. output/" in (ROOT / ".github/workflows" / name).read_text(), name


def test_a_cut_row_says_why_the_run_passed_it_over() -> None:
    """The producer, 2026-11-21: "Can we add the skip reason?" The podcast's cut rows carry
    `reason`; the row shows it, escaped with the rest of its meta line."""
    page = (Path(__file__).resolve().parent.parent / "review.html").read_text(encoding="utf-8")
    body = page[page.index("function renderEpisodeCuts"):page.index("function episodeDates")]
    assert "typeof c.reason === 'string' && c.reason ? c.reason" in body
    assert "const meta = [c.source, why," in body
    assert "${escHtml(meta)}" in body
