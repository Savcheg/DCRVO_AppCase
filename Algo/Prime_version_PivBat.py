#ИМПОРТ БИБЛИОТЕК
import imaplib, email
import pymorphy2
import re
import string
import codecs

import codecs
import imaplib
import email
from email.header import decode_header
import webbrowser
import os
from dateutil.parser import parse
import datetime
#ВВОД ПАРАМЕТРОВ ВХОДА В ПОЧТУ
user = 'vip.vasapupkin10@gmail.com'
password = 'fyfyfc2003'
imap_url = 'imap.gmail.com'
#ПОДКЛЮЧЕНИЕ К ПОЧТЕ
con = imaplib.IMAP4_SSL(imap_url)
con.login(user,password)
#ОТКРЫВАЕМ ПОЧТУ И СМОТРИМ НАЛИЧИЕ НОВЫХ СООБЕНИЙ
status, messages = con.select("INBOX")
imap_server = imaplib.IMAP4_SSL("imap.gmail.com",993)
imap_server.login(user, password)
imap_server.select('INBOX')
status, response = imap_server.status('INBOX', "(UNSEEN)")
left_index = str(response[0]).find('UNSEEN') + 7
right_index = str(response[0]).rfind(')')
response[0] = str(response[0])[left_index : right_index]
unreadcount = int(response[0])
messages = int(messages[0])
#НАЧАЛО РАБОТЫ С БАЗОЙ ДАННЫХ
import sqlite3
conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
#ФУНЦИЯ ВВОДА ЗНАЧЕНИЙ В БАЗУ ДАННЫХ
def insert_task(subject, body, reporter,
                            implementor, report_date, due_date, status, 
                            _id, department, problem_type, importance):
    conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    query = '''
    INSERT INTO tasks
                      VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}", "{9}", "{10}")
    '''
    cursor.execute(query.format(subject, body, reporter,
                            implementor, report_date, due_date, status, 
                            _id, department, problem_type, importance))
    conn.commit()
    conn.close()
#ВЫВОД БД В ПИТОНЕ
query = '''
select
    *
from tasks
'''
for row in cursor.execute(query):
    print(row)
#ФУНКЦИИ ДЛЯ ОБРАБОТКИ ТЕКСТА
def delete_punc(s):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    return regex.sub('', s)
def to_normal(input_data):
    import pymorphy2
    morph = pymorphy2.MorphAnalyzer()
    result = pd.DataFrame(columns=['Raw', 'Normalized', 'Tags'])
    input_data = input_data.split()
    for i in input_data:
        parsed = morph.parse(i)
        result = result.append({'Raw' : i, 'Normalized' : parsed[0].normal_form, 'Tags' : parsed[0].tag}, ignore_index=True)
    return result
def get_lines(body_task):
    fileObj = body_task
    result = []
    for line in fileObj.split('\n'):
        result.append(line)
    return result
def get_normal_form_of_prefix_line(lines):
    special_symb = '!@#$%^&*"":* \t'
    result = []
    for line in lines:
        uk = 0;
        for c in line:
            if (c in special_symb):
                uk += 1
            else:
                break
        while (len(line) > 0 and line[-1] in special_symb):
            line = line[:len(line) - 1]
        if (uk != len(line)):
            result.append(line[uk:])
    return result
def check_is_date(string):  # xx.xx.xxxx считаем что даты полные, потом можно допилить
    mn_arr = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    digits = '0123456789'
    count = 0
    for i in range(len(string)):
        if (i == 2 or i == 5):
            if (string[i] == '.' or string[i] == '/' or string[i] == '\\' or string[i] == '-'):
                count += 1
        else:
            if (digits.find(string[i]) != -1):
                count += 1
    if (count != len(string)):
        return False
    s = string
    day = int(s[0] + s[1])
    month = int(s[3] + s[4])
    year = int(s[6] + s[7] + s[8] + s[9])
    if (year < 2019):
        return False
    if (year > 2099):
        return False
    if (month > 12):
        return False
    if (month != 2):
        if (mn_arr[month - 1] < day):
            return False
        else:
            return True
    if (month == 2):
        if (year % 4 == 0):
            if (mn_arr[month - 1] + 1 < day):
                return False
            else:
                return True
        else:
            if (mn_arr[month - 1] < day):
                return False
            else:
                return True
    return False;
