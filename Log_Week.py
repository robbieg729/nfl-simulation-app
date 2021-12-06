import os
from Base.Classes import Team
from Base.Gamelog import log_game, write_team_data_to_excel_files

# Team abbreviations used in gamebooks
team_mnemonics = {"Bills": "BUF", "Dolphins": "MIA", "Jets": "NYJ", "Patriots": "NE", "Bengals": "CIN", "Browns": "CLV", "Ravens": "BAL", "Steelers": "PIT", "Colts": "IND", "Jaguars": "JAX", "Texans": "HST", "Titans": "TEN", "Broncos": "DEN", "Chargers": "LAC", "Chiefs": "KC", "Raiders": "LV", "Cowboys": "DAL", "Eagles": "PHI", "Football Team": "WAS", "Giants": "NYG", "Bears": "CHI", "Lions": "DET", "Packers": "GB", "Vikings": "MIN", "Buccaneers": "TB", "Falcons": "ATL", "Panthers": "CAR", "Saints": "NO", "49ers": "SF", "Cardinals": "ARZ", "Rams": "LA", "Seahawks": "SEA"}
year = "2021" # The year of the week we want to log
week = 12 # The week of the season we want to log
directory = "Base/Gamebooks/" + year + "/Week " + str(week) # The directory where the gamebooks for the specified year and week are
for filename in os.listdir(directory): # Loop through gamebooks
    print(filename)
    road = filename[0:filename.index(" at")] # Road team name
    home = filename[filename.index(" at") + 4:filename.index(".txt")] # Home team name
    for i in range(0, 2): # Want to log data twice, for overall data and current year data    
        # Create Team objects for each team, with different year depending on iteration. Also create players data for each team
        road_team = Team(road) if i == 0 else Team(road, year=year + " ") 
        road_team.create_players_data()
        home_team = Team(home) if i == 0 else Team(home, year=year + " ")
        home_team.create_players_data()
        log_game(road_team, home_team, int(year), week, team_mnemonics) # Update team and players data    
        if i == 0: # Want to write to overall data sheet
            write_team_data_to_excel_files(road_team, year="", include_players_data=True)
            write_team_data_to_excel_files(home_team, year="", include_players_data=True)
        else: # Want to write to single year data sheet
            write_team_data_to_excel_files(road_team, year=year + " ", include_players_data=False) # Don't want to write players data twice (no separate year data for players)
            write_team_data_to_excel_files(home_team, year=year + " ", include_players_data=False)
print("Done")