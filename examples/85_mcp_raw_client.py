"""85 — MCP raw client: AmberTrace's verified organs over bare JSON-RPC 2.0.

The lowest-level MCP integration: hand-built JSON-RPC POSTs to ``/mcp`` with
``httpx`` — the wire format, no abstractions. Discover the tools, then call
decide (``query``), authorize (``authorize_action``) and, optionally,
``predict``. MCP is a preview capability: a deployment without it returns 404
and this script says so and exits 0.

    python 85_mcp_raw_client.py --platform-id 12
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import httpx

from _common import DEFAULT_BASE_URL, _load_dotenv


def main() -> int:
    _load_dotenv()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--platform-id", type=int, help="verified-profile platform id")
    ap.add_argument("--prediction-config-id", type=int, help="enables the predict step")
    ap.add_argument("--query", default="What is the decision?")
    ap.add_argument("--action-tool", default="place_order")
    ap.add_argument("--base-url", default=os.environ.get("AMBERTRACE_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument("--api-key", default=os.environ.get("AMBERTRACE_API_KEY"))
    args = ap.parse_args()
    if not args.api_key:
        sys.exit("AMBERTRACE_API_KEY is not set (export it or use examples/.env).")

    url = args.base_url.rstrip("/") + "/mcp"
    headers = {"Authorization": f"Bearer {args.api_key}"}
    next_id = iter(range(1, 1000))

    def mcp_call(method: str, params: dict | None = None) -> dict | None:
        body: dict = {"jsonrpc": "2.0", "id": next(next_id), "method": method}
        if params is not None:
            body["params"] = params
        resp = httpx.post(url, json=body, headers=headers, timeout=120.0)
        if resp.status_code == 404:
            print("MCP server not enabled on this deployment.")
            sys.exit(0)
        if resp.status_code == 401:
            sys.exit("Invalid API key.")
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            print(f"  JSON-RPC error: {data['error']}")
            return None
        return data["result"]

    def call_tool(name: str, arguments: dict) -> dict | None:
        result = mcp_call("tools/call", {"name": name, "arguments": arguments})
        return json.loads(result["content"][0]["text"]) if result else None

    print("== Handshake ==")
    info = mcp_call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                   "clientInfo": {"name": "example-85", "version": "1"}})
    if info:
        print(f"  server: {info['serverInfo']['name']}  protocol: {info['protocolVersion']}")
    httpx.post(url, json={"jsonrpc": "2.0", "method": "notifications/initialized"},
               headers=headers, timeout=30.0)

    print("\n== Step 1: tools/list ==")
    for tool in (mcp_call("tools/list") or {}).get("tools", []):
        print(f"  {tool['name']}: {tool['description'].splitlines()[0][:90]}")

    print("\n== Step 2: list_domains ==")
    domains = call_tool("list_domains", {}) or {}
    for d in domains.get("domains", []):
        print(f"  domain {d.get('id')}: {d.get('name')}")

    if args.platform_id is None:
        print("\nPass --platform-id to run query / authorize_action.")
        return 0

    print("\n== Step 3: query ==")
    ans = call_tool("query", {"platform_id": args.platform_id, "query": args.query}) or {}
    for key in ("decision", "proof_checked", "deciding_rule", "certified_facts"):
        print(f"  {key}: {ans.get(key)}")

    print("\n== Step 4: authorize_action ==")
    verdict = call_tool("authorize_action", {
        "platform_id": args.platform_id, "action": {"tool": args.action_tool, "args": {}}}) or {}
    print(f"  {json.dumps(verdict)[:300]}")

    if args.prediction_config_id is not None:
        print("\n== Step 5: predict ==")
        pred = call_tool("predict", {"platform_id": args.platform_id,
                                     "prediction_config_id": args.prediction_config_id}) or {}
        print(f"  {json.dumps(pred)[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
