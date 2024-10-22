import requests
from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
import os


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    url = "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp"
    page.goto(url)

    # Espera a página carregar completamente
    page.wait_for_load_state("networkidle")

    cpf = '06474251735'  # Substitua pelo CPF desejado
    data_nascimento = '13022003'  # Substitua pela data de nascimento desejada
    page.fill('input[name="txtCPF"]', cpf)
    page.fill('input[name="txtDataNascimento"]', data_nascimento)

    hcaptcha_frame = page.frame_locator("iframe[title='Widget contendo caixa de seleção para desafio de segurança hCaptcha']")

    checkbox = hcaptcha_frame.locator('div[role="checkbox"]')
    checkbox.click()

    print("Por favor, resolva o captcha manualmente se for solicitado.")
    page.wait_for_timeout(10000) 

    # Capturar o token hCaptcha gerado após a resolução
    captcha_token = page.evaluate('document.querySelector("[name=h-captcha-response]").value')
    print(f'Token Capturado: {captcha_token}')

    # Preencher o campo oculto com o token do captcha
    page.evaluate(f'document.querySelector("[name=h-captcha-response]").value = "{captcha_token}";')

    page.click('input[type="submit"]')

    print("Formulário enviado. Verifique os resultados no navegador.")
    page.wait_for_load_state("networkidle")

    # Capturar o conteúdo da página de resposta e usar BeautifulSoup para processar
    response_html = page.content()
    soup = BeautifulSoup(response_html, 'html.parser')

    download_dir = 'consultas'
    os.makedirs(download_dir, exist_ok=True)

    file_name = f"{cpf}.txt"
    file_path = os.path.join(download_dir, file_name)

    # Encontrar e salvar os conteúdos dentro de <div class="clConteudoEsquerda"> no arquivo txt
    conteudos_esquerda = soup.find_all('div', class_='clConteudoEsquerda')

    with open(file_path, "w", encoding="utf-8") as file:
        for div in conteudos_esquerda:
            bold_tags = div.find_all('b')
            for bold in bold_tags:
                file.write(bold.get_text(strip=True) + '\n')

    print(f"Conteúdo salvo em {file_path}")

    # Manter o navegador aberto para verificar os resultados
    page.wait_for_timeout(10000)

    # Fechar o navegador manualmente ou automaticamente
    # browser.close()

