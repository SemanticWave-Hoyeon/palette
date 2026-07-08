from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_web_ui_assets_are_wired_for_github_pages():
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "docs" / "web" / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "docs" / "web" / "app.js").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")

    assert './web/styles.css' in html
    assert './web/app.js' in html
    assert "Paper Palette Web UI" in html
    assert 'class="app-body"' in html
    assert 'class="workbench"' in html
    assert 'id="paletteGrid"' in html
    assert 'id="paletteOutput"' in html
    assert 'id="previewStrip"' in html
    assert 'id="metricCount"' in html
    assert "grid-template-columns: repeat(var(--columns, 4), minmax(0, 1fr));" in css
    assert ".workspace" in css
    assert ".app-body" in css
    assert ".workbench" in css
    assert ".output-panel" in css
    assert "actions/deploy-pages@v4" in workflow
    assert "path: docs" in workflow
    assert "github-pages" in workflow
    assert "observable" in js
    assert "jama" in js
    assert "frontiers" in js
    assert "#4A6990" in js
    assert "function pythonArray" in js


def test_multilingual_readmes_link_to_web_ui():
    expected_url = "https://semanticwave-hoyeon.github.io/paper-palette/"
    for filename in ["README.md", "README.ko.md", "README.ja.md", "README.zh-CN.md", "README.zh-TW.md"]:
        text = (ROOT / filename).read_text(encoding="utf-8")
        assert expected_url in text
        assert "python3 -m http.server 8000 --directory docs" in text
