import os
from sqlite3.dbapi2 import SQLITE_UPDATE, connect
from flask import Flask, render_template, flash, request, redirect,send_file, url_for, session
import sqlite3
import re
import os
from flask.helpers import total_seconds
import librosa
from werkzeug.utils import secure_filename
from flask import jsonify
from thongke_each import get_each_info


app = Flask(__name__)
app.config['SECRET_KEY'] = '1234567891011121'

app.config['UPLOAD_FOLDER'] = os.getcwd()+ '/static/audios'

conn = sqlite3.connect('transcripts.db')
c= conn.cursor()
c.execute("SELECT * FROM transcripts")
dict_sentences = c.fetchall()
all_sens_num = len(dict_sentences)
conn.commit()
conn.close()


@app.route("/", methods=['POST', 'GET'])
def index():
    if 'id' in session:
        id = session['id']
        with sqlite3.connect("transcripts.db") as conn:
            try:
                c = conn.cursor()
                c.execute("select fullname from users where id ={0}".format(id))
                fullname = c.fetchone()[0]
                c.execute("select role from users where id ={0}".format(id))
                role = c.fetchone()[0]
                print(role)
            except:
                conn.rollback()
            conn.commit()
        # return redirect(url_for("record", id = id, fullname =fullname))
        if (role == 1):
            return redirect("/thongke_admin")
        return redirect("/record")

    else:
        return render_template('login.html', title="Đăng nhập")
@app.route("/login", methods=['POST','GET'])
def login():
    # if form.validate_on_submit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        # kiểm tra xem đã tồn tại tài khoản này chưa (kiểm tra ở bảng users)
        with sqlite3.connect("transcripts.db") as conn:
            c = conn.cursor()
            c.execute("select id from users where username = '{0}' and password = '{1}'".format(username, password))
            id_arr = c.fetchall()
            try:
                id = id_arr[0][0]
                 # nếu đã tồn  tại tài khoản => lưu id vào session, đến trang record
                session['id']=id
                session['username'] = username
                # print(session['id'])
                c.execute("select fullname from users where id = {0}".format(id))
                fullname = c.fetchone()[0]
                c.execute("select cur_id from users where id = {0}".format(id))
                cur_id = c.fetchone()[0]
                session['cur_id'] = cur_id
                print(fullname)
                c.execute("select role from users where id ={0}".format(id))
                role = c.fetchone()[0]
                print(role)
                conn.commit()
                flash('Đăng nhập thành công!','success')
                # return redirect(url_for("record", id = id, fullname =fullname))
                if (role ==1):
                    return redirect("/thongke_admin")
                return redirect("/record")
                
            except: 
                conn.rollback()         
                # trường hợp chưa có tài khoản => đến trang đăng ký
                flash('Tài khoản chưa được đăng ký!','danger')
                return render_template('register.html', title = "Đăng ký")
        # return render_template('login.html',title = "Đăng nhập")

