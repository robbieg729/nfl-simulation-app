from Base.Image_Making import create_power_rankings_image
# Team abbreviations to use in the image
team_mnemonics = {"Bills": "BUF", "Dolphins": "MIA", "Jets": "NYJ", "Patriots": "NE", "Bengals": "CIN", "Browns": "CLE", "Ravens": "BAL", "Steelers": "PIT", "Colts": "IND", "Jaguars": "JAX", "Texans": "HOU", "Titans": "TEN", "Broncos": "DEN", "Chargers": "LAC", "Chiefs": "KC", "Raiders": "LV", "Cowboys": "DAL", "Eagles": "PHI", "Football Team": "WAS", "Giants": "NYG", "Bears": "CHI", "Lions": "DET", "Packers": "GB", "Vikings": "MIN", "Buccaneers": "TB", "Falcons": "ATL", "Panthers": "CAR", "Saints": "NO", "49ers": "SF", "Cardinals": "ARI", "Rams": "LAR", "Seahawks": "SEA"}
# Base team colors
team_colors = {"Bills": (2, 45, 147), "Dolphins": (1, 142, 151), "Jets": (12, 87, 64), "Patriots": (206, 2, 29), "Bengals": (239, 72, 30), "Browns": (221, 96, 6), "Ravens": (42, 44, 129), "Steelers": (240, 200, 24), "Colts": (0, 50, 101), "Jaguars": (18, 101, 119), "Texans": (199, 35, 62), "Titans": (68, 148, 209), "Broncos": (242, 105, 34), "Chargers": (55, 120, 188), "Chiefs": (204, 3, 25), "Raiders": (209, 209, 211), "Cowboys": (212, 213, 215), "Eagles": (0, 71, 81), "Football Team": (88, 20, 19), "Giants": (0, 57, 124), "Bears": (27, 27, 63), "Lions": (1, 116, 181), "Packers": (31, 53, 48), "Vikings": (70, 23, 89), "Buccaneers": (234, 18, 5), "Falcons": (200, 33, 59), "Panthers": (12, 149, 211), "Saints": (209, 187, 140), "49ers": (196, 168, 114), "Cardinals": (176, 5, 57), "Rams": (0, 53, 148), "Seahawks": (99, 187, 38)}
teams = list()
week = 13 # Week of season
for i in range(0, 32): # Loop through each rank
    team = ""
    while team == "": # No team has been selected for the current rank
        mnemonic = input("Team " + str(i + 1) + ": ") # Allow user to input team for this rank, using abbreviations in team_mnemonics
        # Find team
        for key in team_mnemonics:
            if team_mnemonics[key] == mnemonic:
                team = key
        if team == "": # Input not valid
            print("Try again:")
    teams.append(team) # Add team to end of teams list (maintains correct order)
create_power_rankings_image(teams, team_colors, week) # Create image (automatically saved)
print("Done")