import sys
from scripts.Elastic_5_5_3 import main as elastic_main
from ILCourtScraper.Parser.parser import main as parser_main
from ILCourtScraper.Extra.sync import uploadSync, downloadSync
from ILCourtScraper.Scrapers.SupremeCourt_Scraper import main as scraper_main

if __name__ == '__main__':
    functions = {1: scraper_main,
                 2: parser_main,
                 3: elastic_main,
                 4: uploadSync,
                 5: downloadSync
                 }
    if len(sys.argv) > 1:
        choice = int(sys.argv[1])

    else:
        choice = int(input("Enter which function you want to run:\n"
                           "1: Supreme Court Scraper\n"
                           "2: Parser\n"
                           "3: Elastic\n"
                           "4: Upload Sync\n"
                           "5: Download Sync\n"
                           ))
    if len(functions) >= choice > 0:
        func = functions[choice]
        func()
