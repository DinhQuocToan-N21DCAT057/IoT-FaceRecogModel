const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
app.use(bodyParser.json());

const TELEGRAM_API_URL = 'https://api.telegram.org/bot7336190513:AAEj0IPDP0AICI7pnNCK4jp5gMWs6Dv-2Pk/sendMessage'; // Thay YOUR_BOT_TOKEN bằng token của bạn
const CHAT_ID = '-4520217667'; // Thay YOUR_CHAT_ID bằng chat ID của bạn

app.post('/webhook', (req, res) => {
    console.log('Received JSON:', JSON.stringify(req.body)); // Log JSON nhận được

    const intent = req.body.queryResult.intent.displayName;
    let textMessage;

    if (intent === 'TurnOnLight') {
        textMessage = 'Turn on the light';
    } else if (intent === 'TurnOffLight') {
        textMessage = 'Turn off the light';
    } else {
        textMessage = 'Unknown command';
    }

    axios.post(TELEGRAM_API_URL, {
        chat_id: CHAT_ID,
        text: textMessage
    })
    .then(() => {
        res.sendStatus(200);
    })
    .catch(error => {
        console.error('Error sending message to Telegram:', error);
        res.sendStatus(500);
    });
});

app.listen(3000, () => {
    console.log('Server is listening on port 3000');
});
