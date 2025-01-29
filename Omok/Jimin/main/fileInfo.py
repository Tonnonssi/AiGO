import os

def get_cwd_path(fname, path_name=None):
    f_cwd = os.path.abspath(os.path.join(os.getcwd(), ".."))
    f_path = f"{f_cwd}/{path_name}/{fname}" if path_name is not None else f"{f_cwd}/{path_name}"
    return f_cwd, f_path

F_CWD, F_PATH = get_cwd_path('Omok_1', 'model')