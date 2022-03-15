import time
from tkinter import END
from turtle import up
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from modules.db import insert_db, consult_db, insert_db_recusadas 
from modules.telegrambots import telegram_msg, telegram_img
from modules.ini_config import config
import numpy
import pyautogui
import os

#Selenium argumentos
dir_path = os.getcwd()
profile = os.path.join(dir_path, "profile", "wpp")
options = Options()
#options.add_argument("headless")
options.add_argument("window-size=1500,1200")
options.add_argument("no-sandbox")
options.add_argument("disable-dev-shm-usage")
options.add_argument("disable-gpu")
options.add_argument("log-level=3")
options.add_argument(r"user-data-dir={}".format(profile))
#options.add_argument(f"user-agent={userAgent}")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Configurações extraídas do arquivo config.ini
reddit_user = config['APP']['reddit_user']
nft_wallet = config['APP']['nft_wallet']
emojis = config.get('APP', 'emojis')
texts_mandatory = config.get('DATABASE', 'texts_mandatory')
phases_mandatory = config.get('DATABASE', 'texts_mandatory')
rules_list = config.get('DATABASE', 'rules_list')
source_posts = config.get('DATABASE', 'source_posts')
random_emoji = None

# Listas operacionais
rules_post = []      # Regras da postagem, coletadas
texts_post = []      # Textos da postagem
posts_confirm = []   # Lista de tuplas com (author, text_index, link_index)
posts_select = []    # Postagens selecionadas   

def print_full_screen(image_name='img'):
    """Função para tirar um print completo da tela"""
    image_name = f'{image_name}.png'
    image = pyautogui.screenshot(image_name)
    #image.save(image_name)
    return image_name

def number_select(text):
    """Função para cortar e retornar apenas números entre o texto"""
    from decimal import Decimal
    print(f'☄  Iniciando coleta de dados na tela!')
    time.sleep(2)
    replaces = ['+', '-', '.', ',', ';', ':']
    try:
        for i, d in enumerate(text):
            for c in replaces:
                d = d.replace(c, '')
            if d.isdigit():
                text = text[i]
                break
            return time
    except:
        return False

def time_post_select():
    """Retorna a hora exata da postagem"""
    text_time_post = driver.find_element(by=By.CLASS_NAME, value=('_3jOxDPIQ0KaOWpzvSQo-1s')).text
    time_post = number_select(text_time_post)
    return time_post

def get_data_post():
    """
    posts_index = Lista com todas as postagens da página
    """
    try:
        posts_index = driver.find_elements(by=By.XPATH, value=('//*[@data-testid="post-container"]')) 
    except:
        return
    return posts_index

def scrolls(x, updown):
    """Função para dar scroll na página inteira
    x: Número de scrolls 
    updown: Direção do scroll
    """
    for n in range(x):
        time.sleep(2)
        ActionChains(driver).send_keys(updown).perform()

def text_correct(text_index):
    termos = ['min', 'minuto', 'minutos', 'hora', 'horas']
    for termo in termos:
        try:
            text_index = text_index.split(termo)[1]
            text_index = text_index.split('\n')
            text_index = list(filter(None, text_index))
            try:
                if len(text_index[0]) > 5:
                    text_index = text_index[0]
                else:
                    text_index = text_index[1]
            except:
                pass
            return text_index
        except:
            continue
    return False

def rules_verify(title_text_index):
    rules_point = 0
    for rule in texts_mandatory:
        if rule in title_text_index.upper():
            rules_point += 1 
            if rules_point >= 2:
                if title_text_index not in posts_confirm:
                    return True

    for phase in phases_mandatory:
        if phase in title_text_index.upper():
            return True
    return False

