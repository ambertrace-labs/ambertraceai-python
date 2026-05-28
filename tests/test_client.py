"""Tests for AmbertraceAPI client initialization."""

import pytest
from ambertraceai import AmbertraceAPI


class TestAmbertraceAPIClient:
    def test_init_sets_base_url(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test")
        assert api._http.base_url == "https://example.com"
        api.close()

    def test_init_sets_auth_header(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test")
        assert api._http.headers["authorization"] == "Bearer at_test"
        api.close()

    def test_init_missing_api_key_raises(self):
        with pytest.raises(ValueError, match="api_key"):
            AmbertraceAPI(base_url="https://example.com", api_key="")

    def test_init_missing_base_url_raises(self):
        with pytest.raises(ValueError, match="base_url"):
            AmbertraceAPI(base_url="", api_key="at_test")

    def test_domains_property_returns_resource(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test")
        from ambertraceai import DomainResource
        assert isinstance(api.domains, DomainResource)
        api.close()

    def test_datasets_property_returns_resource(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test")
        from ambertraceai import DatasetResource
        assert isinstance(api.datasets, DatasetResource)
        api.close()

    def test_platforms_property_returns_resource(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test")
        from ambertraceai import PlatformResource
        assert isinstance(api.platforms, PlatformResource)
        api.close()

    def test_predictions_property_returns_resource(self):
        api = AmbertraceAPI(base_url="https://example.com", api_key="at_test")
        from ambertraceai import PredictionResource
        assert isinstance(api.predictions, PredictionResource)
        api.close()

    def test_context_manager(self):
        with AmbertraceAPI(base_url="https://example.com", api_key="at_test") as api:
            assert api._http is not None

    def test_strips_trailing_slash_from_base_url(self):
        api = AmbertraceAPI(base_url="https://example.com/", api_key="at_test")
        assert str(api._http.base_url) == "https://example.com"
        api.close()
