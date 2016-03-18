import binascii

from math import floor, ceil

import pytest

from bigchaindb.crypto.condition import Condition
from bigchaindb.crypto.ed25519 import ED25519PrivateKey, ED25519PublicKey
from bigchaindb.crypto.fulfillment import Fulfillment
from bigchaindb.crypto.fulfillments.ed25519_sha256 import Ed25519Sha256Fulfillment
from bigchaindb.crypto.fulfillments.threshold_sha256 import ThresholdSha256Fulfillment


class TestBigchainILPSha256Condition:
    CONDITION_SHA256_ILP = 'cc:1:1:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:1'

    def test_deserialize_condition(self):
        example_condition = self.CONDITION_SHA256_ILP
        condition = Condition.from_uri(example_condition)
        assert condition.serialize_uri() == self.CONDITION_SHA256_ILP


class TestBigchainILPEd25519Sha256Fulfillment:
    PUBLIC_HEX_ILP = b'ec172b93ad5e563bf4932c70e1245034c35467ef2efd4d64ebf819683467e2bf'
    PUBLIC_B64_ILP = b'7Bcrk61eVjv0kyxw4SRQNMNUZ+8u/U1k6/gZaDRn4r8'
    PUBLIC_B58_ILP = 'Gtbi6WQDB6wUePiZm8aYs5XZ5pUqx9jMMLvRVHPESTjU'

    PRIVATE_HEX_ILP = b'833fe62409237b9d62ec77587520911e9a759cec1d19755b7da901b96dca3d42'
    PRIVATE_B64_ILP = b'gz/mJAkje51i7HdYdSCRHpp1nOwdGXVbfakBuW3KPUI'
    PRIVATE_B58_ILP = '9qLvREC54mhKYivr88VpckyVWdAFmifJpGjbvV5AiTRs'

    CONDITION_ED25519_ILP = 'cc:1:8:qQINW2um59C4DB9JSVXH1igqAmaYGGqryllHUgCpfPU:113'
    FULFILLMENT_ED25519_ILP = \
        'cf:1:8:IOwXK5OtXlY79JMscOEkUDTDVGfvLv1NZOv4GWg0Z-K_DEhlbGxvIHdvcmxkISAVIENvbmRpdGlvbnMgYXJlIGhlcmUhQENbql531' \
        'PbCJlRUvKjP56k0XKJMOrIGo2F66ueuTtRnYrJB2t2ZttdfXM4gzD_87eH1nZTpu4rTkAx81hSdpwI'
    HASH_ED25519_HEX_ILP = b'a9020d5b6ba6e7d0b80c1f494955c7d6282a026698186aabca59475200a97cf5'

    def test_ilp_keys(self):
        sk = ED25519PrivateKey(self.PRIVATE_B58_ILP)
        assert sk.private_key.to_ascii(encoding='base64') == self.PRIVATE_B64_ILP
        assert binascii.hexlify(sk.private_key.to_bytes()[:32]) == self.PRIVATE_HEX_ILP

        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)
        assert vk.public_key.to_ascii(encoding='base64') == self.PUBLIC_B64_ILP
        assert binascii.hexlify(vk.public_key.to_bytes()) == self.PUBLIC_HEX_ILP

    def test_serialize_condition_and_validate_fulfillment(self):
        sk = ED25519PrivateKey(self.PRIVATE_B58_ILP)
        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32  # defaults to 0

        assert fulfillment.condition.serialize_uri() == self.CONDITION_ED25519_ILP
        assert binascii.hexlify(fulfillment.condition.hash) == self.HASH_ED25519_HEX_ILP

        fulfillment.message = ' Conditions are here!'

        # ED25519-SHA256 condition not fulfilled
        assert fulfillment.validate() == False

        # Fulfill an ED25519-SHA256 condition
        fulfillment.sign(sk)

        assert fulfillment.serialize_uri() == self.FULFILLMENT_ED25519_ILP
        assert fulfillment.validate()

    def test_deserialize_condition(self):
        deserialized_condition = Condition.from_uri(self.CONDITION_ED25519_ILP)

        assert deserialized_condition.serialize_uri() == self.CONDITION_ED25519_ILP
        assert binascii.hexlify(deserialized_condition.hash) == self.HASH_ED25519_HEX_ILP

    def test_serialize_deserialize_condition(self):
        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32

        condition = fulfillment.condition
        deserialized_condition = Condition.from_uri(condition.serialize_uri())

        assert deserialized_condition.bitmask == condition.bitmask
        assert deserialized_condition.hash == condition.hash
        assert deserialized_condition.max_fulfillment_length == condition.max_fulfillment_length
        assert deserialized_condition.serialize_uri() == condition.serialize_uri()

    def test_deserialize_fulfillment(self):
        fulfillment = Fulfillment.from_uri(self.FULFILLMENT_ED25519_ILP)

        assert fulfillment.serialize_uri() == self.FULFILLMENT_ED25519_ILP
        assert fulfillment.condition.serialize_uri() == self.CONDITION_ED25519_ILP
        assert binascii.hexlify(fulfillment.condition.hash) == self.HASH_ED25519_HEX_ILP
        assert fulfillment.public_key.public_key.to_ascii(encoding='hex') == self.PUBLIC_HEX_ILP
        assert fulfillment.validate()

    def test_serialize_deserialize_fulfillment(self):
        sk = ED25519PrivateKey(self.PRIVATE_B58_ILP)
        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32  # defaults to 0
        fulfillment.message = ' Conditions are here!'
        fulfillment.sign(sk)

        assert fulfillment.validate()

        deserialized_fulfillment = Fulfillment.from_uri(fulfillment.serialize_uri())
        assert deserialized_fulfillment.serialize_uri() == fulfillment.serialize_uri()
        assert deserialized_fulfillment.condition.serialize_uri() == fulfillment.condition.serialize_uri()
        assert deserialized_fulfillment.public_key.public_key.to_bytes() == fulfillment.public_key.public_key.to_bytes()
        assert deserialized_fulfillment.validate()


