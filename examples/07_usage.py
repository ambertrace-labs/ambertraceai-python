"""07 — Usage: check your API consumption.

Reports the account's API usage summary (requests, tokens, and any monthly
token budget). Read-only — creates nothing.

    python 07_usage.py
"""

from _common import banner, get_client, step


def main() -> None:
    api = get_client()
    banner("Usage summary")

    usage = api.usage.get()
    step(f"Period: last {usage.get('period_days')} days")
    step(f"Total requests: {usage.get('total_requests')}")
    step(f"Total tokens: {usage.get('total_tokens')}")
    step(f"Avg response time: {usage.get('avg_response_time_ms')} ms")

    budget = usage.get("token_budget", {})
    if budget.get("budget") is None:
        step("Token budget: unlimited")
    else:
        step(f"Token budget: {budget.get('remaining')} / {budget.get('budget')} remaining")

    print("\n✓ Usage report complete.")


if __name__ == "__main__":
    main()
