import os
import torch

from main.fileInfo import *

def get_cwd_path(fname, path_name=None):
    f_cwd = os.path.abspath(os.path.join(os.getcwd(), ".."))
    f_path = f"{f_cwd}/{path_name}/{fname}" if path_name is not None else f"{f_cwd}/{path_name}"
    return f_cwd, f_path

def make_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"'{path}' directory is created.")
    else:
        print(f"'{path}' already exists.")

def save_model(model, f_name='best_model_weight'):
    torch.save(model.state_dict(), f'{F_PATH}/{f_name}.pth')
    print("Model saving complete.")

def load_model(model_body, f_name):
    params = torch.load(f"{F_PATH}/{f_name}", weights_only=False)
    model_body.load_state_dict(params)
    print("Model is loaded.")

def make_valid_file_paths(idx):
    # make path 
    valid_f_path = f"{F_PATH}/valid_{idx}"
    valid_recent_f_path = f"{valid_f_path}/recent"
    valid_best_f_path = f"{valid_f_path}/best"

    make_directory(valid_recent_f_path)
    make_directory(valid_best_f_path)

    return valid_f_path, valid_recent_f_path, valid_best_f_path


def save_as_txt(type, txt):
    with open(f"{F_PATH}/{type}.txt", "w", encoding="utf-8") as file:
        file.write(txt)
    print("Complete.")