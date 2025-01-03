from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import csv
import pandas as pd

#abrindo instancia do Chrome
service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

url = "https://portal.cfm.org.br/busca-medicos"
driver.get(url)

id_municipio = "2754"

time.sleep(2)

botao_aceito = driver.find_element(By.CLASS_NAME, "button")
botao_aceito.click()

time.sleep(2)

uf = driver.find_element(By.ID, "uf")
select = Select(uf)
select.select_by_value("MG")

time.sleep(2)

municipio = driver.find_element(By.ID, "municipio")
select = Select(municipio)
select.select_by_value(id_municipio)

time.sleep(2)

tipo_situacao = driver.find_element(By.ID,"tipoSituacao")
select = Select(tipo_situacao)
select.select_by_value("A")

time.sleep(3)

situacao = driver.find_element(By.ID,"situacao")
select = Select(situacao)
select.select_by_value("A")

time.sleep(1)

botao_enviar = driver.find_element(By.CLASS_NAME, "btnPesquisar")
botao_enviar.click()

time.sleep(25)

card_body = driver.find_elements(By.CLASS_NAME, "card-body")
dados_medicos = []

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
        # Captura todo o texto da div
        div_text = div.get_attribute("innerText").strip()
        
        # Separa as linhas por quebras de linha (inclui <br>)
        linhas = div_text.split("\n")
        
        # Adiciona cada linha à lista, se não estiver vazia
        for linha in linhas:
            if linha.strip():  # Ignora linhas vazias
                especialidades.append(linha.strip())
                
    endereco_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md-7') and .//b[text()='Endereço:']]")
    endereco = endereco_div.text.split("Endereço:")[-1].strip()
    
    telefone_div = card.find_element(By.XPATH, ".//div[contains(@class, 'col-md-7') and .//b[text()='Telefone:']]")
    telefone = telefone_div.text.split("Telefone:")[-1].strip()
    
    print(nome, crm, data_inscricao, primeira_inscricao, inscricao, situacao, especialidades, endereco, telefone)
    dados_medicos.append([nome, crm, data_inscricao, primeira_inscricao, inscricao, situacao, ", ".join(especialidades), endereco, telefone])

# Criando o DataFrame
df = pd.DataFrame(dados_medicos, columns=["Nome", "CRM", "Data Inscrição", "Primeira Inscrição", "Inscrição", "Situação", "Especialidades", "Endereço", "Telefone"])

# Remove tudo após "Especialidades/Áreas de Atuação:" (inclusive ela) na coluna "Especialidades"
df["Inscrições em Outros Estados"] = df["Especialidades"].replace(r"Especialidades/Áreas de Atuação:.*,", "", regex=True)

# Remove tudo à esquerda de "Especialidades/Áreas de Atuação:" (inclusive ela) e mantém apenas o que está à direita
df["Especialidades"] = df["Especialidades"].replace(r".*Especialidades/Áreas de Atuação:,", "", regex=True) 

# Salvando em CSV
df.to_csv("medicos.csv", index=False, encoding="utf-8")

print("Arquivo CSV gerado com sucesso!")
