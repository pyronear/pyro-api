from app.api.external import post_request


def test_post_request():
    response = post_request("https://httpbin.org/post")
    assert response.status_code == 200
