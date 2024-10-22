import pandas as pd
from playwright.sync_api import sync_playwright

# Carregar a planilha com CPFs e Datas de Nascimento
file_path = 'nome_caged.csv'
df = pd.read_csv(file_path)

def processar_cpf_data(cpf, data_nascimento):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()

        url = "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp"
        page.goto(url)

        page.wait_for_load_state("networkidle")

        page.fill('input[name="txtCPF"]', cpf)
        page.fill('input[name="txtDataNascimento"]', data_nascimento)

        hcaptcha_frame = page.frame_locator("iframe[title='Widget contendo caixa de seleção para desafio de segurança hCaptcha']")

        checkbox = hcaptcha_frame.locator('div[role="checkbox"]')
        checkbox.click()

        print("resolva o captcha manualmente se necessário.")
        page.wait_for_timeout(10000)

        captcha_token = page.evaluate('document.querySelector("[name=h-captcha-response]").value')
        print(f'Token Capturado: {captcha_token}')

        page.evaluate(f'document.querySelector("[name=h-captcha-response]").value = "{captcha_token}";')

        page.click('input[type="submit"]')

        print(f"Formulário enviado para o CPF {cpf}. Verifique os resultados no navegador.")
        page.wait_for_timeout(30000)  # Aguarde 30 segundos para observar o resultado

        # Fechar o navegador manualmente ou automaticamente
        # browser.close()

# Iterar sobre cada linha do DataFrame e processar
for index, row in df.iterrows():
    cpf = row['CPF']  
    data_nascimento = row['DT_NASCIMENTO'].replace("-", "")
    
    print(f"Processando CPF: {cpf} e Data de Nascimento: {data_nascimento}")
    processar_cpf_data(cpf, data_nascimento)
