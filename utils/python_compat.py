"""Compatibility support for the legacy SKALE SDK dependency chain."""

import inspect
from collections import namedtuple
import warnings


def install_legacy_dependency_compatibility():
    """Install compatibility shims before importing the Web3 5.x stack."""
    # eth-abi 2.x requires parsimonious <0.9, which still imports getargspec.
    # Python 3.11 removed that API, so provide its compatible subset before
    # Web3 and the SKALE SDK load their ABI parser.
    if not hasattr(inspect, 'getargspec'):
        arg_spec = namedtuple('ArgSpec', 'args varargs keywords defaults')

        def getargspec(function):
            spec = inspect.getfullargspec(function)
            return arg_spec(spec.args, spec.varargs, spec.varkw, spec.defaults)

        inspect.getargspec = getargspec

    # The SKALE SDK currently depends on Web3 5.x, whose transitive packages
    # still import pkg_resources. Setuptools remains pinned below 81 until that
    # stack can be upgraded, so this warning is not actionable for CLI users.
    warnings.filterwarnings(
        'ignore',
        message=r'pkg_resources is deprecated as an API.*',
        category=UserWarning,
        module=r'^(eth_keyfile|eth_abi|web3)(\.|$)',
    )
