import os, re
from typing import final
import librosa
import sqlite3
from flask import request

def get_each_info(user_id):
    sens_id_arr,files_path= [],[]
    skip_sens_id = []
    skip_sens_content =[]
    dur_item = 0
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
            dur_item = "{:.2f}".format(dur_item/3600)


            #  lấy mảng những câu bị bỏ qua skip_sens_id, skip_sens_content
            c.execute("select cur_id from users where id ={0}".format(user_id))
            cur_id = c.fetchone()[0]   # cur_id -1 là id lớn nhất trong số các câu đã được thu
            for i in range(0,int(cur_id)):
                if i not in sens_id_arr:
                    skip_sens_id.append(i)
            for item in skip_sens_id:
                c.execute("select sen_content from transcripts where sen_id = {0}".format(item))
                skip_sens_content.append(str(c.fetchone()[0].capitalize()))
            conn.commit()  
        except:
            conn.rollback()
    return dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content
if __name__ == '__main__':
    get_each_info(id)
        
    
