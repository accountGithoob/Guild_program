from scripts.classes import File
from scripts.classes import System
import csv

file = File()
sys = System(file)

data = sys.create_members()

with open('test.csv', 'w', newline='') as csvfile:
    fieldnames = ['name', 'join_date', 'member_id', 'total_points', 'redeemed_points', 'raids', 'challenges', 'deposited']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)