def posts_selecteds(posts_db):
    """Seleciona na lista de postagens os posts 
    que correspondem aos critérios de seleção
    """
    time.sleep(5)
    scrolls(4, Keys.END)
    time.sleep(5)

    posts_index = get_data_post()

    print(f'\n{len(posts_index)} posts_index encontrados')
    rules = 0 
    for num, index in enumerate(posts_index):
        if index.text:
            if not 'PATROCINADO' in index.text.upper():
                try:
                    title_text_index = text_correct(posts_index[num].text)
                    if title_text_index: 
                        if title_text_index in posts_db:
                            print('Post cancelado, encontrado no banco de dados!')
                            insert_db_recusadas(title_text_index)
                            continue
                        if posts_confirm:
                            for post in posts_confirm:
                                if title_text_index in post:
                                    continue
                        if rules_verify(title_text_index): 
                            author = index.text.split()[2].split('/')[1]
                            link_index = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=(title_text_index))
                            link_index = link_index.get_attribute('href')                           
                            posts_confirm.append((author, title_text_index, link_index))
                        else:
                            print(f'\nTexto rejeitado: \n{title_text_index}\n')
                    else:
                        continue    
                except:
                    continue

    print(f'{len(posts_confirm)} postagens confirmadas para acesso')    

def author_comment():
    """Retorna o comentário do autor da postagem 
    para analisar as regras na função post_rules()"""
    try:
        post_comments = driver.find_element(by=By.CLASS_NAME, value=('_1YCqQVO-9r-Up6QPB9H6_4')).text.split('\nPartilhar')
        for post in post_comments:
            if 'OP' in post:
                post_author = post
                return post_author
        return False
    except:
        return False

def all_rules(title_text_index, author=False):
    """Para coletar as regras da postagem, 
    através do comenário do author da postagem
    que geralmente é um dos primeiros comentários
    """
    rules_post = []
    author_text = False
    if author:
        author_text = author_comment()
        if author_text:
            for rule in rules_list:
                if author_text:
                    if rule in author_text.lower() and rule not in rules_post:
                        rules_post.append(rule)    
                    if rule in title_text_index.lower() and rule not in rules_post:
                        rules_post.append(rule)
            return rules_post, author_text
    if title_text_index:
        for rule in rules_list:
            if rule in title_text_index.lower() and rule not in rules_post:
                rules_post.append(rule)
        return rules_post, False
    return False, False

def message_custom(text_title, text_rules):
    """retorna menssagem personalizada"""
    #post_author = author_comment()
    rules_campaign = text_rules
    if rules_campaign:
        message = []
        for rules in rules_campaign:
            if rules in rules_list:
                message.append(f'{rules.title()}: {rules_list[rules]}')
        return message
    return False

def final_message(text, text_box):
    try:
        text_box.find_element(by=By.XPATH, value=('//*[@class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr"]')).send_keys(f'{text}\n') 
    except:
        text_box.find_element(by=By.XPATH, value=('//*[@class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr"]'))[0].send_keys(f'{text}\n') 

def upvote():
    """Clica no botão principal Upvote para curtir a postagem"""
    try:
        scrolls(1, Keys.PAGE_UP)
        time.sleep(2)
        upvote_button = driver.find_elements(by=By.CLASS_NAME, value=('icon-upvote'))[0]
        upvote_button.click()  
        return
    except:
        try:
            scrolls(1, Keys.PAGE_UP)
            time.sleep(2)
            upvote_button = driver.find_element(by=By.XPATH, value=('//*[@data-click-id="upvote"]'))
            upvote_button.click() 
            return
        except:
            pass
    return False

def submit_comment():
    time.sleep(1)
    try:
        button_post = driver.find_element(by=By.XPATH, value=('//*[@type="submit"]'))
        button_post.click()
        time.sleep(4)
        if driver.find_element(by=By.XPATH, value=('//*[@type="submit"]')):
            button_post.click()
    except:
        return False

def post_execute(link_url, text_title):
    """Executa a postagem personalizada de acordo 
    com todas as regras extraídas"""

    try:
        driver.get(link_url)
        time.sleep(5)

        texts_posteds = []
        text_rules, author_text = all_rules(text_title, author=True)        
        if text_title in texts_posteds or user_visited():
            return
        upvote()
        message = message_custom(text_title, text_rules)
        text_box = driver.find_element(by=By.CLASS_NAME, value=('DraftEditor-editorContainer'))
        text_box.click()
        time.sleep(1)
        final_message(nft_wallet, text_box)
        if message:
            try:
                #img = print_full_screen() 
                #telegram_img(img)
                author_text = author_text.replace('\n', ' ')
                telegram_msg(author_text)
                #os.remove('\img.png')
            except:
                pass
            for text in message:
                final_message(text, text_box)
        final_message('Upvoted!', text_box)
        final_message('Done!', text_box)

        submit_comment()
        texts_posteds.append(text_title)
        insert_db(text_title)
        
        return True
    except:
        return

