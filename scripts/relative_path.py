import os


def get_parent_dir(directory):
    return os.path.dirname(directory)


def get_path(folder):
    if "AccessibleCourtData" in os.getcwd().split('/')[-1]:
        directory = os.getcwd()
    else:
        directory = get_parent_dir(os.getcwd())
    return os.path.join(directory, folder)
