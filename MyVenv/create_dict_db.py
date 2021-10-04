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

# c.execute("select * from transcripts where sen_id >= 1 and sen_id <=10")
# sens_arr_temp = c.fetchall()
# sens_arr=[]
       
# for sen in sens_arr_temp:
#     sen[1].capitalize()
#     item = [sen[0],sen[1].capitalize(),sen[2]]
#     sens_arr.append(item)
# print(sens_arr)

# c.execute("select save_dir_url from relationships")
# arr = c.fetchall()
# print(arr)
# conn.commit()
# recorded_sen =[]  #những câu đã thu rồi
# for item in arr:
#     temp1=item[0].split("_")
#     # print(len(temp1))
#     temp = str(temp1[3])
#     # print(temp)
#     temp2= temp.split(".")
#     id = int(temp2[0])
#     recorded_sen.append(id)
# max_sen = max(recorded_sen)  # câu lớn nhất thu được
# # print(recorded_sen)
# skipped_sen=[] # những câu bị bỏ qua (thống kê tổng quát, k kể người dùng)
# for i in range(0,max_sen+1):
#     if i not in recorded_sen:
#         skipped_sen.append(i)
c.execute("select * from relationships")
print(c.fetchall())
conn.commit()
conn.close()
