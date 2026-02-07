"""
英语口语练习程序
功能：通过中英翻译练习提高英语口语能力
特点：
1. 支持语音朗读英文句子
2. 自动检测用户翻译准确度
3. 记录错题并提供复习功能
4. 可自定义语音参数(音色、语速)
5. 支持缩写自动扩展(如将"it's"转为"it is")
"""

import json
import pygame
import os
import pyttsx3
import re
import random
import difflib
import time
from typing import Dict, Tuple

# ===================== 可自定义参数区域 =====================
# 缩写词与全称映射字典 - 可自行添加更多缩写
ABBREVIATION_MAPPING = {
    "it's": "it is", "can't": "cannot", "won't": "will not",
    "i'm": "i am", "you're": "you are", "they're": "they are",
    "we're": "we are", "don't": "do not", "didn't": "did not",
    "doesn't": "does not", "i'll": "I will", "what's": "what is",
    "I'd": "I would", "how's": "how is"
}

# 语音设置
VOICE_SETTINGS = {
    'voice_type': 1,  # 0为英文男声，1为英文女声(注意：根据系统语音库可能不同)
    'speech_rate': 135  # 语速(正常值约100-200)
}

# 音频文件路径
SOUND_FILES = {
    'correct': "sound/right.mp3",
    'wrong': "sound/wrong.wav",
    'success': "sound/success.mp3"
}

# 练习设置
PRACTICE_SETTINGS = {
    'similarity_threshold': 0.95,  # 答案相似度阈值(0-1之间)
    'retry_wrong_questions': True  # 是否自动重做错题
}

# 颜色代码(控制台输出颜色)
COLORS = {
    'prompt': "\033[32;1m",  # 提示信息-绿色
    'correct': "\033[34;1m",  # 正确-蓝色
    'wrong': "\033[31;1m",    # 错误-红色
    'question': "\033[36;1m", # 问题-青色
    'answer': "\033[33;1m",   # 答案-黄色
    'reset': "\033[0m",        # 重置颜色
    'almost': "\033[35;1m"  # 差一点-紫色
}
# ===================== 可自定义参数区域结束 =====================

def expand_abbreviations(text: str) -> str:
    """扩展文本中的缩写为完整形式

    Args:
        text: 需要处理的文本

    Returns:
        处理后的文本，所有已知缩写已被替换为完整形式
    """
    for abbr, full in ABBREVIATION_MAPPING.items():
        text = text.replace(abbr, full)
    return text

