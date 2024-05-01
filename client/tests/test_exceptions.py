import pytest

from pyroclient.exceptions import HTTPRequestException


@pytest.mark.parametrize(
    ("status_code", "response_msg", "expected_repr"),
    [
        (404, "not found", "HTTPRequestException(status_code=404, response_message='not found')"),
        (502, "internal error", "HTTPRequestException(status_code=502, response_message='internal error')"),
    ],
)
def test_httprequestexception(status_code, response_msg, expected_repr):
    exception = HTTPRequestException(status_code, response_msg)
    assert repr(exception) == expected_repr
