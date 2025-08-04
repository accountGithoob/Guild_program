import os
import csv
from scripts.variables import GUILD_MEMBERS
from scripts.variables import RAID_POINTS
import math

from typing import Literal

class Member:
    def __init__(self, name, discord_id, join_date):
        self.name = name
        self.discord_id = discord_id
        self.join_date = join_date
        self.total_points = 0
        self.raids_partecipated = 0
        self.items_deposited = {}
        self.challenges_contribution = {}
        self.points_redeemed = 0


class File:
    def __init__(self):
        ### PATHS ###
        __current_directory = os.path.dirname(os.path.abspath(__file__)) # Get the path of the current folder
        __parent_directory = os.path.dirname(__current_directory) # 'Steps back' to reach the main folder (of this project)
        __folder_path = os.path.join(__parent_directory, "files") # Get the path to the 'files' folder

        ### FILES ###
        self.CHALLENGE_FILE: str = os.path.join(__folder_path, "Challenge_contributions.csv")
        self.GUILD_DATA_FILE: str = os.path.join(__folder_path, "Guild_data.csv")
        self.RAID_FILE: str = os.path.join(__folder_path, "Raid_contributions.csv")
        self.ITEMS_FILE: str = os.path.join(__folder_path, "Items_points_value.csv")
        self.DEPOSITED_ITEMS_FILE = os.path.join(__folder_path, "Deposited_items.csv")
        
    def get_items_contribution(self, flag: Literal['challenges', 'deposit']) -> dict:
        guild_contributions = {}
        file = None

        if flag == 'challenges':
            file = self.CHALLENGE_FILE
        elif flag == 'deposit':
            file = self.DEPOSITED_ITEMS_FILE

        try:
            with open(file, newline='') as csvfile:
                reader = csv.reader(csvfile) # Get a reader object
                for row in reader: # read each row, which is a list
                    if not row[1].isdecimal() or row[0] not in GUILD_MEMBERS: # row[1] is a number, if it isn't skip it. row[0] is a name, skip it if isn't in GUILD_MEMBERS
                        continue

                    self._add_to_challenges_dictionary(guild_contributions, row[0], int(row[1]), row[2]) # func(dict, member_name, amount, item_name)
                return guild_contributions
        except (FileNotFoundError, TypeError, ValueError) as err:
            print(f'The following error: {err} was thrown from "get_challenges_contributions"')

    def _add_to_challenges_dictionary(self, dictionary: dict, member_name: str, items_donated: int, item_name: str) -> None:
        if member_name in dictionary: # 'Name' is already inside the dictionary?
            if item_name in dictionary[member_name]: # 'Name' has already contributed 'item'?
                dictionary[member_name][item_name] += items_donated
            else:
                dictionary[member_name][item_name] = items_donated
        else:
            dictionary[member_name] = {item_name: items_donated}

    def get_raid_contribution(self) -> dict:
        raid_data = {}

        try:
            with open(self.RAID_FILE, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader: # CONTEXT: raids' file has only a column, thus the row is the name of a member
                    name = ''.join(row)

                    if name not in GUILD_MEMBERS:
                        continue
                    
                    self._add_to_raid_dictionary(raid_data, name)
                return raid_data
        except (FileNotFoundError, TypeError, ValueError) as err:
            print(f'The following error: {err} was thrown from "refractor_raids_file"')

    def _add_to_raid_dictionary(self, dictionary: dict, name: str) -> None:
        if name in dictionary:
            dictionary[name] += 1  # Add to the existing sum
        else:
            dictionary[name] = 1  # Initialise the sum with the first contribution

    def get_points_table(self) -> dict:
        points_table = {}

        try:
            with open(self.ITEMS_FILE, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if not row[1].isdecimal():
                        continue

                    item_name = row[0]
                    item_value = int(row[1])

                    if item_name not in points_table:
                        points_table[item_name] = item_value
                return points_table
        except Exception as err:
            print(f'Something went wrong inside "", error message: {err}')

    def get_guild_data(self) -> dict:
        guild_table = {}

        try:
            with open(self.GUILD_DATA_FILE, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if not row[1].isdecimal():
                        continue

                    member_id = row[1]
                    member_name = row[2]
                    member_join_date = row[3]
                    redeemed_points = row[4]

                    if member_id not in guild_table:
                        guild_table[member_name] = {'member_id': member_id, 'join_date': member_join_date, 'redeemed_points': redeemed_points}
                return guild_table
        except Exception as err:
            print(f'Something went wrong inside "get_guild_data", error message: {err}')


class System:
    def __init__(self, file: File):
        self.file = file
        self.guild_data = self.file.get_guild_data()
        self.raid_data = self.file.get_raid_contribution()
        self.challenges_item_data = self.file.get_items_contribution('challenges')
        self.deposited_item_data = self.file.get_items_contribution('deposit')
        self.items_data = self.file.get_points_table()
    
    def _safe_call(self, method, member): # Reason: if any member doesn't have data, it throws an error. In this case it will set it to {}
        try:
            return method(member)
        except (KeyError, AttributeError):
            return {}

    def create_members(self):
        try:
            data = []
            for member in GUILD_MEMBERS:
                member_data = {}

                member_data['name'] = member
                member_data['join_date'] = self._safe_call(self._get_member_join_date, member)
                member_data['member_id'] = self._safe_call(self._get_member_member_id, member)
                member_data['raids'] = self._safe_call(self._get_raid_participation, member)
                member_data['challenges'] = self._safe_call(self._get_challenges_participation, member)
                member_data['deposited'] = self._safe_call(self._get_items_deposited, member)
                member_data['redeemed_points'] = self._get_redeemed_points(member)
                member_data['total_points'] = self._get_member_points(member, member_data['redeemed_points'], member_data['raids'], member_data['challenges'], member_data['deposited'])

                data.append(member_data)
            return data
        except Exception as err:
            print(f'Something went wrong inside "create_members", error message: {err}')

    def _get_member_join_date(self, name):
        return self.guild_data[name]['join_date']
    def _get_redeemed_points(self, name):
        return self.guild_data[name]['redeemed_points']
    def _get_member_member_id(self, name):
        return self.guild_data[name]['member_id']
    def _get_raid_participation(self, name):
        return self.raid_data[name]
    def _get_challenges_participation(self, name):
        return self.challenges_item_data[name]
    def _get_items_deposited(self, name):
        return self.deposited_item_data[name]
    def _get_member_points(self, member, redeemed_points, raids, challenge_items, deposited_items):
        try:
            raid_points = int(raids) * RAID_POINTS
            challenges_points = 0
            deposited_points = 0

            for item in challenge_items:
                #print(f'{member}: {total_points} += {int(self.items_data[item])} * {int(challenge_items[item])} ({item})')
                challenges_points += int(self.items_data[item]) * int(challenge_items[item])

            for item in deposited_items:
                #print(f'{member}: {total_points} += {int(self.items_data[item])} * {int(deposited_items[item])} ({item})')
                deposited_points += int(self.items_data[item]) * int(deposited_items[item])


            # Not the most efficient way, but who minds?
            total_points = raid_points + challenges_points + deposited_points
            usable_points = total_points - int(redeemed_points)
            ten_percent = math.ceil((usable_points/100)*8) # points/10 = 10% # PS: modified to 8%
            taxes = math.floor(ten_percent/20) # points//200 = 0.5% of 10% # PS: modified to 0.4% of 8%
            paycheck = ten_percent - taxes
            print(f'{member}: TP: {total_points}, Red pts: {redeemed_points}, Raid pts: {raid_points}, CP: {challenges_points}, DP: {deposited_points}, 8%: {ten_percent}, "taxes": {taxes} paycheck: {paycheck}')
            return total_points
        except (KeyError, AttributeError) as err:
            print(f'Problem with {member} inside "_get_member_points": {err} {self.items_data[item]}, {challenge_items[item]}')
            return 0
