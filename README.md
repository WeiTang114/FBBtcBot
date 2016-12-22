# FBBtcBot
An FB bot to notify you the BitCoin price.

# Usage

## Start the Bot
1. Create an FB account, get the email and password.
2. Copy "btcnotifier.ini.example" to "btcnotifier.ini" and fill in your email/password.
3. Start the program and leave it running:
```bash
python btcnotifier.py
```

## Play with the Bot
Send a message to your bot for various functions.

1. /now: for current btc price
2. /up \<price\>: for notification when the current price higher than \<price\>
3. /down \<price\>: else.

**Note that each notification will work only once.**
