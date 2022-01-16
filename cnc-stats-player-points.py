from urllib.request import urlopen
import json
import time
import argparse
import logging
from datetime import datetime
from datetime import timedelta
import seaborn as sns # for data visualization
import pandas as pd # for data analysis
import matplotlib.pyplot as plt # for data visualization
import code

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

BASE_URL = "https://cnc-stats-api.azurewebsites.net/api"

parser = argparse.ArgumentParser()
parser.add_argument('id')
args = parser.parse_args()
PLAYER_ID = args.id

def get_player_stats():
    endpoint = f'{BASE_URL}/Player/{PLAYER_ID}'
    logging.debug(f"Getting stats from {endpoint}")
    player_stats = urlopen(endpoint)
    player_stats_json = json.loads(player_stats.read())
    player_rank = str(player_stats_json['position']['rank'])
    player_points = str(int(player_stats_json['position']['points']))
    player_ratio = f"{player_stats_json['position']['winPercentage']}"
    player_name = f"{player_stats_json['position']['name']}"
    player_details = {'player_rank':player_rank, 'player_points':player_points, 'player_ratio':player_ratio, 'player_name':player_name}
    logging.debug(f"{player_details}")
    return(player_details)

def get_match_history(limit=None):
    if limit != None:
        endpoint = f'{BASE_URL}/Player/{PLAYER_ID}/Matches?limit={limit}'
    else:
        endpoint = f'{BASE_URL}/Player/{PLAYER_ID}/Matches'
    logging.debug(f"Getting latest matches from {endpoint}")
    match_history = urlopen(endpoint)
    match_history_json = json.loads(match_history.read())
    logging.debug(f"Got {len(match_history_json)} matches")
    return match_history_json

def write_graph_to_file(match_history, player_name):
    match_labels = []
    points = []

    for x in match_history:
        match_labels.append(x)

    for x in range(0,len(match_history)-1):
        points.append(int(match_history[x]['playerPoints']))

    maxPoints = max(points)
    minPoints = min(points)

    points = points[::-1]
    plt.style.use("dark_background")
    for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
        plt.rcParams[param] = '0.9'  # very light grey
    for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
        plt.rcParams[param] = '#212946'  # bluish dark grey
    colors = [
    '#08F7FE',  # teal/cyan
    '#FE53BB',  # pink
    '#F5D300',  # yellow
    '#00ff41',  # matrix green
    ]

    temp_df = pd.DataFrame({"points":points})
    fig, ax = plt.subplots()
    temp_df.plot(color=colors, ax=ax, legend=False)
    # Redraw the data with low alpha and slighty increased linewidth:
    n_shades = 10
    diff_linewidth = 1.05
    alpha_value = 0.3 / n_shades

    for n in range(1, n_shades+1):

        temp_df.plot(marker='o',
                linewidth=2+(diff_linewidth*n),
                alpha=alpha_value,
                legend=False,
                ax=ax,
                color=colors)

    # Color the areas below the lines:
    for column, color in zip(temp_df, colors):
        ax.fill_between(x=temp_df.index,
                        y1=temp_df[column].values,
                        y2=[0] * len(temp_df),
                        color=color,
                        alpha=0.1)

    ax.grid(color='#2A3459')

    ax.set_xlim([ax.get_xlim()[0] - 0.2, ax.get_xlim()[1] + 0.2])  # to not have the markers cut off
    ax.set_ylim(minPoints - 50, maxPoints + 50)
    ax.set_xlabel("Game #")
    ax.set_title("%s - Season 7" % (player_name))
    #sns.set_context("poster")
    sns.lineplot(y = "points", data=temp_df, legend=False)
    fig = plt.gcf()
    fig.set_size_inches(10,5)
    plt.savefig('%s season points.png' % (player_name))
    plt.clf()
    plt.cla()
    plt.close()

def main():
    player_stats = get_player_stats()
    match_history = get_match_history(limit=None)
    write_graph_to_file(match_history, player_stats['player_name'])

if __name__ == "__main__":
    main()
