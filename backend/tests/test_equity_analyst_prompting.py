from app.agents.equity_analyst import EquityAnalystAgent


def test_sanitize_response_removes_markdown_formatting() -> None:
    agent = EquityAnalystAgent()

    raw = "# Investment View\n\n**Bull case:** The company is attractive.\n\n- Revenue growth remains healthy.\n\n**Risks:** Execution remains the main concern."

    sanitized = agent._sanitize_response(raw)

    assert "# Investment View" not in sanitized
    assert "**Bull case:**" not in sanitized
    assert "**Risks:**" not in sanitized
    assert "Bull case:" in sanitized
    assert "Risks:" in sanitized
    assert "- Revenue growth remains healthy." in sanitized
