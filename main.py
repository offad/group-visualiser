import argparse
import os
import sys
import json
import math
import networkx as nx
import pandas as pd
from pyvis.network import Network
from scraper import Scraper

# Create argument parser
parser = argparse.ArgumentParser(description='Facebook Group Scraper and Visualiser.')

parser.add_argument("group_id", help="The Facebook Group Id.")
parser.add_argument("-m", "--members", help="The file location of an array of facebook group members.")
parser.add_argument("-f", "--friends", help="The file location of a dictionary mapping facebook members to friends.")
parser.add_argument("-s", help="The position of the group member to start with (exclusive).")
parser.add_argument("-e", help="The position of the group member to end with (inclusive).")

args = parser.parse_args()
    
# Functions:

def visualise():
    """
    Network program process.
    """

    # Open nodes
    with open("members", "r", encoding="utf-8") as file:
        nodes = json.load(file)

    # Open edges
    with open(friends_file_path, "r", encoding="utf-8") as file:
        links = json.load(file)

    # Create undirected graph with networkx
    graph = nx.Graph()

    # Add nodes
    graph.add_nodes_from([
        (
            member["id"],
            dict(name=member["name"])
        ) 
        for member in nodes
    ])

    # Add edges
    edges = []
    for id, friends in links.items():
        edges += [
            (
                id,
                friend["id"]
            ) for friend in friends
        ]
    graph.add_edges_from(edges)

    # Plot with pyvis
    net = Network(
        select_menu = True, # Show part 1 in the plot (optional)
        filter_menu = True, # Show part 2 in the plot (optional)
    )
    net.show_buttons() # Show part 3 in the plot (optional)
    net.from_nx(graph) # Create directly from nx graph
    net.show('network.html', notebook = False) # for some reason the Network .show() function has notebook=True

def main(group_id, members=None, friends=None, start_pos=0, end_pos=None):
    """
    Main program process.
    
    :param group_id: The Facebook id of the group to scrape
    :param members: An existing list of facebook group members
    :param friends: An existing dictionary of members mapped to their friends
    :param start_pos: The position of the group member to start with
    :param end_pos: The position of the group member to end with
    """
    # Login
    scraper = Scraper(group_id=group_id, members=members, friends_all=friends)
    scraper.login()

    # Scrape Facebook group members
    if members is None:
        members = scraper.scrape()

    # Scrape Facebook friends of each group member that are also in the group
    friends_all = scraper.crawl(start_pos=start_pos, end_pos=end_pos)
    
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

    # Visualise the group network
    visualise()