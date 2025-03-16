from blockchain.crypto import PublicKey
from blockchain.blockchain import Blockchain


def get_balance(blockchain: Blockchain, pk: PublicKey) -> float:
    """Retourne le solde associé à l'adresse <pk>."""
    # TODO: Votre code ici
