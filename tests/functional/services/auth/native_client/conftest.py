import pytest

import globus_sdk


@pytest.fixture
def auth_client(no_retry_transport):
    class CustomAuthClient(globus_sdk.NativeAppAuthClient):
        transport_class = no_retry_transport

    return CustomAuthClient("dummy_client_id")
