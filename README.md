# NYT rankbot 🤖
Calculates daily rankings in group chats for NYT games.

![example_screenshot](https://github.com/harryl99/nyt-rankbot/assets/79798424/cea1ded0-eb9a-46fc-ae67-bf8f5724b2a2)

## Infrastructure
* Get a Telegram bot from [BotFather](https://t.me/BotFather). Give it an appropriate name/description/picture and note down the token.
* Disable "Group privacy" for the Telegram bot within the BotFather menu, in order for it to receive all messages. 
* Set up a GCP VM micro instance.
* Connect to the VM instance via SSH. 
  * `sudo apt update`, `sudo apt install git python3 python3-venv`.
  * `git clone` this repository and `cd` to the root folder.
  * With Nano, create an `.env` file in the root, and paste your `TELEGRAM_BOT_TOKEN`.
  * `python3 -m venv nyt-rankbot`, `source nyt-rankbot/bin/activate`, `pip install -r requirements.txt`.
  * Run application in the background with `nohup python3 main.py &`.
* Add the bot to a group-chat with friends and try it out with some commands, below.

## Commands
* The bot scans and automatically parses results shared via the NYT website/app, for the games: *Connections*, *Mini Crossword*, *Wordle*.
* `/clear`: clears the database table for today's date and a specific user (if provided).
* `/scoreboard`: lists the scores for all users, for both today and this month's running total.
