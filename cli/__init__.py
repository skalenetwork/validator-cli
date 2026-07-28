__version__ = '1.3.3'

import collections
import collections.abc

# Python 3.10+ removed these aliases from the top-level collections module.
# Several transitive dependencies (sgx-py, web3 5.x) still import them from
# there, so we restore the aliases before any of those packages are loaded.
for _name in ('Mapping', 'MutableMapping', 'Callable', 'Iterable', 'Iterator',
              'MutableSequence', 'Sequence', 'MutableSet', 'Set',
              'Hashable', 'Sized', 'Container', 'Awaitable', 'Coroutine',
              'AsyncIterable', 'AsyncIterator', 'AsyncGenerator', 'Generator'):
    if not hasattr(collections, _name):
        setattr(collections, _name, getattr(collections.abc, _name))


if __name__ == "__main__":
    print(__version__)
