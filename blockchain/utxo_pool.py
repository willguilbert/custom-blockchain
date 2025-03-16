from __future__ import annotations

from blockchain.utxo import UTXO
from blockchain.transaction import Transaction


class UTXOPool:
    def __init__(self):
        """Crée un nouveau UTXOPool vide."""
        # La collection actuelle d'UTXOs, chacun étant mappé à sa sortie de transaction correspondante
        self.pool: dict[UTXO, Transaction.Output] = {}

    @classmethod
    def from_utxo_pool(cls, utxo_pool: UTXOPool):
        """Crée un nouveau UTXOPool qui est une copie de <utxo_pool>."""
        up = cls()
        up.pool = utxo_pool.pool.copy()
        return up

    def add_utxo(self, utxo: UTXO, tx_output: Transaction.Output) -> None:
        """Ajoute un mappage de UTXO <utxo> à la sortie de transaction <tx_output> au pool."""
        self.pool[utxo] = tx_output

    def remove_utxo(self, utxo: UTXO) -> None:
        """Supprime l'UTXO <utxo> du pool."""
        self.pool.pop(utxo)

    def get_tx_output(self, utxo: UTXO) -> Transaction.Output:
        """Renvoie la sortie de la transaction correspondant à l'UTXO <utxo>."""
        return self.pool[utxo]

    def __contains__(self, utxo: UTXO) -> bool:
        """Renvoie True si l'UTXO <utxo> est dans le pool et False sinon."""
        return utxo in self.pool

    def get_all_utxo(self) -> list[UTXO]:
        """Renvoie une liste de tous les UTXO du pool."""
        return list(self.pool.keys())
