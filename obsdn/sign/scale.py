from __future__ import annotations

from obsdn.error import SignError

DECIMALS = 18


def scale_decimal_str(s: str) -> int:
    """Scale a decimal string by 10^18, truncating toward zero.

    Accepts integer literals ("1", "1500"), decimal fractions ("1.5", "0.000001"),
    and long fractions where excess digits are truncated.
    Rejects signed values, exponent notation, leading dots, and multiple dots.
    """
    if not s:
        raise SignError("empty decimal")
    if s[0] in ("+", "-"):
        raise SignError(f"signed decimal not allowed: {s}")

    if "." in s:
        parts = s.split(".")
        if len(parts) != 2:
            raise SignError(f"malformed decimal: {s}")
        int_part, frac_part = parts
    else:
        int_part, frac_part = s, ""

    if not int_part:
        raise SignError(f"decimal must have an integer part: {s}")

    if not int_part.isdigit() or (frac_part and not frac_part.isdigit()):
        raise SignError(f"non-digit in decimal: {s}")

    if len(frac_part) >= DECIMALS:
        padded = int_part + frac_part[:DECIMALS]
    else:
        padded = int_part + frac_part + "0" * (DECIMALS - len(frac_part))

    try:
        return int(padded)
    except ValueError as e:
        raise SignError(f"scaled value overflows: {s} ({e})") from e
