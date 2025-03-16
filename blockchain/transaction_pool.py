from __future__ import annotations

from blockchain.transaction import Transaction


class TransactionPool:
    def __init__(self):
        self.pool: dict[bytes, Transaction] = {}

    def add_transaction(self, tx: Transaction) -> None:
        self.pool[tx.hash] = tx

    def remove_transaction(self, tx_hash: bytes) -> None:
        self.pool.pop(tx_hash)

    def get_transaction(self, tx_hash: bytes) -> Transaction | None:
        return self.pool.get(tx_hash)

    def get_transactions(self) -> list[Transaction]:
        return list(self.pool.values())
