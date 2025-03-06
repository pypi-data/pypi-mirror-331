# TeleBee library provided by Mohammed Ghanam.

![PyPI - Version](https://img.shields.io/pypi/v/TeleBee?color=blue&label=version)  
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)  
![Status](https://img.shields.io/badge/status-active-success)  

--------

`TeleBee` is a Python library designed to simplify the management and organization of code in bot projects using the `Telebot` library. This library allows you to load code from Python files located in specific directories without interfering with the `polling` or `infinity_polling` processes. You can write your code normally, and the library will automatically load and organize it.

## Features

- Load code from Python files in specified directories.
- Does not interfere with `polling` or `infinity_polling` processes.
- A flexible and easy-to-use library that allows developers to write code normally in separate files.
- Supports organizing code in different directories.

## Installation

1. First, install the `pyTelegramBotAPI` library (if not installed already):

```bash
  pip install pyTelegramBotAPI
``


##Usage

- 1. Setting up TeleBee:

At the beginning of your Python file, import the library, create a TeleBee object, and pass in your bot's token.
``python
from telebot import TeleBot
from telebee import TeleBee

# Set up the bot using your bot's token
bot = TeleBot('YOUR_BOT_TOKEN')

# Set up TeleBee and load code from specified directories
telebee_bot = TeleBee(function_dirs=['start', 'functions'])
telebee_bot.load_functions()

# The developer controls polling separately
bot.infinity_polling()
``

- 2. Adding code:

The developer writes their code in Python files within the specified directories. For example, the developer can add files like start.py or functions/another_function.py.

Example of start.py:

``python
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Welcome to the bot!")
``

Example of functions/another_function.py:

``python
@bot.message_handler(commands=['hello'])
def hello_message(message):
    bot.reply_to(message, "Hello, how are you?")
``

- 3. Customizing directories:

You can customize the directories containing the code by passing them to TeleBee in the function_dirs argument.

``python
telebee_bot = TeleBee(function_dirs=['your_custom_folder', 'another_folder'])
telebee_bot.load_functions()
``

## For Contact:

- My telegram Account: [@midoghanam](https://t.me/midoghanam)
- My Channel: [@mido_ghanam](https://t.me/mido_ghanam)

## Best Regards ♡