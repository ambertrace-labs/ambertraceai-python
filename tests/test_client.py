"""Tests for AmbertraceAPI client initialization."""

import pytest
from ambertraceai import AmbertraceAPI


class TestAmbertraceAPIClient:
    def test_init_sets_base_url(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test", warm=False)
        assert api._http.base_url == "https://example.com"
        api.close()

    def test_init_sets_auth_header(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test", warm=False)
        assert api._http.headers["authorization"] == "Bearer at_test"
        api.close()

    def test_init_missing_api_key_raises(self, monkeypatch):
        # With no explicit key and no env key, construction fails closed.
        monkeypatch.delenv("AMBERTRACE_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key"):
            AmbertraceAPI(base_url="https://example.com", api_key="")

    def test_init_missing_base_url_falls_back_to_default(self, monkeypatch):
        # base_url is now optional — an unset base_url (no env override) falls
        # back to the production endpoint rather than raising (item 7).
        monkeypatch.delenv("AMBERTRACE_BASE_URL", raising=False)
        api = AmbertraceAPI(base_url="", api_key="at_test", warm=False)
        assert str(api._http.base_url) == "https://app.ambertrace.ai"
        api.close()

    def test_domains_property_returns_resource(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test", warm=False)
        from ambertraceai import DomainResource
        assert isinstance(api.domains, DomainResource)
        api.close()

    def test_datasets_property_returns_resource(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test", warm=False)
        from ambertraceai import DatasetResource
        assert isinstance(api.datasets, DatasetResource)
        api.close()

    def test_platforms_property_returns_resource(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test", warm=False)
        from ambertraceai import PlatformResource
        assert isinstance(api.platforms, PlatformResource)
        api.close()

    def test_predictions_property_returns_resource(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test", warm=False)
        from ambertraceai import PredictionResource
        assert isinstance(api.predictions, PredictionResource)
        api.close()

    def test_context_manager(self):
        with AmbertraceAPI(base_url="https://example.com", api_key="at_test", warm=False) as api:
            assert api._http is not None

    def test_strips_trailing_slash_from_base_url(self):
        api = AmbertraceAPI(base_url="https://example.com/", api_key="at_test", warm=False)
        assert str(api._http.base_url) == "https://example.com"
        api.close()


class TestWrongApiHost:
    @pytest.mark.parametrize("bad_url", [
        "https://api.ambertrace.ai",
        "http://api.ambertrace.ai",
        "https://api.ambertrace.ai/",
        "https://API.Ambertrace.AI",       # case-insensitive
        "https://api.ambertrace.ai:443",   # explicit port
        "api.ambertrace.ai",               # no scheme
    ])
    def test_wrong_api_host_raises(self, bad_url):
        with pytest.raises(ValueError, match="app.ambertrace.ai"):
            AmbertraceAPI(base_url=bad_url, api_key="at_test", warm=False)

    def test_correct_app_host_constructs(self):
        api = AmbertraceAPI(base_url="https://app.ambertrace.ai", api_key="at_test", warm=False)
        assert str(api._http.base_url) == "https://app.ambertrace.ai"
        api.close()

    def test_arbitrary_custom_host_constructs(self):
        # A self-hosted / custom endpoint is NOT the known-wrong host — allowed.
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test", warm=False)
        assert str(api._http.base_url) == "https://example.com"
        api.close()
