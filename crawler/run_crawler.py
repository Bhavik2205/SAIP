#!/usr/bin/env python

import sys
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from smart_crawler.spiders.universal_spider import UniversalSpider


def find_config_path():
    possible_paths = [
        "./config.yaml",
        "../config.yaml",
        "/app/config.yaml",
    ]
    for path in possible_paths:
        if Path(path).exists():
            print(f"[+] Found config at: {path}")
            return path

    print("[!] No config found. Using './config.yaml'")
    return "./config.yaml"


def main(sector="Energy_Venezuela"):
    config_path = find_config_path()

    settings = get_project_settings()

    print("[*] Using CrawlerProcess (no Playwright, no reactor install)")
    process = CrawlerProcess(settings)

    process.crawl(UniversalSpider, sector=sector, config_path=config_path)

    process.start(stop_after_crawl=True)


if __name__ == "__main__":
    sector = sys.argv[1] if len(sys.argv) > 1 else "Energy_Venezuela"
    print(f"[*] Starting Smart Crawler for sector: {sector}")
    print(f"[*] Python: {sys.version.split()[0]}")
    main(sector)
