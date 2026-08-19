"""The one-shot query path. A client with no watcher has nothing to keep warm,
so it asks a question in a subprocess rather than through a port."""

import json

import pytest

from metamind_vault_rag import query


def test_parser_defaults_to_five_hybrid_hits() -> None:
    args = query.build_parser().parse_args(["how does auth work"])
    assert args.query == "how does auth work"
    assert args.limit == 5
    assert args.mode == "hybrid"
    assert args.rerank is False


def test_parser_accepts_a_limit_and_a_mode() -> None:
    args = query.build_parser().parse_args(["x", "-k", "3", "--mode", "keyword-only"])
    assert args.limit == 3
    assert args.mode == "keyword-only"


def test_parser_rejects_an_unknown_mode() -> None:
    with pytest.raises(SystemExit):
        query.build_parser().parse_args(["x", "--mode", "vibes"])


def test_text_output_numbers_hits_and_names_the_file() -> None:
    out = query.format_text(
        [{"file": "systems/auth.md", "heading": "Tokens", "score": 0.42, "text": "A body."}],
        None,
    )
    assert "1. [0.420] systems/auth.md > Tokens" in out
    assert "A body." in out


def test_text_output_says_so_when_nothing_matched() -> None:
    assert query.format_text([], None) == "no hits"


def test_text_output_carries_confidence_when_the_corpus_has_bands() -> None:
    out = query.format_text([{"file": "a.md", "heading": "h", "score": 1.0, "text": "t"}], "high")
    assert "confidence: high" in out


def test_text_output_omits_confidence_on_an_uncalibrated_corpus() -> None:
    out = query.format_text([{"file": "a.md", "heading": "h", "score": 1.0, "text": "t"}], None)
    assert "confidence" not in out


def test_a_heading_less_hit_reads_as_root() -> None:
    assert "(root)" in query.format_text([{"file": "a.md", "score": 1.0, "text": "t"}], None)


def test_json_output_is_parseable_and_carries_the_query(monkeypatch, capsys) -> None:
    hits = [{"file": "a.md", "heading": "h", "score": 1.0, "text": "t"}]
    monkeypatch.setattr(query.search, "search_vault", lambda *a, **k: hits)
    monkeypatch.setattr(query.search, "result_confidence", lambda h: "high")
    monkeypatch.setattr("sys.argv", ["metamind-vault-rag-query", "anything", "--json"])

    with pytest.raises(SystemExit) as exit_info:
        query.main()
    assert exit_info.value.code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["query"] == "anything"
    assert payload["hits"] == hits
    assert payload["confidence"] == "high"


def test_no_hits_exits_zero_because_that_is_an_answer(monkeypatch, capsys) -> None:
    monkeypatch.setattr(query.search, "search_vault", lambda *a, **k: [])
    monkeypatch.setattr(query.search, "result_confidence", lambda h: None)
    monkeypatch.setattr("sys.argv", ["metamind-vault-rag-query", "nothing here"])

    with pytest.raises(SystemExit) as exit_info:
        query.main()
    assert exit_info.value.code == 0
    assert "no hits" in capsys.readouterr().out
