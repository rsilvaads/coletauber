from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from datetime import datetime
import pandas as pd
import schedule
import time
import sys
import re

# Inicialização de listas e variáveis globais
locais = []
coletados = []
nome_arquivo = 'uber.xlsx'  # Nome da planilha do Uber
numero_celular = ''  # Número de celular (para receber o código de verificação)
senha = ''  # Senha da conta Uber

# Lê os dados do arquivo Excel para um DataFrame do pandas.
df_excel_uber = pd.read_excel(nome_arquivo)
origens = list(dict.fromkeys(df_excel_uber.iloc[1:,1].tolist()))
destinos = list(dict.fromkeys(df_excel_uber.iloc[1:,2].tolist()))
horarios = list(dict.fromkeys(df_excel_uber.iloc[1:,3].tolist()))
horarioatual = datetime.now().time().strftime("%H:%M:%S")

# Configurações do WebDriver do Firefox, incluindo o modo "headless" (sem interface gráfica)
options = webdriver.FirefoxOptions()
options.add_argument('--headless')

# Inicializa o navegador Firefox com as opções definidas
browser = webdriver.Firefox(options=options)
browser.get('https://m.uber.com/looking')

# Definição de função para formatar um número de telefone
def formataNumero(numero_original):
    numero_original = str(numero_original)
    format_string = "({area_code}) {exchange}-{line_number}"

    if len(numero_original) == 11:
        area_code = numero_original[:2]
        exchange = numero_original[2:7]
        line_number = numero_original[7:]
    else:
        area_code = numero_original[:2]
        exchange = numero_original[2:6]
        line_number = numero_original[6:]

    numero_formatado = format_string.format(area_code=area_code, exchange=exchange, line_number=line_number)
    return str(numero_formatado)

# Definição de função para realizar o login no Uber
def loginUber():

    # Função interna para preencher a tela inicial com o número de celular
    def telainicial():
        global codigo        
        browser.find_element("id", "PHONE_NUMBER_or_EMAIL_ADDRESS").send_keys(numero_celular)
        browser.find_element("id", "forward-button").click()

    for origem in range(len(origens)):

        while True:
            try:
                # Verifica se o campo de número de telefone ou e-mail está presente
                if browser.find_element("id", "PHONE_NUMBER_or_EMAIL_ADDRESS"):
                    telainicial()
                    time.sleep(10)
                    browser.find_element("id", "PASSWORD").send_keys(senha)
                    browser.find_element("id", "forward-button").click()
            except NoSuchElementException:       
                try:
                    while True:
                        try:
                            # Verifica se o código SMS está presente
                            if browser.find_element("id", "PHONE_SMS_OTP-0"):
                                codigo = input("Digite o código do Uber que chegou no celular "+formataNumero(numero_celular)+" : ")
                                digitos_codigo = [int(digito) for digito in codigo]
                                if codigo.isnumeric():
                                    if len(digitos_codigo) == 4 or len(digitos_codigo) == 6:
                                        break
                                    else:
                                        continue
                                else:
                                    print("Saindo...")
                                    browser.quit()
                                    break
                        except:
                            try:
                                # Verifica se ocorreram muitas tentativas de login
                                if browser.find_element("xpath", "/html/body/div[5]/div[2]/div/div/div/div/h1"):
                                    print("Muitas tentativas!")
                                    browser.quit()
                                    break
                                    sys.exit(0)
                            except:
                                print("Código não digitado ou não foi possível usar esse número de telefone!")
                                browser.quit()
                                break

                    try:
                        browser.find_element("id", "PHONE_SMS_OTP-0").send_keys(digitos_codigo[0])
                        browser.find_element("id", "PHONE_SMS_OTP-1").send_keys(digitos_codigo[1])
                        browser.find_element("id", "PHONE_SMS_OTP-2").send_keys(digitos_codigo[2])
                        browser.find_element("id", "PHONE_SMS_OTP-3").send_keys(digitos_codigo[3])
                    except:
                        pass

                    try:
                        browser.find_element("id", "PHONE_SMS_OTP-4").send_keys(digitos_codigo[4])
                        browser.find_element("id", "PHONE_SMS_OTP-5").send_keys(digitos_codigo[5])
                    except:
                        pass

                    time.sleep(10)

                    try:
                        if browser.find_element("id", "PASSWORD"):
                            browser.find_element("id", "PASSWORD").send_keys(senha)
                            browser.find_element("id", "forward-button").click()
                            break
                    except NoSuchElementException:
                        pass

                    try:
                        if browser.find_element("id", "alt-alternate-forms-option-modal"):
                            browser.find_element("id", "alt-alternate-forms-option-modal").click()
                            time.sleep(5)
                            browser.find_element("xpath", "/html/body/div[1]/div[2]/div/div[2]/div/div/div/div/button[3]").click()
                            break
                    except NoSuchElementException:
                        pass

                    try:
                        if browser.find_element("id", "alt-PASSWORD"):
                            browser.find_element("id", "alt-PASSWORD").click()
                            print("Logando direto com a senha...")
                            browser.find_element("id", "alt-PASSWORD").click()
                            break
                    except NoSuchElementException:
                        pass

                    try:
                        if browser.find_element("xpath", "//input[@placeholder='Add a pickup location']"):
                            break
                    except:
                        print("Deu ruim... Tentando novamente...")
                        browser.quit()
                        telainicial()
                            
                except NoSuchElementException:
                    break
                
        while True:
            WebDriverWait(browser, 30).until(
                EC.presence_of_element_located(("xpath", "//input[@placeholder='Add a pickup location']"))
            )
            if browser.find_element("xpath", "//input[@placeholder='Add a pickup location']"):
                break
            continue

        print("Logado no Uber!")
        return True

