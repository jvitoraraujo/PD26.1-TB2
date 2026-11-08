import unittest
from datetime import datetime, timedelta, timezone

from app.core.validadores import como_utc, cpf_valido, somente_digitos


class CpfTest(unittest.TestCase):
    def test_cpfs_validos(self):
        for cpf in ("52998224725", "11144477735", "39053344705"):
            self.assertTrue(cpf_valido(cpf), cpf)

    def test_digito_verificador_errado(self):
        self.assertFalse(cpf_valido("52998224724"))

    def test_tamanho_e_repetidos(self):
        for cpf in ("", "123", "529982247250", "11111111111", "00000000000", "abcdefghijk"):
            self.assertFalse(cpf_valido(cpf), cpf)

    def test_somente_digitos(self):
        self.assertEqual(somente_digitos("529.982.247-25"), "52998224725")


class DataTest(unittest.TestCase):
    def test_naive_vira_utc(self):
        r = como_utc(datetime(2026, 1, 1, 10, 0))
        self.assertEqual(r.tzinfo, timezone.utc)
        self.assertEqual(r.hour, 10)

    def test_com_fuso_converte(self):
        r = como_utc(datetime(2026, 1, 1, 10, 0, tzinfo=timezone(timedelta(hours=-3))))
        self.assertEqual(r.hour, 13)
        self.assertEqual(r.utcoffset(), timedelta(0))

    def test_resultados_sao_comparaveis(self):
        self.assertLess(como_utc(datetime(2026, 1, 1)), como_utc(datetime(2026, 1, 2, tzinfo=timezone.utc)))


if __name__ == "__main__":
    unittest.main()
