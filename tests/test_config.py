from backend.app.core.config import settings


def test_configuration():
    print("\n===== CONFIGURATION TEST =====")

    print(
        "Database URL configured:",
        bool(settings.database_url)
    )

    print(
        "Algorithm:",
        settings.algorithm
    )

    print(
        "Access token expiry:",
        settings.access_token_expire_minutes
    )

    assert settings.database_url
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30

    print("\nConfiguration test passed.")


if __name__ == "__main__":
    test_configuration()