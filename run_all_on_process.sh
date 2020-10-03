#!/bin/bash

# gnome-terminal --geometry 101x36+0+0 -- bash -c "python main.py 2; exec bash"
# gnome-terminal --geometry 101x36+0+721 -- bash -c "python main.py 3; exec bash"
# gnome-terminal --geometry 101x76+990+0 -- bash -c "python main.py 1; exec bash"

nohup python ~/Documents/AccessibleCourtData/main.py 1 &
nohup python ~/Documents/AccessibleCourtData/main.py 2 &
nohup python ~/Documents/AccessibleCourtData/main.py 3 &
