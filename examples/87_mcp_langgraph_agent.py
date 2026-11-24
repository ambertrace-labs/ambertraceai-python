"""87 — LangGraph ReAct agent over AmberTrace's MCP tools (bring your own LLM).

AmberTrace's tools load as LangChain tools; a LangGraph ReAct agent decides
when to call them. The LLM is YOUR model server (any OpenAI-compatible
endpoint, e.g. LM Studio or Ollama) — this example calls no hosted LLM and
requires ``OPENAI_API_BASE``.

    pip install langgraph langchain-mcp-adapters langchain-openai
    export OPENAI_API_BASE=http://localhost:1234/v1
    python 87_mcp_langgraph_agent.py --platform-id 12

Optional env: ``OPENAI_API_KEY`` (default "none"), ``OPENAI_MODEL_NAME``.
MCP is a preview capability: a deployment without it is reported, exit 0.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from _common import DEFAULT_BASE_URL, _load_dotenv


async def run(args: argparse.Namespace) -> None:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    client = MultiServerMCPClient({"ambertrace": {
        "transport": "streamable_http",
        "url": args.base_url.rstrip("/") + "/mcp",
        "headers": {"Authorization": f"Bearer {args.api_key}"},
    }})
    tools = await client.get_tools()
    print(f"Loaded {len(tools)} MCP tools: {', '.join(t.name for t in tools)}")

    llm = ChatOpenAI(base_url=args.llm_base, api_key=args.llm_key, model=args.model)
    agent = create_react_agent(llm, tools)
    task = ("List the available domains, then query platform "
            f"{args.platform_id} with '{args.query}' and show me the proof certificate.")
    result = await agent.ainvoke({"messages": [("human", task)]})

    for msg in result["messages"]:
        calls = getattr(msg, "tool_calls", None)
        if calls:
            for c in calls:
                print(f"[tool call] {c['name']}({c['args']})")
        elif msg.type == "tool":
            print(f"[tool result] {str(msg.content)[:300]}")
        elif msg.type == "ai":
            print(f"[answer] {msg.content}")


def main() -> int:
    _load_dotenv()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--platform-id", type=int, required=True)
    ap.add_argument("--query", default="What is the decision?")
    ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL_NAME", "default"))
    ap.add_argument("--base-url", default=os.environ.get("AMBERTRACE_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument("--api-key", default=os.environ.get("AMBERTRACE_API_KEY"))
    args = ap.parse_args()
    if not args.api_key:
        sys.exit("AMBERTRACE_API_KEY is not set (export it or use examples/.env).")
    args.llm_base = os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")
    if not args.llm_base:
        sys.exit("This example requires a local LLM. Set OPENAI_API_BASE to your model "
                 "server (e.g. http://localhost:1234/v1 for LM Studio, "
                 "http://localhost:11434/v1 for Ollama). It does NOT call a cloud LLM.")
    args.llm_key = os.environ.get("OPENAI_API_KEY", "none")
    try:
        import langchain_mcp_adapters  # noqa: F401
        import langchain_openai  # noqa: F401
        import langgraph  # noqa: F401
    except ImportError:
        print("This example requires: pip install langgraph langchain-mcp-adapters langchain-openai")
        return 0
    try:
        asyncio.run(run(args))
    except Exception as exc:  # noqa: BLE001 - surface 404/401 cleanly
        text = str(exc)
        if "404" in text:
            print("MCP server not enabled on this deployment.")
            return 0
        if "401" in text:
            sys.exit("Invalid API key.")
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
