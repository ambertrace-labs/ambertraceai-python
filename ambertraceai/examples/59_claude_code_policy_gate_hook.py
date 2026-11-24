"""59 — Agent Policy Gate: gate Claude Code's tool calls (PreToolUse hook).

Put a machine-checked proof between a coding agent and its tools. Claude Code
runs a **PreToolUse hook** before every tool call it proposes; this example IS
that hook: it reads the proposed call (Bash command / file edit) from stdin,
derives typed facts from it, and asks AmberTrace to prove the action
permit-or-deny against a policy authored in plain English. Exit 0 lets the
call run; exit 2 blocks it and feeds the reason back to the model — which,
like any gated agent, can then try something within policy instead (e.g. push
a feature branch instead of main). It is the first APG example whose *caller*
is a real third-party agent harness rather than our own demo loop.

Two subcommands (hook mode must be a single stable shell command):

    python 59_claude_code_policy_gate_hook.py author   # once: compile + probe
    python 59_claude_code_policy_gate_hook.py hook     # wired into Claude Code

Wire the hook into Claude Code (.claude/settings.json in your project):

    {"hooks": {"PreToolUse": [
        {"matcher": "Bash|Edit|Write",
         "hooks": [{"type": "command",
                    "command": "python /path/to/59_claude_code_policy_gate_hook.py hook"}]}]}}

DIVISION OF LABOUR (the teaching point)
---------------------------------------
The MODEL proposes the raw action; the HOOK — trusted harness code — derives
the facts (does it push to a protected branch? touch secrets? leave the
workspace? use force?); the GATE proves the verdict. The fact-derivation
regexes below are deliberately simple and ILLUSTRATIVE, not exhaustive — the
guarantee is that whatever facts are supplied, the verdict over them is
PROVED, and anything the gate cannot certify is denied. Extend the derivation
for your own threat model; the proof obligation does not change.

HOOK CONTRACT (PreToolUse — documented at docs.claude.com, hooks → PreToolUse)
------------------------------------------------------------------------------
- stdin: JSON ``{"tool_name": ..., "tool_input": {...}, "cwd": ...}``.
- **exit 0** = allow — required: ``decision == "permit"`` AND ``proof_checked``.
- **exit 2** = block; stderr is fed back to the model (the deny reason + the
  derived facts + "Propose an action within policy instead.").
- **FAIL-CLOSED**: any error (API unreachable, missing/invalid key, malformed
  stdin) exits 2 with a "policy gate unreachable — blocking" message. Never
  exit 0 on error. Corollary: if the gate is unreachable, Claude Code loses
  gated tools until the hook is removed from settings — that is the point,
  and the escape hatch (remove the settings entry) is explicit.

KEY HANDLING
------------
- ``author`` mode needs a **user/owner-scoped** key: authoring REPLACES the
  org's ONE active agent-policy gate (don't run it in an org whose gate
  another workload depends on). Platform-scoped keys are query-only and
  receive 403 from authoring.
- ``hook`` mode: set ``GATE_PLATFORM_ID`` to skip the ``status()`` lookup
  entirely (a platform-scoped key gets a *redacted* status — no platform id —
  so with the env var set, hook mode calls only ``authorize_action``). A
  platform-scoped key bound to the gate platform is the least-privilege
  credential for hook mode.
- Key resolution: ``AMBERTRACE_API_KEY`` env, falling back to ``.env`` in the
  hook's ``cwd``.

LIVE RESULTS (deploy 7cee1fe2a17d, SDK 2.1.0)
---------------------------------------------
- Compile: 0 findings; ``input_fields`` typed exactly as written (``tool``
  enum + 4 booleans); ``admitted_controls`` read-back present, including the
  named controls (``no_secrets_touched``, ``no_force_used``, ...).
- 12/12 probes decided as policy requires, every verdict
  ``proof_checked=True`` (3 permits incl. the feature-branch push; 9 denies
  incl. push-to-main, --force, .env/.ssh/.aws reads, /etc/hosts write,
  rm outside the workspace).
- Hook exit codes: permit case exits 0; deny case exits 2 with the proven
  requirement on stderr; an invalid key exits 2 (fail-closed).
- Sample deny fed back to the model:
  ``Blocked by the Agent Policy Gate (decision='deny', proof_checked=True):
  Action pushes to a protected branch. ... Propose an action within policy
  instead.``

CAVEATS (honest)
----------------
1. **Org-singleton gate**: ``author`` claims the org's one active gate.
2. **Latency**: one ``authorize_action`` round trip (~0.5–2 s) per gated
   tool call.
3. **Fail-closed availability trade-off**: an unreachable gate blocks gated
   tools (see the hook contract above).
4. The Claude Code hook API used here (exit 0 allow / 2 block + stderr) is
   the stable documented contract.

Run with --help for options.

    python 59_claude_code_policy_gate_hook.py author
    echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' \\
        | python 59_claude_code_policy_gate_hook.py hook
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The gate's Decision Table, declared explicitly (it is the product's default binary table, so
# nothing is left for the platform to infer): `permit` is the default outcome when no obligation
# is violated; `deny` blocks. `permits` says whether the action may proceed; a gate table is a
# ladder with at least one permitting and one non-permitting row.
DECISION_TABLE = {
    "mode": "ladder",
    "rows": [
        {"label": "deny", "order": 2, "permits": False},
        {"label": "permit", "order": 1, "default": True, "permits": True},
    ],
}

# The coding-agent policy, authored in plain English. Deliberately inside the
# known-clean compile shapes: an enum allowlist (tool) + four boolean flags.
POLICY = (
    "A coding agent proposes actions. Each action has a tool, a "
    "pushes_to_protected_branch flag, a touches_secrets flag, an "
    "inside_workspace flag, and a uses_force flag. Only allow actions whose "
    "tool is bash, read, edit, or write. Permit an action only when the "
    "inside_workspace flag is true, the pushes_to_protected_branch flag is "
    "false, the touches_secrets flag is false, and the uses_force flag is "
    "false."
)

# ---------------------------------------------------------------------------
# Fact derivation — TRUSTED HARNESS CODE (illustrative, not exhaustive)
# ---------------------------------------------------------------------------

SECRET_PAT = re.compile(
    r"(\.env\b|\.ssh\b|id_rsa|\.aws\b|credentials|secrets?\.(json|ya?ml|toml)"
    r"|_API_KEY)",
    re.IGNORECASE)
PUSH_PROTECTED_PAT = re.compile(r"\bgit\b[^|;&]*\bpush\b[^|;&]*\b(main|master)\b")
FORCE_PAT = re.compile(r"\bgit\b[^|;&]*\bpush\b[^|;&]*(\s--force\b|\s-f\b)")
OUTSIDE_PAT = re.compile(r"(^|\s)(rm|mv|cp|chmod|chown)\s[^|;&]*(\s/|\s~\/)")


def derive_facts(tool_name: str, tool_input: dict, cwd: str) -> dict:
    """The model's raw proposal in, typed facts out.

    The regexes are illustrative — the guarantee is the PROVED verdict over
    whatever facts are supplied; extend the derivation for your threat model.
    """
    tool = {"Bash": "bash", "Read": "read", "Edit": "edit", "Write": "write"}.get(
        tool_name, tool_name.lower())
    command = tool_input.get("command", "") if tool == "bash" else ""
    path = tool_input.get("file_path", "")

    inside = True
    if path:
        try:
            inside = Path(path).resolve().is_relative_to(
                Path(cwd or ".").resolve())
        except (OSError, ValueError):
            inside = False
    if command and OUTSIDE_PAT.search(command):
        inside = False

    return {
        "tool": tool,
        "pushes_to_protected_branch": bool(
            command and PUSH_PROTECTED_PAT.search(command)),
        "touches_secrets": bool(SECRET_PAT.search(command or path)),
        "inside_workspace": inside,
        "uses_force": bool(command and FORCE_PAT.search(command)),
    }


# ---------------------------------------------------------------------------
# Hook mode — the PreToolUse entry point (exit 0 allow / exit 2 block)
# ---------------------------------------------------------------------------

def _hook_env_key(cwd: str) -> str:
    """AMBERTRACE_API_KEY from the environment, else from ``cwd``/.env."""
    key = os.environ.get("AMBERTRACE_API_KEY")
    if key:
        return key
    env_path = Path(cwd or ".") / ".env"
    if env_path.exists():
        for raw in env_path.read_text().splitlines():
            line = raw.strip()
            if line.startswith("AMBERTRACE_API_KEY") and "=" in line:
                return line.partition("=")[2].strip().strip('"').strip("'")
    raise KeyError("AMBERTRACE_API_KEY not set (env or <cwd>/.env)")


def run_hook() -> int:
    """PreToolUse contract: exit 0 = allow; exit 2 = block, stderr to the model.

    FAIL-CLOSED by construction: the ONLY exit-0 path requires a verdict with
    ``decision == "permit"`` AND a checked proof. Every exception lands in the
    except-arm and blocks.
    """
    from ambertraceai import AmbertraceAPI
    try:
        payload = json.load(sys.stdin)
        cwd = payload.get("cwd") or os.getcwd()
        facts = derive_facts(payload.get("tool_name", ""),
                             payload.get("tool_input") or {}, cwd)
        api = AmbertraceAPI(
            base_url=os.environ.get("AMBERTRACE_BASE_URL",
                                    "https://app.ambertrace.ai"),
            api_key=_hook_env_key(cwd), timeout=60.0)
        try:
            # With GATE_PLATFORM_ID set, hook mode calls ONLY authorize_action
            # — required for a platform-scoped key, whose status() is redacted
            # (no platform id in it).
            pid_env = os.environ.get("GATE_PLATFORM_ID")
            if pid_env:
                pid = int(pid_env)
            else:
                pid = (api.agent_policy.status().get("platform") or {}).get("id")
            tool = facts.pop("tool")
            verdict = api.agent_policy.authorize_action(pid, tool=tool, args=facts)
        finally:
            api.close()
    except Exception as exc:  # fail-closed: no proof, no tool call
        print(f"policy gate unreachable — blocking (fail-closed): {exc}",
              file=sys.stderr)
        return 2
    if verdict.get("decision") == "permit" and verdict.get("proof_checked"):
        return 0
    print("Blocked by the Agent Policy Gate "
          f"(decision={verdict.get('decision')!r}, "
          f"proof_checked={verdict.get('proof_checked')}): "
          f"{verdict.get('denied_reason') or 'not certifiable within policy'}. "
          f"Derived facts: {dict(facts, tool=tool)}. "
          "Propose an action within policy instead.",
          file=sys.stderr)
    return 2


# ---------------------------------------------------------------------------
# Author mode — compile the policy, read it back, self-score the probe matrix
# ---------------------------------------------------------------------------

# (description, tool_name, tool_input, expected decision) — 12 canned tool
# calls through the SAME fact derivation as the hook. WORKSPACE is replaced
# with the current directory at run time.
PROBES = [
    ("ls in the workspace", "Bash", {"command": "ls -la src/"}, "permit"),
    ("run the tests", "Bash", {"command": "pytest -q"}, "permit"),
    ("push a feature branch", "Bash",
     {"command": "git push -u origin feat/thing"}, "permit"),
    ("push to main", "Bash", {"command": "git push origin main"}, "deny"),
    ("push to master via upstream", "Bash",
     {"command": "git push upstream master"}, "deny"),
    ("force-push a branch", "Bash",
     {"command": "git push --force origin feat/thing"}, "deny"),
    ("cat the .env", "Bash", {"command": "cat .env"}, "deny"),
    ("read ssh keys", "Bash", {"command": "cat ~/.ssh/id_rsa"}, "deny"),
    ("edit a repo file", "Edit", {"file_path": "WORKSPACE/src/app.py"}, "permit"),
    ("write outside the workspace", "Write", {"file_path": "/etc/hosts"}, "deny"),
    ("write aws credentials", "Write",
     {"file_path": "WORKSPACE/.aws/credentials"}, "deny"),
    ("rm outside the workspace", "Bash", {"command": "rm -rf /tmp/other"}, "deny"),
]


def _print_compile(status: dict) -> None:
    """The compile read-back — confirm the gate admitted what you wrote."""
    print("  The gate reads back what it admitted — confirm it means what "
          "you wrote:")
    for c in status.get("admitted_controls", []):
        print(f"    + {c.get('name')}: {c.get('description')}")
    for r in status.get("rejected") or []:
        print(f"    - REJECTED {r.get('name')}: {r.get('reason')}")
    fields = [(f.get("name"), f.get("type"))
              for f in status.get("input_fields", [])]
    print(f"  input_fields: {fields}")
    findings = status.get("findings") or []
    print(f"  self-probe findings: {len(findings)}")
    for f in findings:
        print(f"    ! {f.get('severity')} {f.get('check')} -> {f.get('control')}")


def run_author(api, args: argparse.Namespace) -> None:
    print_section(1, 2, "Authoring the coding-agent policy (plain English in)")
    print(f"  POLICY:\n    {POLICY}\n")
    try:
        result = api.agent_policy.author(POLICY, decision_table=DECISION_TABLE)
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability), or your credentials lack write "
                  "authority over an existing org gate — skipping.")
            return
        raise
    pid = (result.get("platform") or {}).get("id")
    print(f"  active gate platform id = {pid}")
    print("  (authoring REPLACES the org's single agent-policy gate — see "
          "the docstring caveats)")
    _print_compile(api.agent_policy.status())

    print_section(2, 2, "Probing the gate (12 canned tool calls, hook-identical "
                        "fact derivation)")
    cwd = os.getcwd()
    correct = 0
    proof_checked = 0
    for label, tool_name, tool_input, expected in PROBES:
        tool_input = {k: v.replace("WORKSPACE", cwd)
                      for k, v in tool_input.items()}
        facts = derive_facts(tool_name, tool_input, cwd)
        tool = facts.pop("tool")
        v = api.agent_policy.authorize_action(pid, tool=tool, args=facts)
        ok = v.get("decision") == expected
        correct += ok
        proof_checked += bool(v.get("proof_checked"))
        mark = "OK" if ok else f"!! expected {expected}"
        print(f"  {label}\n    -> {str(v.get('decision')).upper():7s} [{mark}]  "
              f"proof_checked={v.get('proof_checked')}")
    print(f"\n  {correct}/{len(PROBES)} probes decided as policy requires; "
          f"{proof_checked}/{len(PROBES)} proof-checked.")
    print("\nDone. Wire the hook into Claude Code (.claude/settings.json — "
          "see the docstring) and every proposed Bash/Edit/Write call is "
          "proved against this policy before it runs; denies are fed back to "
          "the model so it can self-correct within policy.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Policy Gate — gate Claude Code's tool calls with a "
                    "proof-carrying PreToolUse hook (author once, then wire "
                    "'hook' into .claude/settings.json)")
    parser.add_argument(
        "mode", choices=["author", "hook"],
        help="author = compile + self-score the 12-probe matrix; "
             "hook = run as the Claude Code PreToolUse hook (stdin JSON)")
    add_common_args(parser)
    args = parser.parse_args()
    if args.mode == "hook":
        sys.exit(run_hook())
    run_demo(run_author, args)


if __name__ == "__main__":
    main()
