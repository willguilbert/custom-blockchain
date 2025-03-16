import hashlib

from tp2.transaction import Transaction
from tp2.crypto import PublicKey


class Block:
    """
    Représente un bloc de la chaîne de blocs.

    Attributes:
        prev_block_hash (bytes): Hash du bloc précédent.
        coinbase (Transaction): Transaction coinbase.
        transactions (list): Ensemble de transactions du bloc.
        hash (bytes): hash du bloc.
    """

    COINBASE: float = 25.0  # Récompense de bloc

    def __init__(self, address: PublicKey, prev_block_hash: bytes = None):
        """
        Args:
            address (PublicKey): L'adresse à laquelle la transaction coinbase sera attribuée.
            prev_block_hash (bytes, optional): Hash du bloc précédent. None s'il s'agit du bloc de genèse.
        """
        self.prev_block_hash: bytes | None = prev_block_hash
        self.coinbase: Transaction = Transaction.create_coinbase(self.COINBASE, address)
        self.transactions: list[Transaction] = []
        self.hash: bytes | None = None  # le hash du bloc lui-même

    def get_transaction(self, index: int) -> Transaction:
        """Renvoie la transaction du bloc se trouvant à l'index <index>."""
        return self.transactions[index]

    def add_transaction(self, tx: Transaction) -> None:
        """Ajoute une nouvelle transaction <tx> au bloc."""
        self.transactions.append(tx)

    def to_bytes(self) -> bytes:
        """Renvoie une représentation en bytes du bloc."""
        raw_block: bytes = b""

        if self.prev_block_hash is not None:
            raw_block += self.prev_block_hash

        for transaction in self.transactions:
            raw_block += transaction.to_bytes()

        return raw_block

    def finalize(self) -> None:
        """Finalise le bloc en lui assignant un hash."""
        self.hash = hashlib.sha256(self.to_bytes()).digest()
