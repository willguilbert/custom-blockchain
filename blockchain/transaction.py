from __future__ import annotations

import hashlib
import struct

from blockchain.crypto import PrivateKey, PublicKey


class Transaction:
    class Input:
        def __init__(self, prev_hash: bytes, index: int):
            # Hash de la transaction dont la sortie est utilisée
            self.prev_tx_hash: bytes = prev_hash

            # Index de sortie utilisé de la transaction self.prev_tx_hash
            self.output_index: int = index

            # Signature produite pour vérifier la validité
            self.signature: bytes | None = None

        def add_signature(self, sig: bytes) -> None:
            self.signature = sig

    class Output:
        def __init__(self, value: float, address: PublicKey):
            # Valeur en iftcoins de la sortie
            self.value = value

            # Adresse (clé publique) du destinataire
            self.address = address

    def __init__(self):
        # Hash de la transaction (identifiant unique)
        self.hash: bytes = None

        self.inputs: list[Transaction.Input] = []
        self.outputs: list[Transaction.Output] = []
        self.coinbase: bool = False

    @classmethod
    def create_coinbase(cls, coinbase: float, address: PublicKey) -> Transaction:
        """Crée une transaction coinbase de valeur <coinbase> et appelle generate_hash."""
        t = cls()
        t.inputs = []
        t.outputs = []
        t.coinbase = True

        t.add_output(coinbase, address)
        t.generate_hash()

        return t

    def is_coinbase(self) -> bool:
        return self.coinbase

    def add_input(self, prev_tx_hash: bytes, output_index: int) -> None:
        input_: Transaction.Input = Transaction.Input(prev_tx_hash, output_index)
        self.inputs.append(input_)

    def add_output(self, value: float, address: PublicKey) -> None:
        output: Transaction.Output = Transaction.Output(value, address)
        self.outputs.append(output)

    def remove_input_via_index(self, index: int) -> None:
        del self.inputs[index]

    def get_raw_data_to_sign(self, index: int) -> bytes:
        sig_data: bytes = b""

        if index > len(self.inputs):
            raise ValueError(f"Index {index} invalide!")

        # ième entrée et toutes les sorties
        input_: Transaction.Input = self.inputs[index]
        prev_tx_hash: bytes = input_.prev_tx_hash
        output_index: bytes = input_.output_index.to_bytes(2, byteorder="big")

        if prev_tx_hash is not None:
            sig_data += prev_tx_hash

        sig_data += output_index

        for output in self.outputs:
            value: bytes = struct.pack("f", output.value)

            sig_data += value
            sig_data += output.address.to_string()

        return sig_data

    def add_signature(self, signature: bytes, index: int) -> None:
        self.inputs[index].add_signature(signature)

    def to_bytes(self) -> bytes:
        raw_tx: bytes = b""

        for input_ in self.inputs:
            prev_tx_hash: bytes = input_.prev_tx_hash
            output_index: bytes = input_.output_index.to_bytes(2, byteorder="big")
            assert input_.signature is not None
            signature: bytes = input_.signature

            if prev_tx_hash is not None:
                raw_tx += prev_tx_hash

            raw_tx += output_index

            if signature is not None:
                raw_tx += signature

        for output in self.outputs:
            value: bytes = struct.pack("f", output.value)
            raw_tx += value

            raw_tx += output.address.to_string()

        return raw_tx

    def generate_hash(self) -> None:
        self.hash = hashlib.sha256(self.to_bytes()).digest()

    def sign(self, sk: PrivateKey, index: int) -> None:
        sig = sk.sign(self.get_raw_data_to_sign(index))
        self.add_signature(sig, index)
        self.generate_hash()

    def get_input(self, index: int) -> Transaction.Input:
        if index < self.num_inputs():
            return self.inputs[index]

        raise ValueError(f"Index {index} invalide!")

    def get_output(self, index: int) -> Transaction.Output:
        if index < self.num_outputs():
            return self.outputs[index]

        raise ValueError(f"Index {index} invalide!")

    def num_inputs(self) -> int:
        return len(self.inputs)

    def num_outputs(self) -> int:
        return len(self.outputs)
