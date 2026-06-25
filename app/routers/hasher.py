import hashlib

def calcular_hash(algoritmo: str, valor: str) -> str:
    algoritmos = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256
    }
    # A lógica que você já criou:
    input_bytes = valor.encode('utf-8')
    hash_obj = algoritmos[algoritmo.lower()](input_bytes)
    
    return hash_obj.hexdigest()