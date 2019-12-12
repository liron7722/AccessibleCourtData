import os


def get_parent_dir(directory):
    return os.path.dirname(directory)


def get_path(folder):
    current_dirs_parent = get_parent_dir(os.getcwd())
    return os.path.join(current_dirs_parent, folder)
