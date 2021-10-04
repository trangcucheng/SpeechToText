from sqlite3.dbapi2 import SQLITE_UPDATE, connect
from flask import Flask, json, render_template, flash, request, redirect,send_file, url_for, session
from flask.helpers import total_seconds
from werkzeug.utils import secure_filename
from flask import jsonify
from wtforms.validators import ValidationError
from thongke_each import get_each_info
import os
import sqlite3
import re
import time
import librosa


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

@app.route("/")
@app.route("/home")
def home():
    if 'id' in session:
        id = session['id']
        with sqlite3.connect("transcripts.db") as conn:
            try:
                c = conn.cursor()
                c.execute("select fullname from users where id ={0}".format(id))
                fullname = c.fetchone()[0]
                c.execute("select role from users where id ={0}".format(id))
                role = c.fetchone()[0]
            except:
                conn.rollback()
            conn.commit()
        # return redirect(url_for("record", id = id, fullname =fullname))
        if (role == 1):
            return redirect("/admin")
        return redirect("/record")
    return render_template("home.html")

@app.route("/admin")
def admin():
        
        path_to_folders = os.path.join(str(app.config['UPLOAD_FOLDER']))
        folders_arr = os.listdir(path_to_folders)
        # lấy ra số tin nhắn chưa được phản hồi
        id = session['id']
        cur_id = session['cur_id']
        with sqlite3.connect("transcripts.db") as conn:
            c = conn.cursor()
            c.execute("select * from messages where isCheck = 0")
            msg_arr = c.fetchall()
            c.execute("select fullname from users where id ={0}".format(id))
            fullname = c.fetchone()[0]

            c.execute("select save_dir_url from relationships")
            arr = c.fetchall()
            conn.commit()
            recorded_sen =[]  #những câu đã thu rồi
            for item in arr:
                temp1=item[0].split("_")
                temp2= temp1[3].split(".")
                id = int(temp2[0])
                recorded_sen.append(id)
            max_sen = max(recorded_sen)  # câu lớn nhất thu được
            print(recorded_sen)
            skipped_sen=[] # những câu bị bỏ qua (thống kê tổng quát, k kể người dùng)
            for i in range(0,max_sen+1):
                if i not in recorded_sen:
                    skipped_sen.append(i)
            
            sentences_info=[]

            c.execute("select * from transcripts ")
            arr = c.fetchall()
            for item in arr:
                # nếu tồn tại save_folder của câu này ( đã được lưu rồi)
                if item[2]: # sentence_01 - tên của folder lưu các file ghi âm của từng câu
                    folder_save = os.path.join(str(app.config['UPLOAD_FOLDER']),item[2])
                    if os.path.exists(folder_save):
                        files_arr=os.listdir(folder_save) # mảng lưu tên file của các files ghi âm từng câu ['namcute_11_55.wav', 'namcute_2_55.wav']
                        # nếu câu này có người thu rồi
                        if len(files_arr):
                            sentence=[] 
                            sentence.append(item[0]) #id của câu
                            sentence.append(item[1].capitalize()) # nội dung của câu
                            sentence.append(len(files_arr)) # số người dùng đã thu
                            sentences_info.append(sentence)
            #  câu còn lại
        remain_per = all_sens_num - len(skipped_sen)- len(sentences_info)
       
        
        return render_template("admin.html", fullname = fullname, sentences_info = sentences_info, complete_per= len(sentences_info), skip_per = len(skipped_sen), remain_per= remain_per, all_sens_num = all_sens_num, createdFolders =len(folders_arr))


@app.route("/admin_post", methods=['POST','GET']) 
def admin_post():
    if request.method == 'POST':
        num = int(request.form['folders_num'])
        print("Da thuc hien")
        print(num)
        path_to_folders = os.path.join(str(app.config['UPLOAD_FOLDER']))
        folders_arr = os.listdir(path_to_folders)
        for i in range(len(folders_arr), len(folders_arr)+num ):
                folder_name = "sentence_"+str(i)
                print(folder_name)
                folder_upload = os.path.join(str(app.config['UPLOAD_FOLDER']),folder_name)
                print(folder_upload)
                os.mkdir(folder_upload)
    return redirect("/admin")
        
