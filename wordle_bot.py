from selenium.webdriver import *;
import time
from selenium.webdriver.common.keys import Keys
from collections import Counter
from itertools import chain
import requests
import pyperclip
from selenium.webdriver.common.by import By
import warnings
import os


def telegram_bot_sendtext(bot_message):
    """
    send message on telegram
    :param bot_message:
    :return:
    """
    bot_token = input("Please enter the bot token ")
    bot_chatID = input("Please enter chatID  ")
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def calculate_word_score(word):
    """
    calculate the score of each word
    :param word:
    :return:
    """
    score = 0
    for character in word:
        score += letter_frequency_average[character]
    return score / (word_length - len(set(word))+1)


def send_keys(word):
    """
    send key inputs to the browswer
    :param word:
    :return:
    """
    Elem.send_keys(word)
    time.sleep(1)
    Elem.send_keys(Keys.RETURN)


def get_errors_after_key():
    """
    Get current word feedback from wordle website
    :return:
    """
    global feedback_list
    host = driver.find_element(By.TAG_NAME, "game-app")
    game = driver.execute_script("return arguments[0].shadowRoot.getElementById('game')", host)
    keyboard = game.find_elements_by_tag_name("game-row")
    iteration_num = 0

    for a in keyboard:
        if iteration_num == current_attempt:
            row = driver.execute_script("return arguments[0].shadowRoot.querySelector('div')", a)
            letters = row.find_elements_by_tag_name("game-tile")
            for b in letters:
                if b.get_attribute("evaluation") == "present":
                    feedback_list += "y"
                elif b.get_attribute("evaluation") == "absent":
                    feedback_list += "n"
                elif b.get_attribute("evaluation") == "correct":
                    feedback_list += "g"
        iteration_num += 1


def check_finished():
    """
    Check if the game is finished
    :return:
    """
    host = driver.find_element_by_tag_name("game-app")
    game = driver.execute_script("return arguments[0].shadowRoot.getElementById('game')", host)
    keyboard = game.find_element_by_tag_name("game-modal")
    overlay = driver.execute_script("return arguments[0].getElementsByTagName('game-stats')", keyboard)
    if len(overlay) == 0:
        return False
    else:
        return True


def sharing():
    """
    Click the share button once the game is finished
    :return:
    """
    host = driver.find_element_by_tag_name("game-app")
    button = driver.execute_script(
        "return document.querySelector('game-app').shadowRoot.querySelector('game-modal').querySelector('game-stats').shadowRoot.getElementById('share-button')")
    button.click()


path = str(os.path.dirname(__file__))

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

#get word score
today_word = []
word_file = open(path+"/wordle-answers-alphabetical.txt", "r").read().splitlines()
word_length = 5
words = {word.lower() for word in word_file}
letter_frequency = Counter(chain.from_iterable(words))
total = 0
letter_frequency_average = {
    key: int(value) / int(sum(letter_frequency.values()))
    for key, value in letter_frequency.items()
}
word_scores = {word: calculate_word_score(word) for word in words}

#create browser
driver = Chrome(executable_path=path+"/chromedriver") # create browser
driver.get('https://www.powerlanguage.co.uk/wordle/')
time.sleep(1)
Elem = driver.find_element(By.TAG_NAME,'html')
Elem.click()

time.sleep(1)
current_attempt = 0
feedback_list = ""
daily_finished = False
previous_word = "arose"
send_keys(previous_word)
get_errors_after_key()
time.sleep(3)

#Try words
while not daily_finished:
    finished = previous_word
    wordle_output = feedback_list
    if str(wordle_output) == "ggggg":
        daily_finished = True
    else:
        wordle_list = list(wordle_output)
        for i in range(len(wordle_list)):
            if str(wordle_list[i]) == "g":
                for word in word_scores.copy():
                    if word[i] != finished[i]:
                        del word_scores[word]
                        continue
            elif str(wordle_list[i]) == "y":
                for word in word_scores.copy():
                    if finished[i] not in word:
                        del word_scores[word]
                        continue
            elif str(wordle_list[i]) == "n":
                for word in word_scores.copy():
                    if finished[i] in word:
                        del word_scores[word]
                        continue

    max_key = max(word_scores, key=word_scores.get)
    previous_word = max_key
    del word_scores[max_key]
    send_keys(max_key)
    feedback_list = ""
    time.sleep(3)
    current_attempt += 1
    get_errors_after_key()
    time.sleep(5)
    if check_finished():
        daily_finished = True

time.sleep(2)
sharing()
time.sleep(2)
s = pyperclip.paste()
pyperclip.copy(s)
telegram_bot_sendtext(s)


driver.close()








