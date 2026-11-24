"""86 — MCP Python SDK client: the standard MCP flow against AmberTrace.

The same walk as example 85, using the official MCP client library
(``streamablehttp_client`` + ``ClientSession``) — what MCP hosts such as Claude
Desktop / Claude Code do under the hood. Optional dependency (not installed
with ``ambertraceai``):

    pip install "mcp>=1.0"
    python 86_mcp_python_client.py --platform-id 12

MCP is a preview capability: a deployment without it is reported and exits 0.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from _common import DEFAULT_BASE_URL, _load_dotenv


def _args() -> argparse.Namespace:
    _load_dotenv()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--platform-id", type=int, help="verified-profile platform id")
    ap.add_argument("--prediction-config-id", type=int, help="enables the predict step")
    ap.add_argument("--query", default="What is the decision?")
    ap.add_argument("--action-tool", default="place_order")
    ap.add_argument("--base-url", default=os.environ.get("AMBERTRACE_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument("--api-key", default=os.environ.get("AMBERTRACE_API_KEY"))
    return ap.parse_args()


async def _tool(session, name: str, arguments: dict) -> dict:
    result = await session.call_tool(name, arguments)
    return json.loads(result.content[0].text)


async def run(args: argparse.Namespace) -> None:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(
        url=args.base_url.rstrip("/") + "/mcp",
        headers={"Authorization": f"Bearer {args.api_key}"},
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("== Step 1: list_tools ==")
            for tool in (await session.list_tools()).tools:
                print(f"  {tool.name}: {(tool.description or '').splitlines()[0][:90]}")

            print("\n== Step 2: list_domains ==")
            for d in (await _tool(session, "list_domains", {})).get("domains", []):
                print(f"  domain {d.get('id')}: {d.get('name')}")
            if args.platform_id is None:
                print("\nPass --platform-id to run query / authorize_action.")
                return

            print("\n== Step 3: query ==")
            ans = await _tool(session, "query",
                              {"platform_id": args.platform_id, "query": args.query})
            for key in ("decision", "proof_checked", "deciding_rule", "certified_facts"):
                print(f"  {key}: {ans.get(key)}")

            print("\n== Step 4: authorize_action ==")
            verdict = await _tool(session, "authorize_action", {
                "platform_id": args.platform_id,
                "action": {"tool": args.action_tool, "args": {}}})
            print(f"  {json.dumps(verdict)[:300]}")

            if args.prediction_config_id is not None:
                print("\n== Step 5: predict ==")
                pred = await _tool(session, "predict", {
                    "platform_id": args.platform_id,
                    "prediction_config_id": args.prediction_config_id})
                print(f"  {json.dumps(pred)[:300]}")


def main() -> int:
    args = _args()
    if not args.api_key:
        sys.exit("AMBERTRACE_API_KEY is not set (export it or use examples/.env).")
    try:
        import mcp  # noqa: F401
    except ImportError:
        print("This example requires the mcp package. Install with: pip install 'mcp>=1.0'")
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
