# -功能與使用說明-
英語口語練習

這是一個用Python語言寫的英語口語練習程序，它可以讓你從一個json文件中隨機選擇一個英語句子，並用中文翻譯。你可以聽到句子的語音，並輸入你的答案。程序會判斷你的答案是否正確，並給出正確的翻譯。你還可以選擇是否要練習錯題，直到你全部答對為止。

安裝

你需要安裝以下的模塊，才能運行這個程序：

- json
- pygame
- pyttsx3
- re
- random
- time

你可以使用pip命令來安裝這些模塊，例如：

pip install pygame

使用

你需要準備一個json文件，裡面存儲了英語句子和中文翻譯，格式如下：

{
  "Hello, world!": "你好，世界！",
  "How are you?": "你好嗎？",
  "What's your name?": "你叫什麼名字？"
}

你可以自行編輯這個文件，增加或刪除你想要練習的句子。你需要將這個文件的路徑設定為一個常量，例如：

JSON_FILE = 'C:/Users/Jie/OneDrive/文件/py_project/英语口语/english_sentence.json'

然後，你可以運行main.py文件，開始練習英語口語。你會看到以下的界面：

![Screenshot of the program interface](https://docs.github.com/zh/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

你可以按照提示輸入你的答案，或者輸入quit退出程序。你可以聽到句子的語音，並看到你的答案是否正確，以及正確的翻譯。你還可以選擇是否要練習錯題，直到你全部答對為止。

貢獻

歡迎你對這個程序提出任何的建議或改進，你可以通過以下的方式聯繫我：

- Email: lixiujie85@gmail.com

授權

這個程序是基於MIT協議開源的，你可以自由地使用、修改和分發它，但你需要保留原作者的版權聲明。詳細的協議內容請參考[LICENSE](https://www.ithome.com.tw/news/155842)文件。

