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

# Define algumas variáveis globais.
locais = [] 
coletados = []
nome_arquivo = 'uber.xlsx'  # Nome do arquivo Excel.
numero_celular = ''  # Número de celular (para receber o código).
senha = ''  # Senha da conta Uber.

# Lê os dados do arquivo Excel para um DataFrame do pandas.
df_excel_uber = pd.read_excel(nome_arquivo)

# Extrai listas de origens, destinos e horários únicos dos dados do Excel.
origens = list(dict.fromkeys(df_excel_uber.iloc[1:, 1].tolist()))
destinos = list(dict.fromkeys(df_excel_uber.iloc[1:, 2].tolist()))
horarios = list(dict.fromkeys(df_excel_uber.iloc[1:, 3].tolist()))
horarioatual = datetime.now().time().strftime("%H:%M:%S")

# Configura as opções do driver do Firefox, tornando-o "headless" (invisível).
options = webdriver.FirefoxOptions()
options.add_argument('--headless')

# Inicializa o navegador Firefox com as opções especificadas.
browser = webdriver.Firefox(options=options)

# Abre a página inicial do Uber.
browser.get('https://m.uber.com/looking')

# Define uma função para formatar números de telefone.
def formataNumero(numero_original):
    # Código para formatar o número de telefone de acordo com um formato específico.
    # Retorna o número formatado como uma string.
    return str(numero_formatado)

# Define uma função para fazer login no Uber.
def loginUber():
    # Define uma função interna para a tela inicial do login.
    def telainicial():
        global codigo
        # Preenche o número de celular e clica no botão "Avançar".
        browser.find_element("id", "PHONE_NUMBER_or_EMAIL_ADDRESS").send_keys(numero_celular)
        browser.find_element("id", "forward-button").click()

    for origem in range(len(origens)):
        while True:
            try:
                if browser.find_element("id", "PHONE_NUMBER_or_EMAIL_ADDRESS"):
                    telainicial()
                    time.sleep(10)
                    browser.find_element("id", "PASSWORD").send_keys(senha)
                    browser.find_element("id", "forward-button").click()
            except NoSuchElementException:
                # Lida com exceções quando elementos não são encontrados na página.
                try:
                    while True:
                        try:
                            if browser.find_element("id", "PHONE_SMS_OTP-0"):
                                codigo = input("Digite o código do Uber que chegou no celular " + formataNumero(numero_celular) + " : ")
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

# Define uma função para realizar a coleta de preços das viagens.
def fazColeta(origens, destinos):
    global coletados
    for i in range(len(origens)):

        def enviar(caminho):
            try:
                browser.find_element("xpath", "//p[@contains(text(), '{caminho}')]").click()
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
                if browser.find_element("xpath", "/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div/span/div/div[3]/div/ul/li[1]/div[2]/div[2]/div/p[2]"):
                    precos = browser.find_element("xpath", "/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div/span/div/div[3]/div/ul/li[1]/div[2]/div[2]/div/p[2]").text

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

# Define uma função para definir os locais coletados no DataFrame do Excel.
def set_locais(df_excel_uber, date, time, dicionario):
    for rota in dicionario.keys():
        df_excel_uber.loc[(df_excel_uber['Horário'] == time) & (df_excel_uber['Origem'].iloc[1:, ] == rota),
                          df_excel_uber.iloc[0] == datetime.strptime(date, '%Y-%m-%d')] = dicionario[rota]

# Define uma função para realizar a coleta de dados.
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

    print("Coleta feita às: " + str(horarioatual))
    coletados = []

# Define uma função para agendar as coletas em horários específicos.
def defineColetas():
    # Agenda as coletas para os horários especificados.
    schedule.every().day.at(horarios[0]).do(coleta, horarios[0])
    schedule.every().day.at(horarios[1]).do(coleta, horarios[1])
    schedule.every().day.at(horarios[2]).do(coleta, horarios[2])
    schedule.every().day.at(horarios[3]).do(coleta, horarios[3])

# Função principal do programa.
def main():
    loginUber()
    while True:
        defineColetas()
        schedule.run_pending()
        time.sleep(60)  # Espera 60 segundos antes de verificar as tarefas agendadas novamente.

if __name__ == "__main__":
    main()

