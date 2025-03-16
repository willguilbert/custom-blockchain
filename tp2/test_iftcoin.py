import secrets

from ecdsa import SigningKey, VerifyingKey

from tp2.block import Block
from tp2.blockchain import Blockchain
from tp2.block_handler import BlockHandler
from tp2.transaction import Transaction
from tp2.crypto import KeyPairGenerator
from tp2.wallet import get_balance


class TestIFTCoin:
    def test_keypair_generation(self):
        # Génération des paires de clés pour Nakamoto, Alice et Bob
        nakamoto_sk, nakamoto_pk = KeyPairGenerator.generate_key_pair()
        alice_sk, alice_pk = KeyPairGenerator.generate_key_pair()
        bob_sk, bob_pk = KeyPairGenerator.generate_key_pair()

        assert isinstance(nakamoto_sk, SigningKey)
        assert isinstance(nakamoto_pk, VerifyingKey)
        assert isinstance(alice_sk, SigningKey)
        assert isinstance(alice_pk, VerifyingKey)
        assert isinstance(bob_sk, SigningKey)
        assert isinstance(bob_pk, VerifyingKey)

    def test_blockchain_operations(self):
        # Génération des paires de clés pour Nakamoto, Alice et Bob
        nakamoto_sk, nakamoto_pk = KeyPairGenerator.generate_key_pair()
        alice_sk, alice_pk = KeyPairGenerator.generate_key_pair()
        bob_sk, bob_pk = KeyPairGenerator.generate_key_pair()

        # Création du bloc de genèse : aucune autre transaction à part la transaction coinbase
        genesis_block: Block = Block(nakamoto_pk, prev_block_hash=None)
        genesis_block.finalize()

        # Création de la chaîne de blocs et du gestionnaire de blocs
        blockchain: Blockchain = Blockchain(genesis_block)
        block_handler: BlockHandler = BlockHandler(blockchain)

        assert genesis_block.prev_block_hash is None
        assert genesis_block.hash is not None
        assert secrets.compare_digest(
            genesis_block.hash.hex(),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

        assert get_balance(blockchain, nakamoto_pk) == 25  # 25 de coinbase
        assert get_balance(blockchain, alice_pk) == 0
        assert get_balance(blockchain, bob_pk) == 0

        # Création d'un bloc miné par Alice avec une transaction de Nakamoto à Alice

        # Nouvelle TX : Nakamoto paie 25 iftcoins à Alice
        tx1: Transaction = Transaction()

        # Le bloc de genèse a une valeur de 25 iftcoins appartenant à Nakamoto
        tx1.add_input(genesis_block.coinbase.hash, 0)
        tx1.add_output(5, alice_pk)
        tx1.add_output(10, alice_pk)
        tx1.add_output(10, alice_pk)

        # Il n'y a qu'une seule entrée Transaction.Input (en position 0) dans tx1
        # et elle contient les iftcoins de Nakamoto.
        # Nous devons donc signer avec la clé privée de Nakamoto.
        tx1.sign(nakamoto_sk, 0)

        block_handler.process_transaction(tx1)

        assert blockchain.tx_pool.pool

        block1 = block_handler.create_block(alice_pk)
        assert block1 is not None

        assert not blockchain.tx_pool.pool

        assert get_balance(blockchain, nakamoto_pk) == 0
        assert (
            get_balance(blockchain, alice_pk) == 50
        )  # 25 de Nakamoto + 25 de coinbase
        assert get_balance(blockchain, bob_pk) == 0

        # Création d'un bloc miné par Bob avec une transaction d'Alice à Bob
        # et d'Alice à Nakamoto
        block2: Block = Block(bob_pk, block1.hash)

        # Nouvelle TX : Alice envoie 5 iftcoins à Bob et 20 iftcoins à Nakamoto
        tx2: Transaction = Transaction()
        tx2.add_input(block1.coinbase.hash, 0)  # 25 iftcoins
        tx2.add_output(5, bob_pk)
        tx2.add_output(20, nakamoto_pk)
        tx2.sign(alice_sk, 0)

        blockchain.add_transaction(tx2)
        block2.add_transaction(tx2)
        block2.finalize()
        assert block_handler.process_block(block2)

        assert not blockchain.tx_pool.pool

        assert get_balance(blockchain, nakamoto_pk) == 20
        assert get_balance(blockchain, alice_pk) == 25
        assert get_balance(blockchain, bob_pk) == 30  # 25 de coinbase + 5 d'Alice

        # Création d'un nouveau bloc miné par nakamoto_pk avec une transaction d'Alice à Bob
        block3: Block = Block(nakamoto_pk, block2.hash)

        # Nouvelle TX : Alice envoie 20 iftcoins à Bob
        tx3: Transaction = Transaction()
        tx3.add_output(20, bob_pk)
        tx3.add_input(tx1.hash, 1)  # 10 iftcoins
        tx3.sign(alice_sk, 0)
        tx3.add_input(tx1.hash, 2)  # 10 iftcoins
        tx3.sign(alice_sk, 1)

        blockchain.add_transaction(tx3)
        block3.add_transaction(tx3)
        block3.finalize()
        assert block_handler.process_block(block3)

        assert get_balance(blockchain, nakamoto_pk) == 45  # 20 avant + 25 de coinbase
        assert get_balance(blockchain, alice_pk) == 5
        assert get_balance(blockchain, bob_pk) == 50  # 30 avant + 20 d'Alice

        assert not blockchain.tx_pool.pool

        # Création d'un nouveau bloc avec une transaction de Bob à lui-même
        block4: Block = Block(alice_pk, block3.hash)

        # Nouvelle TX : Bob ne peut pas dépenser plus que la valeur de son entrée.
        tx4: Transaction = Transaction()
        tx4.add_output(10, bob_pk)
        tx4.add_output(11, bob_pk)
        tx4.add_input(tx3.hash, 0)  # Cette entrée n'a que 20 iftcoins
        tx4.sign(bob_sk, 0)

        blockchain.add_transaction(tx4)
        block4.add_transaction(tx4)
        block4.finalize()
        assert not block_handler.process_block(block4)

        assert get_balance(blockchain, nakamoto_pk) == 45
        assert get_balance(blockchain, alice_pk) == 5
        assert get_balance(blockchain, bob_pk) == 50

        assert blockchain.tx_pool.pool

        # Création d'un nouveau bloc (block5) enchaîné au bloc 4 avec une tx Alice -> Bob
        block5: Block = Block(alice_pk, block3.hash)

        # Nouvelle TX : Alice et Nakamoto envoie 30 (5 + 25) iftcoins à Bob
        tx5: Transaction = Transaction()
        tx5.add_output(30, bob_pk)
        tx5.add_input(tx1.hash, 0)  # 5 iftcoins
        tx5.sign(alice_sk, 0)
        tx5.add_input(block3.coinbase.hash, 0)  # 25 iftcoins
        tx5.sign(nakamoto_sk, 1)

        blockchain.add_transaction(tx5)
        block5.add_transaction(tx5)
        block5.finalize()
        assert block_handler.process_block(block5)

        assert blockchain.tx_pool.pool

        assert get_balance(blockchain, nakamoto_pk) == 20
        assert get_balance(blockchain, alice_pk) == 25  # 25 de coinbase
        assert get_balance(blockchain, bob_pk) == 80

        # La transaction tx4 toujours dans le pool
        assert (
            len(blockchain.tx_pool.pool) == 1
            and blockchain.tx_pool.get_transactions()[0] is tx4
        )

        # On ne peut pas créer de bloc contenant une transaction invalide
        assert block_handler.create_block(alice_pk) is None

        # On retire la transaction tx4 du pool
        blockchain.tx_pool.remove_transaction(tx4.hash)
        assert len(blockchain.tx_pool.pool) == 0

        # On ne peut pas créer de bloc contenant 0 transactions
        assert block_handler.create_block(alice_pk) is None
