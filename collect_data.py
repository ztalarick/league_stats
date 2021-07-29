# Author: Zachary Talarick
# Date: 07/21/20
# I want to find the relationship between champion mastery and winrate
# Do this for each individual champion

# Method:
# Data collection
# randomly choose 10 (out of 28) Tier/Division combos
# get 50 pages of data
# look up all their winrates
# look up all their champion masteries

# Analysis
# choose every summoner with more than 10 ranked games played on a champion
# find the correlation between winrate and champion mastery



# Bonus
# store it in a google doc or something and put it on reddit

import requests
import json
import random
import csv
import time

#get your own key
KEY = "KEY HERE"

#get a dictionary of champ_ids to champ names
version = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()[0]
datadragon = requests.get('http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json'.format(version)).json()
champions = {}
for champion in datadragon["data"]:
    key = int(datadragon["data"][champion]["key"])
    champions[key] = champion

#randomly select the tier, rank, and page for data collection
QUEUE = "RANKED_SOLO_5x5"

tiers = ['IRON/I', 'IRON/II', 'IRON/III', 'IRON/IV',
        'BRONZE/I', 'BRONZE/II', 'BRONZE/III', 'BRONZE/IV',
        'SILVER/I', 'SILVER/II', 'SILVER/III', 'SILVER/IV',
        'GOLD/I', 'GOLD/II', 'GOLD/III', 'GOLD/IV',
        'PLATINUM/I', 'PLATINUM/II', 'PLATINUM/III', 'PLATINUM/IV',
        'DIAMOND/I', 'DIAMOND/II', 'DIAMOND/III', 'DIAMOND/IV']

tier_ind = random.randint(0, 23)
page = random.randint(1, 100)

r = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/" + tiers[tier_ind] + "?page=" + str(page) + "&api_key=" + KEY)

r_json= r.json()
text = json.dumps(r.json(), sort_keys = True, indent = 4)

# build results in this list
result_list = []
data = {}

for summoner in r_json:
    # data["summonerName"] = summoner['summonerName']
    # data["tier"] = summoner["tier"]
    # data["rank"] = summoner["rank"]
    # data["total_wins"] = summoner["wins"]

    data["summonerName"] = "YouGotTroubles"
    data["tier"] = "Gold"
    data["rank"] = "III"
    # data["total_wins"] = summoner["wins"]

    print(data["summonerName"])
    #get account_id
    # summoner_id = summoner["summonerId"]
    # account_json = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/" + summoner_id + "?api_key=" + KEY).json()
    account_json = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/YouGotTroubles?api_key=" + KEY).json()
    account_id = account_json["accountId"]
    summoner_id = account_json["id"]
    #must pause because of the api rate limits
    #time.sleep(120)
    champ_ids = champions.keys()
    for champ_id in champ_ids:
        #get the mastery for the champion
        mastery_req = requests.get("https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + summoner_id + "/by-champion/" + str(champ_id) + "?api_key=" + KEY)
        if mastery_req.ok:
            #add the mastery score to result
            mastery_json = mastery_req.json()
            data[champions[champ_id] + "_mastery"] = mastery_json["championPoints"]
        else:
            #this guy never played the champ so make it a 0
            data[champions[champ_id] + "_mastery"] = 0
        #get the winrate for the champion
        matchlist_req = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id + "?champion=" + str(champ_id) + "&queue=420&api_key=" + KEY)
        if matchlist_req.ok:
            #now determine the wins/losses for each match in the match list
            wins = 0
            losses = 0
            matchlist_json = matchlist_req.json()
            print(champions[champ_id])
            # print(matchlist_json)
            matchlist = matchlist_json["matches"]
            for match in matchlist:
                gameId = str(match["gameId"])
                match_req = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + gameId + "?api_key=" + KEY)
                if not match_req.ok:
                    print(match_req.status_code)
                    break
                match_json = match_req.json()
                team1_win = match_json["teams"][0]["win"] == "Win"
                participantIdentities = match_json["participantIdentities"]
                for player in participantIdentities:
                    if player["player"]["summonerName"] == data["summonerName"]:
                        participantId = int(player["participantId"])
                        if participantId < 6 and team1_win == True:
                            wins += 1
                        elif participantId < 6 and team1_win == False:
                            losses += 1
                        elif participantId > 5 and team1_win == True:
                            losses += 1
                        elif participantId > 5 and team1_win == False:
                            wins += 1
                        break
            #calculate total games and winrate
            data[champions[champ_id] + "_total_games"] = wins + losses
            data[champions[champ_id] + "_winrate"] = wins / (wins + losses)

        else:
            #never played the champion
            data[champions[champ_id] + "_total_games"] = 0
            data[champions[champ_id] + "_winrate"] = 0
    result_list.append(json.dumps(data))
    break


print(result_list)
