import os, re
from typing import final
import librosa
import sqlite3
from flask import request

def get_each_info(user_id):
    sens_id_arr,files_path= [],[]
    skip_sens_id = []
    skip_sens_content =[]
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
                print(item[0])

            #  lấy dur_each_sen: thời gian của từng file ghi âm
            dur_item = 0
            for item in files_path:
                dur_item = dur_item + librosa.get_duration(filename =item)
            dur_item = "{:.2f}".format(dur_item/3600)


            #  lấy mảng các câu bị bỏ qua
            c.execute("select skip_sens from users where id ={0}".format(user_id))
            skip_sens_str = c.fetchone()[0]
            skip_sens_str_arr =re.split(",",skip_sens_str)   # string chứa id của những câu bị bỏ qua, lưu dưới dạng chuỗi, mỗi id cách nhau bởi dấu phẩy
            skip_sens_str_arr.pop()  # xóa phần tử rỗng bị thừa ở cuối mảng ['1','2','']
            for item in skip_sens_str_arr:
                skip_sens_id.append(int(item))
            for item in skip_sens_id:
                c.execute("select sen_content from transcripts where sen_id = {0}".format(item))
                skip_sens_content.append(str(c.fetchone()[0].capitalize()))
            conn.commit()  
        except:
            conn.rollback()
    return dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content

if __name__ == '__main__':
    get_each_info(id)
        
    
