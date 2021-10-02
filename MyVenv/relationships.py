import sqlite3
import os
import librosa

conn = sqlite3.connect('transcripts.db')

c= conn.cursor()

# c.execute("""CREATE TABLE relationships (
#      id INTEGER PRIMARY KEY AUTOINCREMENT,
#      user_id int,
#      sen_id int,
#      save_dir_url,
#      foreign key(user_id) references users(user_id),
#      foreign key(sen_id) references transcripts(sen_id)
#  )
#  """)


# delete table's data
# c.execute("delete from relationships where user_id >0")
# c.execute("select sen_id from relationships where user_id = 1 ")
# print(c.fetchall())

# ids_each_user = []
# number_files = []
# for i in range(1, 6):  # noteeee
#         each_id = []
#         c.execute("select sen_id from relationships where user_id = {0}".format(i))
#         for item in (c.fetchall()):
#             each_id.append(item[0])
#         ids_each_user.append(each_id)

#         #lấy numbers_file
#         number_files.append(len(each_id))
# print(ids_each_user)
# print(number_files)

# files_path_each_user = []
# for i in range(1, 6):  # chú ý số 6 đang dùng để test!!!!
#         each_file = []
#         c.execute("select save_dir_url from relationships where user_id = {0}".format(i))
#         for item in (c.fetchall()):
#             each_file.append(os.path.join("static/audios", item[0]))
#         files_path_each_user.append(each_file)

# for item in files_path_each_user:
    # print(item)

# duration_each_user = []
# for item in files_path_each_user:
#         duration_item = 0
#         for sub_item in item:
#             # duration_item = duration_item + librosa.get_duration(sub_item)
#             print(sub_item)
#         duration_each_user.append(duration_item)

# print(duration_each_user)
# print(files_path_each_user)
# duration =0
# for item in files_path_each_user[4]:
#     print(item)
#     # duration = duration + librosa.get_duration(filename=item)
# print(duration)
# c.execute("delete from relationships where id >0")
# c.execute("delete from relationships where sen_id=0")
# c.execute("select count(id) from relationships")
# num = c.fetchall()
# a= num[len(num)-1]
# print(a[0]+1)
# c.execute("select * from relationships where user_id =1")
# id_temp = c.fetchone()[2]
# print(id_temp)
# for item in c.fetchall():
#     print(item)
# print(c.fetchone())
# c.execute("select id from relationships ")
# id_arr= c.fetchall()
# print(id_arr)
# last_item= id_arr[len(id_arr)-1]  
# print(last_item)
# c.execute("delete from relationships where id >=0")
# c.execute("drop table relationships")

# for item in c.fetchall():
#     print(item[0])
c.execute("select * from relationships")
print(c.fetchall())
conn.commit()
conn.close()