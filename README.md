# NYT rankbot 🤖
Calculates daily rankings in group chats for NYT games.

## Infrastructure
* Bot from [BotFather](https://t.me/BotFather).
* MySQL database hosted on GCP, with authorised networks amended
* `main.py` running on a GCP VM instance. Remember to manually copy the `.env` file when cloning from GitHub.
Relevant details placed in an `.env` file.