import os
from typing import final
import librosa
import sqlite3
from flask import request

def get_each_info(user_id):
    sens_id_arr,files_path= [],[]
    with sqlite3.connect("transcripts.db") as conn:
        try:
            c = conn.cursor()
            # lấy sens_id_arr: mảng chứa id của các câu mà user đã ghi âm
            c.execute("select sen_id from relationships where user_id = {0}".format(user_id))
            for item in (c.fetchall()):
                sens_id_arr.append(item[0])
            
            # lấy files_path: đường dẫn tới từng file ghi âm của người này
            c.execute("select save_dir_url from relationships where user_id = {0}".format(user_id))
            for item in (c.fetchall()):
                files_path.append(os.path.join("static/audios", item[0]))

            #  lấy dur_each_sen: thời gian của từng file ghi âm
            dur_item = 0
            for item in files_path:
                dur_item = dur_item + librosa.get_duration(filename =item)

            conn.commit()  
        except:
            conn.rollback()
    return dur_item, files_path, sens_id_arr

if __name__ == '__main__':
    get_each_info()
        
    
