import time

from playwright.sync_api import sync_playwright

from constant import email, link, password
from helpers import export_all_people
from stages.verification import get_security_code


def open_login():
    with sync_playwright() as p:
        # channel="chrome" usa o Google Chrome instalado no sistema
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(link)
        page.wait_for_load_state("domcontentloaded")

        page.fill("#email", email)
        page.fill("input[type='password']", password)
        page.get_by_role("button", name="Sign in", exact=True).click()

        # Seleciona a agência Magnetic Funnels
        page.locator(".agency", has_text="Magnetic Funnels").click()

        # Envia o código de segurança
        sent_at = int(time.time() * 1000)
        page.get_by_role("button", name="Send Security Code").click()

        # Lê o código no Gmail e digita na página
        code = get_security_code(since_ms=sent_at)
        print(f"Código recebido: {code}")
        otp_inputs = page.locator("input.otp-input")
        otp_inputs.first.wait_for(state="visible")
        for i, digit in enumerate(code):
            otp_inputs.nth(i).fill(digit)

        # Alterna para a subconta Habitar Imóveis
        page.get_by_text("Clique aqui para alternar").click()
        search = page.locator("input[name='search']")
        search.click()
        search.fill("Habitar Imóveis")
        page.locator(".hl_location-title", has_text="Habitar Imóveis").first.click()

        # Abre Contatos
        page.locator("#sb_contacts").click()
        page.wait_for_url("**/contacts/**")

        # Exporta os contatos de cada pessoa
        export_all_people(page, page.url)

        input("Pressione Enter para fechar o navegador...")
        page.wait_for_timeout(5000)
        browser.close()
