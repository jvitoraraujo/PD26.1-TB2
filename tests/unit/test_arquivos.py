import unittest

from app.core.arquivos import TIPOS_PERMITIDOS, detectar_tipo


class DetectarTipoTest(unittest.TestCase):
    def test_assinaturas(self):
        casos = {
            b"%PDF-1.7\n...": "application/pdf",
            b"\xff\xd8\xff\xe0\x00\x10JFIF": "image/jpeg",
            b"\x89PNG\r\n\x1a\n\x00\x00": "image/png",
            b"RIFF\x24\x00\x00\x00WEBPVP8 ": "image/webp",
        }
        for cabecalho, esperado in casos.items():
            self.assertEqual(detectar_tipo(cabecalho), esperado)

    def test_rejeita_conteudo_falso(self):
        for cabecalho in (b"<html><script>alert(1)</script>", b"MZ\x90\x00", b"", b"RIFF\x00\x00\x00\x00WAVE"):
            self.assertIsNone(detectar_tipo(cabecalho))

    def test_todo_tipo_permitido_tem_assinatura_detectavel(self):
        self.assertEqual(set(TIPOS_PERMITIDOS), {"application/pdf", "image/jpeg", "image/png", "image/webp"})
        for ext in TIPOS_PERMITIDOS.values():
            self.assertTrue(ext.startswith("."))


if __name__ == "__main__":
    unittest.main()
