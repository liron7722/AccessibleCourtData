import sys
from ILCourtScraper.Parser.parser import main as parser_main
from ILCourtScraper.Scrapers.SupremeCourt_Scraper import main as scraper_main

if __name__ == '__main__':
    functions = {1: scraper_main,
                 2: parser_main
                 }
    if len(sys.argv) > 1:
        choice = int(sys.argv[1])

    else:
        choice = int(input("Enter which function you want to run:\n"
                           "1: Supreme Court Scraper\n"
                           "2: Parser\n"))
    func = functions[choice]
    func()
