# 导入必要的库和模块
import random  # 用于随机选择句子
import pygame  # 用于游戏界面和事件处理
import re  # 正则表达式库，用于文本处理
import pyttsx3  # 用于文字转语音
import time  # 用于时间控制
import json  # 用于读取JSON数据
import difflib  # 用于计算字符串相似度

# 初始化pygame
pygame.init()

# 加载数据和资源
# 从"多鄰國.json"文件加载英文句子数据
with open("json/english_sentence.json", "r", encoding="utf-8") as f:
    english_sentence = json.load(f) # 使用 `json.load(f)` 将 JSON 文件的内容解析为 Python 数据结构 並存入變量english_sentencer

# 设置窗口尺寸和创建主屏幕
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
# 加载并设置背景图片
image = pygame.transform.scale(pygame.image.load("photo/stones.jpg").convert(), (width, height))
# 设置窗口标题
pygame.display.set_caption("英文单词练习")

# 初始化字体样式和大小
font_title = pygame.font.SysFont("SimHei", 60)  # 标题字体
font_sentence = pygame.font.SysFont("SimHei", 40)  # 句子展示字体
font_input = pygame.font.SysFont("Comic Sans MS", 30)  # 用户输入框字体
font_answer = pygame.font.SysFont("SimHei", 30)  # 答案字体
font_tips = pygame.font.SysFont("SimHei", 25)  # 提示信息字体
font_score = pygame.font.SysFont("SimHei", 25)  # 分数显示字体

# 加载音频文件
right_sound = pygame.mixer.Sound("sound/right.mp3")  # 正确回答音效
wrong_sound = pygame.mixer.Sound("sound/wrong.wav")  # 错误回答音效

# 初始化文字转语音引擎并设置参数
engine = pyttsx3.init()
engine.setProperty("voice", engine.getProperty("voices")[1].id)  # 设置语音类型
engine.setProperty("rate", 145)  # 设置语速

# 缩写词与全称映射字典
abbreviation_mapping = {
    # 示例缩写与全称配对
    "it's": "it is",
    "can't": "cannot",
    "i'll": "i will",
    "won't": "will not",
    "i'm": "i am",
    "you're": "you are",
    "they're": "they are",
    "we're": "we are",
    "don't": "do not",
    "didn't": "did not",
    "doesn't": "does not",
    # 添加更多的缩写和其对应的完整形式
}

# 扩展缩写的函数
def expand_abbreviations(text):
    """将文本中的缩写扩展为其全称"""
    for abbr, full in abbreviation_mapping.items(): #abbr{縮寫} full{全寫}
        text = text.replace(abbr, full) #用replace將abbr{縮寫} 替換為full{全寫}
    text = text.replace(" ", "") #將文本中的空格替換為無
    return text