def user_visited():
    """Recebe os comentários para eliminar postragens 
    já visitadas"""
    post_comments = driver.find_element(by=By.CLASS_NAME, value=('_1YCqQVO-9r-Up6QPB9H6_4')).text.split('\nPartilhar')
    for comment in post_comments:
        if reddit_user in comment:
            print('\nPostagem já foi visitada.. ')
            return True
    return False

def main():
    global random_emoji
    global posts_confirm
    posts_executeds = 0
    ERROS = 0

    #Futura função para recolher o karma do Reddit
    #free_button = driver.find_element(by=By.ID, value='COIN_PURCHASE_DROPDOWN_ID')

    #Futura função para fechar janelas poopup de notificação
    #alert = driver.switch_to.alert()
    #alert.accept()

    while True:
        try:
            driver.switch_to.window(driver.window_handles[0]) #Selecionando/retornando a primeira aba do navegador
            body = driver.find_element(by=By.XPATH, value=('/html/body')).click() #Garantir o cursor em tela

            for fonte in source_posts:
                print(f'Acessando: {fonte}')
                driver.get(fonte)
                time.sleep(5) 
                #random_emoji = numpy.random.choice(emojis)
                posts_db = consult_db()
                posts_db = dict(posts_db)
                posts_selecteds(posts_db.values())
                time.sleep(5)
                for post in posts_confirm:
                    author = post[0]
                    text_title = post[1]
                    link_url = post[2]
                    if post_execute(link_url, text_title):
                        posts_executeds += 1
                        print(f"\n{posts_executeds} postagens executadas!")
                        print(f'\nPrévia da postagem executada:\n{text_title}')
                    else:
                        print(f'\nPrévia da postagem descartada:\n{text_title}')
                        insert_db_recusadas(text_title)
                    time.sleep(30)
            print(f'\nAguardando nova sequencia..')
            time.sleep(1200)
        except:
            ERROS += 1
            print(f'{ERROS} ERROs NA SESSÃO')

main()


#'Enviado poru/AstroApeNFT\nhá 3 minutos\n🎁 NFT GIVEAWAY 🎁 AND DROP YOUR WALLET ADDRESS! 🐉Sol Drac NFT🐉 READ COMMENT!\nSelf-Promo\n3 Comentários\nCompartilhar\nSalvar'
#upvote_button = driver.find_element_by_xpath('//*[@id="upvote-button-t3_tb9kr1"]') #Botão do Upvote da postagem principal
post_author = driver.find_element_by_class_name('_2mHuuvyV9doV3zwbZPtIPG').text #Encontrando o autor da postagem
post_comments = driver.find_elements_by_class_name('_1YCqQVO-9r-Up6QPB9H6_4')[0].text.split('\nCompartilhar') #Coletando dados do comentário do author para definir regras
time_post = time_post_select()

#https://www.reddit.com/user/Aluxy16/
#https://www.reddit.com/r/NFTsMarketplace/
#https://www.reddit.com/user/AstroApeNFT/

#jamesarcanjo
#bUnGFXRkrW8kpgX
#NFT GIVEAWAY
#0x5565CD8a2ea7dc42427Ba99F6b261D2985005CcB Discord grupomoura#3625 Twitter JamescMoura
#Discord grupomoura#3625 ✅

"""
0x5565CD8a2ea7dc42427Ba99F6b261D2985005CcB
Discord grupomoura#3625
Upvoted!
"""

#driver.execute_script(f"window.open('{link_url}', '_blank')")
#driver.switch_to.window(driver.window_handles[1]) 
#driver.switch_to.window(driver.current_window_handle) 