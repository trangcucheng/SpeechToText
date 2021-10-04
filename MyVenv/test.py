import os
path_to_folders = os.path.join(os.getcwd(), "/static/audios")
print(path_to_folders)
if os.path.exists(path_to_folders):
    print("Yes")