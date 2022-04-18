from dataclasses import dataclass
from typing import Optional


@dataclass
class TxFee:
    gas_price: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    max_fee_per_gas: Optional[int] = None

    def __str__(self) -> str:
        if self.max_priority_fee_per_gas:
            return '[Fee] ' \
                   f'maxFeePerGas: {self.max_fee_per_gas} ' \
                   f'maxPriorityFeePerGas: {self.max_priority_fee_per_gas}'
        else:
            return f'[Fee] gasPrice: {self.gas_price}'