# 定义练习状态类
class PracticeState:
    def __init__(self):
        self.is_running = False  # 练习是否正在进行
        self.question_num = 0  # 已回答问题数量
        self.correct_num = 0  # 正确回答数量
        self.incorrect_num = 0  # 错误回答数量
        self.errors = {}  # 记录错误答案及其正确句子
        self.current_sentence = None  # 当前展示的句子
        self.current_english_sentence = None  # 当前英语句子
        self.current_answer = None  # 当前正确答案
        self.user_input_text = ""  # 用户输入的答案
        self.show_answer = False  # 是否显示答案

    def practice(self):
        """开始新的练习题目"""
        # 随机选取一个问题
        sentence_keys = list(english_sentence.keys())
        random.shuffle(sentence_keys)
        self.current_answer = sentence_keys[0]
        self.current_english_sentence = self.current_answer
        self.current_sentence = english_sentence[self.current_answer]
        self.user_input_text = ""  # 清空用户输入
        self.show_answer = False  # 隐藏答案
        self.question_num += 1  # 问题计数加一

    def check_answer(self, answer):
        """检查用户答案是否正确"""
        # 处理答案（去除特殊字符，转换为小写，去空格），并展开缩写

        #移除傳入參數answer非字母、数字、空白字符及撇号，将其转换为小写并删除空格，再将缩写展开为完整形式

        #该表达式的含义为：r 表示这是一个 原始字符串（raw string）。使用原始字符串时，反斜杠 \ 不会被解释为转义字符，而是会被保留为普通字符。`^` 表示“非”，`\w` 表示所有字母和数字，`\s` 表示空白字符（空格、制表符等），`'’` 表示撇号和右撇号。
        # re.sub()` 函数将这些匹配的字符替换为空字符串 `""`，即删除它们。

        def normalize(text):
            text = text.lower()  # 转小写
            text = expand_abbreviations(text)  # 扩展缩写
            text = re.sub(r"[^a-z0-9]", "", text)  # 去掉所有非字母数字字符
            return text

        # 使用difflib计算答案与正确答案的相似度
        normalized_answer = normalize(answer)
        normalized_correct = normalize(self.current_answer)

        # 使用 difflib 计算相似度
        ratio = difflib.SequenceMatcher(None, normalized_answer, normalized_correct).ratio()

        # 如果相似度超过阈值，则认为回答正确
        if ratio > 0.95:
            self.correct_num += 1
            right_sound.play()  # 播放正确音效
            time.sleep(1)  # 等待一秒
            self.practice()  # 进入下一题
            return True
        else:
            self.incorrect_num += 1
            wrong_sound.play()  # 播放错误音效
            time.sleep(1)  # 等待一秒
            # 记录错误答案
            self.errors.setdefault(self.current_answer, self.current_sentence)
            self.user_input_text = ""  # 清空输入框
            return False

# 实例化练习状态
state = PracticeState()

# 文字转语音的函数
def speak(audio):
    """朗读文本"""
    engine.say(audio)
    engine.runAndWait()

# 绘制按钮函数
def draw_button(x, y, text, color, hover_color):
    """绘制按钮并返回是否被点击"""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, 150, 50)  # 按钮矩形
    clicked = False
    if rect.collidepoint((mouse_x, mouse_y)):
        pygame.draw.rect(screen, hover_color, rect)
        # 鼠标左键按下则返回 True
        if pygame.mouse.get_pressed()[0]:
            clicked = True
    else:
        pygame.draw.rect(screen, color, rect)
    # 绘制文字
    text_surface = font_answer.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + 75, y + 25))
    screen.blit(text_surface, text_rect)
    return clicked


