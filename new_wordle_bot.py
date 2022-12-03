import time
from selenium.webdriver.common.keys import Keys
from collections import Counter
from itertools import chain
from selenium.webdriver.chrome.options import Options
import os
from selenium import webdriver
from bs4 import BeautifulSoup


def calculate_word_score(word, frequency_table):
    """
    Calculate the score of a word to determine which word to choose
    Args:
        word: The word to calculate the score with
        frequency_table: Frequency table containing frequency for each letter

    Returns:
        overall_score: Return the overall score for the word
    """
    letter_frequency_average = frequency_table
    score = 0
    # Use frequency of each letter to calculate the score of the word
    for character in word:
        score += letter_frequency_average[character]
    overall_score = score / (len(word) - len(set(word))+1)

    return overall_score


def word_score():
    """
    Create a dictionary containing all possible words and their individual score
    Returns:
        word_scores_dict: Dictionary containing all possible words and their score
    """
    word_file = open(path+"/wordle-answers-alphabetical.txt", "r").read().splitlines()
    words = {word.lower() for word in word_file}
    letter_frequency = Counter(chain.from_iterable(words))
    letter_frequency_average = {
        key: int(value) / int(sum(letter_frequency.values()))
        for key, value in letter_frequency.items()
    }
    word_scores_dict = {word: calculate_word_score(word, letter_frequency_average) for word in words}
    return word_scores_dict


def send_word(driver, word):
    """
    Send the letters from the word to the broswer for checking
    Args:
        driver: The selenium web driver object
        word: String containing the word to be sent to the browser


    """
    webdriver.ActionChains(driver).send_keys(word).perform()
    time.sleep(1)
    webdriver.ActionChains(driver).send_keys(Keys.RETURN).perform()


def get_errors(driver, current_row):
    """

    Args:
        driver: The selenium web driver object
        current_row: The current attempt number

    Returns:
        feedback_string: String containing letters representing which letters are correct or wrong
    """
    row_num = current_row
    feedback_string = ""
    soup = BeautifulSoup(driver.page_source, "lxml")
    rows = soup.select(".Row-module_row__dEHfN")
    for letter in rows[row_num].select('div'):
        if "absent" in str(letter) and "animation-delay" in str(letter):
            feedback_string += "n"
        elif "present" in str(letter) and "animation-delay" in str(letter):
            feedback_string += "y"
        elif "correct" in str(letter) and "animation-delay" in str(letter):
            feedback_string += "g"
    return feedback_string


if __name__ == "__main__":
    path = str(os.path.dirname(__file__))
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=path+"/chromedriver", options=chrome_options)  # create browser
    driver.get('https://www.nytimes.com/games/wordle/index.html')
    time.sleep(2)
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()  # close initial window
    time.sleep(2)

    previous_word = "arose"  # initial word
    send_word(driver, previous_word)  # send initial word
    time.sleep(2)

    daily_finished = False

    word_scores = word_score()  # Calculate score for each available word
    current_attempt = 0  # Current row
    # Try words
    while not daily_finished:
        finished = previous_word
        # Retrieves string representation for each letter is wrong
        string_validation = get_errors(driver, current_attempt)
        if str(string_validation) == "ggggg":
            daily_finished = True
            print(finished)
            break
        else:
            wordle_list = list(string_validation)
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
        send_word(driver, max_key)
        previous_word = max_key
        del word_scores[max_key]
        time.sleep(2)
        current_attempt += 1
        time.sleep(2)

    driver.close()










