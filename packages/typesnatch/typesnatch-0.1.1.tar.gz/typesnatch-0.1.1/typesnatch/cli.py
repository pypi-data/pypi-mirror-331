import os
import requests
from font_chuffer.core import search_fonts, install_font
import click
import inquirer
from colorama import Fore

BASE_URL = "https://www.dafont.com"
FONTS_DIR = os.path.expanduser("~/Library/Fonts")

@click.group()
def cli() -> None:
    "A CLI tool for searching, downloading, and installing fonts from DaFont."
    pass

@cli.command(name='install')
@click.argument('query')
@click.option('--debug', is_flag=True, help='Print debug information.')
def install(query: str, debug: bool) -> None:
    "Install fonts from DaFont.com."
    results, url, html_content = search_fonts(query, debug)


    if not results:
        print("No results found.")
        return

    choices = [
        (f"{Fore.LIGHTCYAN_EX}{font.name} {Fore.RESET}- {Fore.LIGHTMAGENTA_EX}Author: {font.author}, {Fore.LIGHTYELLOW_EX}Status: {font.status}, {Fore.LIGHTGREEN_EX}Downloads: {font.downloads} {Fore.LIGHTRED_EX}{'(Installed)' if font.is_installed else ''}{Fore.RESET}", font)
        for font in results
    ]

    questions = [inquirer.List('font', message="Select a font to install", choices=[choice[0] for choice in choices])]

    answer = inquirer.prompt(questions)
    if answer is None:
        print(Fore.YELLOW + "\nExiting without installing a font.")
        return

    selected_font = next((font for _, font in choices if _ == answer.get('font')), None)
    if selected_font:
        if selected_font.is_installed:
            print(Fore.YELLOW + f"Font {selected_font.name} is already installed.")
            exit(0)

        print(Fore.CYAN + f"Installing font: {selected_font}...")
        install_font(selected_font, debug)
        print(Fore.GREEN + "Font installed successfully.")
    else:
        # shouldn't happen
        raise ValueError("No valid font selected.")

if __name__ == '__main__':
    cli()
