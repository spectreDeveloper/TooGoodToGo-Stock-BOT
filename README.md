# TooGoodToGo Telegram Monitor Stocks 🛠️

With this bot, you can track shippable boxes from TooGoodToGo directly on Telegram. It's useful for receiving notifications about price changes and when items are back in stock.

## Example Screenshots 📸

![Monitor Running](https://telegra.ph/file/6a6a44dc30db2858344d2.jpg)

![Telegram Results](https://telegra.ph/file/f445cac4177b239436b3b.jpg)

## Requirements

- Docker

## How to Configure 🛠️

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-folder>
2. **Create a .env file in root and paste this:**
```bash
   USER_AGENT="TooGoodToGo/24.8.11 (29805) (iPhone/Unknown; iOS 17.5.1; Scale/3.00/iOS)"
   DATADOME_COOKIE= # (Leave this empty at first; after the first launch, complete the captcha and add the extracted datadome here)
   TELEGRAM_BOT_TOKEN=YOURTELEGRAMBOTTOKEN
   TELEGRAM_API_ID=YOURTELEGRAMAPIID
   TELEGRAM_API_HASH=YOURTELEGRAMAPIHASH
   TELEGRAM_CHAT_IDS=-100123456,-10012344555 # Separate multiple chat IDs with commas
   REFRESH_INTERVAL=300 # Refresh interval in seconds
```
3. **Launch for the first time using docker:**
   ```bash
   docker-compose build && docker-compose up
   ```
4) After the first launch, you will receive a geocaptcha url, copy-paste in a browser, open Network tab, complete the captcha and extract from "check" endpoint the datadome token.
5) Set the datadome in the env file.
6) Launch the docker command again to start the bot definitively.


### Contributing 🤝 ###

Contributions are welcome! Fork the repository and submit a pull request.
### Support ℹ️ ###

Feel free to open an issue here on GitHub to keep in touch.