# 绘制用户输入文本的函数
def draw_input_text(text, current_english_sentence):
    """绘制用户输入框及提示文本"""
    # 计算输入框的宽度：获取 `current_english_sentence` 字符串的像素宽度，增加 30 像素的额外空间，
    # 并确保输入框宽度至少为 300 像素，以便足够容纳用户输入的文本。
    #font_input.size(current_english_sentence) 返回一个元组，包含了渲染文本的宽度和高度。[0] 是用来访问这个元组中的第一个元素，也就是文本的宽度。
    input_text_width = max(300, font_input.size(current_english_sentence)[0] + 30)
    # 创建输入框的矩形区域
    input_answer = pygame.Rect(width // 2 - input_text_width // 2, 250, input_text_width, 60)# 创建输入框的矩形区域（Rect）：将输入框水平居中对齐（计算方法为屏幕宽度的一半减去输入框宽度的一半），纵向位置固定在 y=250，輸入框的寬度為要輸入文本的寬度，高度为 60 像素。
    pygame.draw.rect(screen, (255, 255, 255), input_answer, 2)  # 在屏幕上绘制一个白色矩形，作为输入框的边框。矩形的位置和大小由 `input_answer` 定义，边框宽度为 2 像素。
    # 创建并绘制用户输入的文本
    input_text_surface = font_input.render(text, True, (255, 255, 255))# 使用 `font_input` 字体将 `text` 渲染为一张图像（Surface），文本颜色为白色 (255, 255, 255)，`True` 参数表示启用抗锯齿，确保文本边缘更平滑。

    """輸入框 輸入文本的位置"""
    input_text_rect = input_text_surface.get_rect(topleft=(input_answer.left + 15, input_answer.top)) # 获取渲染后的文本图像的矩形边界（Rect），并将其左上角位置设置在输入框内的 (input_answer.left + 15, input_answer.top)，使文本在输入框内有适当的边距。
    screen.blit(input_text_surface, input_text_rect) # 获取渲染后的文本图像的矩形边界（Rect），并将其左上角位置设置在输入框内的 (input_answer.left + 15, input_answer.top)，使文本在输入框内有适当的边距。

# 开始第一次练习
state.practice()# 调用 `state.practice()` 方法，开始或重新开始一个新的练习题目。这将随机选择一个句子作为当前问题，并初始化用户输入等状态信息。

running = True # 当 `running` 为 `True` 时，主循环将持续运行；当 `running` 变为 `False` 时，主循环将退出。

clock = pygame.time.Clock()# 创建一个 `Clock` 对象，用于控制游戏主循环的帧率。通过调用 `clock.tick()` 方法，可以限制循环的速度，确保游戏运行平稳。

while running:
    # 主循环：当 `running` 为 `True` 时，持续执行以下代码块，以处理事件和更新屏幕。

    # 事件处理
    for event in pygame.event.get():
        # 处理所有从 Pygame 事件队列中获取的事件
        if event.type == pygame.QUIT:
            # 如果事件类型为 `QUIT`（例如点击关闭窗口），将 `running` 设置为 `False`，退出主循环
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 如果事件类型为 `MOUSEBUTTONDOWN`（鼠标点击事件）
            if not state.is_running:
                # 如果练习尚未开始
                if width // 2 - 75 <= event.pos[0] <= width // 2 + 75 and height // 2 - 25 <= event.pos[1] <= height // 2 + 25:
                    # 检查鼠标点击位置是否在“开始练习”按钮区域内
                    state.is_running = True  # 开始练习
                    state.practice()  # 启动新的练习
                    speak(state.current_english_sentence)  # 朗读当前的英语句子
            else:
                # 如果练习正在进行
                if width - 200 <= event.pos[0] <= width - 50 and height - 70 <= event.pos[1] <= height - 20:
                    # 检查鼠标点击位置是否在“下一题”按钮区域内
                    state.practice()  # 进入下一题
                    speak(state.current_english_sentence)  # 朗读当前的英语句子
                if 70 <= event.pos[0] <= 220 and height - 70 <= event.pos[1] <= height - 20:
                    # 检查鼠标点击位置是否在“显示答案”按钮区域内
                    state.show_answer = True  # 显示当前题目的答案
        elif event.type == pygame.KEYDOWN and state.is_running:
            # 如果事件类型为 `KEYDOWN`（键盘按键事件），且练习正在进行
            if event.key == pygame.K_RETURN:
                # 如果按下的是回车键
                if state.user_input_text.strip() == "":
                    # 输入框为空，朗读当前句子
                    speak(state.current_english_sentence)
                else:
                    # 输入框有文字，提交答案
                    if state.check_answer(state.user_input_text):
                        state.practice()  # 如果正确，进入下一题
                        speak(state.current_english_sentence)

            elif event.key == pygame.K_BACKSPACE:
                # 如果按下的是退格键
                state.user_input_text = state.user_input_text[:-1]  # 删除用户输入的最后一个字符
            elif event.key != pygame.K_TAB and len(state.user_input_text) < 50:
                # 如果按下的是其他键（非 Tab 键），且用户输入的文本长度小于 50 个字符
                state.user_input_text += event.unicode  # 将按下的键字符添加到用户输入文本中
            if event.key == pygame.K_TAB:
                # 如果按下的是 Tab 键
                speak(state.current_english_sentence)  # 朗读当前的英语句子
            elif event.key == pygame.K_LCTRL:
                # 如果按下的是左 Ctrl 键
                state.show_answer = True  # 显示当前题目的答案

    # 绘制界面元素
    screen.blit(image, (0, 0))  # 在屏幕上绘制背景图片

    # 绘制标题
    title_surface = font_title.render("英文单词练习", True, (255, 255, 255))
    # 使用 `font_title` 字体渲染标题文本，颜色为白色，启用抗锯齿
    title_rect = title_surface.get_rect(center=(width // 2, 100))
    # 获取文本矩形区域，并将其中心设置在屏幕上方的指定位置
    screen.blit(title_surface, title_rect)
    # 在屏幕上绘制标题

    # 绘制当前句子
    if state.current_sentence:
        sentence_surface = font_sentence.render(f'"{state.current_sentence}"', True, (255, 255, 255))
        # 使用 `font_sentence` 字体渲染当前句子文本，颜色为白色，启用抗锯齿
        sentence_rect = sentence_surface.get_rect(center=(width // 2, 200))
        # 获取文本矩形区域，并将其中心设置在屏幕中间的指定位置
        screen.blit(sentence_surface, sentence_rect)
        # 在屏幕上绘制当前句子

    # 绘制用户输入框
    draw_input_text(state.user_input_text, state.current_english_sentence)
    # 调用 `draw_input_text` 函数绘制用户输入框及当前英语句子

    # 绘制提示信息
    tips_surface = font_tips.render("请用英文翻译句子", True, (255, 255, 255))
    # 使用 `font_tips` 字体渲染提示信息文本，颜色为白色，启用抗锯齿
    tips_rect = tips_surface.get_rect(center=(width // 2, 450))
    # 获取文本矩形区域，并将其中心设置在屏幕下方的指定位置
    screen.blit(tips_surface, tips_rect)
    # 在屏幕上绘制提示信息

    # 显示答案
    if state.show_answer:
        answer_surface = font_answer.render(f"答案: {state.current_answer}", True, (255, 255, 255))
        # 使用 `font_answer` 字体渲染答案文本，颜色为白色，启用抗锯齿
        answer_rect = answer_surface.get_rect(center=(width // 2, 500))
        # 获取文本矩形区域，并将其中心设置在屏幕下方的指定位置
        screen.blit(answer_surface, answer_rect)
        # 在屏幕上绘制当前题目的答案

    # 绘制开始/继续练习按钮和显示答案按钮


    if not state.is_running:
        # 背景
        screen.blit(image, (0,0))

        # 标题
        title = font_title.render("英文口语练习", True, (255,255,255))
        screen.blit(title, (width//2 - title.get_width()//2, 100))

        # 功能介绍
        tips = [
            "功能特点:",
            "1. 支持语音朗读英文句子",
            "2. 自动检测翻译准确度",
            "3. 记录错题并提供复习功能",
            "4. 支持缩写自动扩展",
            "5. 按Tab键重复朗读句子",
            "6. 按Ctrl键显示答案",
        ]
        for i, tip in enumerate(tips):
            text = font_tips.render(tip, True, (255,255,255))
            screen.blit(text, (width//2 - 250, 200 + i*35))

        # 开始按钮
        if draw_button(width//2 - 100, 450, "开始练习", (0,255,0), (255,255,0)):
            state.is_running = True
            state.practice()
            speak(state.current_english_sentence)  # 朗读当前的英语句子

    else:
        # 如果练习正在进行
        draw_button(width - 200, height - 70, "下一题", (255, 255, 255), (200, 200, 200))
        # 绘制“下一题”按钮，颜色为白色，鼠标悬停时变为灰色
        draw_button(70, height - 70, "显示答案", (255, 255, 255), (200, 200, 200))
        # 绘制“显示答案”按钮，颜色为白色，鼠标悬停时变为灰色

    # 显示分数
    score_surface = font_score.render(f"答对: {state.correct_num}", True, (255, 255, 255))
    # 使用 `font_score` 字体渲染分数文本，颜色为白色，启用抗锯齿
    score_rect = score_surface.get_rect(topright=(width - 20, 20))
    # 获取文本矩形区域，并将其右上角设置在屏幕的指定位置
    screen.blit(score_surface, score_rect)
    # 在屏幕上绘制当前的分数

    # 更新屏幕
    pygame.display.flip()
    # 更新整个屏幕显示，将所有绘制的内容刷新到屏幕上

    # 控制帧率
    clock.tick(60)
    # 控制主循环的最大帧率为 60 帧每秒，确保游戏运行平稳

# 退出pygame
pygame.quit()
# 退出 Pygame 库，释放资源并关闭游戏窗口
