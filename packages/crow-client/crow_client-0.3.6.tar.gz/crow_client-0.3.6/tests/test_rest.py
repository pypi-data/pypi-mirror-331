import os
import time
from unittest.mock import patch

import pytest
from crow_client.clients.rest_client import JobFetchError, RestClient
from crow_client.models.app import AuthType, Stage
from crow_client.utils.auth import AuthTokenCache, get_password_credentials

ADMIN_USER = os.environ["ADMIN_USER"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
PUBLIC_USER = os.environ["PUBLIC_USER"]
PUBLIC_PASSWORD = os.environ["PUBLIC_PASSWORD"]


def test_get_password_credentials():
    with (
        patch("builtins.input", return_value="test123@gmail.com"),
        patch("getpass.getpass", return_value="test456"),
    ):
        credentials = get_password_credentials()

        assert credentials.email == "test123@gmail.com"
        assert credentials.password.get_secret_value() == "test456"


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
def test_futurehouse_dummy_env_crow():
    with (
        patch("builtins.input", return_value=ADMIN_USER),
        patch("getpass.getpass", return_value=ADMIN_PASSWORD),
    ):
        client = RestClient(stage=Stage.DEV, auth_type=AuthType.PASSWORD)

        job_data = {
            "name": "job-futurehouse-dummy-env-dev",
            "query": "How many moons does earth have?",
        }
        client.create_job(job_data)

        while any(
            (job_status := j["status"]) in {"queued", "in progress"}
            for j in (
                [client.get_job()]
                if isinstance(client.get_job(), dict)
                else client.get_job()
            )
        ):
            time.sleep(5)

        assert job_status == "success"


@pytest.mark.timeout(30)
def test_insufficient_permissions_request():
    AuthTokenCache().clear()
    with (
        patch("builtins.input", return_value=PUBLIC_USER),
        patch("getpass.getpass", return_value=PUBLIC_PASSWORD),
    ):
        # Create a new instance so that cached credentials aren't reused
        client = RestClient(stage=Stage.DEV, auth_type=AuthType.PASSWORD)
        job_data = {
            "name": "job-futurehouse-dummy-env-dev",
            "query": "How many moons does earth have?",
        }

        with pytest.raises(JobFetchError) as exc_info:
            client.create_job(job_data)

        assert "Error creating job" in str(exc_info.value)
