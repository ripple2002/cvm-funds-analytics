from pathlib import Path
import requests
import zipfile




def download_cvm_file(url: str, dest_dir: str = "data/raw", chunk_size: int = 8192, inner_filename: str | None = None) -> Path:
    
    file_name = url.split("/")[-1]
    
    target = Path(dest_dir) / file_name
    
    target.parent.mkdir(parents=True, exist_ok=True)

    if inner_filename:
        final_target = target.parent / inner_filename
    else:
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
            
            target.unlink() 
            return final_target

    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise

    return target


def get_registro_classe_url() -> str:
    return "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/registro_fundo_classe.zip"


def get_inf_diario_url(ano: str, mes: str) -> str:
    return f"https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}{mes}.zip"