import os
import pprint
import sys
import requests
from playwright.sync_api import sync_playwright
import shutil
import inquirer
from bs4 import BeautifulSoup
from typing import List, Tuple
from dataclasses import dataclass
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "https://www.dafont.com"
FONTS_DIR = os.path.expanduser("~/Library/Fonts")

@dataclass
class FontInfo:
    name: str
    author: str
    status: str
    downloads: str
    link: str
    download_url: str
    is_installed: bool = False

def search_fonts(query: str, debug: bool = False) -> Tuple[List[FontInfo], str, str]:
    print(f"Searching for '{query}' on DaFont.com...")
    url = f"{BASE_URL}/search.php?q={query}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Disable loading of images and stylesheets
        context.route("**/*", lambda route, request: route.abort() if request.resource_type in ["image", "stylesheet"] else route.continue_())

        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")  # Use 'domcontentloaded' to speed up navigation
        html_content = page.content()
        browser.close()
    soup = BeautifulSoup(html_content, 'html.parser')
    if debug:
        print(Fore.CYAN + "Debug: Pretty-printed HTML Content:")
        print(soup.prettify())
        print(Fore.CYAN + "Debug: HTML Fragments for Selectors:")

    results = []
    font_left_elements = soup.select("div.lv1left.dfbg")
    font_right_elements = soup.select("div.lv2right")

    for left_element, right_element in zip(font_left_elements, font_right_elements):
        name_tag = left_element.select_one("span.highlight")
        if debug:
            print(Fore.GREEN + "Font Name (Selector: span.highlight)")
            print(Fore.YELLOW + (name_tag.prettify() if name_tag else Fore.RED + "<None>"))

        by_tag = left_element.select_one("a")
        if debug:
            print(Fore.GREEN + "Author (Selector: a)")
            print(Fore.YELLOW + (by_tag.prettify() if by_tag else Fore.RED + "<None>"))

        downloads_tag = right_element.select_one("span.light")
        if debug:
            print(Fore.GREEN + "Downloads (Selector: span.light)")
            print(Fore.YELLOW + (downloads_tag.prettify() if downloads_tag else Fore.RED + "<None>"))

        free_paid_tag = right_element.select_one("a.tdn.help.black")
        if debug:
            print(Fore.GREEN + "Free/Paid Status (Selector: a.tdn.help.black)")
            print(Fore.YELLOW + (free_paid_tag.prettify() if free_paid_tag else Fore.RED + "<None>"))

        dl_container = right_element.find_next_sibling("div")
        dl_link_tag = dl_container.find("a", class_="dl") if dl_container else None
        download_url = f"https:{dl_link_tag['href']}" if dl_link_tag else None

        url_container = dl_container.find_next_sibling("div")
        url_tag = url_container.find("a") if url_container else None
        if debug:
            print(Fore.GREEN + "URL (Selector: a.dl)")
            print(Fore.YELLOW + (url_container.prettify() if url_container else Fore.RED + "<None>"))

        if name_tag and by_tag and downloads_tag and free_paid_tag and url_tag:
            name = name_tag.get_text(strip=True)
            for content in left_element.contents:
                if content.name is None:  # This checks if the content is a NavigableString
                    name += content.replace(' by ', '').strip()
            name = name
            by = by_tag.get_text(strip=True)
            downloads = downloads_tag.get_text(strip=True)
            free_paid = free_paid_tag.get_text(strip=True)
            link = url_tag['href']
            is_installed = any(
                font_file.lower().startswith(name.lower()) for font_file in os.listdir(FONTS_DIR)
            )
            results.append(FontInfo(name.lower(), by, free_paid, downloads, f"{BASE_URL}/{link}", download_url, is_installed))

    if not results:
        print("No results found.")
        return [], url, html_content

    return results, url, html_content

def install_font(font_info: FontInfo, debug: bool = False) -> None:
    if debug:
        print(Fore.CYAN + f"Debug: Starting installation for '{font_info.name}'")

    print(f"Downloading font from {font_info.download_url}...")
    if debug:
        print(Fore.CYAN + "Debug: Starting font download...")
    font_zip_response = requests.get(font_info.download_url, stream=True)

    if font_zip_response.status_code != 200:
        print("Error: Unable to download font.")
        sys.exit(1)

    zip_file_path = f"/tmp/{font_info.name}.zip"
    if debug:
        print(Fore.CYAN + "Debug: Starting font download...")
    font_zip_response = requests.get(font_info.download_url, stream=True)

    if font_zip_response.status_code != 200:
        print("Error: Unable to download font.")
        sys.exit(1)

    zip_file_path = f"/tmp/{font_info.name}.zip"
    if debug:
        print(Fore.CYAN + f"Debug: Writing ZIP to {zip_file_path}")
    with open(zip_file_path, 'wb') as zip_file:
        shutil.copyfileobj(font_zip_response.raw, zip_file)

    print(f"Downloaded font ZIP to {zip_file_path}. Extracting...")
    extracted_dir = f"/tmp/{font_info.name}"
    if debug:
        print(Fore.CYAN + f"Debug: Extracting ZIP to {extracted_dir}")
    shutil.unpack_archive(zip_file_path, extracted_dir)

    print(f"Installing font to {FONTS_DIR}...")
    if debug:
        print(Fore.CYAN + f"Debug: Copying font files to {FONTS_DIR}")
    for root, _, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(".ttf") or file.endswith(".otf"):
                shutil.copy(os.path.join(root, file), FONTS_DIR)

    print(f"Font '{font_info.name}' installed successfully.")
    if debug:
        print(Fore.CYAN + "Debug: Installation complete.")
