import os
from neurionpy.crypto.keypairs import PrivateKey
from neurionpy.synapse.wallet import LocalWallet


def get_wallet():
    """
    Retrieve wallet using either the private key or mnemonic from the environment.
    """
    private_key = os.getenv("NEURION_PRIVATE_KEY")
    mnemonic = os.getenv("NEURION_MNEMONIC")
    if private_key:
        print("Using private key from environment")
        return LocalWallet(PrivateKey(private_key))

    if mnemonic:
        print("Using mnemonic key from environment")
        return LocalWallet.from_mnemonic(mnemonic)

    raise ValueError("No private key or mnemonic found in environment")