@app.route("/register", methods=['POST','GET'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username'] 
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if (confirm_password!=password):
            flash('Mật khẩu không khớp!','danger')
            return redirect(request.url)

        with sqlite3.connect("transcripts.db") as conn:
            try:
                c = conn.cursor()
                c.execute("insert into users(username, password, fullname,cur_id, role, skip_sens) values(?,?,?,?,?,?)",(username,password,fullname,0,0,''))
                c.execute("select id from users where username = '{0}' and password='{1}'".format(username, password))
                id = c.fetchone()[0]
                c.execute("select cur_id from users where id = {0}".format(id))
                cur_id = c.fetchone()[0]
                session['id']=id
                session['username'] = username
                session['cur_id'] = cur_id

                conn.commit()
            except:
                conn.rollback()
        
        flash('Đăng ký thành công!','success')
        # return redirect(url_for("record", id = id, fullname =fullname))
        return redirect("/record")

    return render_template('register.html', title = "Đăng ký")

@app.route("/record", methods=['POST', 'GET'] )
def record():
    #  lấy id của user hiện tại để kiểm tra 
    id = session.get('id')
    cur_id = session['cur_id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        # lấy thông tin của user hiện tại
        c.execute("select * from users where id={0}".format(id))
        user = c.fetchone()
        fullname = user[3]
        username = user[1]
        cur_id_next = cur_id+4
        sen_id = [] # mảng chứa id của các câu được show lên
        for i in range(cur_id, cur_id_next+1):
            sen_id.append(i)
            folder_name = "sentence_"+ str(i)
            # kiểm tra trong bảng transcripts câu này đã có save_folder chưa
            c.execute("select save_folder from transcripts where sen_id ={0}".format((i)))
            save_folder = c.fetchone()[0]
            # nếu chưa có save_folder: update bảng transcripts
            if not save_folder:
                try:
                    c.execute("update transcripts set save_folder ='{0}' where sen_id={1} ".format(folder_name,i))
                except:
                    conn.rollback()
                    print("can not add folder_name to transcripts")
            folder_upload = os.path.join(str(app.config['UPLOAD_FOLDER']),folder_name)
            if not os.path.exists(folder_upload):
                os.mkdir(folder_upload)
        # lấy mảng các câu để show lên record
        c.execute("select count(save_dir_url) from relationships where user_id ={0}".format(id))
        complete_sens = c.fetchone()[0] # số câu đã thu
        c.execute("select * from transcripts where sen_id >= {0} and sen_id <={1}".format(cur_id, cur_id_next))
        sens_arr = c.fetchall()
        sens_arr_number = len(sens_arr)
        # cur_id_next= cur_id_next+1
        # try:
        #     c.execute("update users set cur_id = {0} where id = {1}".format(cur_id_next,id))
        #     c.execute("select * from transcripts ")
        #     all_sens_num = len(c.fetchall())  # tổng số các câu trong db
        # except:
        #     conn.rollback()
        # finally:
        #     conn.commit()
        skip_sens_str_arr =re.split(",",user[6])   # string chứa id của những câu bị bỏ qua, lưu dưới dạng chuỗi, mỗi id cách nhau bởi dấu phẩy
        skip_sens_str_arr.pop()
        skip_sens_arr=[]
        for item in skip_sens_str_arr:
            skip_sens_arr.append(int(item))
        skip_sens = len(skip_sens_arr)  # số câu đã bỏ qua
        left_sens = all_sens_num -complete_sens - skip_sens  #số câu còn lại
       
    return render_template('record.html', title = "Thu âm",skip_sens_arr = skip_sens_arr, id=id, sens_arr= sens_arr,sens_arr_number=sens_arr_number, skip_sens = skip_sens, complete_sens = complete_sens, left_sens = left_sens,fullname=fullname, sen_id= sen_id, username=username)

@app.route("/save_audios", methods=['POST'])
def save_audios():
    if request.method =='POST':
        username = session['username']
        user_id = session['id']
        files = request.files.getlist('audio_data')
        if files.count ==0:
            flash('No file selected for uploading!')
            return redirect(request.url)
        else:
            print(files)
            for file in files:
                if file:
                    filename= secure_filename(file.filename)
                    file_name_temp1=filename
                    file_name_temp2 = ".".join(file_name_temp1.split(".")[:-1])
                    sen_id = int(file_name_temp2.split("_")[-1])  # lấy được sen_id => tìm folder 
                    folder_name = "sentence_"+ str(sen_id)
                    folder_upload = os.path.join(str(app.config['UPLOAD_FOLDER']), folder_name)
                    # lưu file vào folder_upload
                    file.save(os.path.join(folder_upload,filename))

                    # lưu đường dẫn tới file vào relationships
                    path_to_file = os.path.join(folder_name,filename)
                    with sqlite3.connect("transcripts.db") as conn:
                        c = conn.cursor()
                        try:
                            c.execute("insert into relationships(user_id, sen_id, save_dir_url) values(?,?,?)",(user_id,sen_id,path_to_file))
                        except:
                            conn.rollback()
                        finally:
                            conn.commit()

            return jsonify({"upload": "Success"})

@app.route('/nghethu_each/<int:id>', methods = ['GET', 'POST'])
def nghethu_each(id):
    if not id:
        id = session['id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id = {0}".format(id))
        fullname = c.fetchone()[0]
    global dur_item, files_path, sens_id_arr            
    dur_item, files_path, sens_id_arr = get_each_info(id)
    upload_file = request.files.getlist('files_path')
    total_duration = "{:.2f}".format(dur_item/3600)

    sens_id_arr, files_path = zip(*sorted(zip(sens_id_arr, files_path)))
    global dict_sentences
    transcripts = []
    print(sens_id_arr)
    for i in sens_id_arr:
        transcripts.append(dict_sentences[i][1])

    # for dict_sentence in dict_sentences:
    #     if dict_sentence[0] == int(sens_id_arr[i]):
    #         transcripts.append(dict_sentence[1])
    #         print(dict_sentence[1])
    #         i = i + 1
    #         if i == len(sens_id_arr):
    #             break
    return render_template("nghethu_each.html", id = id,fullname = fullname, complete_sens = len(sens_id_arr), total_duration = total_duration, sens_id_arr = sens_id_arr, transcripts = transcripts, files_path = files_path )

@app.route("/skip_show/<int:id>")
def skip_show(id):
    id = session['id']
    username = session['username']
    cur_id = session['cur_id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id = {0}".format(id))
        fullname = c.fetchone()[0]
        c.execute("select count(save_dir_url) from relationships where user_id ={0}".format(id))
        complete_sens = c.fetchone()[0] # số câu đã thu
        c.execute("select skip_sens from users where id ={0}".format(id))
        skip_sens_str = c.fetchone()[0]
        skip_sens_str_arr =re.split(",",skip_sens_str)   # string chứa id của những câu bị bỏ qua, lưu dưới dạng chuỗi, mỗi id cách nhau bởi dấu phẩy
        skip_sens_str_arr.pop()  # xóa phần tử rỗng bị thừa ở cuối mảng ['1','2','']
        sen_id=[] # mảng chứa id của các câu bị bỏ qua
        for item in skip_sens_str_arr:
            sen_id.append(int(item))
        skip_sens_content = []
        for item in sen_id:
            c.execute("select sen_content from transcripts where sen_id = {0}".format(item))
            skip_sens_content.append(c.fetchone()[0])
    skip_sens = len(sen_id)  # số câu đã bỏ qua
    left_sens = all_sens_num -complete_sens - skip_sens   # số câu còn lại phải thu
    return render_template('skip_show.html', username = username, id = id, fullname = fullname, sen_id = sen_id, complete_sens = complete_sens, skip_sens = skip_sens, left_sens= left_sens, skip_sens_content = skip_sens_content)

@app.route("/upload_skip")
def upload_skip():
    id = session['id']
    username = session['username']
    cur_id = session['cur_id']
    print("cur_id in upload_Skip")
    print(cur_id)
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id = {0}".format(id))
        fullname = c.fetchone()[0]
        # lấy danh sách id những câu đã được ghi âm rồi
        complete_sens_arr = []
        c.execute("select save_dir_url from relationships where user_id ={0}".format(id))
        for item in (c.fetchall()):
            temp = ".".join(item[0].split(".")[:-1])
            sen_id = int(temp.split("_")[-1])  # lấy được sen_id 
            complete_sens_arr.append(sen_id)
        complete_sens = len(complete_sens_arr)    # số câu đã thu âm  

        sen_id=[] # mảng chứa id của các câu bị bỏ qua
        sens_id_str = '' #chuỗi chứa id của các câu bị bỏ qua để đẩy vào users
        for i in range(0, cur_id):
            if i not in complete_sens_arr:
                sen_id.append(i)
                sens_id_str = sens_id_str + str(i)+','
        try:
            c.execute("update users set skip_sens = '{0}' where id ={1}".format(sens_id_str,id))
        except:
            conn.rollback()
        skip_sens_content = []
        for item in sen_id:
            c.execute("select sen_content from transcripts where sen_id = {0}".format(item))
            skip_sens_content.append(c.fetchone()[0])
    skip_sens = len(sen_id)  # số câu đã bỏ qua
   
    left_sens = all_sens_num -skip_sens - complete_sens   # số câu còn lại phải thu
    return render_template('skip_show.html', username = username, id = id, fullname = fullname, sen_id = sen_id, complete_sens = complete_sens, skip_sens = skip_sens, left_sens= left_sens, skip_sens_content = skip_sens_content)
@app.route("/thongke_admin")
def thongke_admin():
    id = session['id']
    cur_id = session['cur_id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id ={0}".format(id))
        fullname = c.fetchone()[0]
        conn.commit()

    # lấy thông tin của người dùng
    users_info = []
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select * from users")
        users_arr= c.fetchall()
        print(users_arr)
        for item in users_arr:
            if (item[0]!=1):
                user=[]
                user.append(item[0]) # id
                user.append(item[1]) #username
                user.append(item[3]) #fullname
                complete_sens_arr = []
                c.execute("select save_dir_url from relationships where user_id ={0}".format(item[0]))
                for i in (c.fetchall()):
                    temp = ".".join(i[0].split(".")[:-1])
                    sen_id = int(temp.split("_")[-1])  # lấy được sen_id 
                    complete_sens_arr.append(sen_id)
                
                user.append(len(complete_sens_arr)) # số câu đã thu
                count=0 #biến count lưu số câu bị bỏ qua
                for i in range(0, item[4]):
                    if i not in complete_sens_arr:
                        count = count+1
                user.append(count)
                user.append(all_sens_num - len(complete_sens_arr)-count) # số câu còn lại
                users_info.append(user)
    sentences_info = []
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select * from transcripts ")
        arr = c.fetchall()
        for item in arr:
            # nếu tồn tại save_folder của câu này ( đã được lưu rồi)
            if item[2]: # sentence_01 - tên của folder lưu các file ghi âm của từng câu
                folder_save = os.path.join(str(app.config['UPLOAD_FOLDER']),item[2])
                files_arr=os.listdir(folder_save) # mảng lưu tên file của các files ghi âm từng câu ['namcute_11_55.wav', 'namcute_2_55.wav']
                # nếu câu này có người thu rồi
                if len(files_arr):
                    sentence=[] 
                    sentence.append(item[0]) #id của câu
                    sentence.append(item[1]) # nội dung của câu
                    sentence.append(len(files_arr)) # số người dùng đã thu
                    sentences_info.append(sentence)
    return render_template("thongke_admin.html", id = id, fullname = fullname, users_info = users_info, sentences_info = sentences_info)
@app.route("/export_lst_user")
def export_lst_user():
    global files_path, sens_id_arr
    sens_id_arr, files_path = zip(*sorted(zip(sens_id_arr, files_path)))
    transcripts = []
    global dict_sentences
    for id in sens_id_arr:
        transcripts.append(dict_sentences[id][1])
    duration = []
    for file_path in files_path:
        duration.append(round(librosa.duration(filename=file_path),2))
    with open("static/collect_data_web.lst","w+",encoding="utf-8" ) as f_write:
        for i in range(0,len(sens_id_arr)):
            f_write.write("collect_data"+str(i)+"\t"+files_path[i]+"\t"+str(duration[i])+"\t"+transcripts[i])
    return send_file("static/collect_data_web.lst", as_attachment=True)

@app.route("/export_lst_sentence")
def export_lst_sentence():
    
# @app.route("/thongke_admin")
# def thongke_admin():
@app.route("/skip")
def skip():
    id = session['id']
    cur_id = session['cur_id']
    print("trong skip")
    print(cur_id)
    cur_id = cur_id+5
    session['cur_id'] = cur_id
    with sqlite3.connect("transcripts.db") as conn:
        try:
            c = conn.cursor()
            c.execute("select skip_sens from users where id = {0}".format(id))
            skip_str = c.fetchone()[0]
            print(skip_str)
            for i in range(cur_id, cur_id+5):
                skip_str = skip_str + str(i) +','
            c.execute("update users set skip_sens = '{0}' where id = {1}".format(skip_str,id))
            c.execute("update users set cur_id = '{0}' where id = {1}".format(cur_id,id))
            c.execute("select skip_sens from users where id ={0}".format(id))
            skip_sens_str = c.fetchone()[0]
            conn.commit()
        except:
            conn.rollback()
    
    skip_sens_str_arr =re.split(",",skip_sens_str)   # string chứa id của những câu bị bỏ qua, lưu dưới dạng chuỗi, mỗi id cách nhau bởi dấu phẩy
    skip_sens_str_arr.pop()  # xóa phần tử rỗng bị thừa ở cuối mảng ['1','2','']
    skip_sens_arr=[]
    for item in skip_sens_str_arr:
        skip_sens_arr.append(int(item))
    skip_sens = len(skip_sens_arr)  # số câu đã bỏ qua
    complete_sens = cur_id-skip_sens  # số câu đã thu 
    left_sens = all_sens_num -cur_id   # số câu còn lại phải thu
   
    return redirect(url_for('record',left_sens = left_sens, complete_sens = complete_sens, skip_sens = skip_sens))
    

@app.route("/upload_continue")
def upload_continue():
    id = session['id']
    cur_id = session['cur_id']
    session['cur_id'] = cur_id +5
    print("trong continue")
    print(cur_id+5)
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        try:
            c.execute("update users set cur_id = '{0}' where id = {1}".format(cur_id +5,id))
            conn.commit()
        except:
            conn.rollback()
        c.execute("select skip_sens from users where id ={0}".format(id))
        skip_sens_str = c.fetchone()[0]
        skip_sens_str_arr =re.split(",",skip_sens_str)   # string chứa id của những câu bị bỏ qua, lưu dưới dạng chuỗi, mỗi id cách nhau bởi dấu phẩy
        skip_sens_str_arr.pop()  # xóa phần tử rỗng bị thừa ở cuối mảng ['1','2','']
        skip_sens_arr=[]
        for item in skip_sens_str_arr:
            skip_sens_arr.append(int(item))
        skip_sens = len(skip_sens_arr)  # số câu đã bỏ qua
        complete_sens = cur_id-skip_sens  # số câu đã thu 

        left_sens = all_sens_num -cur_id 
    return redirect(url_for('record',left_sens = left_sens, complete_sens = complete_sens, skip_sens = skip_sens))

@app.route("/logout")
def logout():
    # xóa id, username khỏi session
    session.pop('id')
    session.pop('username')
    # return render_template('login.html',title="Đăng nhập")
    return render_template('login.html')
if (__name__ == "__main__"):
   app.run(debug=True) 
