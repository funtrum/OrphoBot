# -*- coding: utf-8 -*-
from pymongo import MongoClient
import telepot
from os.path import abspath, expanduser
import time
import re
from datetime import datetime

def getAccent( w ):

    c = MongoClient()
    db = c.telegram
    dict = db.dict

    accent = {u"а":u"а́", u"е":u"е́", u"и":u"и́", "ы":"ы́", u"о":u"о́", u"у":u"у́", u"э":u"э́", u"ю":u"ю́", u"я":u"я́"}

    word = str(w).lower()
    rev = word[::-1]
    e = rev[0:4]

    if e == 'ьшеа' or e == 'ьшея':
        r_word = getAccent(word[0:-3]+'ть')
        return r_word[0:-2]+'ешь'
    else:

        vowels = sum(1 for _ in word if _ in 'аеиыоуэюя')

        if vowels == 1:
            a_word = u""


            for l in word:
                if l in 'аеиыоуэюя':
                    if 'ё' in word:
                        a_word += l
                    else:
                        a_word += accent[l]
                else:
                    a_word += l
            return a_word
        else:
            count = dict.find({'w': word}).count()
            if count == 1:
                cur = dict.find_one({'w': word})
                a = int(cur['a'])-1

                a_word = u""

                i = 0

                for l, al in accent.items():
                    if word[a] == l:
                        a_l = al

                for l in word:
                    if i == a:
                        a_word += a_l
                    else:
                        a_word += l
                    i += 1

                return a_word
            elif count > 1:
                r_word = u"("

                j = 0
                dup = []

                for cur in dict.find({'w': word}):
                    a_word = u""
                    a = int(cur['a'])-1
                    if a not in dup:
                        dup.append(a)
                        i = 0

                        for l, al in accent.items():
                            if word[a] == l:
                                a_l = al

                        for l in word:
                            if i == a:
                                a_word += a_l
                            else:
                                a_word += l
                            i += 1
                        if j != 0:
                            r_word += " | "
                        r_word += a_word
                        j += 1

                r_word += u")"
                return r_word

bot = telepot.Bot('218858639:AAGX3kyiZUYWmQfIw_usrAdtuubqhpsgz1I')

filepath = abspath(expanduser("~/") + '/Documents/orphobot_last_update_id.txt')

last_f = open(filepath)
last_update = last_f.read()
last_f.close()

def getUpdates(u_id):
    response = bot.getUpdates(u_id)
    for item in response:
        update_id = int(item['update_id'])
        u_id = update_id+1
        message = item['message']
        text = str(message['text'])
        chat = message['chat']
        chat_id = chat['id']
        time = str(datetime.now())
        print("%s by %i on %s" % (text, chat_id, time))
        accented = u""

        if text[0] != "/":
            text = re.sub(r'[^а-яА-Я ]',r'',text)
            if " " in text:
                for word in text.split():
                    aWord = getAccent(word)
                    accented += " "
                    if aWord == None:
                        accented += word
                    else:
                        accented += aWord
                bot.sendMessage(chat_id, accented)
            else:
                aWord = getAccent(text)
                if aWord == None:
                    accented = "В моем словаре еще нет такого слова ;("
                else:
                    accented = getAccent(text)
                bot.sendMessage(chat_id, accented)
    last_f = open(filepath, "w")
    last_f.write(str(u_id))
    last_f.close()

    global last_update
    last_update = u_id

while True:
    time.sleep(1)
    getUpdates(last_update)
