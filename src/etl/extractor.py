from pathlib import Path
import requests
import zipfile

def download_cvm_file(url: str, dest_dir: str = "data/raw", chunk_size: int = 8192) -> Path:
    
    file_name = url.split("/")[-1]
    
    target = Path(dest_dir) / file_name
    
    target.parent.mkdir(parents=True, exist_ok=True)

    final_target = target.with_suffix(".csv") if target.suffix == ".zip" else target

    if final_target.exists() and final_target.stat().st_size > 0:
        return final_target

    tmp_path = target.with_suffix(target.suffix + ".tmp")

    try:
        with requests.get(url, stream=True, timeout=30) as response:
            response.raise_for_status()

            with open(tmp_path, "wb") as tmp_file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        tmp_file.write(chunk)
        

        tmp_path.rename(target)

        if target.suffix == ".zip":
            with zipfile.ZipFile(target, "r") as zip_ref:
                zip_ref.extractall(target.parent)
            
            target.unlink() # Apaga o .zip pesado após extrair
            return final_target

    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise

    return target



if __name__ == "__main__":
    URL_CADASTRO = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
    CAMINHO_DESTINO = Path("data/raw/cad_fi.csv")

    print("--- Teste 1: Primeiro Download (Deve ir no servidor) ---")
    arquivo_salvo = download_cvm_file(URL_CADASTRO)
    print(f"Resultado: {arquivo_salvo}\n")

    print("--- Teste 2: Segundo Download (Deve bater no Cache) ---")
    arquivo_salvo = download_cvm_file(URL_CADASTRO)
    print(f"Resultado: {arquivo_salvo}")

    arquivo_salvo = download_cvm_file("https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_202606.zip")