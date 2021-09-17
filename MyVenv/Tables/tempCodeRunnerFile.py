c.execute("""CREATE TABLE relationships (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     user_id int,
     sen_id int,
     save_dir_url,
     foreign key(user_id) references users(user_id),
     foreign key(sen_id) references transcripts(sen_id)
 )
 """)