"""One-shot search: answer a query, print, exit.

The HTTP server exists for a client that queries often enough to want a warm
process. A client that has no watcher and rebuilds only in continuous
integration has nothing to keep warm, and opening a port to ask one question
is a cost with no return. This entry point runs the same search and exits.
"""

import argparse
import json
import sys

from . import search


def format_text(hits: list[dict], confidence: str | None) -> str:
    if not hits:
        return "no hits"
    lines = []
    for index, hit in enumerate(hits, 1):
        heading = hit.get("heading") or "(root)"
        score = hit.get("score")
        score_text = f"[{score:.3f}] " if isinstance(score, (int, float)) else ""
        lines.append(f"{index}. {score_text}{hit.get('file', '?')} > {heading}")
        text = str(hit.get("text") or "").strip().replace("\n", " ")
        if text:
            lines.append(f"   {text[:280]}")
    if confidence:
        lines.append(f"confidence: {confidence}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metamind-vault-rag-query",
        description="Search the indexed corpus and exit.",
    )
    parser.add_argument("query", help="what to search for")
    parser.add_argument("-k", "--limit", type=int, default=5, help="how many hits")
    parser.add_argument(
        "--mode",
        choices=("hybrid", "semantic-only", "keyword-only"),
        default="hybrid",
        help="retriever strategy",
    )
    parser.add_argument("--rerank", action="store_true", help="apply the cross-encoder tier")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    hits = search.search_vault(args.query, args.limit, rerank=args.rerank, mode=args.mode)
    confidence = search.result_confidence(hits)

    if args.json:
        print(json.dumps({"query": args.query, "hits": hits, "confidence": confidence}))
    else:
        print(format_text(hits, confidence))

    # A query that matches nothing is a fact about the corpus, not a failure,
    # so this exits zero. A caller wanting to branch on it reads the payload.
    sys.exit(0)


if __name__ == "__main__":
    main()