@app.route("/login", methods=['POST','GET'])
def login():
    # if form.validate_on_submit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # kiểm tra xem đã tồn tại tài khoản này chưa (kiểm tra ở bảng users)
        with sqlite3.connect("transcripts.db") as conn:
            c = conn.cursor()
            c.execute("select id from users where username = '{0}' and password = '{1}'".format(username, password))
            id_arr1 = c.fetchall()
            c.execute("select id from users where username='{0}' or password='{1}'".format(username, password))
            id_arr2= c.fetchall()
            if (len(id_arr2)!=0):
                #  trường hợp người dùng chỉ nhập đúng mật khẩu hoặc tên đăng nhập
                if (len(id_arr1)==0):
                    flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
                    return redirect("/")
                else:
                    id = id_arr1[0][0]
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
                        # return redirect(url_for("record", id = id, fullname =fullname))
                    if (role ==1):
                        return redirect("/admin")
                    return redirect("/record")
        
            else:         
                # trường hợp chưa có tài khoản => đến trang đăng ký
                flash('Tài khoản chưa được đăng ký!','error')
                return render_template("register.html",title = "Đăng ký")
    # return render_template('login.html',title = "Đăng nhập")
    return render_template("login.html")

@app.route("/register", methods=['POST','GET'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username'] 
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if (confirm_password!=password):
           flash('Mật khẩu không khớp!', 'error')
           return redirect("/register")
        with sqlite3.connect("transcripts.db") as conn:
            c = conn.cursor()
            c.execute("select * from users where username='{0}' and password='{1}'".format(username, password))
            if (len(c.fetchall())!=0):
               flash('Tài khoản này đã tồn tại, vui lòng đăng ký một tài khoản khác!', 'error')
               return redirect("/register")

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
        
        return redirect("/record")

    return render_template('register.html')

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/upload_msg", methods=['POST'])
def upload_msg():
    if request.method == 'POST':
        email = request.form['email']
        msg = request.form['message'] 
        with sqlite3.connect("transcripts.db") as conn:
            c = conn.cursor()
            try:
                c.execute("insert into messages(email,msg) values(?,?)",(email,msg))
            except:
                conn.rollback()
    return redirect("/")

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
            # folder_upload = os.path.join(str(app.config['UPLOAD_FOLDER']),folder_name)
            # if not os.path.exists(folder_upload):
            #     os.mkdir(folder_upload)
        # lấy mảng các câu để show lên record
        c.execute("select count(save_dir_url) from relationships where user_id ={0}".format(id))
        complete_sens = c.fetchone()[0] # số câu đã thu
        c.execute("select * from transcripts where sen_id >= {0} and sen_id <={1}".format(cur_id, cur_id_next))
        sens_arr_temp = c.fetchall()
        sens_arr = []
        for sen in sens_arr_temp:
            sen[1].capitalize()
            item = [sen[0],sen[1].capitalize(),sen[2]]
            sens_arr.append(item)

    dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content = get_each_info(id)
    left_sens = all_sens_num -complete_sens - len(skip_sens_id)  #số câu còn lại 
    return render_template('record.html',skip_sens = len(skip_sens_id),skip_sens_id = skip_sens_id, id = id,sens_arr= sens_arr,sens_arr_number=len(sens_arr), complete_sens = complete_sens, left_sens = left_sens,fullname=fullname, sen_id= sen_id, username=username, total_duration = dur_item)

@app.route("/save_audios", methods=['POST'])
def save_audios():
    if request.method =='POST':
        username = session['username']
        user_id = session['id']
        files = request.files.getlist('audio_data')
        if files.count ==0:
            flash(f'No file selected for uploading!')
            return redirect(request.url)
        else:
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
    global dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content            
    dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content = get_each_info(id)
    print(skip_sens_id)
    sens_id_arr, files_path = zip(*sorted(zip(sens_id_arr, files_path)))
    global dict_sentences
    transcripts = []
    for i in sens_id_arr:
        transcripts.append(dict_sentences[i][1].capitalize())
    left_sens = all_sens_num - len(sens_id_arr) - len(skip_sens_id)
    return render_template("nghethu_each.html", id = id,fullname = fullname, complete_sens = len(sens_id_arr), total_duration = dur_item, sens_id_arr = sens_id_arr, transcripts = transcripts, files_path = files_path, skip_sens= len(skip_sens_id), left_sens = left_sens)


@app.route("/listen_each_sentence/<int:id>")
def listen_each_sentence(id): # id là id của câu
    # tạo ra path tới folder lưu câu này
    admin_id = session['id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select save_folder from transcripts where sen_id = {0}".format(id))
        save_folder = c.fetchone()[0]
        c.execute("select fullname from users where id = {0}".format(admin_id))
        admin_fullname = c.fetchone()[0]
        conn.commit()
    path = os.path.join(str(app.config['UPLOAD_FOLDER']), save_folder)
    files_arr = os.listdir(path)
    users_arr = []
    duration = 0
    for file in files_arr:
        #lấy id của người dùng
        user=[]
        temp = re.split("_",file)  #['namcute', '11', '3.wav']
        user_id = int(temp[1])
        user.append(user_id) # lấy id của người dùng
        user.append(temp[0]) # lấy username
        with sqlite3.connect("transcripts.db") as conn:
            c = conn.cursor()
            # lấy fullname của user
            c.execute("select fullname from users where id = {0}".format(user_id))
            fullname = c.fetchone()[0]
            # lấy nội dung của câu
            c.execute("select sen_content from transcripts where sen_id = {0}".format(user_id))
            sen_content = c.fetchone()[0]
            conn.commit()
        user.append(fullname)
        files_path_temp=os.path.join("static/audios",save_folder)

        file_path = os.path.join(str(files_path_temp),file)
        duration = duration + librosa.get_duration(filename = file_path)
        user.append(file_path)
        users_arr.append(user)
    duration = float("{:.2f}".format(duration/3600))
    return render_template('listen_each_sentence.html', fullname = admin_fullname,users_arr=users_arr, id=admin_id,sen_id = id,sen_content = sen_content, num_files = len(users_arr), duration = duration  )
@app.route("/skip_show/<int:id>")
def skip_show(id):
    id = session['id']
    username = session['username']
    cur_id = session['cur_id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id = {0}".format(id))
        fullname = c.fetchone()[0]
    dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content = get_each_info(id)
    left_sens = all_sens_num -len(sens_id_arr) - len(skip_sens_id)  #số câu còn lại 
    return render_template('skip_show.html', username = username, id = id, fullname = fullname, skip_sens_id= skip_sens_id, complete_sens = len(sens_id_arr), skip_sens = len(skip_sens_id), left_sens= left_sens, skip_sens_content = skip_sens_content, total_duration = dur_item)

@app.route("/upload_skip")
def upload_skip():
    id = session['id']
    username = session['username']
    cur_id = session['cur_id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id = {0}".format(id))
        fullname = c.fetchone()[0]
    global dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content
    dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content = get_each_info(id)
    print(skip_sens_id)
    left_sens = all_sens_num -len(skip_sens_id) - len(sens_id_arr)   # số câu còn lại phải thu
    return render_template('skip_show.html', fullname=fullname,id=id,total_duration = dur_item, complete_sens = len(sens_id_arr), skip_sens = len(skip_sens_id), left_sens= left_sens, skip_sens_id = skip_sens_id, skip_sens_content = skip_sens_content)



@app.route("/thongke_admin")
def thongke_admin():
    id = session['id']
    cur_id = session['cur_id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id ={0}".format(id))
        fullname = c.fetchone()[0]
        conn.commit()

    # lấy thông tin của tất cả các câu:
    # global dict_sentences
    # dict_sentences_show=[]
    # with sqlite3.connect("transcripts.db") as conn:
    #     c = conn.cursor()
    #     c.execute("select save_folder from transcripts")
    #     save_dir_arr = c.fetchall()
    #     conn.commit()
    
    # for i in range(0,len(save_dir_arr)):
    #     item=[]
    #     item.append(dict_sentences[0])
    #     item.append(dict_sentences[1])
    #     temp = "static/audios/"+str(save_dir_arr)
    #     item.append(temp)
    #     dict_sentences_show.append(item)
    #  lấy thông tin thống kê theo câu
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select save_dir_url from relationships")
        arr = c.fetchall()
        conn.commit()
        recorded_sen =[]  #những câu đã thu rồi
        for item in arr:
            temp1=item[0].split("_")
            temp2= temp1[3].split(".")
            id = int(temp2[0])
            recorded_sen.append(id)
        max_sen = max(recorded_sen)  # câu lớn nhất thu được
        print(recorded_sen)
        skipped_sen=[] # những câu bị bỏ qua (thống kê tổng quát, k kể người dùng)
        for i in range(0,max_sen+1):
            if i not in recorded_sen:
                skipped_sen.append(i)
        
        sentences_info=[]
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select * from transcripts ")
        arr = c.fetchall()
        for item in arr:
            # nếu tồn tại save_folder của câu này ( đã được lưu rồi)
            if item[2]: # sentence_01 - tên của folder lưu các file ghi âm của từng câu
                folder_save = os.path.join(str(app.config['UPLOAD_FOLDER']),item[2])
                if os.path.exists(folder_save):
                    files_arr=os.listdir(folder_save) # mảng lưu tên file của các files ghi âm từng câu ['namcute_11_55.wav', 'namcute_2_55.wav']
                    # nếu câu này có người thu rồi
                    if len(files_arr):
                        sentence=[] 
                        sentence.append(item[0]) #id của câu
                        sentence.append(item[1].capitalize()) # nội dung của câu
                        sentence.append(len(files_arr)) # số người dùng đã thu
                        sentences_info.append(sentence)
        #  câu còn lại
    remain_per = all_sens_num - len(skipped_sen)- len(sentences_info)
    return render_template("thongke_admin.html", fullname = fullname, sentences_info = sentences_info, complete_per= len(sentences_info), skip_per = len(skipped_sen), remain_per= remain_per, all_sens_num = all_sens_num)
@app.route("/export_xls_user/<int:id>")
def export_xls_user(id):
    if not id:
        id = session['id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id = {0}".format(id))
        fullname = c.fetchone()[0]
    global dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content           
    dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content = get_each_info(id)
    upload_file = request.files.getlist('files_path')
    sens_id_arr, files_path = zip(*sorted(zip(sens_id_arr, files_path)))
    global dict_sentences
    transcripts = []
    duration = []
    for i in sens_id_arr:
        transcripts.append(dict_sentences[i][1])
    for file_path in files_path:
        duration.append(round(librosa.get_duration(filename=file_path),2))

    file_download = "static/collect_data_"+str(id) +".xls"
    with open(file_download,"w+",encoding="utf-8" ) as f_write:
        f_write.write("ID\tDuration\tPath to file\tContent\n")
        for i in range(0,len(sens_id_arr)):
            f_write.write(str(sens_id_arr[i])+"\t"+str(duration[i])+"\t"+files_path[i]+"\t"+transcripts[i].capitalize())
    return send_file(file_download, as_attachment=True)

@app.route("/export_xls_sen/<int:id>")
def export_xls_sen(id): # id là id của câu
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select save_folder from transcripts where sen_id = {0}".format(id))
        save_folder = c.fetchone()[0]
        conn.commit()
    path = os.path.join(str(app.config['UPLOAD_FOLDER']), save_folder)
    files_arr = os.listdir(path)
    users_arr = [] # lấy user_name và user_id
    duration = []
    files_path=[] # mảng lưu đường dẫn tới các file của các câu
    path_to_file =[]
    for file in files_arr:
        #lấy id của người dùng
        user=[]
        temp = re.split("_",file)  #['namcute', '11', '3.wav']
        user_id = int(temp[1])
        user.append(user_id) # lấy id của người dùng
        user.append(temp[0]) # lấy username
        users_arr.append(user)
        file_path = os.path.join(str(path),file)
        files_path.append(file_path)
        duration.append(round(librosa.get_duration(filename=file_path),2))
        file = os.path.join("static/audios",file)
        path_to_file.append(file)
    file_download = "static/collect_sen_"+str(id)+".xls"
    with open(file_download,"w+",encoding="utf-8" ) as f_write:
        f_write.write("stt\tuser_id\tusername\tduration\tpath_to_file:\n")
        for i in range(0,len(files_arr)):
            f_write.write(str(i)+"\t"+str(users_arr[i][0])+"\t"+users_arr[i][1]+"\t"+str(duration[i])+"\t"+path_to_file[i]+"\n")
    return send_file(file_download, as_attachment=True)

@app.route("/download_users")
def download_users():
    users_info=[]
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select id from users where role=0")
        for i in c.fetchall():
            id=i[0]
            user=[]
            user.append(id)  #id
            global dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content
            dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content = get_each_info(id)
            c.execute("select fullname from users where id = {0}".format(id))
            user.append(c.fetchone()[0])
            user.append(len(sens_id_arr))
            user.append(dur_item)
            users_info.append(user)

    file_download = "static/users.xls"
    with open(file_download,"w+",encoding="utf-8" ) as f_write:
        f_write.write("ID\tTên đầy đủ\tSố câu đã thu\tTổng thời gian\n")
        for user in users_info:
            f_write.write(str(user[0])+"\t"+str(user[1])+"\t"+str(user[2])+"\t"+str(user[3])+"\n")

    return send_file(file_download, as_attachment=True)

@app.route("/skip")
def skip():
    id = session['id']
    cur_id = session['cur_id']
    cur_id = cur_id+5
    session['cur_id'] = cur_id
    with sqlite3.connect("transcripts.db") as conn:
        try:
            c = conn.cursor()
            c.execute("select skip_sens from users where id = {0}".format(id))
            skip_str = c.fetchone()[0]
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
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        try:
            c.execute("update users set cur_id = '{0}' where id = {1}".format(cur_id +5,id))
            conn.commit()
        except:
            conn.rollback()
        skip_sens_str = ""
        skip_sens_arr=[]
        complete_sens_arr=[]  # mảng chứa các câu đã được thu rồi
        c.execute("select save_dir_url from relationships where user_id = {0}".format(id))
        for item in c.fetchall():
            item_temp = ".".join(item[0].split(".")[:-1])
            sen_id = int(item_temp.split("_")[-1])
            complete_sens_arr.append(sen_id)
        for i in range(0, cur_id+5):
            if i not in complete_sens_arr:
                skip_sens_arr.append(i)
                skip_sens_str = skip_sens_str + str(i)+","
        with sqlite3.connect("transcripts.db") as conn:
            try:
                c = conn.cursor()
                c.execute("update users set skip_sens = '{0}'".format(skip_sens_str))
                conn.commit()
            except:
                conn.rollback()
        skip_sens = len(skip_sens_arr)  # số câu đã bỏ qua
        complete_sens = len(complete_sens_arr)  # số câu đã thu 

        left_sens = all_sens_num -complete_sens - skip_sens
    return redirect(url_for('record',left_sens = left_sens, complete_sens = complete_sens, skip_sens = skip_sens))

@app.route("/user_collections")
def user_collections():
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
        for item in users_arr:
            if (item[5]!=1):
                user=[]
                user.append(item[0]) # id
                user.append(item[1]) #username
                user.append(item[3]) #fullname
                
                dur_item, files_path, sens_id_arr, skip_sens_id, skip_sens_content = get_each_info(item[0])
                user.append(len(sens_id_arr))  # số câu đã thu
                user.append(len(skip_sens_id))  # số câu bị bỏ qua
                user.append(dur_item)  # thời gian
                users_info.append(user)
    return render_template("user_collections.html", fullname = fullname, users_info = users_info, users_num = len(users_info))

@app.route("/sentences_collections")
def sentences_collections():
    id = session['id']
    cur_id = session['cur_id']
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select fullname from users where id ={0}".format(id))
        fullname = c.fetchone()[0]
        conn.commit()
    sentences_info=[]
    with sqlite3.connect("transcripts.db") as conn:
        c = conn.cursor()
        c.execute("select * from transcripts ")
        arr = c.fetchall()
        for item in arr:
            # nếu tồn tại save_folder của câu này ( đã được lưu rồi)
            if item[2]: # sentence_01 - tên của folder lưu các file ghi âm của từng câu
                folder_save = os.path.join(str(app.config['UPLOAD_FOLDER']),item[2])
                if os.path.exists(folder_save):
                    files_arr=os.listdir(folder_save) # mảng lưu tên file của các files ghi âm từng câu ['namcute_11_55.wav', 'namcute_2_55.wav']
                    # nếu câu này có người thu rồi
                    if len(files_arr):
                        sentence=[] 
                        sentence.append(item[0]) #id của câu
                        sentence.append(item[1].capitalize()) # nội dung của câu
                        sentence.append(len(files_arr)) # số người dùng đã thu
                        sentences_info.append(sentence)
    return render_template("sentences_collections.html", fullname= fullname, sentences_info= sentences_info, sens_num = len(sentences_info))

@app.route("/logout")
def logout():
    # xóa id, username khỏi session
    session.pop('id')
    session.pop('username')
    # return render_template('login.html',title="Đăng nhập")
    return redirect("/")
if (__name__ == "__main__"):
   app.run(debug=True) 
 