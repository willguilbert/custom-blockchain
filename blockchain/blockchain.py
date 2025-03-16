from __future__ import annotations

from blockchain.block import Block
from blockchain.transaction import Transaction
from blockchain.transaction_handler import TransactionHandler
from blockchain.transaction_pool import TransactionPool
from blockchain.utxo import UTXO
from blockchain.utxo_pool import UTXOPool


class Blockchain:
    CUT_OFF_AGE: int = 10

    class BlockNode:
        def __init__(
            self, block: Block, parent: Blockchain.BlockNode | None, utxo_pool: UTXOPool
        ):
            self.block: Block = block
            self.parent: Blockchain.BlockNode | None = None
            self.children: list[Blockchain.BlockNode] = []
            # pool utxo pour créer un nouveau bloc au-dessus de ce bloc
            self.utxo_pool: UTXOPool = utxo_pool
            self.height: int = 1
            if parent is not None:
                self.height = parent.height + 1
                self.parent = parent
                self.parent.children.append(self)

    def __init__(self, genesis_block: Block):
        """
        Crée une chaîne de blocs vide avec juste un bloc de genèse.
        """
        assert genesis_block.hash is not None, "Bloc de genèse invalide!"

        self.blockchain: dict[str, Blockchain.BlockNode] = {}
        utxo_pool: UTXOPool = UTXOPool()
        self.add_coinbase_to_utxo_pool(genesis_block, utxo_pool)
        genesis_node: Blockchain.BlockNode = Blockchain.BlockNode(
            genesis_block, None, utxo_pool
        )
        self.blockchain[genesis_block.hash.hex()] = genesis_node
        self.tx_pool: TransactionPool = TransactionPool()
        self.max_height_node: Blockchain.BlockNode = genesis_node

    def get_max_height_block(self) -> Block:
        """Renvoie le bloc de hauteur maximale."""
        # TODO: Votre code ici
        return self.max_height_node.block
                

    def get_max_height_utxo_pool(self) -> UTXOPool:
        """Renvoie le pool utxo pour miner un nouveau bloc
        au-dessus du bloc de hauteur maximale."""
        # TODO: Votre code ici
        return self.max_height_node.utxo_pool

    def add_transaction(self, tx: Transaction) -> None:
        """Ajoute une transaction au memory pool."""
        # TODO: Votre code ici
        self.tx_pool.add_transaction(tx)

    def add_block(self, block: Block) -> bool:
        """
        Ajoute <block> à la chaîne de blocs s'il est valide.
        Pour que le bloc soit considéré comme valide, toutes les transactions
        qui s'y trouvent doivent être valides et le bloc doit être à une
        hauteur > (max_height - CUT_OFF_AGE).

        Par exemple, vous pouvez essayer de créer un nouveau bloc sur le bloc de genèse
        (hauteur de bloc 2) si la hauteur de la blockchain est <= CUT_OFF_AGE + 1.
        Dès que la hauteur > CUT_OFF_AGE + 1, vous ne pouvez pas créer de nouveau bloc à hauteur 2.

        Returns:
            bool: True si le bloc a été ajouté avec succès, False sinon.
        """
        assert block.hash is not None, "Bloc invalide!"

        # Vérifie si le bloc est un bloc de genèse
        prev_block_hash: bytes | None = block.prev_block_hash
        if prev_block_hash is None:
            return False

        # Vérifie si le bloc parent existe
        parent_block_node: Blockchain.BlockNode | None = self.blockchain.get(
            prev_block_hash.hex()
        )
        if parent_block_node is None:
            return False

        # Vérification de la hauteur
        proposed_height: int = parent_block_node.height + 1
        if proposed_height <= self.max_height_node.height - self.CUT_OFF_AGE:
            return False

        # Vérifie si toutes les transactions dans le bloc sont valides
        txs: list[Transaction] = block.transactions

        if len(txs) == 0:
            return False

        handler: TransactionHandler = TransactionHandler(parent_block_node.utxo_pool)

        valid_txs: list[Transaction] = handler.handle_transactions(txs)

        if len(valid_txs) != len(txs):
            return False

        utxo_pool: UTXOPool = handler.utxo_pool
        self.add_coinbase_to_utxo_pool(block, utxo_pool)

        # Retrait des transactions du pool
        for tx in block.transactions:
            self.tx_pool.remove_transaction(tx.hash)

        node: Blockchain.BlockNode = Blockchain.BlockNode(
            block, parent_block_node, utxo_pool
        )
        self.blockchain[block.hash.hex()] = node
        if proposed_height > self.max_height_node.height:
            self.max_height_node = node

        return True

    @staticmethod
    def add_coinbase_to_utxo_pool(block: Block, utxo_pool: UTXOPool) -> None:
        coinbase: Transaction = block.coinbase
        for i in range(coinbase.num_outputs()):
            output: Transaction.Output = coinbase.get_output(i)
            utxo: UTXO = UTXO(coinbase.hash, i)
            utxo_pool.add_utxo(utxo, output)
