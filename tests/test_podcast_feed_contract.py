"""The writer's half of the podcast-feed contract with curated-podcast-generator.

The show reads a fixed set of keys from feed-podcast-{day}.json and defaults any
that are missing, so a renamed or dropped key never errors: it just changes the
episode. This pins PODCAST_FEED_CONTRACT against the dict literals
generate_podcast_feed() actually writes, read from the source with ast so no
pipeline run (and no API key) is needed.
"""
import ast
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parent.parent / "super_rss_curator_json.py"


def _contract() -> dict:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "PODCAST_FEED_CONTRACT" for t in node.targets):
            return ast.literal_eval(node.value)
    pytest.fail("PODCAST_FEED_CONTRACT is gone from super_rss_curator_json.py")


def _writer() -> ast.FunctionDef:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "generate_podcast_feed":
            return node
    pytest.fail("generate_podcast_feed() is gone from super_rss_curator_json.py")


def _literal_keys(node: ast.Dict) -> set[str]:
    return {k.value for k in node.keys if isinstance(k, ast.Constant)}


def _assigned_dict(func: ast.FunctionDef, name: str) -> ast.Dict:
    for node in ast.walk(func):
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
                and any(getattr(t, "id", None) == name for t in node.targets)):
            return node.value
    pytest.fail(f"no `{name} = {{...}}` literal in generate_podcast_feed()")


def test_every_item_carries_the_contract_keys():
    item = _assigned_dict(_writer(), "item")
    missing = set(_contract()["items"]) - _literal_keys(item)
    assert not missing, f"feed-podcast items no longer write {sorted(missing)}"


def test_the_feed_metadata_carries_the_contract_keys():
    feed = _assigned_dict(_writer(), "feed")
    podcast = next((v for k, v in zip(feed.keys, feed.values)
                    if isinstance(k, ast.Constant) and k.value == "_podcast"), None)
    assert isinstance(podcast, ast.Dict), "the feed no longer writes a `_podcast` literal"
    missing = set(_contract()["_podcast"]) - _literal_keys(podcast)
    assert not missing, f"`_podcast` no longer writes {sorted(missing)}"


def test_no_contract_key_is_removed_after_it_is_written():
    """A `del item[...]` or `.pop()` later in the function would pass the literal check."""
    keys = set(_contract()["items"]) | set(_contract()["_podcast"])
    for node in ast.walk(_writer()):
        if isinstance(node, ast.Delete):
            for target in node.targets:
                if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant):
                    assert target.slice.value not in keys, f"del of contract key {target.slice.value}"
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "pop" and node.args
                and isinstance(node.args[0], ast.Constant)):
            assert node.args[0].value not in keys, f"pop of contract key {node.args[0].value}"
