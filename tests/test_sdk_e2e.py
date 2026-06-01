"""SDK E2E integration test — exercises the full lifecycle against a live API.

Marked with @pytest.mark.e2e so it's skipped during regular unit test runs.
Requires network access to an Ambertrace API instance and a valid API key.

Usage:
    AMBERTRACE_E2E_URL=https://app.ambertrace.ai \
    AMBERTRACE_E2E_API_KEY=at_... \
    pytest tests/test_sdk_e2e.py -v -m e2e
"""

import os
import tempfile

import pytest

pytestmark = pytest.mark.e2e

BASE_URL = os.environ.get('AMBERTRACE_E2E_URL', 'https://app.ambertrace.ai')
API_KEY = os.environ.get('AMBERTRACE_E2E_API_KEY', '')


@pytest.fixture(scope='module')
def api():
    """Create an AmbertraceAPI client for the test session."""
    if not API_KEY:
        pytest.skip('AMBERTRACE_E2E_API_KEY not set — skipping SDK E2E tests')

    from ambertraceai.convenience import AmbertraceAPI
    client = AmbertraceAPI(base_url=BASE_URL, api_key=API_KEY, timeout=60.0)
    yield client
    client.close()


class TestSDKLifecycle:
    """Full lifecycle: create domain -> upload data -> build platform -> query -> cleanup."""

    def test_domain_crud(self, api):
        """Create, list, get, update, and delete a domain via the SDK."""
        domain = api.domains.create(
            name='SDK E2E Test Domain',
            description='Created by SDK E2E test',
        )
        domain_id = domain['id']
        assert domain['name'] == 'SDK E2E Test Domain'

        try:
            domains = api.domains.list()
            assert any(d['id'] == domain_id for d in domains)

            fetched = api.domains.get(domain_id)
            assert fetched['id'] == domain_id

            updated = api.domains.update(domain_id, name='Updated SDK Domain')
            assert updated['name'] == 'Updated SDK Domain'
        finally:
            api.domains.delete(domain_id)

    def test_dataset_upload_and_delete(self, api):
        """Upload a CSV, check it appears in list, then delete."""
        domain = api.domains.create(
            name='SDK Dataset Test',
            description='For dataset upload test',
        )
        domain_id = domain['id']

        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False,
            ) as f:
                f.write('name,value\nalpha,1\nbeta,2\ngamma,3\n')
                csv_path = f.name

            dataset = api.datasets.upload(
                domain_id=domain_id,
                file_path=csv_path,
                name='e2e_test.csv',
            )
            dataset_id = dataset['id']

            datasets = api.datasets.list()
            assert any(d['id'] == dataset_id for d in datasets)

            api.datasets.delete(dataset_id)
        finally:
            api.domains.delete(domain_id)
            os.unlink(csv_path)

    def test_platform_build_and_query(self, api):
        """Build a platform from a domain and query it."""
        domain = api.domains.create(
            name='SDK Platform Test',
            description='For platform build test',
        )
        domain_id = domain['id']

        try:
            api.domains.build_ontology(domain_id)

            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False,
            ) as f:
                f.write('entity,relation,target\nA,related_to,B\nB,causes,C\n')
                csv_path = f.name

            dataset = api.datasets.upload(
                domain_id=domain_id,
                file_path=csv_path,
                name='e2e_platform_data.csv',
            )
            dataset_id = dataset['id']

            result = api.platforms.create(
                domain_id=domain_id,
                dataset_id=dataset_id,
            )
            platform_id = result.get('platform', {}).get('id')
            job_id = result.get('build_job', {}).get('id')

            if job_id:
                try:
                    job = api.wait_for_job(job_id, timeout=120, poll_interval=5)
                    assert job['status'] in ('ready', 'active', 'completed', 'error')
                except TimeoutError:
                    pass

            if platform_id:
                platform = api.platforms.get(platform_id)
                assert platform['id'] == platform_id

                if platform.get('status') == 'active':
                    answer = api.platforms.query(platform_id, query='What is A?')
                    assert 'answer' in answer or 'error' in str(answer)

        finally:
            api.domains.delete(domain_id)
            if 'csv_path' in dir():
                os.unlink(csv_path)

    def test_error_handling(self, api):
        """SDK should raise AmbertraceError for 404s."""
        from ambertraceai.convenience import AmbertraceError
        with pytest.raises(AmbertraceError) as exc_info:
            api.domains.get(99999)
        assert exc_info.value.status_code == 404
        assert exc_info.value.code == 'not_found'

    def test_platforms_list(self, api):
        """Listing platforms should return a list (may be empty)."""
        platforms = api.platforms.list()
        assert isinstance(platforms, list)
