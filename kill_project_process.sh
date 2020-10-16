#!/bin/bash


ps -ef | grep main.py | grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep opt/google/chrome/chrome | grep -v grep | awk '{print $2}' | xargs kill