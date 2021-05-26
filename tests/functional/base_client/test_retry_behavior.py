import pytest
import requests
import responses

import globus_sdk


@pytest.mark.parametrize("error_status", [500, 429, 502, 503, 504])
def test_retry_on_transient_error(client, mocksleep, error_status):
    responses.add(
        responses.GET,
        "https://foo.api.globus.org/bar",
        status=error_status,
        body="Uh-oh!",
    )
    responses.add(responses.GET, "https://foo.api.globus.org/bar", body='{"baz": 1}')

    # no sign of an error in the client
    res = client.get("/bar")
    assert res.http_status == 200
    assert res["baz"] == 1

    # there was a sleep (retry was triggered)
    mocksleep.assert_called_once()


def test_retry_on_network_error(client, mocksleep):
    # set the response to be a requests NetworkError -- responses will raise the
    # exception when the call is made
    responses.add(
        responses.GET,
        "https://foo.api.globus.org/bar",
        body=requests.ConnectionError("foo-err"),
    )
    responses.add(responses.GET, "https://foo.api.globus.org/bar", body='{"baz": 1}')

    # no sign of an error in the client
    res = client.get("/bar")
    assert res.http_status == 200
    assert res["baz"] == 1

    # there was a sleep (retry was triggered)
    mocksleep.assert_called_once()


@pytest.mark.parametrize("num_errors,expect_err", [(5, False), (6, True)])
def test_retry_limit(client, mocksleep, num_errors, expect_err):
    # N errors followed by a success
    for _i in range(num_errors):
        responses.add(
            responses.GET, "https://foo.api.globus.org/bar", status=500, body="Uh-oh!"
        )
    responses.add(responses.GET, "https://foo.api.globus.org/bar", body='{"baz": 1}')

    if expect_err:
        with pytest.raises(globus_sdk.GlobusAPIError):
            client.get("/bar")

        assert mocksleep.call_count < num_errors
    else:
        # no sign of an error in the client
        res = client.get("/bar")
        assert res.http_status == 200
        assert res["baz"] == 1

        assert mocksleep.call_count == num_errors


def test_no_retry_401_no_authorizer(client):
    responses.add(
        responses.GET, "https://foo.api.globus.org/bar", status=401, body="Unauthorized"
    )
    responses.add(responses.GET, "https://foo.api.globus.org/bar", body='{"baz": 1}')

    # error gets raised in client (no retry)
    with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
        client.get("/bar")
    assert excinfo.value.http_status == 401


def test_retry_with_authorizer(client):
    responses.add(
        responses.GET, "https://foo.api.globus.org/bar", status=401, body="Unauthorized"
    )
    responses.add(responses.GET, "https://foo.api.globus.org/bar", body='{"baz": 1}')

    # an authorizer class which does nothing but claims to support handling of
    # unauthorized errors
    dummy_authz_calls = []

    class DummyAuthorizer(globus_sdk.authorizers.GlobusAuthorizer):
        def set_authorization_header(self, headers):
            dummy_authz_calls.append("set_authz")

        def handle_missing_authorization(self):
            dummy_authz_calls.append("handle_missing")
            return True

    authorizer = DummyAuthorizer()
    client.authorizer = authorizer

    # no sign of an error in the client
    res = client.get("/bar")
    assert res.http_status == 200
    assert res["baz"] == 1

    # ensure that setting authz was called twice (once for each request)
    # and that between the two calls, handle_missing_authorization was called once
    assert dummy_authz_calls == ["set_authz", "handle_missing", "set_authz"]


def test_no_retry_with_authorizer_no_handler(client):
    responses.add(
        responses.GET, "https://foo.api.globus.org/bar", status=401, body="Unauthorized"
    )
    responses.add(responses.GET, "https://foo.api.globus.org/bar", body='{"baz": 1}')

    # an authorizer class which does nothing and does not claim to handle
    # unauthorized errors
    dummy_authz_calls = []

    class DummyAuthorizer(globus_sdk.authorizers.GlobusAuthorizer):
        def set_authorization_header(self, headers):
            dummy_authz_calls.append("set_authz")

        def handle_missing_authorization(self):
            dummy_authz_calls.append("handle_missing")
            return False

    authorizer = DummyAuthorizer()
    client.authorizer = authorizer

    # error gets raised in client (no retry)
    with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
        client.get("/bar")
    assert excinfo.value.http_status == 401

    # only two calls, single setting of authz and a call to ask about handling the error
    assert dummy_authz_calls == ["set_authz", "handle_missing"]


def test_retry_with_authorizer_persistent_401(client):
    responses.add(
        responses.GET, "https://foo.api.globus.org/bar", status=401, body="Unauthorized"
    )
    responses.add(
        responses.GET, "https://foo.api.globus.org/bar", status=401, body="Unauthorized"
    )
    responses.add(responses.GET, "https://foo.api.globus.org/bar", body='{"baz": 1}')

    # an authorizer class which does nothing but claims to support handling of
    # unauthorized errors
    dummy_authz_calls = []

    class DummyAuthorizer(globus_sdk.authorizers.GlobusAuthorizer):
        def set_authorization_header(self, headers):
            dummy_authz_calls.append("set_authz")

        def handle_missing_authorization(self):
            dummy_authz_calls.append("handle_missing")
            return True

    authorizer = DummyAuthorizer()
    client.authorizer = authorizer

    # the error gets raised in this case because it persists -- the authorizer only gets
    # one chance to resolve the issue
    with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
        client.get("/bar")
    assert excinfo.value.http_status == 401

    # ensure that setting authz was called twice (once for each request)
    # and that between the two calls, handle_missing_authorization was called once
    # but the handler should not be called a second time because the 401 repeated
    assert dummy_authz_calls == ["set_authz", "handle_missing", "set_authz"]
