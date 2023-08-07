import argparse
import os
import sys
import json
from scrape import fetch_profile_path, login, scrape, crawl

# Create argument parser
parser = argparse.ArgumentParser(description='Facebook Group Scraper and Visualiser.')

parser.add_argument("group_id", help="The Facebook Group Id.")
parser.add_argument("-m", "--members", help="The file location of an array of facebook group members.")
parser.add_argument("-f", "--friends", help="The file location of a dictionary mapping facebook members to friends.")
parser.add_argument("-s", help="The position of the group member to start with (exclusive).")
parser.add_argument("-e", help="The position of the group member to end with (inclusive).")

args = parser.parse_args()
    
# Functions:

def main(group_id, members=None, friends=None, start_pos=0, end_pos=None):
    """
    Main program process.
    
    :param group_id: The Facebook id of the group to scrape
    """
    # Login
    login()

    # Scrape Facebook group members
    if members is None:
        members = scrape(group_id=group_id)

    # Scrape Facebook friends of each group member that are also in the group
    friends_all = crawl(members=members, friends_all=friends, start_pos=start_pos, end_pos=end_pos)
    
    return 0

if __name__ == '__main__':
    # Check for the file path to group members
    members_file_path = args.members
    try:
        # Opening the file
        with open(members_file_path, 'r') as file:
            members = json.load(file) # Load as json
    except OSError as e:
        members = None

    # Check for the file path to friends dictionary
    friends_file_path = args.friends
    try:
        # Opening the file
        with open(friends_file_path, 'r') as file:
            friends = json.load(file) # Load as json
    except OSError as e:
        friends = None

    # Check range for members
    start_param = args.s and int(args.s) or 0
    end_param = args.e and int(args.e) or None

    # Run the program
    main(group_id=args.group_id, members=members, friends=friends, start_pos=start_param, end_pos=end_param)