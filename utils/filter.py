import logging
import time

logger = logging.getLogger(__name__)


class SkaleFilterError(Exception):
    pass


class SkaleFilter:
    def __init__(self, event_class, from_block, argument_filters,
                 to_block='latest',
                 timeout=1, retries=10):
        self.event_class = event_class
        self.from_block = from_block
        self.argument_filters = argument_filters
        self.to_block = to_block
        self.timeout = timeout
        self.retries = retries
        self.web3_filter = self.create_filter()

    def create_filter(self):
        return self.event_class.createFilter(
            fromBlock=self.from_block,
            toBlock=self.to_block,
            argument_filters=self.argument_filters
        )

    def get_events(self):
        events = None
        for _ in range(self.retries):
            try:
                events = self.web3_filter.get_all_entries()
            except Exception as err:
                self.create_filter()
                time.sleep(self.timeout)
                logger.error(
                    f'Retrieving events from filter failed with {err}'
                )
            else:
                break

        if events is None:
            raise SkaleFilterError('Filter get_events timed out')
        return events
