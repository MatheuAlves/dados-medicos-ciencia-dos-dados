from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import time
import random
import pandas as pd
import os

# Configurando o navegador
service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

url = "https://portal.cfm.org.br/busca-medicos"
driver.get(url)

# Variável para definir a página inicial
pagina_inicial = 1
id_municipio = "3206"
aleatorio = random.uniform(3, 6)

time.sleep(1)

def aguardar_captcha_sumir():
    try:
        print("Verificando presença do captcha...")

        # Espera até que o captcha desapareça (com verificação contínua)
        WebDriverWait(driver, 3000, poll_frequency=1).until_not(
            EC.presence_of_element_located((By.ID, "rc-imageselect"))
        )

        print("Captcha resolvido ou desapareceu.")
    except Exception as e:
        print(f"Nenhum captcha detectado ou erro: {e}")

# Aceitando cookies
botao_aceito = driver.find_element(By.CLASS_NAME, "button")
botao_aceito.click()
time.sleep(1)

# Selecionando UF e Município
uf = driver.find_element(By.ID, "uf")
select = Select(uf)
select.select_by_value("MG")

time.sleep(1)

municipio = driver.find_element(By.ID, "municipio")
select = Select(municipio)
select.select_by_value(id_municipio)

time.sleep(1)

# Selecionando situação
tipo_situacao = driver.find_element(By.ID, "tipoSituacao")
select = Select(tipo_situacao)
select.select_by_value("A")

time.sleep(1)

situacao = driver.find_element(By.ID, "situacao")
select = Select(situacao)
select.select_by_value("A")

time.sleep(1)

# Enviando formulário
botao_enviar = driver.find_element(By.CLASS_NAME, "btnPesquisar")
botao_enviar.click()

# Exemplo de navegação
aguardar_captcha_sumir()  # Chama a função para verificar o captcha

# Inicializando lista para armazenar os dados
dados_medicos = []

# Nome do arquivo CSV
nome_arquivo_csv = "medicos.csv"

    
# Função para coletar dados da página atual
def coletar_dados_pagina():
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
    salvar_csv(dados_medicos,["Nome", "CRM", "Data Inscrição", "Primeira Inscrição", "Inscrição", "Situação", "Especialidades", "Endereço", "Telefone"],nome_arquivo_csv)
    dados_medicos.clear()

# Função para salvar os dados no arquivo CSV
def salvar_csv(dados, colunas, nome_arquivo):
    if not os.path.isfile(nome_arquivo):  # Se o arquivo não existir, cria com cabeçalho
        df = pd.DataFrame(dados, columns=colunas)
        df.to_csv(nome_arquivo, index=False, encoding="utf-8")
    else:  # Se o arquivo já existir, anexa sem duplicar cabeçalho
        df = pd.DataFrame(dados, columns=colunas)
        df.to_csv(nome_arquivo, index=False, encoding="utf-8", mode="a", header=False)

# Identificando o número total de páginas
try:
    last_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "paginationjs-last")))
    total_pages = int(last_page.get_attribute("data-num"))
    print(f"Total de páginas: {total_pages}")
except TimeoutException:
    print("Erro: Timeout ao tentar encontrar o número total de páginas.")
    total_pages = 1

#Navegando para a página inicial
if pagina_inicial > 1:
    for page in range(1, pagina_inicial):
        try:
            print(f"Navegando para a página {page}...")
            
            # Chama a função para verificar o captcha
            aguardar_captcha_sumir()
            
            # Tenta clicar no botão da próxima página com uma abordagem mais robusta
            while True:
                try:
                    next_page = WebDriverWait(driver, 100).until(
                        EC.element_to_be_clickable((By.XPATH, f'//li[@data-num="{page + 1}"]/a'))
                    )
                    next_page.click()
                    break  # Sai do loop se o clique for bem-sucedido
                except StaleElementReferenceException:
                    print("Elemento obsoleto. Tentando novamente...")
                    continue  # Recarrega o elemento e tenta novamente
                except TimeoutException:
                    print(f"Erro: Timeout ao navegar para a página {page}.")
                    break  # Sai do loop se não conseguir encontrar o elemento
        except Exception as e:
            print(f"Erro inesperado ao navegar para a página {page}: {e}")
            break

    time.sleep(15)  # Pequena pausa após navegar pelas páginas


# Iterando por todas as páginas
for page in range(pagina_inicial, total_pages + 1):
    print(f"Coletando dados da página {page}...")
    coletar_dados_pagina()
    
    # Navegando para a próxima página, se não for a última
    if page < total_pages:
        aguardar_captcha_sumir()  # Chama a função para verificar o captcha

        while True:
            try:
                # Localiza o botão da próxima página
                next_page = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//li[@data-num="{page + 1}"]/a'))
                )
                next_page.click()  # Clica no botão da próxima página
                break  # Sai do loop se o clique for bem-sucedido
            except StaleElementReferenceException:
                print("Elemento obsoleto. Tentando localizar novamente...")
                continue  # Recarrega o elemento e tenta novamente
            except TimeoutException:
                print(f"Erro: Timeout ao tentar navegar para a página {page + 1}.")
                break  # Sai do loop se o tempo esgotar sem localizar o elemento

        # Pequena pausa antes de processar a próxima página
        time.sleep(aleatorio)



# Fechando o navegador
print(f"Dados salvos em {nome_arquivo_csv} com sucesso!")
driver.quit()
