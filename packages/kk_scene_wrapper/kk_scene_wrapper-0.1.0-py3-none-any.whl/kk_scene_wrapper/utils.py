import re
from typing import Generator, Iterable, Optional, Tuple


def int_to_bytes(number: int) -> bytes:
    # Calculate the minimum number of bytes required to represent the integer
    min_bytes = (number.bit_length() + 7) // 8
    # Convert the integer to a big-endian byte string of the minimum length
    return number.to_bytes(min_bytes, byteorder="big")


def flag_to_int_array(flag: bytes) -> Tuple[int, int]:
    return int.from_bytes(flag[0:1], byteorder="big"), int.from_bytes(
        flag[1:], byteorder="big"
    )


def sfx_terms() -> "Generator[bytes]":
    for term in ("sound", "audio", "voice", "moan"):
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")
    for term in ["3DSE"]:
        yield term.encode("utf-8")


def sfx_extra_terms() -> "Generator[bytes]":
    for term in ["sfx"]:
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")
    for term in ("SE", "VA"):
        yield term.encode("utf-8")


def animation_terms() -> "Generator[bytes]":
    for term in ("animation", "motion", "move"):
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")


def body_terms() -> "Generator[bytes]":
    for term in (
        "body",
        "hips",
        "waist",
        "chest",
        "thigh",
        "head",
        "neck",
        "shoulder",
        "hand",
        "finger",
        "knee",
        "foot",
        "elbow",
    ):
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")


def body_extra_terms() -> "Generator[bytes]":
    for term in ("arm", "leg"):
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")


def make_terms_regex(terms: "Iterable[bytes]") -> "re.Pattern":
    # For a term to be considered "found" it must be surrounded by non-ASCII characters or spaces
    return re.compile(
        rb"(?<=[\x00-\x1F\x7F-\x9F])("
        + b"|".join(re.escape(term) for term in terms)
        + rb")(?=[\x00-\x1F\x7F-\x9F])",
    )


