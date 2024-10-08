class Config:
    TEST_CASES = [
        {
            "article_text": "ETH Prices zooms 10 percent today while Bitcoin's price surged to $70,000 today, breaking all previous records. Analysts attribute this to increased institutional adoption and positive regulatory news from several countries.",
            "expected_classification": "RELEVANT",
        },
        {
            "article_text": "A new Tesla facility has opened in Texas, utilizing 100% renewable energy.",
            "expected_classification": "NOT RELEVANT",
        },
        # Add more test cases as needed
    ]

    LOCAL_AGENT_URL = "http://127.0.0.1:5000/"
