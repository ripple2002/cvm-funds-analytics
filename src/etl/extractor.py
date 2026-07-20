from pathlib import Path
import requests


def download_cvm_file(url: str, dest_path: str, chunk_size: int = 8192) -> Path:
    
    target = Path(dest_path)
    
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and target.stat().st_size > 0:
        return target

    tmp_path = target.with_suffix(target.suffix + ".tmp")

    try:
        with requests.get(url, stream=True, timeout=30) as response:
            response.raise_for_status()

            with open(tmp_path, "wb") as tmp_file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        tmp_file.write(chunk)  
      
        tmp_path.rename(target)

    except Exception:
       
        if tmp_path.exists():
            tmp_path.unlink()
        raise 

    return target


if __name__ == "__main__":
    URL_CADASTRO = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
    CAMINHO_DESTINO = Path("data/raw/cad_fi.csv")

    print("--- Teste 1: Primeiro Download (Deve ir no servidor) ---")
    arquivo_salvo = download_cvm_file(URL_CADASTRO, CAMINHO_DESTINO)
    print(f"Resultado: {arquivo_salvo}\n")

    print("--- Teste 2: Segundo Download (Deve bater no Cache) ---")
    arquivo_salvo = download_cvm_file(URL_CADASTRO, CAMINHO_DESTINO)
    print(f"Resultado: {arquivo_salvo}")