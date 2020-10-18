import sqlite3
 
conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
cursor.execute("""CREATE TABLE tasks
                  (subject text, 
                  body text,
                  reporter text,
                  implementor text,
                  report_date text,
                  due_date text,
                  status text,
                  id integer,
                  department text,
                  problem_type text,
                  importance text)
               """)