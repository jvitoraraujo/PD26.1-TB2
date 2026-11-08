import hashlib
import unittest

from app.core.hasher import AlgoritmoHash, gerar_hash


class HasherTest(unittest.TestCase):
    def test_algoritmos(self):
        for algoritmo, funcao in (
            (AlgoritmoHash.MD5, hashlib.md5),
            (AlgoritmoHash.SHA1, hashlib.sha1),
            (AlgoritmoHash.SHA256, hashlib.sha256),
        ):
            self.assertEqual(gerar_hash("olá", algoritmo), funcao("olá".encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