# Definição de função para realizar a coleta de preços de corridas do Uber
def fazColeta(origens, destinos):
    global coletados
    for i in range(len(origens)):

        # Função interna para enviar o local (origem ou destino)
        def enviar(caminho):
            try:
                browser.find_element("xpath", "//p

[@contains(text(), '{caminho}')]").click()
            except:
                browser.find_element("xpath", "/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div/span/div/div[3]/ul/li[1]/div[1]").click()
                
        origem = browser.find_element("xpath", "//input[@placeholder='Add a pickup location']")
        destino = browser.find_element("xpath", "//input[@placeholder='Enter your destination']")

        origem.send_keys(origens[i])
        time.sleep(3)
        enviar(origens[i])
        time.sleep(3)

        destino.send_keys(destinos[i])
        time.sleep(3)
        enviar(destinos[i])
        time.sleep(3)      

        try:
            try:
                if browser.find_element("xpath", "/html/body/div[1]/div/div/div/1/div/div[2]/div[2]/div/span/div/div[3]/div/ul/li[1]/div[2]/div[2]/div/p[2]"):
                    precos = browser.find_element("xpath", "/html/body/div[1]/div/div/div/1/div/div[2]/div[2]/div/span/div/div[3]/div/ul/li[1]/div[2]/div[2]/div/p[2]").text

            except:
                if browser.find_element("xpath", "/html/body/div[1]/div/div/div/1/div/div[2]/div[2]/div/span/div/div[3]/div/ul/li[1]/div[2]/div[2]/div/p[1]"):
                    precos = browser.find_element("xpath", "/html/body/div[1]/div/div/div/1/div/div[2]/div[2]/div/span/div/div[3]/div/ul/li[1]/div[2]/div[2]/div/p[1]").text
                
            coletados.append(precos)

            origem.clear()
            time.sleep(3)
            destino.clear()
            time.sleep(3)
            print(coletados)
        except:
            precos = 0
            coletados.append(precos)

    return coletados

# Define uma função para definir os locais coletados no DataFrame
def set_locais(df_excel_uber, date, time, dicionario):
    for rota in dicionario.keys():
        df_excel_uber.loc[(df_excel_uber['Horário'] == time) & (df_excel_uber['Origem'].iloc[1:,] == rota), df_excel_uber.iloc[0] == datetime.strptime(date, '%Y-%m-%d')] = dicionario[rota]

# Definição de função para realizar a coleta de preços em um horário específico
def coleta(horario):
    global locais
    global coletados
    print("Coletando...")
    fazColeta(origens, destinos)
    locais = origens * len(horarios)
    dicionario = dict(zip(locais, coletados))
    hoje = pd.Timestamp.now().strftime('%Y-%m-%d')
    set_locais(df_excel_uber, hoje, horario, dicionario)

    # Salva os dados no arquivo Excel.
    with pd.ExcelWriter(nome_arquivo, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        df_excel_uber.to_excel(writer, header=False, index=False)

    print("Coleta feitas às: "+str(horarioatual))
    coletados = []

# Definição de função para agendar as coletas em horários específicos
def defineColetas():
    # Está agendando quatro coletas diferentes, uma para cada horário. Pode ser otimizado.
    schedule.every().day.at(horarios[0]).do(coleta, horarios[0])
    schedule.every().day.at(horarios[1]).do(coleta, horarios[1])
    schedule.every().day.at(horarios[2]).do(coleta, horarios[2])
    schedule.every().day.at(horarios[3]).do(coleta, horarios[3])

# Função principal que inicia o processo de login e agendamento de coletas
def main():
    loginUber()
    while True:
        defineColetas()
        schedule.run_pending()
        # def formataPlanilha
        # def enviaGoogleDrive
        time.sleep(60)

if __name__ == "__main__":
    main()
