This python script continuously scans the local network and stores connected 
machines in a sqlite database.

# Installation
Requirements: python, pip.

Run `pip install python-nmap`.

# Running
Make sure you run the script as root, otherwise you won't be able to use IMCP
(whatever that is) and you won't get the really juicy info such as MACs.