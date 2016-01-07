"""Unit tests for mbedtls.md."""

# Disable checks for violations that are acceptable in tests.
# pylint: disable=missing-docstring
# pylint: disable=attribute-defined-outside-init
# pylint: disable=invalid-name
from functools import partial
import hashlib
import hmac

from nose.tools import assert_equal

# pylint: disable=import-error
from mbedtls._md import MD_NAME
import mbedtls.hash as md_hash
import mbedtls.hmac as md_hmac
# pylint: enable=import-error

from . import _rnd


def make_chunks(buffer, size):
    for i in range(0, len(buffer), size):
        yield buffer[i:i+size]


def test_make_chunks():
    buffer = _rnd(1024)
    assert_equal(b"".join(buf for buf in make_chunks(buffer, 100)),
                 buffer)


def test_md_list():
    assert len(MD_NAME) == 10


def test_algorithms():
    assert set(md_hash.algorithms_guaranteed).issubset(
        md_hash.algorithms_available)


def test_copy_hash():
    for name in md_hash.algorithms_available:
        buf0 = _rnd(512)
        buf1 = _rnd(512)
        alg = md_hash.new(name, buf0)
        copy = alg.copy()
        alg.update(buf1)
        copy.update(buf1)
        # Use partial to have the correct name in failed reports (by
        # avoiding late bindings).
        test = partial(assert_equal, alg.digest(), copy.digest())
        test.description = "test_copy_hash(%s)" % name
        yield test


def test_check_hexdigest_against_hashlib():
    for name in md_hash.algorithms_available:
        buf = _rnd(1024)
        alg = md_hash.new(name, buf)
        ref = hashlib.new(name, buf)
        test = partial(assert_equal, alg.hexdigest(), ref.hexdigest())
        test.description = "check_hexdigest_against_hashlib(%s)" % name
        yield test


def test_check_against_hashlib_nobuf():
    for name in md_hash.algorithms_available:
        buf = _rnd(1024)
        alg = md_hash.new(name, buf)
        ref = hashlib.new(name, buf)
        test = partial(assert_equal, alg.digest(), ref.digest())
        test.description = "check_against_hashlib_nobuf(%s)" % name
        yield test


def test_check_against_hashlib_buf():
    for name in md_hash.algorithms_available:
        buf = _rnd(4096)
        alg = md_hash.new(name)
        ref = hashlib.new(name)
        for chunk in make_chunks(buf, 500):
            alg.update(chunk)
            ref.update(chunk)
        test = partial(assert_equal, alg.digest(), ref.digest())
        test.description = "check_against_hashlib_buf(%s)" % name
        yield test


def test_check_against_hmac_nobuf():
    for name in md_hmac.algorithms_available:
        buf = _rnd(1024)
        key = _rnd(16)
        alg = md_hmac.new(key, buf, digestmod=name)
        ref = hmac.new(key, buf, digestmod=name)
        # Use partial to have the correct name in failed reports (by
        # avoiding late bindings).
        test = partial(assert_equal, alg.digest(), ref.digest())
        test.description = "check_against_hmac_nobuf(%s)" % name
        yield test


def test_check_against_hmac_buf():
    for name in md_hmac.algorithms_available:
        buf = _rnd(4096)
        key = _rnd(16)
        alg = md_hmac.new(key, digestmod=name)
        ref = hmac.new(key, digestmod=name)
        for chunk in make_chunks(buf, 500):
            alg.update(chunk)
            ref.update(chunk)
        test = partial(assert_equal, alg.digest(), ref.digest())
        test.description = "check_against_hmac_buf(%s)" % name
        yield test


def test_instantiation():
    import inspect

    def check_instantiation(fun, name):
        alg1 = fun()
        alg2 = md_hash.new(name)
        assert_equal(type(alg1), type(alg2))
        assert_equal(alg1.name, alg2.name)

    for name, member in inspect.getmembers(md_hash):
        if name in md_hash.algorithms_available:
            test = partial(check_instantiation, member, name)
            test.description = "check_instantiation(%s)" % name
            yield test
