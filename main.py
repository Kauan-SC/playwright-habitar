from playwright.sync_api import sync_playwright
from constant import link


def main():
    with sync_playwright() as p:
        # channel="chrome" usa o Google Chrome instalado no sistema
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(link)
        page.wait_for_load_state("domcontentloaded")

        input("Pressione Enter para fechar o navegador...")
        browser.close()


if __name__ == "__main__":
    main()
