import numpy as np
from Base.Classes import Simulation_Team
from Base.Simulate import simulate

# Allow user to input teams
road = input("Road team:")
home = input("Home team:")
# Get team objects and create players data
road_team = Simulation_Team(road)
home_team = Simulation_Team(home)
road_team.create_players_data()
home_team.create_players_data()
n = 100 # Number of times to simulate the game
_playoff_game = True if input("Playoff game (Y/N)?:") == "Y" else False # Asks user if desired game is a playoff game
simulate_from_start = input("Simulate from beginning (Y/N)?:") # Asks user if desired game should be simulated from the beginning
if simulate_from_start == "Y": # Want to simulate from the start
    for i in range(0, n): # Loop n times
        simulate(road_team, home_team, playoff_game=_playoff_game) # Simulate game with no initial variables
        # Update and reset stats
        road_team.update_all_games_or_season_stats(home_team, "games")
        home_team.update_all_games_or_season_stats(road_team, "games")
        road_team.reset_game_or_season_stats("game")
        home_team.reset_game_or_season_stats("game")
    # Output data
    print(road)
    print("PTS=", np.mean(road_team.all_games_stats["PTS"]))
    print(np.mean(road_team.all_games_stats["PYDs"]))
    print(np.mean(road_team.all_games_stats["PTDs"]))
    print("INTs=", np.mean(road_team.all_games_stats["INTs"]))
    print("FMBLs=", np.mean(road_team.all_games_stats["FMBLs"]))
    print(np.mean(road_team.all_games_stats["RYDs"]))
    print(np.mean(road_team.all_games_stats["RTDs"]))
    print("FPTS=", np.mean(road_team.all_games_stats["FPTS"]))
    print(home)
    print("PTS=", np.mean(home_team.all_games_stats["PTS"]))
    print(np.mean(home_team.all_games_stats["PYDs"]))
    print(np.mean(home_team.all_games_stats["PTDs"]))
    print("INTs=", np.mean(home_team.all_games_stats["INTs"]))
    print("FMBLs=", np.mean(home_team.all_games_stats["FMBLs"]))
    print(np.mean(home_team.all_games_stats["RYDs"]))
    print(np.mean(home_team.all_games_stats["RTDs"]))
    print("FPTS=", np.mean(home_team.all_games_stats["FPTS"]))
    print("***********")
else: # Want to simulate from a certain point in the game
    # Ask user for various initial variables
    _quarter = input("Quarter (1/2/3/4/OT):")
    _time_left_in_quarter = input("Time remaining in quarter (MM:SS):")   
    _down = int(input("Down:"))
    _distance = int(input("Distance:"))
    _yards_to_endzone = int(input("Yards to endzone:"))
    _initial_ko_team = input("Initial kickoff team:")
    if _initial_ko_team == road_team.name:
        _initial_ko_team = road_team
    elif _initial_ko_team == home_team.name:
        _initial_ko_team = home_team
    else:
        _initial_ko_team = None  
    _team_in_poss = input("Team in possession:")
    _opposition = None
    if _team_in_poss == road_team.name:
        _team_in_poss = road_team
        _opposition = home_team
    elif _team_in_poss == home_team.name:
        _team_in_poss = home_team
        _opposition = road_team
    else:
        _team_in_poss = None    
    _road_timeouts = int(input(road_team.name + " timeouts:"))
    _home_timeouts = int(input(home_team.name + " timeouts:"))
    _road_points = int(input(road_team.name + " points:"))
    _home_points = int(input(home_team.name + " points:"))
    _clock_running = True if input("Clock running (Y/N)?:") == "Y" else False
    _td_play = True if input("Points after try (Y/N)?:") == "Y" else False
    _kickoff = True if input("Kickoff (Y/N)?:") == "Y" else False
    _safety_kick = True if input("Safety kick (Y/N)?:") == "Y" else False
    _hurry_up = True if input("Hurry up (Y/N)?:") == "Y" else False
    _overtime = False
    _sudden_death = False

    # Calculate time left in seconds
    _t = 3600
    if _quarter != "OT": # In regulation
        _t = 3600 - 900 * int(_quarter) + 60 * int(_time_left_in_quarter[0:2]) + int(_time_left_in_quarter[3:])
    else: # In overtime
        _overtime = True
        _t = 60 * int(_time_left_in_quarter[0:2]) + int(_time_left_in_quarter[3:])
        _sudden_death = True if input("Sudden death (Y/N)?:") == "Y" else False
    # Create initial variables dictionary
    _initial_variables = {"t": _t, "down": _down, "distance": _distance, "yards_to_endzone": _yards_to_endzone, "ko_team": _initial_ko_team, "team_in_poss": _team_in_poss, "opposition": _opposition, "road_team_timeouts": _road_timeouts, "home_team_timeouts": _home_timeouts, "road_team_points": _road_points, "home_team_points": _home_points, "clock_running": _clock_running, "td_play": _td_play, "kickoff": _kickoff, "safety_kick": _safety_kick, "hurry_up": _hurry_up, "overtime": _overtime, "sudden_death": _sudden_death}
    # Simulate game n times from desired starting point
    for i in range(0, n):
        simulate(road_team, home_team, initial_variables=_initial_variables, playoff_game=_playoff_game)
# Output number of wins for each team
print(road_team.name + " WINS: " + str(road_team.record[0]))
print(home_team.name + " WINS: " + str(home_team.record[0]))
print(str(home_team.record[2]) + " TIES")