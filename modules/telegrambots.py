import telegram as telegrambots
from modules.ini_config import config
# importando a biblioteca do telegram

# declarando o Token identificador do Bot
TOKEN = config['TELEGRAM']['TOKEN']
chat_id = config['TELEGRAM']['chat_id']

bot = telegrambots.Bot(token=TOKEN)
# aqui estamos criando o bot a partir da função Bot, e passando como parâmetro o token identificador do bot

#print(bot.get_me()) - Retornar as informações do bot

def telegram_msg(txt):
    bot.send_message(text=txt, chat_id=chat_id)

def telegram_img(img):
    #To send a photo from URL:
    #bot.send_photo(chat_id=chat_id, photo='https://telegram.org/img/t_logo.png')

    #To send a photo from local Drive:
    #bot.send_photo(chat_id=chat_id, photo=open('tests/test.png', 'rb'))
    bot.send_photo(img, chat_id)


#FIX_BUG
#pip uninstall python-telegram-bot telegram -y
#pip install python-telegram-bot