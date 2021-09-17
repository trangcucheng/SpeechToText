# tạo bảng transcripts
import sqlite3


conn = sqlite3.connect('transcripts.db')

c= conn.cursor()

# c.execute("""CREATE TABLE transcripts (
#      sen_id int primary key,
#      sen_content text
#  )
#  """)

# with open("transcript_1.txt", "r", encoding='UTF-8') as f:
#      lines = f.readlines()
#      id =-1
#      for line in lines:
#      #    print(line)
#          id = id+1
#          to_db = (id, line)
#          c.execute("INSERT INTO transcripts VALUES(?, ?)", to_db)
#          conn.commit()


# c.execute("SELECT * FROM transcripts where sen_id <10 and sen_id >5")
# # print(c.fetchmany(10))
# result = c.fetchall()
# print(result)
# print(len(result))
# for item in result:
#     print(item[1])
# c.execute("select * from transcripts")
#  ===== : tạo thêm cột save_folder để lưu địa chỉ folder mà mỗi file ghi âm của câu đấy đc lưu vào
# try:
#     c.execute("""ALTER TABLE transcripts 
#         ADD COLUMN save_folder TEXT
#     """)
#     conn.commit()
# except:
#     conn.rollback()

# c.execute("select save_folder from transcripts where sen_id =0 ")

# save_folder = c.fetchone()[0]
# if not save_folder:
#     print("No!")
# c.execute("select * from transcripts where save_folder != '' "
c.execute("select * from transcripts ")
arr = c.fetchall()
for item in arr:
    if item[2]: 
        print(item[2])
print(c.fetchall())
conn.commit()
conn.close()
