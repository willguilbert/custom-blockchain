from ecdsa import SigningKey, SECP256k1, VerifyingKey


# Alias de la classe SigningKey
class PrivateKey(SigningKey):
    pass


# Alias de la classe VerifyingKey
class PublicKey(VerifyingKey):
    pass


class KeyPairGenerator:
    @classmethod
    def generate_key_pair(cls) -> tuple[PrivateKey, PublicKey]:
        sk = PrivateKey.generate(curve=SECP256k1)
        pk = sk.get_verifying_key()
        return sk, pk


def verify_signature(pk: PublicKey, message: bytes, signature: bytes) -> bool:
    return pk.verify(signature, message)