def less_date(a, b): # true if a <= b
    day_a = int(a[0] + a[1])
    month_a = int(a[3] + a[4])
    year_a = int(a[6] + a[7] + a[8] + a[9])
    
    day_b = int(b[0] + b[1])
    month_b = int(b[3] + b[4])
    year_b = int(b[6] + b[7] + b[8] + b[9])
    if (year_a < year_b):
        return True
    if (year_a > year_b):
        return False
    if (month_a < month_b):
        return True
    if (month_a > month_b):
        return False
    return a <= b;
def get_tasks(words_example, lines):
    words = words_example
    words.append(":")
    digits = '0123456789'
    word_of_theme = ['Приказ', 'приказ', 'заявление', 'Заявление', 'уведомление', 'Уведомление', 'Напоминание', 'напоминание']
    theme = '';
    date = '00.00.0000'
    next_line = False
    tasks = []
    for line in lines:
        for word in word_of_theme:
                if (line.find(word) != -1 and theme == ''):
                    theme = word
        if (next_line):
            tasks.append(line)
            next_line = False
            continue
        if (len(line) > 3):
            if ((line[0] in digits) and ((line[1] == '.') or (line[1] == ')'))):
                tasks.append(line)
            elif ((line[0] in digits) and (line[1] in digits) and ((line[2] == '.') or (line[2] == ')'))):
                tasks.append(line)
            else:
                min_index = len(line)
                max_index = -1
                for word in words:
                    if (line.find(word) != -1):
                        index = line.find(word)
                        if (min_index > index):
                            max_index = index + len(word)
                            min_index = index
                if (max_index == -1):
                    continue
                if (max_index + 5 > len(line)):
                    next_line = True
                else:
                    tasks.append(line[min_index:])
    return tasks
def get_date(lines):
    date = '00.00.0000'
    for line in lines:
        for i in range(0, len(line) - 9):
            if (check_is_date(line[i : i + 10])):
                if (less_date(date, line[i : i + 10])):
                    date = line[i : i + 10]
    return date
def main(body_task):
    global re
    global string
    global codecs
    global pd
    import re
    import string
    import codecs
    import pandas as pd
    input_data = body_task
    input_data = delete_punc(input_data)
    normalized = to_normal(input_data)
    
    infinities = []
    for i in normalized.index:
        if ('INFN' in normalized.loc[i, 'Tags']) or ('impr' in normalized.loc[i, 'Tags']):
            infinities.append(normalized.loc[i, 'Raw'])
            
    lines = get_lines(body_task)
    lines = get_normal_form_of_prefix_line(lines)
    tasks = get_tasks(infinities, lines)
    deadline = get_date(lines)
    return (tasks, deadline)
#ФОРМИРОВАНИЕ ID ДЛЯ ЗАДАЧИ
def idshnik(): 

    conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    query = '''
    select
        max(id)
    from tasks
    '''
    cursor.execute(query)
    conn.commit()
    try:
        for row in cursor.execute(query):
            id_el = row[0]+1
    except:
        id_el = 1
    return id_el;
#ПРОВЕРКА НА НАЛИЧИЕ НОВЫХ СООБЩЕНИЙ, И ДОБАВЛЕНИЕ ДАННЫХ ПИСЕМ В SQL
if unreadcount != 0:
    for i in range(messages, messages-unreadcount, -1):
        # fetch the email message by ID
        res, msg = con.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject = msg['Subject']
                if subject != None: 
                    subject = decode_header(subject)[0][0]
                    if isinstance(subject, bytes):
                        try:
                            subject = subject.decode('utf-8')
                        except:
                            subject = subject.decode('cp1251')
                left_index = msg['From'].rfind('<') + 1
                right_index = msg['From'].rfind('>')
                from_ = msg['From'][left_index : right_index]
                print("Subject:", subject)
                print("From:", from_)
                body_task = ''
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body_task = body
                            print(body)
                else:
                    content_type = msg.get_content_type()
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        body_task = body
                        print(body)
                reporter = from_
                implementor = user
                report_date = parse(msg['Date']).date()
                due_date = main(body_task)[1]
                status = 'To_do'
                _id = idshnik()
                department = ''
                perevod = main(body_task)
                due_date = perevod[1]
                if len(perevod)!=0:
                    problem_type = perevod[0]
                else:
                    problem_type = 'Задача неопределена'
                print(problem_type)
                importance = 'Hz'
                insert_task(subject, body_task, reporter,
                                 implementor, report_date, due_date, status, 
                                 _id, department, problem_type, importance)
                print("="*100)
else:
    print('нет непрочитанных сообщений')    
    
    
    
    
