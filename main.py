from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# # Abrindo instância do Chrome
service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

url = "https://portal.cfm.org.br/busca-medicos"
driver.get(url)

id_municipio = "2754"

time.sleep(2)

# Aceitando cookies
botao_aceito = driver.find_element(By.CLASS_NAME, "button")
botao_aceito.click()

time.sleep(2)

# Selecionando UF e Município
uf = driver.find_element(By.ID, "uf")
select = Select(uf)
select.select_by_value("MG")

time.sleep(2)

municipio = driver.find_element(By.ID, "municipio")
select = Select(municipio)
select.select_by_value(id_municipio)

time.sleep(2)

# Selecionando situação
tipo_situacao = driver.find_element(By.ID, "tipoSituacao")
select = Select(tipo_situacao)
select.select_by_value("A")

time.sleep(3)

situacao = driver.find_element(By.ID, "situacao")
select = Select(situacao)
select.select_by_value("A")

time.sleep(1)

# Enviando formulário
botao_enviar = driver.find_element(By.CLASS_NAME, "btnPesquisar")
botao_enviar.click()

time.sleep(5)

# Inicializando lista para armazenar os dados
dados_medicos = []

# Função para verificar e lidar com CAPTCHA
def resolver_captcha():
    try:
        # Aguarda por um elemento que indique a presença do CAPTCHA
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Eu não sou um robô')]"))
        )
        print("CAPTCHA detectado. Resolva manualmente e pressione Enter para continuar...")
        input()  # Aguarda resolução manual do CAPTCHA
    except:
        pass  # Se nenhum CAPTCHA for detectado, continua normalmente

# Função para coletar dados da página atual
def coletar_dados_pagina():
    resolver_captcha()  # Verifica se há um CAPTCHA antes de prosseguir
    card_body = driver.find_elements(By.CLASS_NAME, "card-body")
    for card in card_body:
        nome = card.find_element(By.TAG_NAME, "h4").text
        
        crm_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md-4') and .//b[text()='CRM:']]")
        crm = crm_div.text.split("CRM:")[-1].strip()
        
        data_inscricao_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md-4') and .//b[text()='Data de Inscrição:']]")
        data_inscricao = data_inscricao_div.text.split("Data de Inscrição:")[-1].strip()
        
        primeira_inscricao_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md-4') and .//b[text()='Primeira inscrição na UF:']]")
        primeira_inscricao = primeira_inscricao_div.text.split("Primeira inscrição na UF:")[-1].strip()
        
        inscricao_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md-6') and .//b[text()='Inscrição:']]")
        inscricao = inscricao_div.text.split("Inscrição:")[-1].strip()
        
        situacao_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md') and .//b[text()='Situação:']]")
        situacao = situacao_div.text.split("Situação:")[-1].strip()
        
        especialidade_divs = card.find_elements(By.CLASS_NAME, "col-md-12")
        especialidades = []
        for div in especialidade_divs:
            div_text = div.get_attribute("innerText").strip()
            linhas = div_text.split("\n")
            for linha in linhas:
                if linha.strip():
                    especialidades.append(linha.strip())
                    
        endereco_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md-7') and .//b[text()='Endereço:']]")
        endereco = endereco_div.text.split("Endereço:")[-1].strip()
        
        telefone_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md-7') and .//b[text()='Telefone:']]")
        telefone = telefone_div.text.split("Telefone:")[-1].strip()
        
        dados_medicos.append([nome, crm, data_inscricao, primeira_inscricao, inscricao, situacao, ", ".join(especialidades), endereco, telefone])

# Extraindo número total de páginas
try:
    last_page = driver.find_element(By.CLASS_NAME, "paginationjs-last")
    total_pages = int(last_page.get_attribute("data-num"))
    print(f"Total de páginas: {total_pages}")
except:
    total_pages = 1  # Caso não haja paginação

# Iterando por todas as páginas
for page in range(1, total_pages + 1):
    print(f"Coletando dados da página {page}...")
    coletar_dados_pagina()
    
    # Navegando para a próxima página, se não for a última
    if page < total_pages:
        next_page = driver.find_element(By.XPATH, f'//li[@data-num="{page + 1}"]/a')
        next_page.click()
        time.sleep(2)  # Ajuste conforme necessário

# Criando o DataFrame
df = pd.DataFrame(dados_medicos, columns=["Nome", "CRM", "Data Inscrição", "Primeira Inscrição", "Inscrição", "Situação", "Especialidades", "Endereço", "Telefone"])

# Salvando em CSV
df.to_csv("medicos.csv", index=False, encoding="utf-8")

print("Arquivo CSV gerado com sucesso!")
driver.quit()
