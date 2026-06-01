from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
import json
import csv


navegador = webdriver.Firefox()

url = "https://app.powerbi.com/view?r=eyJrIjoiOGU2ZGM3NjUtYzFlOS00Y2E3LWJlZmUtZjkzMzdiODQ1M2IxIiwidCI6IjQwNmMyNTc1LWM5ZDQtNGQ0NC1hNWI2LWJiNThiYzg2MDMzZSJ9"
navegador.get(url)

wait = WebDriverWait(navegador, 20)

try:
    # ! Encontrando o contêiner de rolagem da tabela
    scrollable_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.mid-viewport")))

    # ! Usa um conjunto para armazenar linhas de dados únicas
    linhas_extraidas_unicas = set()

    # ! Para controle de rolagem
    posicao_anterior = -1
    posicao_atual = 0

    # + Coletando os primeiros dados antes da primeira rolagem
    html_inicial = navegador.execute_script("return arguments[0].innerHTML", scrollable_div)
    soup_inicial = BeautifulSoup(html_inicial, 'html.parser')
    linhas = soup_inicial.find_all('div', {'role': 'row', 'class': 'row'})
    for linha in linhas:
        linhas_extraidas_unicas.add(str(linha))

    # ! Iniciando um loop de rolagem
    # ! Faz a rolagem até a posição for diferente da posição anterior
    while posicao_atual != posicao_anterior:
        posicao_anterior = posicao_atual
        
        # ! Rola para baixo pela altura do contêiner visível
        altura_div = navegador.execute_script("return arguments[0].clientHeight", scrollable_div)
        navegador.execute_script(f"arguments[0].scrollTop += {altura_div}", scrollable_div)
        sleep(2)

        # + Coleta os novos dados que apareceram na tela
        html_atual = navegador.execute_script("return arguments[0].innerHTML", scrollable_div)
        soup_atual = BeautifulSoup(html_atual, 'html.parser')
        linhas = soup_atual.find_all('div', {'role': 'row', 'class': 'row'})
        for linha in linhas:
            linhas_extraidas_unicas.add(str(linha))

        posicao_atual = navegador.execute_script("return arguments[0].scrollTop", scrollable_div)
    
    # ! Processar todas as linhas únicas após a rolagem completa
    dados_extraidos = []
    for linha_str in linhas_extraidas_unicas:
        soup_linha = BeautifulSoup(linha_str, 'html.parser')
        linha = soup_linha.find('div', {'role': 'row'})
        
        celulas = linha.find_all('div', class_='pivotTableCellWrap')
        
        if len(celulas) >= 4:
            modelo = celulas[0].get_text(strip=True)
            fabricante = celulas[1].get_text(strip=True)
            quantidade = celulas[2].get_text(strip=True)
            marketshare = celulas[3].get_text(strip=True)
            
            dados_extraidos.append({
                'Modelo': modelo,
                'Fabricante': fabricante,
                'Quantidade': quantidade,
                'MarketShare': marketshare
            })

    # + Salvando os dados no arquivo CSV
    if dados_extraidos:
        nome_do_arquivo = 'veiculos_vendidos.csv'
        chaves = dados_extraidos[0].keys()
        
        with open(nome_do_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
            writer = csv.DictWriter(arquivo_csv, fieldnames=chaves)
            writer.writeheader()
            writer.writerows(dados_extraidos)

        print(f"\nDados salvos com sucesso em '{nome_do_arquivo}'")

    else:
        print("Nenhum dado foi extraído. O arquivo CSV não foi criado.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")

finally:
    navegador.quit()