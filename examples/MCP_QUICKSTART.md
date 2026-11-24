# Connect your agent to AmberTrace via MCP

The [Model Context Protocol](https://modelcontextprotocol.io) (MCP) is an open standard
for giving AI agents tools. AmberTrace exposes its verified capabilities as MCP tools, so any
MCP-compatible client can decide, predict and authorize with proof-carrying answers.

## Endpoint and authentication

`POST https://app.ambertrace.ai/mcp` -- stateless JSON-RPC 2.0.

`Authorization: Bearer at_xxxxx` -- the same API key as the REST API. OAuth 2.1 support is
planned. Discovery metadata: `GET /.well-known/oauth-protected-resource` (RFC 9728).

## Tools

| Tool | What it does |
|------|--------------|
| `query` | Neurosymbolic decision with proof: `decision`, `proof_checked`, `deciding_rule`, `certified_facts` |
| `predict` | Verified forecast with confidence interval |
| `authorize_action` | Proof-carrying permit/deny gate for an agent action |
| `list_domains` | List your domains |
| `get_job_status` | Poll a long-running job |

## Preview

MCP is currently in preview. Contact your account team to enable it. Where it is not enabled,
the endpoint returns 404 and each example below says so and exits cleanly.

## Examples

| Script | Shows |
|--------|-------|
| `85_mcp_raw_client.py` | Raw JSON-RPC over `httpx` -- the wire format, no abstractions |
| `86_mcp_python_client.py` | The official MCP Python SDK (`pip install "mcp>=1.0"`) |
| `87_mcp_langgraph_agent.py` | A LangGraph ReAct agent calling the tools; bring your own local LLM via `OPENAI_API_BASE` |

## Claude Desktop / Claude Code

Claude supports MCP natively. See example 85 for the wire format, or configure Claude's MCP
settings to point at your AmberTrace endpoint with your API key as the bearer token.

## What's next

OAuth 2.1 self-serve onboarding (planned).
