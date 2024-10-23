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
    while True:  # Loop para tentar novamente em caso de erro
        try:

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                url = "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp"
                page.goto(url)

                page.wait_for_selector('input[name="txtCPF"]', timeout=10000)

                page.fill('input[name="txtCPF"]', str(cpf))
                page.fill('input[name="txtDataNascimento"]', str(data_nascimento))

                # Localizar o checkbox do captcha
                hcaptcha_frame = page.frame_locator("iframe[title='Widget contendo caixa de seleção para desafio de segurança hCaptcha']")
                checkbox = hcaptcha_frame.locator('div[role="checkbox"]')
                checkbox.click()
                print("Clicando no captcha....")
                
                # page.wait_for_timeout(600)
                page.wait_for_function("""
                    () => document.querySelector("[name='h-captcha-response']").value !== ''
                """, timeout=10000)           

                # Submeter o formulário e esperar a navegação
                page.click('input[name="Enviar"]')
                page.wait_for_selector('div[class="clConteudoEsquerda"]', timeout=10000)
                print("Conteudo encontrado")

                # Capturar o conteúdo da página de resposta e usar BeautifulSoup para processar
                response_html = page.content()
                soup = BeautifulSoup(response_html, 'html.parser')
                conteudos_esquerda = soup.find_all('div', class_='clConteudoEsquerda')

                file_name = f"{cpf}.txt"
                file_path = os.path.join(download_dir, file_name)

                with open(file_path, "w", encoding="utf-8") as file:
                    for div in conteudos_esquerda:
                        bold_tags = div.find_all('b')
                        for bold in bold_tags:
                            file.write(bold.get_text(strip=True) + '\n')

                print(f"Consulta para CPF {cpf} concluída. Conteúdo salvo em {file_path}")

                browser.close()
                
                return
        
        except Exception as e:
            print(f"Erro ao capturar fazer a consulta {e}. Tentando novamente...")
    
# Iterar sobre o DataFrame e realizar consultas para cada CPF
for index, row in df.iterrows():
    cpf = row['CPF']
    data_nascimento = row['DATA_FORMATADA']

    # Chamar a função para realizar a consulta
    realizar_consulta(cpf, data_nascimento)

print(f"Total de consultas realizadas: {len(df)}")
