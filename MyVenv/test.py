# import sqlite3
# import os
# from flask import Flask
# app = Flask(__name__)

# app.config['UPLOAD_FOLDER'] = os.getcwd()+ '/static/audios'
# id = 3
# with sqlite3.connect("transcripts.db") as conn:
#         c = conn.cursor()
#         c.execute("select save_folder from transcripts where sen_id = {0}".format(id))
#         save_folder = c.fetchone()[0]
#         path = os.path.join(str(app.config['UPLOAD_FOLDER']), save_folder)
# print(os.listdir(path))
import re
str = 'namcute_11_3.wav'
a= re.split("_",str)
print(a)