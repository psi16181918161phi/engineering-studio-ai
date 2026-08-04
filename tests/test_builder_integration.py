from pathlib import Path


def test_builder_loader_is_configured_for_frontend() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    index_html = (repo_root / "frontend" / "index.html").read_text(encoding="utf-8")
    env_example = (repo_root / ".env.example").read_text(encoding="utf-8")

    assert 'id="builder-content"' in index_html
    assert 'builder.js' in index_html
    assert 'BUILDER_API_KEY' in env_example
