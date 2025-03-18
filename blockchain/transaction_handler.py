from mailbox import Message

from blockchain.crypto import verify_signature
from blockchain.transaction import Transaction
from blockchain.utxo import UTXO
from blockchain.utxo_pool import UTXOPool


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
        dblDepense = []
        valTotInputs = 0

        for index, txInput in enumerate(tx.inputs):
            utxoAttendu = UTXO(txInput.prev_tx_hash, txInput.output_index)

            if not self.sortieEstDansPool(utxoAttendu):
                return False

            txOutput = self.utxo_pool.get_tx_output(utxoAttendu)
            if not self.validerSignature(txOutput, index, txInput, tx):
                return False

            if utxoAttendu in dblDepense:
                return False
            dblDepense.append(utxoAttendu)

            valTotInputs += txOutput.value

        if not self.validerMontants(tx, valTotInputs):
            return False

        return True

    def handle_transactions(self, possible_txs: list[Transaction]) -> list[Transaction]:
        """
        - Reçoit une liste de transactions proposées,
        - Vérifie l'exactitude de chaque transaction, et
        - Renvoie une liste de transactions valides acceptées
          tout en mettant à jour le pool UTXO actuel.
        """
        # TODO: Votre code ici
        transactionsValides = []
        for transaction in possible_txs:
            if self.is_valid_transaction(transaction):
                transactionsValides.append(transaction)
                self.enleverUtxoDuPool(transaction)
                self.ajouterOutputAuPool(transaction)
        return transactionsValides

    # ===== Fonctions utiles pour simplifier le developpement et le debugging =====#

    def sortieEstDansPool(self, utxo: UTXO) -> bool:
        if utxo not in self.utxo_pool:
            return False
        return True

    def validerSignature(
        self,
        txOutput: Transaction.Output,
        index: int,
        txInput: Transaction.Input,
        tx: Transaction,
    ) -> bool:
        outPutPk = txOutput.address
        message = tx.get_raw_data_to_sign(index)
        if not verify_signature(outPutPk, message, txInput.signature):
            return False
        return True

    def validerMontants(self, tx: Transaction, valTotInputs: int) -> bool:
        valTotOutputs = 0
        for txOutputTx in tx.outputs:
            if txOutputTx.value < 0:
                return False
            valTotOutputs += txOutputTx.value
        if valTotOutputs > valTotInputs:
            return False
        return True

    def enleverUtxoDuPool(self, tx: Transaction):
        for txInput in tx.inputs:
            utxoCorrespondant = UTXO(txInput.prev_tx_hash, txInput.output_index)
            self.utxo_pool.remove_utxo(utxoCorrespondant)

    def ajouterOutputAuPool(self, tx: Transaction):
        for indexOutput, output in enumerate(tx.outputs):
            utxoCree = UTXO(tx.hash, indexOutput)
            self.utxo_pool.add_utxo(utxoCree, output)
