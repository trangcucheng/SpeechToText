import os
import librosa
import sqlite3
from flask import request, session


def get_all_info():
    id = session['id']
    with sqlite3.connect('transcripts.db') as conn:
        c = conn.cursor()
        
    c = conn.cursor()

    names, duration_each_user, number_files, files_path_each_user, ids_each_user = [], [], [], [], []
    
    # lấy tên: okkkk
    c.execute("select user_name from users ")  
    names_arr = c.fetchall() #[('trang',), ('anh',), ('bao',), ('mommm',), ('shin',)]
    for item in names_arr:
        names.append(item[0])
    
    #lấy id each other: okkkk
    for i in range(1, len(names)+1):
        each_id = []
        c.execute("select sen_id from relationships where user_id = {0}".format(i))
        for item in (c.fetchall()):
            each_id.append(item[0])
        ids_each_user.append(each_id)
    #lấy numbers_file : okkkkkk
        number_files.append(len(each_id))

    #  lấy files_path_each_other: okkkkk
    for i in range(1, len(names)+1):
        each_file = []
        c.execute("select save_dir_url from relationships where user_id = {0}".format(i))
        for item in (c.fetchall()):
            each_file.append(os.path.join("static/audios", item[0]))
        files_path_each_user.append(each_file)
    

    # lấy duration_each_other
    for item in files_path_each_user:
        duration_item = 0
        for sub_item in item:
            duration_item = duration_item + librosa.get_duration(filename=sub_item)
        duration_each_user.append(duration_item)
    
    conn.commit()
    conn.close()
    return names, number_files, duration_each_user, files_path_each_user, ids_each_user


if __name__ == '__main__':
    get_all_info()
