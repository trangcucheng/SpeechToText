# Mô tả bảng users: có 6 cột lần lượt là: 
# id, tên đăng nhập, mật khẩu, fullname,
# cur_id: id của câu tiếp theo chuẩn bị thu
# role: vai trò của người dùng: 1: admin (được lưu vào database ngay từ đầu)/ 0: người dùng bình thường

import sqlite3

conn = sqlite3.connect("transcripts.db")
c= conn.cursor()
# c.execute(""" create table users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username text,
#     password text unique,
#     fullname text,
#     cur_id int,
#     role int,
#     skip_sens text
# )""")
# # Tao tai khoan admin
# c.execute("insert into users values(1,'trangyeushin','trangtrang','Nguyễn Huyền Trang',0,1,'')")
# c.execute("drop table users")
# c.execute("delete from users where id >0")
c.execute("select * from users")
# c.execute("select id from users where username = 'trangyeushin'")
print(c.fetchall())
# id_arr=c.fetchall()
# user_id =9
# c.execute("select fullname from users where id = {0}".format(user_id))
# fullname = c.fetchone()[0]
# print(fullname)
# # print(id[0])
# try:
#     id = id_arr[0][0]
#     print(id)
# except:
#     print("No")
conn.commit()
conn.close()


