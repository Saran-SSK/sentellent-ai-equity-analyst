from datetime import date, timedelta

from app.providers.finnhub_provider import finnhub_provider


def test_company_news():
    today = date.today()
    week_ago = today - timedelta(days=7)

    news = finnhub_provider.get_company_news(
        symbol="AAPL",
        from_date=week_ago.isoformat(),
        to_date=today.isoformat(),
    )

    print(news)

    assert isinstance(news, list)
    assert len(news) > 0
