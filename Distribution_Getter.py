from fitter import Fitter
import pandas as pd
import os
from Base.Other_Functions import return_best_fit_in_str_format

# Get names of all teams
teams = set()
for filename in os.listdir("Base/Gamebooks/2020/Week 1"):
    team_one = filename[0:filename.index(" at")]
    team_two = filename[filename.index(" at") + 4:filename.index(".txt")]
    teams.add(team_one)
    teams.add(team_two)
for team in teams: # Loop through teams
    print(team)
    yards_data = pd.ExcelFile("Base/Teams/" + team + "/2021 Team Data.xlsx").parse("YDS") # Get team data
    rush_yards = [int(d) for d in yards_data["OFF"][0].split(" ")] # Get list of team offensive rush yards
    pass_yards = [int(d) for d in yards_data["OFF"][1].split(" ")] # Get list of team offensive pass yards
    rush_yards_against = [int(d) for d in yards_data["DEF"][0].split(" ")] # Get list of team defensive rush yards
    pass_yards_against = [int(d) for d in yards_data["DEF"][1].split(" ")] # Get list of team offensive rush yards
    
    # Get best statistical distribution, along with parameters, for each list. Check only the distributions specified
    f_rush_yards = Fitter(rush_yards, distributions=["f", "johnsonsu", "johnsonsb", "norm", "norminvgauss", "nct", "exponnorm", "mielke"])
    f_pass_yards = Fitter(pass_yards, distributions=["f", "johnsonsu", "johnsonsb", "norm", "norminvgauss", "nct", "exponnorm", "mielke"])
    f_rush_yards_against = Fitter(rush_yards_against, distributions=["f", "johnsonsu", "johnsonsb", "norm", "norminvgauss", "nct", "exponnorm", "mielke"])
    f_pass_yards_against = Fitter(pass_yards_against, distributions=["f", "johnsonsu", "johnsonsb", "norm", "norminvgauss", "nct", "exponnorm", "mielke"])
    
    # Get best fits in string format for each list
    f_rush_yards.fit()
    best_rush_yards = return_best_fit_in_str_format(f_rush_yards.get_best(method="sumsquare_error")) 

    f_pass_yards.fit()
    best_pass_yards = return_best_fit_in_str_format(f_pass_yards.get_best(method="sumsquare_error"))

    f_rush_yards_against.fit()
    best_rush_yards_against = return_best_fit_in_str_format(f_rush_yards_against.get_best(method="sumsquare_error"))

    f_pass_yards_against.fit()
    best_pass_yards_against = return_best_fit_in_str_format(f_pass_yards_against.get_best(method="sumsquare_error"))

    # Create data frame containing best fits in string format
    df = pd.DataFrame([[best_rush_yards, best_pass_yards, best_rush_yards_against, best_pass_yards_against]], columns=["R", "P", "RA", "PA"])

    # Write to excel
    df.to_excel("Base/Teams/" + team + "/Distributions.xlsx", sheet_name="YDS")
print("Done")