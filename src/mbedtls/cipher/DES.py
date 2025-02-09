# SPDX-License-Identifier: MIT
# Copyright (c) 2016, Elaborated Networks GmbH
# Copyright (c) 2019, Mathias Laurin

"""Data Encryption Standard (DES) cipher developed by IBM
in the 70's."""

import sys

if sys.version_info < (3, 8):
    from typing_extensions import Final, Literal
else:
    from typing import Final, Literal

from typing import Optional, Union

from mbedtls.exceptions import TLSError  # type: ignore

from ._cipher import Cipher, Mode

__all__ = ["block_size", "key_size", "new"]


block_size: Final = 8
key_size: Final = 8


def new(
    key: bytes,
    mode: Union[int, Literal[Mode.CBC, Mode.ECB]],
    iv: Optional[bytes] = None,
) -> Cipher:
    """Return a `Cipher` object that can perform DES encryption and
    decryption.

    Data Encryption Standard (DES) cipher developed by IBM in the 70's.

    Parameters:
        key: The key to encrypt decrypt.  If None,
            encryption and decryption are unavailable.
        mode: The mode of operation of the cipher.
        iv: The initialization vector (IV).  The IV is
            required for every mode but ECB and CTR where it is ignored.
            If not set, the IV is initialized to all 0, which should not
            be used for encryption.

    """
    mode_ = Mode(mode)
    if len(key) != key_size:
        raise TLSError(msg="key size must be 16 bytes, got %r" % len(key))
    if mode_ not in {Mode.CBC, Mode.ECB}:
        raise TLSError(msg="unsupported mode %r" % mode_)
    name = ("DES-%s" % mode_.name).encode("ascii")
    return Cipher(name, key, mode_, iv)
