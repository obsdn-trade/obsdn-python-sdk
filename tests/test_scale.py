import pytest

from obsdn.sign.scale import scale_decimal_str
from obsdn.error import SignError


def test_integer_scales_18_zeros():
    assert scale_decimal_str("1") == 1_000_000_000_000_000_000
    assert scale_decimal_str("1500") == 1_500_000_000_000_000_000_000


def test_fractional_pads_to_18():
    assert scale_decimal_str("1.5") == 1_500_000_000_000_000_000
    assert scale_decimal_str("0.000000000000000001") == 1


def test_excess_fractional_truncates():
    assert scale_decimal_str("1.0000000000000000019") == 1_000_000_000_000_000_001


def test_rejects_signed():
    with pytest.raises(SignError):
        scale_decimal_str("-1")
    with pytest.raises(SignError):
        scale_decimal_str("+1")


def test_rejects_exponent():
    with pytest.raises(SignError):
        scale_decimal_str("1e3")


def test_rejects_empty():
    with pytest.raises(SignError):
        scale_decimal_str("")


def test_rejects_multiple_dots():
    with pytest.raises(SignError):
        scale_decimal_str("1.2.3")


def test_rejects_leading_dot():
    with pytest.raises(SignError):
        scale_decimal_str(".5")
    with pytest.raises(SignError):
        scale_decimal_str(".")


def test_leading_dot_well_formed():
    assert scale_decimal_str("0.5") == 500_000_000_000_000_000
