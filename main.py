import requests
from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
import os

# Carregar o arquivo CSV
df = pd.read_csv('nome_caged.csv')

# Função para converter a data de nascimento para o formato DDMMYYYY
def formatar_data_nascimento(data_iso):
    return pd.to_datetime(data_iso).strftime('%d%m%Y')

df['DATA_FORMATADA'] = df['DT_NASCIMENTO'].apply(formatar_data_nascimento)

def capturar_cookies_e_token():
    while True:  # Loop para tentar novamente em caso de erro
        try:
            # Iniciar o Playwright para resolver o captcha e capturar cookies e headers
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False) 
                page = browser.new_page()

                page.goto("https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp")
                page.wait_for_selector("iframe[title='Widget contendo caixa de seleção para desafio de segurança hCaptcha']", timeout=60000)
                
                # Acessar o iframe
                hcaptcha_frame = page.frame_locator("iframe[title='Widget contendo caixa de seleção para desafio de segurança hCaptcha']")

                # Clicar no checkbox dentro do iframe
                checkbox = hcaptcha_frame.locator('div[role="checkbox"]')
                checkbox.click()
                print("Clicando no captcha....")
                token_captcha = page.wait_for_function("""
                    () => document.querySelector("[name='h-captcha-response']").value !== ''
                """, timeout=5000)
                if not token_captcha:
                    raise ValueError("captcha não sucedido")
                else:
                    print("captcha concluido")

                # Captura o token do captcha
                captcha_token = page.evaluate('document.querySelector("[name=h-captcha-response]").value')
                
                # Capturar os cookies da sessão
                cookies = page.context.cookies()

                # Capturar os headers necessários
                headers = page.evaluate('''() => {
                    return {
                        'User-Agent': navigator.userAgent,
                        'Accept-Language': navigator.language,
                        'Referer': document.referrer
                    }
                }''')

                browser.close()

                return cookies, headers, captcha_token
        except Exception as e:
            print(f"Erro ao capturar o token ou cookies: {e}. Tentando novamente...")

def enviar_formulario_com_post(cookies, headers, captcha_token, cpf, data_nascimento):
    if not cookies or not headers or not captcha_token:
        print(f"Consulta para o CPF {cpf} não realizada. Falha na captura do token ou cookies.")
        return
    url = "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublicaExibir.asp"
    # Organiza os cookies para o requests
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    # Adicionar os cabeçalhos padrão necessários
    headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://servicos.receita.fazenda.gov.br",
        "Referer": "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1"
    })
    data = {
        "idCheckedReCaptcha": "false",
        "txtCPF": cpf,
        "txtDataNascimento": data_nascimento,
        "h-captcha-response": captcha_token,
        "Enviar": "Consultar"
    }
    response = requests.post(url, headers=headers, data=data, cookies=cookies_dict)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    file_name = f"{cpf}.txt"
    download_dir = os.path.join('consultas')
    os.makedirs(download_dir, exist_ok=True)
    file_path = os.path.join(download_dir, file_name)
    conteudos_esquerda = soup.find_all('div', class_='clConteudoEsquerda')
    
    with open(file_path, "w", encoding="utf-8") as file:
        for div in conteudos_esquerda:
            bold_tags = div.find_all('b')
            for bold in bold_tags:
                file.write(bold.get_text(strip=True) + '\n')
    print(f"Consulta do CPF {cpf} salva em {file_path}")
  
# Looping para processar cada CPF e data de nascimento na planilha
for index, row in df.iterrows():
    cpf = row['CPF']
    data_nascimento = row['DATA_FORMATADA']
    
    cookies, headers, token_captcha = capturar_cookies_e_token()
    enviar_formulario_com_post(cookies, headers, token_captcha, cpf, data_nascimento)
print(f"Total de consultas realizadas: {len(df)}")
