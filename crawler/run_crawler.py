#!/usr/bin/env python

import argparse
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


def main():
    # -------------------------------------------
    # ARGUMENT PARSER
    # -------------------------------------------
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--sector",
        required=False,
        help="Sector name from config.yaml"
    )

    parser.add_argument(
        "--query",
        required=False,
        help="Keyword or event to dynamically crawl the internet for"
    )

    args = parser.parse_args()

    # -------------------------------------------
    # DYNAMIC SEARCH MODE
    # -------------------------------------------
    if args.query and not args.sector:
        sector_name = "Dynamic_Search"
        query_word = args.query

        print(f"[*] Dynamic Search Mode Activated")
        print(f"[*] Query: {query_word}")

    # -------------------------------------------
    # NORMAL SECTOR MODE
    # -------------------------------------------
    elif args.sector:
        sector_name = args.sector
        query_word = None

    else:
        print("[ERROR] You must specify --sector or --query")
        sys.exit(1)

    print(f"[*] Starting Smart Crawler for sector: {sector_name}")
    print(f"[*] Python: {sys.version.split()[0]}")

    config_path = find_config_path()

    print("[*] Using CrawlerProcess (no Playwright, no reactor install)")
    settings = get_project_settings()

    process = CrawlerProcess(settings)

    # Crawl with sector + optional query
    process.crawl(
        UniversalSpider,
        sector=sector_name,
        config_path=config_path,
        query=query_word
    )

    process.start(stop_after_crawl=True)


if __name__ == "__main__":
    main()
