# Wordle_bot
Program uses python to automatically open up wordle in a website and complete it.

Program created using selenium that automatically guesses the answer for the daily wordle word.
It will open up wordle page in a browswer and guess until it finds the correct answer, once it does, it can be shared to a telegram group.

The program assigns words with invidiual scores using the frequency of the letter's that is in that word. If a word contains letters that appears more frequent in other words, it will have a highest score. When guessing the word, the program will choose the word with highest score. 
