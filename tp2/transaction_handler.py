from tp2.crypto import verify_signature
from tp2.transaction import Transaction
from tp2.utxo import UTXO
from tp2.utxo_pool import UTXOPool


class TransactionHandler:
    def __init__(self, utxo_pool: UTXOPool):
        """
        Crée un registre public dont le pool UTXO actuel est <utxo_pool>.
        Nous faisons une copie défensive de <utxo_pool> en utilisant le constructeur
        UTXOPool.from_utxo_pool(utxo_pool: UTXOPool).
        """
        self.utxo_pool: UTXOPool = UTXOPool.from_utxo_pool(utxo_pool)

    def is_valid_transaction(self, tx: Transaction) -> bool:
        """
        Renvoie True si
        (1) toutes les sorties réclamées par <tx> sont dans le pool UTXO actuel,
        (2) les signatures sur chaque entrée de <tx> sont valides,
        (3) aucun UTXO n'est réclamé plusieurs fois par <tx>,
        (4) toutes les valeurs de sortie de <tx> sont non négatives, et
        (5) la somme des valeurs d'entrée de <tx> est supérieure ou égale à la somme
        de ses valeurs de sortie ; et False sinon.
        """
        # TODO: Votre code ici

    def handle_transactions(self, possible_txs: list[Transaction]) -> list[Transaction]:
        """
        - Reçoit une liste de transactions proposées,
        - Vérifie l'exactitude de chaque transaction, et
        - Renvoie une liste de transactions valides acceptées
          tout en mettant à jour le pool UTXO actuel.
        """
        # TODO: Votre code ici
