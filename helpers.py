from collections import deque
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

PEOPLE = [
    "Milena Castro",
    "Gisele Santos",
    "Luciele Ramos",
    "Gabriel da Silva",
    "Juliana Isadora",
    "Mayara Santos",
    "Sabrina Michele",
]

DOWNLOAD_DIR = Path("downloads")


def export_person(page: Page, contacts_url: str, name: str, download_dir: Path = DOWNLOAD_DIR):
    """Seleciona a pessoa, exporta os contatos e baixa o CSV. Levanta
    PlaywrightTimeoutError se a pessoa não for encontrada."""
    page.goto(contacts_url)

    # Seta que abre a lista de pessoas -> escolhe a atendente
    page.get_by_role("button", name="Mais").click(timeout=15000)
    page.get_by_text(name, exact=True).first.click(timeout=5000)

    # Checkbox do cabeçalho -> "Selecionar tudo" -> Exportar -> confirma no modal
    page.get_by_role("row", name="Select Row Nome do Contato").get_by_label("Select Row").check(timeout=15000)
    page.get_by_text("Selecionar tudo", exact=False).first.click(timeout=5000)
    page.get_by_role("button", name="Exportar").click(timeout=5000)
    page.get_by_role("dialog", name="UI Modal").get_by_role("button", name="Exportar").click(timeout=5000)

    # Tela de progresso dos exports
    page.get_by_role("button", name="Verifique o progresso.").click(timeout=15000)

    # Linha mais recente da pessoa, já concluída
    row = (
        page.locator("tr")
        .filter(has_text=f"Export_Contacts_{name}")
        .filter(has_text="Concluído")
        .first
    )
    row.wait_for(timeout=120000)

    # Ícone de download da linha
    download_dir.mkdir(exist_ok=True)
    # O clique abre um popup que dispara o download; fechamos o popup depois
    with page.expect_download() as download_info:
        with page.expect_popup() as popup_info:
            row.locator("i.hr-icon-inner").first.click()
        popup = popup_info.value
    download = download_info.value
    popup.close()
    path = download_dir / f"{name}.csv"
    download.save_as(path)
    print(f"Baixado: {path}")


def export_all_people(
    page: Page,
    contacts_url: str,
    people: list[str] = PEOPLE,
    max_attempts: int = 3,
    download_dir: Path = DOWNLOAD_DIR,
):
    """Passa por todas as pessoas. Se não conseguir uma, segue para a próxima
    e volta nela depois (até max_attempts tentativas)."""
    pending = deque(people)
    attempts = {name: 0 for name in people}
    failed = []

    while pending:
        name = pending.popleft()
        attempts[name] += 1
        try:
            export_person(page, contacts_url, name, download_dir)
        except PlaywrightTimeoutError:
            print(f"Não achei/falhou: {name} (tentativa {attempts[name]}/{max_attempts})")
            if attempts[name] < max_attempts:
                pending.append(name)  # volta nela depois das outras
            else:
                failed.append(name)

    if failed:
        print(f"Sem sucesso: {', '.join(failed)}")
    return failed
