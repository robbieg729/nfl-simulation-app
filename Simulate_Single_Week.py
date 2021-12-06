from fitter import Fitter
import pandas as pd
import numpy as np
from Base.Classes import Simulation_Team
from Base.Simulate import simulate
from Base.Image_Making import create_win_probabilities_image, create_fantasy_rankings_image, create_primetime_opener_image, create_primetime_stat_projections_image
from Base.Other_Functions import bubble_sort_by_fpts, return_best_fit_in_str_format

# Base team colors, for image making
team_colors = {"Bills": (2, 45, 147), "Dolphins": (1, 142, 151), "Jets": (12, 87, 64), "Patriots": (206, 2, 29), "Bengals": (239, 72, 30), "Browns": (221, 96, 6), "Ravens": (42, 44, 129), "Steelers": (240, 200, 24), "Colts": (0, 50, 101), "Jaguars": (18, 101, 119), "Texans": (199, 35, 62), "Titans": (68, 148, 209), "Broncos": (242, 105, 34), "Chargers": (55, 120, 188), "Chiefs": (204, 3, 25), "Raiders": (209, 209, 211), "Cowboys": (212, 213, 215), "Eagles": (0, 71, 81), "Football Team": (88, 20, 19), "Giants": (0, 57, 124), "Bears": (27, 27, 63), "Lions": (1, 116, 181), "Packers": (31, 53, 48), "Vikings": (70, 23, 89), "Buccaneers": (234, 18, 5), "Falcons": (200, 33, 59), "Panthers": (12, 149, 211), "Saints": (209, 187, 140), "49ers": (196, 168, 114), "Cardinals": (176, 5, 57), "Rams": (0, 53, 148), "Seahawks": (99, 187, 38)}
# Team abbrevations, for image making
team_mnemonics = {"Bills": "BUF", "Dolphins": "MIA", "Jets": "NYJ", "Patriots": "NE", "Bengals": "CIN", "Browns": "CLE", "Ravens": "BAL", "Steelers": "PIT", "Colts": "IND", "Jaguars": "JAX", "Texans": "HOU", "Titans": "TEN", "Broncos": "DEN", "Chargers": "LAC", "Chiefs": "KC", "Raiders": "LV", "Cowboys": "DAL", "Eagles": "PHI", "Football Team": "WAS", "Giants": "NYG", "Bears": "CHI", "Lions": "DET", "Packers": "GB", "Vikings": "MIN", "Buccaneers": "TB", "Falcons": "ATL", "Panthers": "CAR", "Saints": "NO", "49ers": "SF", "Cardinals": "ARI", "Rams": "LAR", "Seahawks": "SEA"}
# Weekly schedule. Games with a value of "Primetime" indicate they are primetime games, and should not be included when making Sunday win probability images
schedule = {"Cowboys at Saints": "Primetime", "Giants at Dolphins": "", "Colts at Texans": "", "Vikings at Lions": "", "Eagles at Jets": "","Cardinals at Bears": "", "Chargers at Bengals": "", "Buccaneers at Falcons": "", "Football Team at Raiders": "", "Jaguars at Rams": "", "49ers at Seahawks": "", "Ravens at Steelers": "", "Broncos at Chiefs": "Primetime", "Patriots at Bills": "Primetime"}
# Fanduel Sportsbook bets for each game (only primetime games considered). In form [road spread, total points over/under]
bets = [[-4.5, 47.5], [], [], [], [], [], [], [], [], [], [], [], [10, 47.5], [3, 43.5]]
week = 13 # Current week being simulated
n = 10000 # Number of times to simulate each game
matchups_data = list()
primetime_data = list()
all_qbs = list()
all_rbs = list()
all_wrs = list()
all_tes = list()
all_ks = list()
all_teams = list()
j = -1 # Acts as an indexer, don't use range() for loop as it looks more readable this way
for game in schedule:
    j += 1

    # Initalize road and home team objects for the current game
    road = game[0:game.index(" at")]
    home = game[game.index(" at") + 4:]
    print(road)
    print(home)
    road_team = Simulation_Team(road, year="2021 ")
    home_team = Simulation_Team(home, year="2021 ")
    road_team.create_players_data()
    home_team.create_players_data()

    # Add road and home team to teams playing this week    
    all_teams.append(road_team)
    all_teams.append(home_team)

    # Add road and home players to respective positional lists
    for position in road_team.players:
        for player in road_team.players[position]:
            if position == "QBs":
                all_qbs.append(player)
            elif position == "RBs":
                all_rbs.append(player)
            elif position == "WRs":
                all_wrs.append(player)
            elif position == "TEs":
                all_tes.append(player)
            elif position == "Ks":
                all_ks.append(player)
    for position in home_team.players:
        for player in home_team.players[position]:
            if position == "QBs":
                all_qbs.append(player)
            elif position == "RBs":
                all_rbs.append(player)
            elif position == "WRs":
                all_wrs.append(player)
            elif position == "TEs":
                all_tes.append(player)
            elif position == "Ks":
                all_ks.append(player)
    point_differential = list() # List of point differential in every simulation for this game
    total_points = list() # List of total points in every simulation for this game
    for i in range(0, n): # Simulate game n times, update stats
        simulate(road_team, home_team)
        point_differential.append(road_team.points - home_team.points)
        total_points.append(road_team.points + home_team.points)
        road_team.update_all_games_or_season_stats(home_team, "games")
        home_team.update_all_games_or_season_stats(road_team, "games")
        road_team.reset_game_or_season_stats("game")
        home_team.reset_game_or_season_stats("game")
    if schedule[road_team.name + " at " + home_team.name] != "Primetime": # Game is not primetime
        # Add data for the matchup to matchups_data, which will later be passed to a function to create the Sunday win probabilities image
        matchups_data.append([road_team.name, round(100 * road_team.record[0] / n, 1), home_team.name, round(100 * home_team.record[0] / n, 1), round(100 - round(100 * home_team.record[0] / n, 1) - round(100 * road_team.record[0] / n, 1), 1)])
    else: # Game is primetime
        primetime_data.append([road_team, home_team, bets[j]]) # Add data for the matchup to primetime_data

    # Statistical distributions to consider when fitting data    
    _distributions = ["exponnorm", "f", "fatiguelife", "gamma", "johnsonsb", "johnsonsu", "mielke", "norminvgauss", "norm"]

    # Fit several stats to data
    f_point_differential = Fitter(point_differential, distributions=_distributions)
    f_point_differential.fit()
    f_total_points = Fitter(total_points, distributions=_distributions)
    f_total_points.fit()
    f_road_points = Fitter(road_team.all_games_stats["PTS"], distributions=_distributions)
    f_road_points.fit()
    f_road_pass_comps = Fitter(road_team.all_games_stats["PCOMPs"], distributions=_distributions)
    f_road_pass_comps.fit()
    f_road_pass_atts = Fitter(road_team.all_games_stats["PATTs"], distributions=_distributions)
    f_road_pass_atts.fit()
    f_road_pass_yards = Fitter(road_team.all_games_stats["PYDs"], distributions=_distributions)
    f_road_pass_yards.fit()
    f_road_pass_tds = Fitter(road_team.all_games_stats["PTDs"], distributions=_distributions)
    f_road_pass_tds.fit()
    f_road_ints = Fitter(road_team.all_games_stats["INTs"], distributions=_distributions)
    f_road_ints.fit()
    f_road_rush_yards = Fitter(road_team.all_games_stats["RYDs"], distributions=_distributions)
    f_road_rush_yards.fit()
    f_road_rush_tds = Fitter(road_team.all_games_stats["RTDs"], distributions=_distributions)
    f_road_rush_tds.fit()
    f_home_points = Fitter(home_team.all_games_stats["PTS"], distributions=_distributions)
    f_home_points.fit()
    f_home_pass_comps = Fitter(home_team.all_games_stats["PCOMPs"], distributions=_distributions)
    f_home_pass_comps.fit()
    f_home_pass_atts = Fitter(home_team.all_games_stats["PATTs"], distributions=_distributions)
    f_home_pass_atts.fit()
    f_home_pass_yards = Fitter(home_team.all_games_stats["PYDs"], distributions=_distributions)
    f_home_pass_yards.fit()
    f_home_pass_tds = Fitter(home_team.all_games_stats["PTDs"], distributions=_distributions)
    f_home_pass_tds.fit()
    f_home_ints = Fitter(home_team.all_games_stats["INTs"], distributions=_distributions)
    f_home_ints.fit()
    f_home_rush_yards = Fitter(home_team.all_games_stats["RYDs"], distributions=_distributions)
    f_home_rush_yards.fit()
    f_home_rush_tds = Fitter(home_team.all_games_stats["RTDs"], distributions=_distributions)
    f_home_rush_tds.fit()

    # Create data frames to write to excel for the game, and write them to an Excel Spreadsheet
    overall_stats_df = pd.DataFrame([[round(100 * road_team.record[0] / n, 1), round(100 * home_team.record[0] / n, 1), round(100 * road_team.record[2] / n, 1), round(np.mean(point_differential), 1), return_best_fit_in_str_format(f_point_differential.get_best(method="sumsquare_error")), " ".join([str(num) for num in point_differential]), round(np.mean(total_points), 1), return_best_fit_in_str_format(f_total_points.get_best(method="sumsquare_error")), " ".join([str(num) for num in total_points]), round(np.mean(road_team.all_games_stats["FPTS"]), 2), round(np.mean(home_team.all_games_stats["FPTS"]), 2)]], columns=[road_team.name + " WIN %", home_team.name + " WIN %", "TIE %", "Avg. Point Differential", "Point Differential Distribution", "Point Differential List", "Avg. Tot. PTS", "PTS Distribution", "PTS List", road_team.name + "Avg. FPTS", home_team.name + "Avg. FPTS"])
    road_stats_df = pd.DataFrame([[round(np.mean(road_team.all_games_stats["PTS"]), 1), round(np.mean(road_team.all_games_stats["PCOMPs"]), 1), round(np.mean(road_team.all_games_stats["PATTs"]), 1), round(np.mean(road_team.all_games_stats["PYDs"]), 2), round(np.mean(road_team.all_games_stats["PTDs"]), 2), round(np.mean(road_team.all_games_stats["INTs"]), 2), round(np.mean(road_team.all_games_stats["RYDs"]), 2), round(np.mean(road_team.all_games_stats["RTDs"]), 2)], [return_best_fit_in_str_format(f_road_points.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_road_pass_comps.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_road_pass_atts.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_road_pass_yards.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_road_pass_tds.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_road_ints.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_road_rush_yards.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_road_rush_tds.get_best(method="sumsquare_error"))], [" ".join([str(num) for num in road_team.all_games_stats["PTS"]]), " ".join([str(num) for num in road_team.all_games_stats["PCOMPs"]]), " ".join([str(num) for num in road_team.all_games_stats["PATTs"]]), " ".join([str(num) for num in road_team.all_games_stats["PYDs"]]), " ".join([str(num) for num in road_team.all_games_stats["PTDs"]]), " ".join([str(num) for num in road_team.all_games_stats["INTs"]]), " ".join([str(num) for num in road_team.all_games_stats["RYDs"]]), " ".join([str(num) for num in road_team.all_games_stats["RTDs"]])]], columns=["PTS", "PCOMPs", "PATTs", "PYDs", "PTDs", "INTs", "RYDs", "RTDs"], index=["Avg.", "Best Dist.", "List"])
    road_qbs_stats_df = pd.DataFrame([[player.name, round(np.mean(player.all_games_stats["PCOMPs"]), 1), round(np.mean(player.all_games_stats["PATTs"]), 1), round(np.mean(player.all_games_stats["PYDs"]), 2), round(np.mean(player.all_games_stats["PTDs"]), 2), round(np.mean(player.all_games_stats["INTs"]), 2), round(np.mean(player.all_games_stats["FMBLs"]), 2), round(np.mean(player.all_games_stats["RATTs"]), 1), round(np.mean(player.all_games_stats["RYDs"]), 2), round(np.mean(player.all_games_stats["RTDs"]), 2), round(np.mean(player.all_games_stats["2PCs"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2)] for player in bubble_sort_by_fpts(road_team.players["QBs"])], columns=["Name", "PCOMPs", "PATTs", "PYDs", "PTDs", "INTs", "FMBLs", "RATTs", "RYDs", "RTDs", "2PCs", "FPTS"])
    road_skill_players_stats_df = pd.DataFrame([[player.name, round(np.mean(player.all_games_stats["Rec"]), 2), round(np.mean(player.all_games_stats["RecYDs"]), 2), round(np.mean(player.all_games_stats["RecTDs"]), 2), round(np.mean(player.all_games_stats["FMBLs"]), 2), round(np.mean(player.all_games_stats["RATTs"]), 1), round(np.mean(player.all_games_stats["RYDs"]), 2), round(np.mean(player.all_games_stats["RTDs"]), 2), round(np.mean(player.all_games_stats["2PCs"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2), round(np.mean(player.all_games_stats["FPTS"]) - np.mean(player.all_games_stats["Rec"]), 2)] for player in bubble_sort_by_fpts(road_team.skill_position_players)], columns=["Name", "Rec", "RecYDs", "RecTDs", "FMBLs", "RATTs", "RYDs", "RTDs", "2PCs", "FPTS (PPR)", "FPTS (Non-PPR)"])
    road_k_stats_df = pd.DataFrame([[road_team.players["Ks"][0].name, round(np.mean(road_team.players["Ks"][0].all_games_stats["XPM"]), 2), round(np.mean(road_team.players["Ks"][0].all_games_stats["XPA"]), 2), round(np.mean(road_team.players["Ks"][0].all_games_stats["FG50-M"]), 2), round(np.mean(road_team.players["Ks"][0].all_games_stats["FG50-A"]), 2), round(np.mean(road_team.players["Ks"][0].all_games_stats["FG50+M"]), 2), round(np.mean(road_team.players["Ks"][0].all_games_stats["FG50+A"]), 2), round(np.mean(road_team.players["Ks"][0].all_games_stats["FPTS"]), 2)]], columns=["Name", "XPM", "XPA", "FG50-M", "FG50-A", "FG50+M", "FG50+A", "FPTS"])
    home_stats_df = pd.DataFrame([[round(np.mean(home_team.all_games_stats["PTS"]), 1), round(np.mean(home_team.all_games_stats["PCOMPs"]), 1), round(np.mean(home_team.all_games_stats["PATTs"]), 1), round(np.mean(home_team.all_games_stats["PYDs"]), 2), round(np.mean(home_team.all_games_stats["PTDs"]), 2), round(np.mean(home_team.all_games_stats["INTs"]), 2), round(np.mean(home_team.all_games_stats["RYDs"]), 2), round(np.mean(home_team.all_games_stats["RTDs"]), 2)], [return_best_fit_in_str_format(f_home_points.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_home_pass_comps.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_home_pass_atts.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_home_pass_yards.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_home_pass_tds.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_home_ints.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_home_rush_yards.get_best(method="sumsquare_error")), return_best_fit_in_str_format(f_home_rush_tds.get_best(method="sumsquare_error"))], [" ".join([str(num) for num in home_team.all_games_stats["PTS"]]), " ".join([str(num) for num in home_team.all_games_stats["PCOMPs"]]), " ".join([str(num) for num in home_team.all_games_stats["PATTs"]]), " ".join([str(num) for num in home_team.all_games_stats["PYDs"]]), " ".join([str(num) for num in home_team.all_games_stats["PTDs"]]), " ".join([str(num) for num in home_team.all_games_stats["INTs"]]), " ".join([str(num) for num in home_team.all_games_stats["RYDs"]]), " ".join([str(num) for num in home_team.all_games_stats["RTDs"]])]], columns=["PTS", "PCOMPs", "PATTs", "PYDs", "PTDs", "INTs", "RYDs", "RTDs"], index=["Avg.", "Best Dist.", "List"])
    home_qbs_stats_df = pd.DataFrame([[player.name, round(np.mean(player.all_games_stats["PCOMPs"]), 1), round(np.mean(player.all_games_stats["PATTs"]), 1), round(np.mean(player.all_games_stats["PYDs"]), 2), round(np.mean(player.all_games_stats["PTDs"]), 2), round(np.mean(player.all_games_stats["INTs"]), 2), round(np.mean(player.all_games_stats["FMBLs"]), 2), round(np.mean(player.all_games_stats["RATTs"]), 1), round(np.mean(player.all_games_stats["RYDs"]), 2), round(np.mean(player.all_games_stats["RTDs"]), 2), round(np.mean(player.all_games_stats["2PCs"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2)] for player in bubble_sort_by_fpts(home_team.players["QBs"])], columns=["Name", "PCOMPs", "PATTs", "PYDs", "PTDs", "INTs", "FMBLs", "RATTs", "RYDs", "RTDs", "2PCs", "FPTS"])
    home_skill_players_stats_df = pd.DataFrame([[player.name, round(np.mean(player.all_games_stats["Rec"]), 2), round(np.mean(player.all_games_stats["RecYDs"]), 2), round(np.mean(player.all_games_stats["RecTDs"]), 2), round(np.mean(player.all_games_stats["FMBLs"]), 2), round(np.mean(player.all_games_stats["RATTs"]), 1), round(np.mean(player.all_games_stats["RYDs"]), 2), round(np.mean(player.all_games_stats["RTDs"]), 2), round(np.mean(player.all_games_stats["2PCs"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2), round(np.mean(player.all_games_stats["FPTS"]) - np.mean(player.all_games_stats["Rec"]), 2)] for player in bubble_sort_by_fpts(home_team.skill_position_players)], columns=["Name", "Rec", "RecYDs", "RecTDs", "FMBLs", "RATTs", "RYDs", "RTDs", "2PCs", "FPTS (PPR)", "FPTS (Non-PPR)"])
    home_k_stats_df = pd.DataFrame([[home_team.players["Ks"][0].name, round(np.mean(home_team.players["Ks"][0].all_games_stats["XPM"]), 2), round(np.mean(home_team.players["Ks"][0].all_games_stats["XPA"]), 2), round(np.mean(home_team.players["Ks"][0].all_games_stats["FG50-M"]), 2), round(np.mean(home_team.players["Ks"][0].all_games_stats["FG50-A"]), 2), round(np.mean(home_team.players["Ks"][0].all_games_stats["FG50+M"]), 2), round(np.mean(home_team.players["Ks"][0].all_games_stats["FG50+A"]), 2), round(np.mean(home_team.players["Ks"][0].all_games_stats["FPTS"]), 2)]], columns=["Name", "XPM", "XPA", "FG50-M", "FG50-A", "FG50+M", "FG50+A", "FPTS"])
    with pd.ExcelWriter("Game Simulations/Week " + str(week) + "/" + road_team.name + " at " + home_team.name + ".xlsx") as writer:
        overall_stats_df.to_excel(writer, sheet_name="Overall game stats")
        road_stats_df.to_excel(writer, sheet_name=team_mnemonics[road_team.name] + " game stats")
        road_qbs_stats_df.to_excel(writer, sheet_name=team_mnemonics[road_team.name] + " pass stats")
        road_skill_players_stats_df.to_excel(writer, sheet_name=team_mnemonics[road_team.name] + " rec and rush stats")
        road_k_stats_df.to_excel(writer, sheet_name=team_mnemonics[road_team.name] + " kicking stats")
        home_stats_df.to_excel(writer, sheet_name=team_mnemonics[home_team.name] + " game stats")
        home_qbs_stats_df.to_excel(writer, sheet_name=team_mnemonics[home_team.name] + " pass stats")
        home_skill_players_stats_df.to_excel(writer, sheet_name=team_mnemonics[home_team.name] + " rec and rush stats")
        home_k_stats_df.to_excel(writer, sheet_name=home_team.name + " kicking stats")

# Create data frames for the full weekly fantasy projections, and write them to an Excel spreadsheet
all_qbs_stats_df = pd.DataFrame([[player.name + "(" + team_mnemonics[player.team] + ")", round(np.mean(player.all_games_stats["PCOMPs"]), 1), round(np.mean(player.all_games_stats["PATTs"]), 1), round(np.mean(player.all_games_stats["PYDs"]), 2), round(np.mean(player.all_games_stats["PTDs"]), 2), round(np.mean(player.all_games_stats["INTs"]), 2), round(np.mean(player.all_games_stats["FMBLs"]), 2), round(np.mean(player.all_games_stats["RATTs"]), 1), round(np.mean(player.all_games_stats["RYDs"]), 2), round(np.mean(player.all_games_stats["RTDs"]), 2), round(np.mean(player.all_games_stats["2PCs"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2)] for player in bubble_sort_by_fpts(all_qbs)], columns=["Name", "PCOMPs", "PATTs", "PYDs", "PTDs", "INTs", "FMBLs", "RATTs", "RYDs", "RTDs", "2PCs", "FPTS"]) 
all_rbs_stats_df = pd.DataFrame([[player.name + "(" + team_mnemonics[player.team] + ")", round(np.mean(player.all_games_stats["Rec"]), 2), round(np.mean(player.all_games_stats["RecYDs"]), 2), round(np.mean(player.all_games_stats["RecTDs"]), 2), round(np.mean(player.all_games_stats["FMBLs"]), 2), round(np.mean(player.all_games_stats["RATTs"]), 1), round(np.mean(player.all_games_stats["RYDs"]), 2), round(np.mean(player.all_games_stats["RTDs"]), 2), round(np.mean(player.all_games_stats["2PCs"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2), round(np.mean(player.all_games_stats["FPTS"]) - np.mean(player.all_games_stats["Rec"]), 2)] for player in bubble_sort_by_fpts(all_rbs)], columns=["Name", "Rec", "RecYDs", "RecTDs", "FMBLs", "RATTs", "RYDs", "RTDs", "2PCs", "FPTS (PPR)", "FPTS (Non-PPR)"])
all_wrs_stats_df = pd.DataFrame([[player.name + "(" + team_mnemonics[player.team] + ")", round(np.mean(player.all_games_stats["Rec"]), 2), round(np.mean(player.all_games_stats["RecYDs"]), 2), round(np.mean(player.all_games_stats["RecTDs"]), 2), round(np.mean(player.all_games_stats["FMBLs"]), 2), round(np.mean(player.all_games_stats["RATTs"]), 1), round(np.mean(player.all_games_stats["RYDs"]), 2), round(np.mean(player.all_games_stats["RTDs"]), 2), round(np.mean(player.all_games_stats["2PCs"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2), round(np.mean(player.all_games_stats["FPTS"]) - np.mean(player.all_games_stats["Rec"]), 2)] for player in bubble_sort_by_fpts(all_wrs)], columns=["Name", "Rec", "RecYDs", "RecTDs", "FMBLs", "RATTs", "RYDs", "RTDs", "2PCs", "FPTS (PPR)", "FPTS (Non-PPR)"])
all_tes_stats_df = pd.DataFrame([[player.name + "(" + team_mnemonics[player.team] + ")", round(np.mean(player.all_games_stats["Rec"]), 2), round(np.mean(player.all_games_stats["RecYDs"]), 2), round(np.mean(player.all_games_stats["RecTDs"]), 2), round(np.mean(player.all_games_stats["FMBLs"]), 2), round(np.mean(player.all_games_stats["RATTs"]), 1), round(np.mean(player.all_games_stats["RYDs"]), 2), round(np.mean(player.all_games_stats["RTDs"]), 2), round(np.mean(player.all_games_stats["2PCs"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2), round(np.mean(player.all_games_stats["FPTS"]) - np.mean(player.all_games_stats["Rec"]), 2)] for player in bubble_sort_by_fpts(all_tes)], columns=["Name", "Rec", "RecYDs", "RecTDs", "FMBLs", "RATTs", "RYDs", "RTDs", "2PCs", "FPTS (PPR)", "FPTS (Non-PPR)"])
all_ks_stats_df = pd.DataFrame([[player.name + "(" + team_mnemonics[player.team] + ")", round(np.mean(player.all_games_stats["XPM"]), 2), round(np.mean(player.all_games_stats["XPA"]), 2), round(np.mean(player.all_games_stats["FG50-M"]), 2), round(np.mean(player.all_games_stats["FG50-A"]), 2), round(np.mean(player.all_games_stats["FG50+M"]), 2), round(np.mean(player.all_games_stats["FG50+A"]), 2), round(np.mean(player.all_games_stats["FPTS"]), 2)] for player in bubble_sort_by_fpts(all_ks)], columns=["Name", "XPM", "XPA", "FG50-M", "FG50-A", "FG50+M", "FG50+A", "FPTS"])
all_defenses_stats_df = pd.DataFrame([[team.name, round(np.mean(team.all_games_stats["FPTS"]), 2)] for team in bubble_sort_by_fpts(all_teams)], columns=["Team", "FPTS"])
with pd.ExcelWriter("Game Simulations/Week " + str(week) + "/Fantasy Projections.xlsx") as writer:
    all_qbs_stats_df.to_excel(writer, sheet_name="QBs")
    all_rbs_stats_df.to_excel(writer, sheet_name="RBs")
    all_wrs_stats_df.to_excel(writer, sheet_name="WRs")
    all_tes_stats_df.to_excel(writer, sheet_name="TEs")
    all_ks_stats_df.to_excel(writer, sheet_name="Ks")
    all_defenses_stats_df.to_excel(writer, sheet_name="DEFs")
   
for p in primetime_data: # Loop through primetime games
    # Create primetime images for each game (automatically saved)
    create_primetime_opener_image(p[0], p[1], week, p[2], n)
    create_primetime_stat_projections_image(p[0], p[1], week)
create_win_probabilities_image(matchups_data[0:8], week, 1) # Create and save win probabilities image for the first 8 Sunday early matchups
create_win_probabilities_image(matchups_data[8:], week, 2) # Create and save win probabilities image for the remaining Sunday early matchups

# Create and save fantasy rankings image for each position, for different scoring formats
all_qbs = bubble_sort_by_fpts(all_qbs)
create_fantasy_rankings_image(all_qbs[0:2*(len(primetime_data) + len(matchups_data))], [qb.team for qb in all_qbs[0:2*(len(primetime_data) + len(matchups_data))]], team_colors, team_mnemonics, "QB", week, 1, schedule=schedule)
all_rbs = bubble_sort_by_fpts(all_rbs)
create_fantasy_rankings_image(all_rbs[0:32], [rb.team for rb in all_rbs[0:32]], team_colors, team_mnemonics, "RB", week, 1, scoring_format="PPR", schedule=schedule)
create_fantasy_rankings_image(all_rbs[32:64], [rb.team for rb in all_rbs[32:64]], team_colors, team_mnemonics, "RB", week, 2, scoring_format="PPR", schedule=schedule, starting_num=33)
all_rbs = bubble_sort_by_fpts(all_rbs, scoring_format="Non-PPR")
create_fantasy_rankings_image(all_rbs[0:32], [rb.team for rb in all_rbs[0:32]], team_colors, team_mnemonics, "RB", week, 1, scoring_format="Non-PPR", schedule=schedule)
create_fantasy_rankings_image(all_rbs[32:64], [rb.team for rb in all_rbs[32:64]], team_colors, team_mnemonics, "RB", week, 2, scoring_format="Non-PPR", schedule=schedule, starting_num=33)
all_wrs = bubble_sort_by_fpts(all_wrs)
create_fantasy_rankings_image(all_wrs[0:32], [wr.team for wr in all_wrs[0:32]], team_colors, team_mnemonics, "WR", week, 1, scoring_format="PPR", schedule=schedule)
create_fantasy_rankings_image(all_wrs[32:64], [wr.team for wr in all_wrs[32:64]], team_colors, team_mnemonics, "WR", week, 2, scoring_format="PPR", schedule=schedule, starting_num=33) 
all_wrs = bubble_sort_by_fpts(all_wrs, scoring_format="Non-PPR")
create_fantasy_rankings_image(all_wrs[0:32], [wr.team for wr in all_wrs[0:32]], team_colors, team_mnemonics, "WR", week, 1, scoring_format="Non-PPR", schedule=schedule)
create_fantasy_rankings_image(all_wrs[32:64], [wr.team for wr in all_wrs[32:64]], team_colors, team_mnemonics, "WR", week, 2, scoring_format="Non-PPR", schedule=schedule, starting_num=33)
all_tes = bubble_sort_by_fpts(all_tes)
create_fantasy_rankings_image(all_tes[0:32], [te.team for te in all_tes[0:32]], team_colors, team_mnemonics, "TE", week, 1, scoring_format="PPR", schedule=schedule)
all_tes = bubble_sort_by_fpts(all_tes, scoring_format="Non-PPR")
create_fantasy_rankings_image(all_tes[0:32], [te.team for te in all_tes[0:32]], team_colors, team_mnemonics, "TE", week, 1, scoring_format="Non-PPR", schedule=schedule)
all_ks = bubble_sort_by_fpts(all_ks)
create_fantasy_rankings_image(all_ks, [k.team for k in all_ks], team_colors, team_mnemonics, "K", week, 1, schedule=schedule)
all_teams = bubble_sort_by_fpts(all_teams)
create_fantasy_rankings_image(all_teams, [team.name for team in all_teams], team_colors, team_mnemonics, "DEF", week, 1, schedule=schedule)
print("Done")