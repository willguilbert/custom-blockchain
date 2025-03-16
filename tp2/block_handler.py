from tp2.blockchain import Blockchain
from tp2.block import Block
from tp2.crypto import PublicKey
from tp2.transaction import Transaction
from tp2.transaction_handler import TransactionHandler
from tp2.transaction_pool import TransactionPool
from tp2.utxo_pool import UTXOPool


class BlockHandler:
    def __init__(self, blockchain: Blockchain):
        """Suppose que la blockchain <blockchain> a un bloc de genèse."""
        self.blockchain: Blockchain = blockchain

    def process_block(self, block: Block) -> bool:
        """
        Ajoute un bloc à la chaîne de blocs s'il est valide.

        Args:
            block (Block): Bloc à ajouter à la chaîne de blocs.

        Returns:
            bool: True si le bloc est valide et a été ajouté à la chaîne de blocs, False sinon.
        """
        return self.blockchain.add_block(block)

    def create_block(self, address: PublicKey) -> Block | None:
        """Crée un nouveau bloc sur le bloc de hauteur maximale"""
        parent: Block = self.blockchain.get_max_height_block()
        assert parent.hash is not None, "Bloc parent invalide!"
        parent_hash: bytes = parent.hash
        current: Block = Block(address, parent_hash)
        utxo_pool: UTXOPool = self.blockchain.get_max_height_utxo_pool()
        tx_handler: TransactionHandler = TransactionHandler(utxo_pool)
        transaction_pool: TransactionPool = self.blockchain.tx_pool
        transactions: list[Transaction] = transaction_pool.get_transactions()
        valid_txs: list[Transaction] = tx_handler.handle_transactions(transactions)

        # valider et ajouter toutes les transactions
        for transaction in valid_txs:
            current.add_transaction(transaction)

        current.finalize()

        return current if self.blockchain.add_block(current) else None

    def process_transaction(self, transaction: Transaction) -> None:
        """Traite une transaction"""
        self.blockchain.add_transaction(transaction)
