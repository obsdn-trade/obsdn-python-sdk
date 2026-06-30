from obsdn.auth import sign_hmac


def test_matches_go_hmac_format():
    body = b'{"symbol":"BTC-USD","side":"buy"}'
    got = sign_hmac(b"my-secret-key", "1234567890", "POST", "/v1/orders", body)
    assert got == "VNdJ7rUFSZvZN2gTGoo/Vz7MQ1S/FEf2GMbgp3fQ+ow="


def test_empty_body():
    got = sign_hmac(b"k", "9", "GET", "/x", b"")
    assert got == "/oo/kZ+guDSuEi/9eOA7ZRkh7ZKNkKzFOUBF2LSJVK4="


def test_place_order_golden():
    got = sign_hmac(b"abc123", "1705929600", "POST", "/orders", b'{"mktId":"BTC-PERP"}')
    assert got == "zlFN4lQ5q7qFbn/cmVoPnX4lGiaFuFgMmp6baRDy/9E="


def test_lowercase_method_normalized():
    s1 = sign_hmac(b"k", "1", "post", "/p", b"x")
    s2 = sign_hmac(b"k", "1", "POST", "/p", b"x")
    assert s1 == s2