def load_json_file(file_path: str) -> Dict[str, str]:
    """加载包含练习句子的JSON文件

    Args:
        file_path: JSON文件路径

    Returns:
        包含中英对照句子的字典
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{COLORS['wrong']}错误：找不到文件 {file_path}{COLORS['reset']}")
        return {}
    except json.JSONDecodeError:
        print(f"{COLORS['wrong']}错误：文件 {file_path} 不是有效的JSON格式{COLORS['reset']}")
        return {}

def init_audio_system() -> Tuple[pygame.mixer.Sound, pygame.mixer.Sound, pygame.mixer.Sound]:
    """初始化音频系统并加载音效

    Returns:
        包含三个音效的元组：(正确音效, 错误音效, 成功音效)
    """
    pygame.mixer.init()
    try:
        right = pygame.mixer.Sound(SOUND_FILES['correct'])
        wrong = pygame.mixer.Sound(SOUND_FILES['wrong'])
        success = pygame.mixer.Sound(SOUND_FILES['success'])
        return right, wrong, success
    except pygame.error as e:
        print(f"{COLORS['wrong']}音频加载错误: {e}{COLORS['reset']}")
        # 返回空音效以避免程序崩溃
        return pygame.mixer.Sound(), pygame.mixer.Sound(), pygame.mixer.Sound()

def init_tts_engine(voice_type: int, speech_rate: int) -> pyttsx3.Engine:
    """初始化文本转语音(TTS)引擎

    Args:
        voice_type: 语音类型索引(取决于系统安装的语音库)
        speech_rate: 语速(单词每分钟)

    Returns:
        配置好的TTS引擎实例
    """
    engine = pyttsx3.init()

    # 设置语音属性
    try:
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[voice_type].id)
    except IndexError:
        print(f"{COLORS['wrong']}警告: 指定的语音类型 {voice_type} 不可用，使用默认语音{COLORS['reset']}")

    engine.setProperty('rate', speech_rate)
    return engine

def speak(engine: pyttsx3.Engine, text: str) -> None:
    """使用TTS引擎朗读文本

    Args:
        engine: 已初始化的TTS引擎
        text: 要朗读的文本
    """
    engine.say(text)
    engine.runAndWait()

def normalize_text(text: str) -> str:
    """规范化用户输入的文本以便比较

    处理步骤:
    1. 移除非字母数字字符(保留空格和撇号)
    2. 转换为小写
    3. 扩展缩写
    4. 移除所有空格

    Args:
        text: 要规范化的文本

    Returns:
        规范化后的文本
    """
    # 移除非字母数字字符(保留空格和撇号)
    cleaned = re.sub(r"[^\w\s'']", "", text)
    # 转换为小写并扩展缩写
    normalized = expand_abbreviations(cleaned.lower())
    # 移除所有空格
    return normalized.replace(" ", "")

def print_result(correct_count: int, wrong_count: int) -> None:
    """打印练习结果统计

    Args:
        correct_count: 正确回答的数量
        wrong_count: 错误回答的数量
    """
    print(
        f"{COLORS['question']}共有"
        f"{COLORS['correct']}{correct_count}題翻譯正確😊{COLORS['reset']}"
        f"{COLORS['wrong']}, {wrong_count}題翻譯錯誤😢{COLORS['reset']}"
        f", 請繼續努力"
        f"{COLORS['correct']}(≧▽≦){COLORS['reset']}"
    )


def highlight_letter_differences(user_answer: str, correct_answer: str) -> str:
    """
    对比用户输入与正确答案，标注缺少或多余的字母
    - 缺少的字母标黄
    - 多余的字母标红
    """
    ua = user_answer
    ca = correct_answer
    s = difflib.SequenceMatcher(None, ua, ca)
    result = ""

    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == "equal":
            result += ca[j1:j2]  # 相同部分直接加
        elif tag == "replace":
            # 用户输入错或少了，正确答案显示黄色
            result += f"{COLORS['answer']}{ca[j1:j2]}{COLORS['reset']}"
        elif tag == "insert":
            # 正确答案多，用户少输入 → 黄色
            result += f"{COLORS['answer']}{ca[j1:j2]}{COLORS['reset']}"
        elif tag == "delete":
            # 用户多输入 → 红色
            result += f"{COLORS['wrong']}{ua[i1:i2]}{COLORS['reset']}"
    return result


def review_wrong_questions(wrong_answers: Dict[str, str],
                          engine: pyttsx3.Engine,
                          right_sound: pygame.mixer.Sound,
                          wrong_sound: pygame.mixer.Sound) -> None:
    """复习错题功能

    Args:
        wrong_answers: 错题字典{英文: 中文}
        engine: TTS引擎
        right_sound: 回答正确音效
        wrong_sound: 回答错误音效
    """
    if not wrong_answers:
        return

    print(f"\n{COLORS['wrong']}開始複習錯題:{COLORS['reset']}")
    question_num = 0

    # 复制一份错题字典以避免修改迭代中的字典
    remaining_questions = wrong_answers.copy()

    while remaining_questions:
        for english, chinese in list(remaining_questions.items()):
            question_num += 1
            # 构建问题字符串
            question = (
                f"\n{COLORS['prompt']}{question_num}. 請用英文翻譯{COLORS['reset']} "
                f'"{COLORS['question']}{chinese}{COLORS['reset']}"\n'
                f"{COLORS['prompt']}翻譯:{COLORS['reset']} "
            )

            # 朗读英文句子
            speak(engine, english)
            user_answer = input(question)

            # 处理空输入
            while not user_answer.strip():
                speak(engine, english)
                user_answer = input(question)

            # 检查是否要退出
            if user_answer.lower() == "quit":
                print(f"{COLORS['prompt']}退出複習模式{COLORS['reset']}")
                return

            # 规范化答案并比较
            normalized_user = normalize_text(user_answer)
            normalized_correct = normalize_text(english)
            similarity = difflib.SequenceMatcher(None, normalized_user, normalized_correct).ratio()

            if similarity > PRACTICE_SETTINGS['similarity_threshold']:
                right_sound.play()
                print(f"{COLORS['correct']}————翻譯正確😊{COLORS['reset']}")
                del remaining_questions[english]
            elif similarity >= PRACTICE_SETTINGS['similarity_threshold']:
              right_sound.play()
              print(f"{COLORS['almost']}————差一點哦😅{COLORS['reset']}")
              # 输出提示：高亮缺少的字母
              highlighted = highlight_letter_differences(user_answer.lower(), english.lower())
              print(f"{COLORS['prompt']}提示: {COLORS['reset']}{highlighted}")
              del remaining_questions[english]
            else:
                wrong_sound.play()
                print(f"{COLORS['wrong']}————翻譯錯誤😡{COLORS['reset']}")
                print(f"{COLORS['answer']}正確翻譯: {english}{COLORS['reset']}")

        # 所有错题都回答正确后显示祝贺信息
        if not remaining_questions:
            time.sleep(1)
            print(f"{COLORS['correct']}————恭喜您已將錯題全部清空，請再繼續吧(≧▽≦q)！{COLORS['reset']}")


quit_early = False

def practice_session(sentences: Dict[str, str],
                    right_sound: pygame.mixer.Sound,
                    wrong_sound: pygame.mixer.Sound,
                    success_sound: pygame.mixer.Sound,
                    engine: pyttsx3.Engine) -> None:
    """主练习会话

    Args:
        sentences: 中英对照句子字典{英文: 中文}
        right_sound: 正确回答音效
        wrong_sound: 错误回答音效
        success_sound: 成功音效
        engine: TTS引擎
    """
    if not sentences:
        print(f"{COLORS['wrong']}错误: 没有可用的练习句子{COLORS['reset']}")
        return

    # 随机打乱问题顺序
    sentence_items = list(sentences.items())
    random.shuffle(sentence_items)

    wrong_answers = {}
    correct_count = wrong_count = 0

    for idx, (english, chinese) in enumerate(sentence_items, 1):
        # 构建问题字符串
        question = (
            f"\n{COLORS['prompt']}{idx}. 請用英文翻譯{COLORS['reset']} "
            f'"{COLORS['question']}{chinese}{COLORS['reset']}"\n'
            f"{COLORS['prompt']}翻譯:{COLORS['reset']} "
        )

        # 朗读英文句子
        speak(engine, english)
        user_answer = input(question)

        # 处理空输入
        while not user_answer.strip():
            speak(engine, english)
            user_answer = input(question)

        # 检查是否要退出
        if user_answer.lower() == "quit":
            print_result(correct_count, wrong_count)
            quit_early = True
            break

        # 规范化答案并比较
        normalized_user = normalize_text(user_answer)
        normalized_correct = normalize_text(english)
        similarity = difflib.SequenceMatcher(None, normalized_user, normalized_correct).ratio()

        if similarity == 1:
            correct_count += 1
            right_sound.play()
            print(f"{COLORS['correct']}————翻譯正確😊{COLORS['reset']}")
        elif similarity >= PRACTICE_SETTINGS['similarity_threshold']:
            correct_count += 1
            right_sound.play()
            print(f"{COLORS['almost']}————差一點哦😅{COLORS['reset']}")
            # 输出提示：高亮缺少的字母
            highlighted = highlight_letter_differences(user_answer.lower(), english.lower())
            print(f"{COLORS['prompt']}提示: {COLORS['reset']}{highlighted}")
        else:
            wrong_count += 1
            wrong_sound.play()
            wrong_answers[english] = chinese
            print(f"{COLORS['wrong']}————翻譯錯誤😡{COLORS['reset']}")
            print(f"{COLORS['answer']}正確翻譯: {english}{COLORS['reset']}")

    # 显示最终结果
    if not quit_early:
      print_result(correct_count, wrong_count)

    # 如果有错题且设置为需要复习，则进入复习模式
    if wrong_answers and PRACTICE_SETTINGS['retry_wrong_questions']:
        print("\n" + "---" * 20)
        choice = input(f"{COLORS['prompt']}是否要練習錯題? (按Enter開始，或输入quit退出){COLORS['reset']} ")
        if choice.lower() != "quit":
            review_wrong_questions(wrong_answers, engine, right_sound, wrong_sound)

def main():
    """程序主入口"""
    # 1. 加载练习数据
    data_file = "json/english_sentence.json"  # 可修改为您的JSON文件路径
    sentences = load_json_file(data_file)

    if not sentences:
        return

    # 2. 初始化音频系统
    right_sound, wrong_sound, success_sound = init_audio_system()

    # 3. 初始化TTS引擎
    tts_engine = init_tts_engine(
        voice_type=VOICE_SETTINGS['voice_type'],
        speech_rate=VOICE_SETTINGS['speech_rate']
    )

    # 4. 开始练习会话
    practice_session(
        sentences=sentences,
        right_sound=right_sound,
        wrong_sound=wrong_sound,
        success_sound=success_sound,
        engine=tts_engine
    )

if __name__ == "__main__":
    main()
