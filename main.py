import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd

df = pd.read_csv('nome_caged.csv')

# Função para converter a data de nascimento para o formato DDMMYYYY
def formatar_data_nascimento(data_iso):
    return pd.to_datetime(data_iso).strftime('%d%m%Y')

df['DATA_FORMATADA'] = df['DT_NASCIMENTO'].apply(formatar_data_nascimento)

# diretorio
download_dir = 'consultas'
os.makedirs(download_dir, exist_ok=True)

def realizar_consulta(cpf, data_nascimento):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        url = "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp"
        page.goto(url)

        page.wait_for_selector('input[name="txtCPF"]', timeout=90000)

        page.fill('input[name="txtCPF"]', str(cpf))
        page.fill('input[name="txtDataNascimento"]', str(data_nascimento))

        # Localizar o checkbox do captcha
        hcaptcha_frame = page.frame_locator("iframe[title='Widget contendo caixa de seleção para desafio de segurança hCaptcha']")
        checkbox = hcaptcha_frame.locator('div[role="checkbox"]')
        checkbox.click()

        print("Resolvendo o captcha manualmente se for solicitado.")
        page.wait_for_timeout(600)

        # Capturar o token hCaptcha gerado após a resolução
        # captcha_token = page.evaluate('document.querySelector("[name=h-captcha-response]").value')

        # Submeter o formulário e esperar a navegação
        with page.expect_navigation(wait_until="networkidle"):
            page.click('input[name="Enviar"]')

        # Capturar o conteúdo da página de resposta e usar BeautifulSoup para processar
        response_html = page.content()
        soup = BeautifulSoup(response_html, 'html.parser')

        file_name = f"{cpf}.txt"
        file_path = os.path.join(download_dir, file_name)

        conteudos_esquerda = soup.find_all('div', class_='clConteudoEsquerda')

        with open(file_path, "w", encoding="utf-8") as file:
            for div in conteudos_esquerda:
                bold_tags = div.find_all('b')
                for bold in bold_tags:
                    file.write(bold.get_text(strip=True) + '\n')

        print(f"Consulta para CPF {cpf} concluída. Conteúdo salvo em {file_path}")

        # Fechar o navegador
        browser.close()

# Iterar sobre o DataFrame e realizar consultas para cada CPF
for index, row in df.iterrows():
    cpf = row['CPF']
    data_nascimento = row['DATA_FORMATADA']

    # Chamar a função para realizar a consulta
    realizar_consulta(cpf, data_nascimento)

print(f"Total de consultas realizadas: {len(df)}")
    
