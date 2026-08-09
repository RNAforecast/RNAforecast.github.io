"""Shared fixtures: one production build, reused by every test that needs it."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

JSONLD = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.I | re.S)


@pytest.fixture(scope='session')
def repo():
    return REPO


@pytest.fixture(scope='session')
def site(tmp_path_factory):
    """Build the site exactly as `make publish` does, into a throwaway dir."""
    out = tmp_path_factory.mktemp('site')
    result = subprocess.run(
        [sys.executable, '-m', 'pelican', 'content',
         '-o', str(out), '-s', 'publishconf.py', '--fatal', 'warnings'],
        cwd=REPO, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f'production build failed:\n{result.stdout}\n{result.stderr}')
    return out


@pytest.fixture
def sabotaged(site, tmp_path):
    """A writable copy of the built site, for fault-injection tests."""
    copy = tmp_path / 'site'
    shutil.copytree(site, copy)
    return copy


def read(path):
    return Path(path).read_text(encoding='utf-8')


def graphs_in(path):
    """Every parsed JSON-LD block on a page."""
    return [json.loads(block) for block in JSONLD.findall(read(path))]


def nodes_of(path, type_):
    return [node
            for graph in graphs_in(path)
            for node in graph.get('@graph', [])
            if node.get('@type') == type_]
