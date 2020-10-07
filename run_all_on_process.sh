#!/bin/bash


ps -ef | grep main.py | grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep opt/google/chrome/chrome | grep -v grep | awk '{print $2}' | xargs kill

nohup python ~/Documents/AccessibleCourtData/main.py 1 > ./logs/Scraper.out &
nohup python ~/Documents/AccessibleCourtData/main.py 2 > ./logs/parser.out &
nohup python ~/Documents/AccessibleCourtData/main.py 3 > ./logs/elastic.out &
