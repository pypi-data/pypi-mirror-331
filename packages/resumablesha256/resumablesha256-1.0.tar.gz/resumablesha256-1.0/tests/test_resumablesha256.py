import unittest
import pickle
import hashlib
import random
from resumablesha256 import sha256


class TestSHA256(unittest.TestCase):
    def test_basic_hash(self):
        h = sha256()
        h.update(b"hello world")
        digest = h.digest()
        self.assertEqual(len(digest), 32)

        h2 = hashlib.sha256()
        h2.update(b"hello world")
        assert h2.digest() == h.digest()

    def test_string_initialization(self):
        h1 = sha256(b"another test")
        h2 = sha256()
        h2.update(b"another test")
        self.assertEqual(h1.digest(), h2.digest())
        self.assertEqual(h1.hexdigest(), h2.hexdigest())

    def test_hexdigest(self):
        h = sha256()
        h.update(b"hello world")
        hex_digest = h.hexdigest()
        self.assertEqual(len(hex_digest), 64)

    def test_copy(self):
        h1 = sha256()
        h1.update(b"hello")
        h2 = h1.copy()
        self.assertEqual(h1.hexdigest(), h2.hexdigest())
        assert h1.__getstate__() == h2.__getstate__()

        # Updating them differently should lead to different digests.
        h1.update(b" world")
        h2.update(b" there")
        self.assertNotEqual(h1.hexdigest(), h2.hexdigest())

    def test_pickling(self):
        h = sha256()
        h.update(b"hello world")
        state = pickle.dumps(h)
        h2 = pickle.loads(state)
        self.assertEqual(h.hexdigest(), h2.hexdigest())

    def test_properties(self):
        h = sha256()
        self.assertEqual(h.digest_size, 32)
        self.assertEqual(h.block_size, 64)
        self.assertEqual(h.name, "sha256")

    def test_string_construction(self):
        with self.assertRaises(TypeError):
            sha256("this is not binary")

    def test_binary(self):
        h1 = sha256()
        h2 = hashlib.sha256()
        random.seed(234230)
        for i in range(200):
            chunk = (random.randint(0, 255).to_bytes(length=1, byteorder="big")
                * random.randint(1, 30))
            h1.update(chunk)
            h2.update(chunk)
            self.assertEqual(h1.digest(), h2.digest())
            self.assertEqual(h1.hexdigest(), h2.hexdigest())
            h1 = pickle.loads(pickle.dumps(h1))


if __name__ == '__main__':
    unittest.main()
