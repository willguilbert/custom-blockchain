from blockchain.crypto import PublicKey
from blockchain.blockchain import Blockchain


def get_balance(blockchain: Blockchain, pk: PublicKey) -> float:
    """Retourne le solde associé à l'adresse <pk>."""
    # TODO: Votre code ici
    utxoPool = blockchain.get_max_height_utxo_pool()
    balance = 0
    for utxo in utxoPool.get_all_utxo():
        output = utxoPool.get_tx_output(utxo)
        if output.address == pk:
            balance += output.value
    return balance
