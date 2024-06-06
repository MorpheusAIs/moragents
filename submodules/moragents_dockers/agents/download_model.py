import os
import shutil
from huggingface_hub import hf_hub_download
from model_config import Config

def download_model(model_name,revision):
    """Function to download model from the hub"""
    model_directory=hf_hub_download(repo_id=model_name,filename=revision)
    return model_directory

def move_files(src_dir, dest_dir):
    """Move files from source to destination directory."""
    for f in os.listdir(src_dir):
        src_path = os.path.join(src_dir, f)  
        dst_path = os.path.join(dest_dir, f)         
        shutil.copy2(src_path, dst_path)
        os.remove(src_path)


if __name__ == "__main__":
    download_dir = Config.DOWNLOAD_DIR
    os.makedirs(download_dir, exist_ok=True)
    model_name=Config.MODEL_NAME
    revision=Config.MODEL_REVISION
    path=download_model(model_name,revision)
    model_path = '/'.join(path.split('/')[:-1])+'/'
    move_files(model_path,download_dir)