class TestBigchainILPThresholdSha256Fulfillment:
    PUBLIC_B58_ILP = 'Gtbi6WQDB6wUePiZm8aYs5XZ5pUqx9jMMLvRVHPESTjU'
    PRIVATE_B58_ILP = '9qLvREC54mhKYivr88VpckyVWdAFmifJpGjbvV5AiTRs'

    CONDITION_ED25519_ILP = 'cc:1:8:qQINW2um59C4DB9JSVXH1igqAmaYGGqryllHUgCpfPU:113'
    FULFILLMENT_ED25519_ILP = \
        'cf:1:8:IOwXK5OtXlY79JMscOEkUDTDVGfvLv1NZOv4GWg0Z-K_DEhlbGxvIHdvcmxkISAVIENvbmRpdGlvbnMgYXJlIGhlcmUhQENbql531' \
        'PbCJlRUvKjP56k0XKJMOrIGo2F66ueuTtRnYrJB2t2ZttdfXM4gzD_87eH1nZTpu4rTkAx81hSdpwI'

    CONDITION_ED25519_ILP_2 = 'cc:1:8:_WzTrHvFnv4I-H0cAKWZ6Q3g3Y0Du3aW01nIsaAsio8:116'
    FULFILLMENT_ED25519_ILP_2 = \
        'cf:1:8:IOwXK5OtXlY79JMscOEkUDTDVGfvLv1NZOv4GWg0Z-K_D0hlbGxvIHVuaXZlcnNlISAbIENvbmRpdGlvbnMgYXJlIGV2ZXJ5d2hlc' \
        'mUhQNmD2Cvk7e3EFOo-arA2TKYTP-474Z4okhbYmKij6XxObIbRsDScjXILAJ6mV5hP7Xyqkg5fcSsZbfRYypzlsAM'
    HASH_ED25519_HEX_ILP = b'a9020d5b6ba6e7d0b80c1f494955c7d6282a026698186aabca59475200a97cf5'

    CONDITION_THRESHOLD_ED25519_ILP_2 = 'cc:1:c:IZgoTeE1Weg6tfGMLWGe2JmS-waBN-CUrlbhtI9GBcQ:230'
    FULFILLMENT_THRESHOLD_ED25519_ILP_2 = \
        'cf:1:4:AgIBCCDsFyuTrV5WO_STLHDhJFA0w1Rn7y79TWTr-BloNGfivwxIZWxsbyB3b3JsZCEgFSBDb25kaXRpb25zIGFyZSBoZXJlIUBDW' \
        '6ped9T2wiZUVLyoz-epNFyiTDqyBqNheurnrk7UZ2KyQdrdmbbXX1zOIMw__O3h9Z2U6buK05AMfNYUnacCAQgg7Bcrk61eVjv0kyxw4SRQN' \
        'MNUZ-8u_U1k6_gZaDRn4r8MSGVsbG8gd29ybGQhIBUgQ29uZGl0aW9ucyBhcmUgaGVyZSFAQ1uqXnfU9sImVFS8qM_nqTRcokw6sgajYXrq5' \
        '65O1GdiskHa3Zm2119cziDMP_zt4fWdlOm7itOQDHzWFJ2nAgEBCCD9bNOse8We_gj4fRwApZnpDeDdjQO7dpbTWcixoCyKj3Q'

    def create_fulfillment_ed25519sha256(self):
        sk = ED25519PrivateKey(self.PRIVATE_B58_ILP)
        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32  # defaults to 0
        fulfillment.message = ' Conditions are here!'
        fulfillment.sign(sk)
        return fulfillment

    def test_serialize_condition_and_validate_fulfillment(self):
        ilp_fulfillment = Fulfillment.from_uri(self.FULFILLMENT_ED25519_ILP)
        ilp_fulfillment_2 = Fulfillment.from_uri(self.FULFILLMENT_ED25519_ILP_2)

        assert ilp_fulfillment.validate() == True
        assert ilp_fulfillment_2.validate() == True

        THRESHOLD = 2

        # Create a threshold condition
        fulfillment = ThresholdSha256Fulfillment()
        fulfillment.add_subfulfillment(ilp_fulfillment_2)
        fulfillment.add_subfulfillment(ilp_fulfillment)
        fulfillment.add_subfulfillment(ilp_fulfillment)
        fulfillment.threshold = THRESHOLD  # defaults to subconditions.length

        assert fulfillment.condition.serialize_uri() == self.CONDITION_THRESHOLD_ED25519_ILP_2
        # Note: If there are more than enough fulfilled subconditions, shorter
        # fulfillments will be chosen over longer ones.
        # thresholdFulfillmentUri.length === 65
        assert fulfillment.serialize_uri() == self.FULFILLMENT_THRESHOLD_ED25519_ILP_2
        assert fulfillment.validate()

    def test_deserialize_fulfillment(self):
        NUM_FULFILLMENTS = 3
        THRESHOLD = 2

        fulfillment = Fulfillment.from_uri(self.FULFILLMENT_THRESHOLD_ED25519_ILP_2)
        assert fulfillment.threshold == THRESHOLD
        assert len(fulfillment.subfulfillments) == THRESHOLD
        assert len(fulfillment.get_all_subconditions()) == NUM_FULFILLMENTS
        assert fulfillment.serialize_uri() == self.FULFILLMENT_THRESHOLD_ED25519_ILP_2
        assert fulfillment.validate()

    def test_serialize_deserialize_fulfillment(self):
        ilp_fulfillment = Fulfillment.from_uri(self.FULFILLMENT_ED25519_ILP)
        NUM_FULFILLMENTS = 100
        THRESHOLD = ceil(NUM_FULFILLMENTS * 2 / 3)

        # Create a threshold condition
        fulfillment = ThresholdSha256Fulfillment()
        for i in range(NUM_FULFILLMENTS):
            fulfillment.add_subfulfillment(ilp_fulfillment)
        fulfillment.threshold = THRESHOLD

        fulfillment_uri = fulfillment.serialize_uri()

        assert fulfillment.validate()
        deserialized_fulfillment = Fulfillment.from_uri(fulfillment_uri)

        assert deserialized_fulfillment.threshold == THRESHOLD
        assert len(deserialized_fulfillment.subfulfillments) == THRESHOLD
        assert len(deserialized_fulfillment.get_all_subconditions()) == NUM_FULFILLMENTS
        assert deserialized_fulfillment.serialize_uri() == fulfillment_uri
        assert deserialized_fulfillment.validate()

    def test_fulfillment_didnt_reach_threshold(self):
        ilp_fulfillment = Fulfillment.from_uri(self.FULFILLMENT_ED25519_ILP)
        THRESHOLD = 10

        # Create a threshold condition
        fulfillment = ThresholdSha256Fulfillment()
        fulfillment.threshold = THRESHOLD

        for i in range(THRESHOLD - 1):
            fulfillment.add_subfulfillment(ilp_fulfillment)

        with pytest.raises(ValueError):
            fulfillment.serialize_uri()

        assert fulfillment.validate() is False

        fulfillment.add_subfulfillment(ilp_fulfillment)

        fulfillment_uri = fulfillment.serialize_uri()
        assert fulfillment.validate()

        deserialized_fulfillment = Fulfillment.from_uri(fulfillment_uri)

        assert deserialized_fulfillment.threshold == THRESHOLD
        assert len(deserialized_fulfillment.subfulfillments) == THRESHOLD
        assert len(deserialized_fulfillment.get_all_subconditions()) == THRESHOLD
        assert deserialized_fulfillment.serialize_uri() == fulfillment_uri
        assert deserialized_fulfillment.validate()
