class UTXO:
    def __init__(self, tx_hash: bytes, index: int):
        """Crée un nouvel UTXO correspondant à la sortie avec l'index <index>
        de la transaction dont le hash est <tx_hash>."""
        # Hash de la transaction à l'origine de cet UTXO
        self.tx_hash = tx_hash

        # Index de la sortie correspondante à ladite transaction
        self.index = index

    def __hash__(self):
        return hash((self.tx_hash, self.index))

    def __eq__(self, other):
        return (self.tx_hash, self.index) == (other.tx_hash, other.index)

    def __ne__(self, other):
        return not (self == other)
