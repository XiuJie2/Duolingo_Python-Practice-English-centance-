# 導入所需的模塊
import json
import pygame
import os
import pyttsx3
import re
import random
import time

# 定義一個常量，存儲json文件的路徑
JSON_FILE = 'C:/Users/Jie/OneDrive/文件/py_project/英语口语/english_sentence.json'

# 定義一個函數，用於讀取json文件，並返回一個字典
def load_json_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 定義一個函數，用於初始化pygame.mixer，並返回兩個聲音對象
def init_mixer():
    pygame.mixer.init()
    right = pygame.mixer.Sound(os.path.join("right.mp3"))
    wrong = pygame.mixer.Sound(os.path.join("wrong.wav"))
    return right, wrong

# 定義一個函數，用於初始化pyttsx3.engine，並設置語速和語音
def init_engine():
    engine = pyttsx3.init()
    rate = engine.getProperty("rate")
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id) # 0為英文，1為中文
    engine.setProperty("rate", 145)
    return engine

# 定義一個函數，用於播放語音
def speak(engine, audio):
    engine.say(audio)
    engine.runAndWait()

# 定義一個函數，用於簡化輸入的文本，刪除非字母數字字符，轉換為小寫並刪除空格
def simplify(input_text):
    s = re.sub(r"[^\w\s]", "", input_text)
    return s.lower().replace(" ", "")

# 定義一個函數，用於練習英語口語
def practice(english_sentence, right, wrong, engine):
    sentence_keys = list(english_sentence.keys()) # 獲取句子列表
    random.shuffle(sentence_keys) # 隨機打亂句子列表
    random_sentence = {key: english_sentence[key] for key in sentence_keys} # 隨機選取一個句子
    erros = {} # 用於存儲錯誤的句子
    correct_num = incorrect_num = question_num = 0
    for key, value in random_sentence.items(): # key對應的是鍵，value對應的是值
        question_num += 1
        question = (
            '\n\033[32;1m'
            + str(question_num)
            + '. 請用英文翻譯\033[0m '
            + '"\033[36;1m'
            + value
            + '\033[0m"'
        )
        speak(engine, key)
        question += "\n\033[32;1m翻譯: \033[0m"
        Y_answer = input(question)
        while not Y_answer.strip():
            Y_answer = input(question)
        Y_answer = simplify(Y_answer)
        answer = simplify(key)
        if Y_answer == answer:
            correct_num += 1
            right.play()
            time.sleep(1)
            print("\033[34;1m————翻譯正確😊\033[0m")
        elif Y_answer == "quit":
            print(
                "\033[36;1m共有"
                + "\033[34;1m"
                + str(correct_num)
                + "題翻譯正確😊\033[0m"
                + "\033[31;1m, \033[0m"
                + "\033[31;1m"
                + str(incorrect_num)
                + "題翻譯錯誤😢\033[0m"
                + ", 請繼續努力"
                + "\033[34;1m(≧▽≦q)\033[0m"
                + "\033[0m"
            )
            if erros:
                print("---" * 65)
                Y_answer = input("\033[36;1m\033[36;1m是否要練習錯題😊 \033[0m")
                if Y_answer == "quit":
                    print("\n")
                    print("\033[31;1m錯題: \033[0m")
                    for keys, values in erros.items():
                        print(
                            "\n\033[36;1m中文: \033[0m"
                            + "\033[32;1m"
                            + values
                            + "\033[0m"
                        )
                        print(
                            "\033[36;1m英文: \033[0m"
                            + "\033[34;1m"
                            + keys
                            + "\033[0m"
                        )
                    break
                elif Y_answer != "quit":
                    boolean = True
                    question_num = 0
                    while boolean:
                        for key, value in list(erros.items()):
                            question_num += 1
                            question = (
                                '\n\033[32;1m'
                                + str(question_num)
                                + '. 請用英文翻譯\033[0m '
                                + '"\033[36;1m'
                                + value
                                + '\033[0m"'
                            )
                            speak(engine, key)
                            question += "\n\033[32;1m翻譯: \033[0m"
                            Y_answer = input(question)
                            while not Y_answer.strip():
                                Y_answer = input(question)
                            Y_answer = simplify(Y_answer)
                            answer = simplify(key)
                            if Y_answer == answer:
                                right.play()
                                time.sleep(1)
                                print("\033[34;1m————翻譯正確😊\033[0m")
                                del erros[key]
                                if len(erros) == 0:
                                    boolean = False
                            elif Y_answer == "quit":
                                for keys, values in erros.items():
                                    print(
                                        "\n\033[36;1m中文: \033[0m"
                                        + "\033[32;1m"
                                        + values
                                        + "\033[0m"
                                    )
                                    print(
                                        "\033[36;1m英文: \033[0m"
                                        + "\033[34;1m"
                                        + keys
                                        + "\033[0m"
                                    )
                                boolean = False
                            else:
                                wrong.play()
                                time.sleep(1)
                                print("\033[31;1m————翻譯錯誤😡\033[0m")
                                print(
                                    "\033[36;1m正確翻譯: \033[0m"
                                    + "\033[34;1m"
                                    + key
                                    + "\033[0m"
                                )
                    break
        else:
            wrong.play()
            time.sleep(1)
            incorrect_num += 1
            erros.setdefault(key, value) # 記錄錯誤
            print("\033[31;1m————翻譯錯誤😡\033[0m")
            print("\033[36;1m正確翻譯: \033[0m" + "\033[34;1m" + key + "\033[0m")

# 定義一個主函數，用於執行程序
def main():
    # 讀取json文件，獲取英語句子字典
    english_sentence = load_json_file(JSON_FILE)
    # 初始化pygame.mixer，獲取正確和錯誤的聲音對象
    right, wrong = init_mixer()
    # 初始化pyttsx3.engine，獲取語音引擎對象
    engine = init_engine()
    # 調用練習函數，開始練習英語口語
    practice(english_sentence, right, wrong, engine)

# 判斷是否是主模塊，如果是，則執行主函數
if __name__ == "__main__":
    main()
