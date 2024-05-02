import pytest

from pyroclient.exceptions import HTTPRequestError


@pytest.mark.parametrize(
    ("status_code", "response_msg", "expected_repr"),
    [
        (404, "not found", "HTTPRequestError(status_code=404, response_message='not found')"),
        (502, "internal error", "HTTPRequestError(status_code=502, response_message='internal error')"),
    ],
)
def test_httprequesterror(status_code, response_msg, expected_repr):
    exception = HTTPRequestError(status_code, response_msg)
    assert repr(exception) == expected_repr
