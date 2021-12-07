import numpy as np
import pandas as pd
import random as rd

class Team:
    """
    A class representing a football team, which stores data including overall team data, and data about its own players. Used for logging games.
    """
    def __init__(self, name, year=""):
        """
        :param name: franchise name of the team.
        :param year: the year for which the data should be collected from. If not specified, default to current and previous year.
        """
        self.name = name
        self.team_data_spreadsheet = pd.ExcelFile("Base/Teams/" + self.name + "/" + year + "Team Data.xlsx") # Loading main data sheet
        self.target_depth_spreadsheet = pd.ExcelFile("Base/Teams/" + self.name + "/" + year + "Target Depth Data.xlsx") # Loading target depth data sheet
        self.roster_spreadsheet = pd.ExcelFile("Base/Teams/" + self.name + "/Players Stats.xlsx") # Loading roster sheet
        self.players_data_spreadsheet = pd.ExcelFile("Base/Teams/" + self.name + "/Players Data.xlsx") # Loading players targets and rush attempts data sheet
        self.players_yards_spreadsheet = pd.ExcelFile("Base/Teams/" + self.name + "/Players Yards Data.xlsx") # Loading players rush and receiving yards gained sheet
        self.qbs_target_depth_spreadsheet = pd.ExcelFile("Base/Teams/" + self.name + "/QBs Target Depth Data.xlsx") # Loading target depth data sheet for individual QBs
        self.players_rush_yards_sheet = self.players_yards_spreadsheet.parse("Rushing") # Getting individual player rush yards gained lists
        self.players_rec_yards_sheet = self.players_yards_spreadsheet.parse("Receiving") # Getting individual player receiving yards gained lists       
        self.team_yards_sheet = self.team_data_spreadsheet.parse("YDS") # Getting team yards gained lists
        self.off_sheet = self.team_data_spreadsheet.parse("OFF") # Getting team offensive data
        self.two_min_off_sheet = self.team_data_spreadsheet.parse("2minOFF") # Getting team offensive data inside 2 minutes
        self.def_sheet = self.team_data_spreadsheet.parse("DEF") # Getting team defensive data
        self.two_min_def_sheet = self.team_data_spreadsheet.parse("2minDEF") # Getting team defensive data inside 2 minutes
        self.st_sheet = self.team_data_spreadsheet.parse("ST") # Getting team special teams data
        self.turns_sheet = self.team_data_spreadsheet.parse("TURNS") # Getting team turnover data
        self.pen_sheet = self.team_data_spreadsheet.parse("PEN") # Getting team penalties data
        self.off_target_depth_sheet = self.target_depth_spreadsheet.parse("OFF") # Getting offensive target depth data
        self.def_target_depth_sheet = self.target_depth_spreadsheet.parse("DEF") # Getting defensive target depth data
        self.rush_yards_list = np.array([int(d) for d in self.team_yards_sheet["OFF"][0].split(" ")]) if self.team_yards_sheet["OFF"][0] != "n" else [] # Team offensive rush yards gained list
        self.pass_yards_list = np.array([int(d) for d in self.team_yards_sheet["OFF"][1].split(" ")]) if self.team_yards_sheet["OFF"][1] != "n" else [] # Team offensive pass yards gained list
        self.rush_yards_against_list = np.array([int(d) for d in self.team_yards_sheet["DEF"][0].split(" ")]) if self.team_yards_sheet["DEF"][0] != "n" else [] # Team defensive rush yards allowed list
        self.pass_yards_against_list = np.array([int(d) for d in self.team_yards_sheet["DEF"][1].split(" ")]) if self.team_yards_sheet["DEF"][0] != "n" else [] # Team offensive pass yards allowed list  
        self.home_off_pass_attempts = self.off_sheet["PATT"][0]
        self.home_off_pass_completions = self.off_sheet["PCOMP"][0]
        self.home_sacks_allowed = self.off_sheet["SACKS"][0]
        self.road_off_pass_attempts = self.off_sheet["PATT"][1]
        self.road_off_pass_completions = self.off_sheet["PCOMP"][1]
        self.road_sacks_allowed = self.off_sheet["SACKS"][1]
        self.off_target_depth_data = self.off_target_depth_sheet.values[:, 1:]
        self.def_target_depth_data = self.def_target_depth_sheet.values[:, 1:]
        self.off_pass_attempts = self.home_off_pass_attempts + self.road_off_pass_attempts
        self.off_pass_completions = self.home_off_pass_completions + self.road_off_pass_completions
        self.sacks_allowed = self.home_sacks_allowed + self.road_sacks_allowed
        self.off_fd = np.transpose(self.off_sheet.values[:, 1:4]) 
        self.off_sd = np.transpose(self.off_sheet.values[:, 4:7])
        self.off_td = np.transpose(self.off_sheet.values[:, 7:10])
        self.two_min_off_fd = np.transpose(self.two_min_off_sheet.values[:, 1:4]) 
        self.two_min_off_sd = np.transpose(self.two_min_off_sheet.values[:, 4:7])
        self.two_min_off_td = np.transpose(self.two_min_off_sheet.values[:, 7:10])
        self.home_def_pass_attempts = self.def_sheet["PATT"][0]
        self.home_def_pass_completions = self.def_sheet["PCOMP"][0]
        self.home_sacks_got = self.def_sheet["SACKS"][0]
        self.road_def_pass_attempts = self.def_sheet["PATT"][1]
        self.road_def_pass_completions = self.def_sheet["PCOMP"][1]
        self.road_sacks_got = self.def_sheet["SACKS"][1]
        self.def_pass_attempts = self.home_def_pass_attempts + self.road_def_pass_attempts
        self.def_pass_completions = self.home_def_pass_completions + self.road_def_pass_completions
        self.sacks_got = self.home_sacks_got + self.road_sacks_got
        self.def_fd = np.transpose(self.def_sheet.values[:, 1:4]) 
        self.def_sd = np.transpose(self.def_sheet.values[:, 4:7])
        self.def_td = np.transpose(self.def_sheet.values[:, 7:10])
        self.two_min_def_fd = np.transpose(self.two_min_def_sheet.values[:, 1:4]) 
        self.two_min_def_sd = np.transpose(self.two_min_def_sheet.values[:, 4:7])
        self.two_min_def_td = np.transpose(self.two_min_def_sheet.values[:, 7:10])
        self.ko = self.st_sheet["KO"][0] # Kickoffs made
        self.kotb = self.st_sheet["KO"][1] # Touchbacks made
        self.kod = np.array([int(self.st_sheet["KO"][2])]) if (type(self.st_sheet["KO"][2]) == np.int64 or type(self.st_sheet["KO"][2]) == float or type(self.st_sheet["KO"][2]) == np.float64) else (np.array([int(d) for d in self.st_sheet["KO"][2].split(" ")]) if self.st_sheet["KO"][2] != "n" else [])
        self.kora = np.array([int(self.st_sheet["KO"][3])]) if (type(self.st_sheet["KO"][3]) == np.int64 or type(self.st_sheet["KO"][3]) == float or type(self.st_sheet["KO"][3]) == np.float64) else (np.array([int(d) for d in self.st_sheet["KO"][3].split(" ")]) if self.st_sheet["KO"][3] != "n" else [])
        self.korm = np.array([int(self.st_sheet["KO"][4])]) if (type(self.st_sheet["KO"][4]) == np.int64 or type(self.st_sheet["KO"][4]) == float or type(self.st_sheet["KO"][4]) == np.float64) else (np.array([int(d) for d in self.st_sheet["KO"][4].split(" ")]) if self.st_sheet["KO"][4] != "n" else [])
        self.pt = self.st_sheet["PT"][0] # Punts made
        self.ptd = np.array([int(self.st_sheet["PT"][1])]) if (type(self.st_sheet["PT"][1]) == np.int64 or type(self.st_sheet["PT"][1]) == float or type(self.st_sheet["PT"][1]) == np.float64) else (np.array([int(d) for d in self.st_sheet["PT"][1].split(" ")]) if self.st_sheet["PT"][1] != "n" else [])
        self.ptra = np.array([int(self.st_sheet["PT"][2])]) if (type(self.st_sheet["PT"][2]) == np.int64 or type(self.st_sheet["PT"][2]) == float or type(self.st_sheet["PT"][2]) == np.float64) else (np.array([int(d) for d in self.st_sheet["PT"][2].split(" ")]) if self.st_sheet["PT"][2] != "n" else [])
        self.ptrm = np.array([int(self.st_sheet["PT"][3])]) if (type(self.st_sheet["PT"][3]) == np.int64 or type(self.st_sheet["PT"][3]) == float or type(self.st_sheet["PT"][3]) == np.float64) else (np.array([int(d) for d in self.st_sheet["PT"][3].split(" ")]) if self.st_sheet["PT"][3] != "n" else [])
        self.fga_40 = self.st_sheet["FG40-A"][0] # Field goals <40 yards attempted
        self.fgm_40 = self.st_sheet["FG40-M"][0] # Field goals <40 yards made
        self.fga_50 = self.st_sheet["FG50-A"][0] # Field goals 40-49 yards attempted
        self.fgm_50 = self.st_sheet["FG50-M"][0] # Field goals 40-49 yards made
        self.fga_60 = self.st_sheet["FG60-A"][0] # Field goals 50-59 yards attempted
        self.fgm_60 = self.st_sheet["FG60-M"][0] # Field goals 50-59 yards made
        self.fga_70 = self.st_sheet["FG70-A"][0] # Field goals 60+ yards attempted
        self.fgm_70 = self.st_sheet["FG70-M"][0] # Field goals 60+ yards made
        self.xpa = self.st_sheet["XPA"][0] # Extra points attempted
        self.xpm = self.st_sheet["XPM"][0] # Extra points made
        self.two_pa = self.st_sheet["2PA"][0] # 2 point conversions attempted
        self.two_pm = self.st_sheet["2PM"][0] # 2 point conversions made      
        self.home_int_thrown = self.turns_sheet["INT"][0]
        self.home_int_got = self.turns_sheet["INTg"][0]
        self.road_int_thrown = self.turns_sheet["INT"][1]
        self.road_int_got = self.turns_sheet["INTg"][1]
        self.home_fmbl = self.turns_sheet["FMBL"][0]
        self.home_fmbl_got = self.turns_sheet["FMBLg"][0]
        self.road_fmbl = self.turns_sheet["FMBL"][0]
        self.road_fmbl_got = self.turns_sheet["FMBLg"][0]        
        self.ofod_a = self.off_sheet["4DA"][0] # Offensive 4th downs attempted
        self.ofod_m = self.off_sheet["4DM"][0] # Offensive 4th downs converted
        self.home_tot_off_plays = self.off_sheet["TOTPLAYS"][0] # Total home offensive plays
        self.road_tot_off_plays = self.off_sheet["TOTPLAYS"][1] # Total road offensive plays
        self.dfod_a = self.def_sheet["4DA"][0] # Defensive 4th downs faced
        self.dfod_m = self.def_sheet["4DM"][0] # Defensive 4th downs allowed
        self.home_tot_def_plays = self.def_sheet["TOTPLAYS"][0] # Total home defensive plays
        self.road_tot_def_plays = self.def_sheet["TOTPLAYS"][1] # Total road defensive plays        
        self.fst = self.pen_sheet["OFF"][0] # False starts
        self.off_hold = self.pen_sheet["OFF"][1] # Offensive holds
        self.opi = self.pen_sheet["OFF"][2] # Offensive pass interferences
        self.intg = self.pen_sheet["OFF"][3] # Intentional groundings
        self.offs = self.pen_sheet["DEF"][0] # Offsides / Encroachments / Neutral Zone Infractions
        self.def_hold = self.pen_sheet["DEF"][1] # Defensive holds
        self.dpi = self.pen_sheet["DEF"][2] # Defensive pass intereferences
        self.qbs_sheet = self.roster_spreadsheet.parse("QB") # Team quarterbacks sheet
        self.rbs_sheet = self.roster_spreadsheet.parse("RB") # Team running backs sheet
        self.wrs_sheet = self.roster_spreadsheet.parse("WR") # Team wide receivers sheet
        self.tes_sheet = self.roster_spreadsheet.parse("TE") # Team tight ends sheet
        self.ks_sheet = self.roster_spreadsheet.parse("K") # Team kickers sheet
        self.rushers_data_sheet = self.players_data_spreadsheet.parse("Rushing") # Players rushing data (attempts by player by down)
        self.receivers_data_sheet = self.players_data_spreadsheet.parse("Receiving") # Players receiving data (targets and completions by player by depth)
        self.players = {"QBs": [], "RBs": [], "WRs": [], "TEs": [], "Ks": []} # Team players dictionary
        self.receivers = list() # Players on team with at least 1 target
        self.rushers = list() # Players on team with at least 1 rush attempt
        self.skill_position_players = list() # All skill position players
        self.targets = np.array([np.sum(v) for v in np.transpose(self.receivers_data_sheet.values[:, 2::2])]) # Total targets by (Short, Deep, Redzone) 
        self.rush_atts = np.array([np.sum(v) for v in np.transpose(self.rushers_data_sheet.values[:, 2:])]) # Total rushes by (1st down, 2nd down, 3rd & 4th down, Redzone)
        self.receiver_probabilities = np.array([[], [], []])
        self.rushing_probabilities = np.array([[], [], [], []])
    def create_players_data(self):
        '''
        Method to initialize players data.
        '''
        for j in range(0, len(self.qbs_sheet["Name"])):
            target_depth_data = self.qbs_target_depth_spreadsheet.parse(self.qbs_sheet["Name"][j]).values[:, 1:] # Target depth data for current QB
            self.players["QBs"].append(Player(self.qbs_sheet["Name"][j], "QB", self.name, self.rushers_data_sheet, self.receivers_data_sheet, self.players_rush_yards_sheet[self.qbs_sheet["Name"][j]][0], self.players_rec_yards_sheet[self.qbs_sheet["Name"][j]][0], target_depth_data=target_depth_data)) # Initalize current QB, add to team QBs list
        for j in range(0, len(self.rbs_sheet["Name"])):
            player = Player(self.rbs_sheet["Name"][j], "RB", self.name, self.rushers_data_sheet, self.receivers_data_sheet, self.players_rush_yards_sheet[self.rbs_sheet["Name"][j]][0], self.players_rec_yards_sheet[self.rbs_sheet["Name"][j]][0]) # Initialize current RB
            self.players["RBs"].append(player) # Add current RB to RBs list
            self.skill_position_players.append(player) # Add current RB to skill position players list
        for j in range(0, len(self.wrs_sheet["Name"])):
            player = Player(self.wrs_sheet["Name"][j], "WR", self.name, self.rushers_data_sheet, self.receivers_data_sheet, self.players_rush_yards_sheet[self.wrs_sheet["Name"][j]][0], self.players_rec_yards_sheet[self.wrs_sheet["Name"][j]][0])
            self.players["WRs"].append(player)
            self.skill_position_players.append(player)
        for j in range(0, len(self.tes_sheet["Name"])):
            player = Player(self.tes_sheet["Name"][j], "TE", self.name, self.rushers_data_sheet, self.receivers_data_sheet, self.players_rush_yards_sheet[self.tes_sheet["Name"][j]][0], self.players_rec_yards_sheet[self.tes_sheet["Name"][j]][0])
            self.players["TEs"].append(player)
            self.skill_position_players.append(player)
        for j in range(0, len(self.ks_sheet["Name"])):
            self.players["Ks"].append(Player(self.ks_sheet["Name"][j], "K", self.name, self.rushers_data_sheet, self.receivers_data_sheet, ["n"], ["n"]))
        for position in self.players:
            for player in self.players[position]:
                if np.any(player.rushing_atts) != 0:
                    self.rushers.append(player) # Add current player to self.rushers if they have at least 1 rushing attempt
                if np.any(player.receiving_data) != 0:
                    self.receivers.append(player) # Add current player to self.receivers if they have at least 1 target
        for player in self.receivers:
            # Initialize target probabilities for current player in self.receivers
            self.receiver_probabilities = np.hstack((self.receiver_probabilities, np.reshape(player.receiving_data[0::2] / self.targets, (3, 1))))          
        for player in self.rushers:
            # Initialize rushing probabilities for current player in self.rushers
            self.rushing_probabilities = np.hstack((self.rushing_probabilities, np.reshape(player.rushing_atts / self.rush_atts, (4, 1))))            

class Player:
    '''
    A class representing a football player, used to store data and stats about him.
    '''
    def __init__(self, name, position, team, rushing_sheet, receiving_sheet, rush_yards_list, rec_yards_list, target_depth_data=None):
        '''
        param name: name of the player in format J.Doe.
        param position: position of the player, abbreviated.
        param team: the team that the player is on.
        param rushing_sheet: the sheet storing rushing data for the player's team.
        param receiving_sheet: the sheet storing receiving data for the player's team.
        param rush_yards_list: a string of space-separated values, with each value representing the yardage gain on a single rush attempt by the player.
        param rec_yards_list: a string of space-separated values, with each value representing the yardage gain on a single reception by the player.
        param target_depth_data: target depth data for the player. Only used if player's position is quarterback, otherwise defaults to None.
        '''
        self.name = name
        self.position = position
        self.team = team
        # List of yardage gains on rush attempts for player
        self.rush_yards_list = [rush_yards_list] if type(rush_yards_list) == np.int64 else (np.array([int(d) for d in rush_yards_list.split(" ")]) if rush_yards_list[0] != "n" else [])
        # List of yardage gains on receptions for player
        self.rec_yards_list = [rec_yards_list] if type(rec_yards_list) == np.int64 else (np.array([int(d) for d in rec_yards_list.split(" ")]) if rec_yards_list[0] != "n" else [])
        self.target_depth_data = target_depth_data
        self.rush_index = 0  # Index of player in team rushing data sheet
        self.rushing_atts = np.zeros(4) # Rushing attempts split by (1st down, 2nd down, 3rd & 4th down, Redzone) for player, to be initialized below
        try:
            self.rush_index = list(rushing_sheet["Name"]).index(self.name)
            self.rushing_atts = rushing_sheet.values[self.rush_index, 2:] 
        except:
            None
        self.receiving_index = 0 # Index of player in team receiving data sheet
        self.receiving_data = np.zeros(6) # Targets and completions split by (Short, Deep, Redzone) for player, to be initialized below
        try:
            self.receiving_index = list(receiving_sheet["Name"]).index(self.name) 
            #self.receiving_data = [receiving_sheet["Short Target"][self.receiving_index], receiving_sheet["Short Comp"][self.receiving_index], receiving_sheet["Deep Target"][self.receiving_index], receiving_sheet["Deep Comp"][self.receiving_index], receiving_sheet["RZ Target"][self.receiving_index], receiving_sheet["RZ Comp"][self.receiving_index]]
            self.receiving_data = receiving_sheet.values[self.receiving_index, 2:] 
        except:
            None
        self.game_stats = dict()
        self.all_games_stats = dict()
        self.season_stats = dict()
        self.all_seasons_stats = dict()
        # Initialize stats based on position of player
        if self.position == "QB":
            self.game_stats = {"PCOMPs": 0, "PATTs": 0, "PYDs": 0, "PTDs": 0, "INTs": 0, "FMBLs": 0, "RATTs": 0, "RYDs": 0, "RTDs": 0, "2PCs": 0, "FPTS": 0}
            self.all_games_stats = {"PCOMPs": [], "PATTs": [], "PYDs": [], "PTDs": [], "INTs": [], "FMBLs": [], "RATTs": [], "RYDs": [], "RTDs": [], "2PCs": [], "FPTS": []}
            self.season_stats = {"PCOMPs": 0, "PATTs": 0, "PYDs": 0, "PTDs": 0, "INTs": 0, "FMBLs": 0, "RATTs": 0, "RYDs": 0, "RTDs": 0, "2PCs": 0, "FPTS": 0}
            self.all_seasons_stats = {"PCOMPs": [], "PATTs": [], "PYDs": [], "PTDs": [], "INTs": [], "FMBLs": [], "RATTs": [], "RYDs": [], "RTDs": [], "2PCs": [], "FPTS": []}
        elif self.position == "WR" or self.position == "RB" or self.position == "TE":
            self.game_stats = {"Rec": 0, "RecYDs": 0, "RecTDs": 0, "FMBLs": 0, "RATTs": 0, "RYDs": 0, "RTDs": 0, "2PCs": 0, "FPTS": 0}
            self.all_games_stats = {"Rec": [], "RecYDs": [], "RecTDs": [], "FMBLs": [], "RATTs": [], "RYDs": [], "RTDs": [], "2PCs": [], "FPTS": []}
            self.season_stats = {"Rec": 0, "RecYDs": 0, "RecTDs": 0, "FMBLs": 0, "RATTs": 0, "RYDs": 0, "RTDs": 0, "2PCs": 0, "FPTS": 0}
            self.all_seasons_stats = {"Rec": [], "RecYDs": [], "RecTDs": [], "FMBLs": [], "RATTs": [], "RYDs": [], "RTDs": [], "2PCs": [], "FPTS": []}
        elif self.position == "K":
            self.game_stats = {"XPM": 0, "XPA": 0, "FG50-M": 0, "FG50-A": 0, "FG50+M": 0, "FG50+A": 0, "FPTS": 0}
            self.all_games_stats = {"XPM": [], "XPA": [], "FG50-M": [], "FG50-A": [], "FG50+M": [], "FG50+A": [], "FPTS": []}
            self.season_stats = {"XPM": 0, "XPA": 0, "FG50-M": 0, "FG50-A": 0, "FG50+M": 0, "FG50+A": 0, "FPTS": 0}
            self.all_seasons_stats = {"XPM": [], "XPA": [], "FG50-M": [], "FG50-A": [], "FG50+M": [], "FG50+A": [], "FPTS": []}
    def update_fantasy_points(self):
        '''
        Method to update fantasy points of a player from a single game, using standard NFL.com PPR scoring rules.
        '''
        for key in self.game_stats:
            if key == "PYDs":
                self.game_stats["FPTS"] += 0.04 * self.game_stats[key]
            elif key == "PTDs":
                self.game_stats["FPTS"] += 4 * self.game_stats[key]
            elif key == "INTs" or key == "FMBLs":
                self.game_stats["FPTS"] -= 2 * self.game_stats[key]
            elif key == "RYDs" or key == "RecYDs":
                self.game_stats["FPTS"] += 0.1 * self.game_stats[key]
            elif key == "RTDs" or key == "RecTDs":
                self.game_stats["FPTS"] += 6 * self.game_stats[key]
            elif key == "Rec":
                self.game_stats["FPTS"] += self.game_stats[key]
            elif key == "XPM":
                self.game_stats["FPTS"] += self.game_stats[key]
            elif key == "FG50-M":
                self.game_stats["FPTS"] += 3 * self.game_stats[key]
            elif key == "FG50+M":
                self.game_stats["FPTS"] += 5 * self.game_stats[key]
            elif key == "2PCs":
                self.game_stats["FPTS"] += 2 * self.game_stats[key]
    def update_all_games_or_season_stats(self, stat_type):
        '''
        Method to update all_games_stats or all_season_stats variable at the end of a simulated game.
        param stat_type: "games" or "season" depending on if all_games_stats or all_season_stats is being updated.
        '''
        for key in self.game_stats:
            if stat_type == "games":
                self.all_games_stats[key].append(self.game_stats[key])
            else:
                self.season_stats[key] += self.game_stats[key]
            self.game_stats[key] = 0
    def update_all_seasons_stats(self):
        '''
        Method to update all_seasons_stats variable at the end of a simulated season.
        '''
        for key in self.season_stats:
            self.all_seasons_stats[key].append(self.season_stats[key])
            self.season_stats[key] = 0

class Simulation_Team(Team):
    '''
    Sub-class of Team, representing a team for simulating a game or season.
    '''
    def __init__(self, name, year="", records=["0-0-0", "0-0-0", "0-0-0"]):
        super().__init__(name, year=year) # Keep same initializations from parent class
        self.dist_sheet = pd.ExcelFile("Base/Teams/" + self.name + "/Distributions.xlsx").parse("YDS") # Sheet storing the statistical distributions for offensive and defensive rush yards and pass yards
        # Offensive rush yards distribution, stored as [distribution_name, [parameters]]
        self.rush_yards_dist = [self.dist_sheet["R"][0][0:self.dist_sheet["R"][0].index("(")], [float(p) for p in self.dist_sheet["R"][0][self.dist_sheet["R"][0].index("(")+1:self.dist_sheet["R"][0].index(")")].split(", ")]]
        # Offensive pass yards distribution, stored as [distribution_name, [parameters]]
        self.pass_yards_dist = [self.dist_sheet["P"][0][0:self.dist_sheet["P"][0].index("(")], [float(p) for p in self.dist_sheet["P"][0][self.dist_sheet["P"][0].index("(")+1:self.dist_sheet["P"][0].index(")")].split(", ")]]
        # Defensive rush yards distribution, stored as [distribution_name, [parameters]]
        self.rush_yards_against_dist = [self.dist_sheet["RA"][0][0:self.dist_sheet["RA"][0].index("(")], [float(p) for p in self.dist_sheet["RA"][0][self.dist_sheet["RA"][0].index("(")+1:self.dist_sheet["RA"][0].index(")")].split(", ")]]
        # Defensive pass yards distribution, stored as [distribution_name, [parameters]]
        self.pass_yards_against_dist = [self.dist_sheet["PA"][0][0:self.dist_sheet["PA"][0].index("(")], [float(p) for p in self.dist_sheet["PA"][0][self.dist_sheet["PA"][0].index("(")+1:self.dist_sheet["PA"][0].index(")")].split(", ")]]
        # Combining home and road target depth data
        self.off_target_depth_data = np.array(self.off_target_depth_data[0] + self.off_target_depth_data[1])
        self.def_target_depth_data = np.array(self.def_target_depth_data[0] + self.def_target_depth_data[1])
        # Combining 2 minute downs data with outside of 2 minute downs data
        self.off_fd = self.off_fd + self.two_min_off_fd
        self.off_sd = self.off_sd + self.two_min_off_sd
        self.off_td = self.off_td + self.two_min_off_td
        self.def_fd = self.def_fd + self.two_min_def_fd
        self.def_sd = self.def_sd + self.two_min_def_sd
        self.def_td = self.def_td + self.two_min_def_td
        self.avg_rush_yards = np.mean(self.rush_yards_list) # Average rush yards
        self.avg_rush_yards_against = np.mean(self.rush_yards_against_list)  # Average rush yards allowed
        self.kotb_per = self.kotb / self.ko # Proportion of kickoffs resulting in touchbacks
        self.xpm_per = self.xpm / self.xpa if self.xpa >= 10 else 0.95 # Percentage of extra points made, set to league average if there are not enough attempts
        self.two_pm_per = self.two_pm / self.two_pa if self.two_pa >= 10 else 0.494 # Percentage of 2 pointers made, set to league average if there are not enough attempts
        self.fgm_40_per = self.fgm_40 / self.fga_40 if self.fga_40 >= 10 else 0.928 # Percentage of field goals <40 yards made, set to league average if there are not enough attempts
        self.fgm_50_per = self.fgm_50 / self.fga_50 if self.fga_50 >= 10 else 0.811 # Percentage of field goals 40-49 yards made, set to league average if there are not enough attempts
        self.fgm_60_per = self.fgm_60 / self.fga_60 if self.fga_60 >= 10 else 0.623 # Percentage of field goals 50-59 made, set to league average if there are not enough attempts
        self.fgm_70_per = self.fgm_70 / self.fga_70 if self.fga_70 >= 10 else 0.1 # Percentage of field goals 60+ yards made, set to league average if there are not enough attempts
        # Combining home and road turnover stats
        self.int_thrown  = self.home_int_thrown + self.road_int_thrown
        self.int_got = self.home_int_got + self.road_int_got
        self.fmbl = self.home_fmbl + self.road_fmbl
        self.fmbl_got = self.home_fmbl_got + self.road_fmbl_got
        # Combining home and road total plays stats
        self.tot_off_plays = self.home_tot_off_plays + self.road_tot_off_plays
        self.tot_def_plays = self.home_tot_def_plays + self.road_tot_def_plays       
        self.fst_per = self.fst / self.tot_off_plays # Proportion of offensive plays beginning with a false start
        self.off_hold_per = self.off_hold / self.tot_off_plays # Proportion of offensive plays containing an offensive hold
        self.opi_per = self.opi / self.tot_off_plays # Proportion of offensive plays containing offensive pass interference
        self.intg_per = self.intg / self.tot_off_plays # Proportion of offensive plays containing intentional grounding
        self.offs_per = self.offs / self.tot_def_plays # Proportion of defensive plays containing an offside/encroachment/neutral zone infraction
        self.def_hold_per = self.def_hold / self.tot_def_plays # Proportion of defensive plays containing a defensive hold
        self.dpi_per = self.dpi / self.tot_def_plays # Proportion of defensive plays containing a defensive pass interference        
        self.timeouts = 3
        self.points = 0 # Points in a single game
        # Team stats
        self.game_stats = {"PCOMPs": 0, "PATTs": 0, "PYDs": 0, "PTDs": 0, "INTs": 0, "RATTs": 0, "RYDs":0, "RTDs": 0, "FMBLs": 0, "FPTS": 0, "DefPTSA": 0}
        self.all_games_stats = {"PTS": [], "PTSA": [], "PCOMPs": [], "PATTs": [], "PYDs": [], "PTDs": [], "PTDsA": [], "INTs": [], "RATTs": [], "RYDs": [], "RTDs": [], "RTDsA": [], "FMBLs": [], "FPTS": []}
        self.season_stats = {"PTS": 0, "PTSA": 0, "PCOMPs": 0, "PATTs": 0, "PYDs": 0, "PTDs": 0, "PTDsA": 0, "INTs": 0, "RATTs": 0, "RYDs": 0, "RTDs": 0, "RTDsA": 0, "FMBLs": 0, "FPTS": 0}
        self.all_seasons_stats = {"WINS": [], "PTS": [], "PTSA": [], "PCOMPs": [], "PATTs": [], "PYDs": [], "PTDs": [], "PTDsA": [], "INTs": [], "RATTs": [], "RYDs": [], "RTDs": [], "RTDsA": [], "FMBLs": [], "FPTS": []}        
        self.conference = "" 
        self.division = ""         
        self.record = [int(n) for n in records[0].split("-")] # Overall record
        self.div_record = [int(n) for n in records[1].split("-")] # Divisional record
        self.conf_record = [int(n) for n in records[2].split("-")] # Conference record
        self.opponents = list() # Opponents in a season
        self.division_position = 0 
        self.seed = 0 # Playoff seed
        self.sov = 0 # Strength of victory
        self.sos = 0 # Strength of schedule
        self.super_bowl_wins = 0
        self.conference_round_apps = 0
        self.conference_champions = 0
        self.division_round_apps = 0
        self.playoff_apps = 0
        self.division_wins = 0
        self.expected_wins = 0
    def set_location_variables(self, location):
        '''
        Method to re-initialize certain variables for a home or a road game.
        param location: "Home" if the team is playing at home, "Road" if the team is playing on the road.
        '''
        if location == "Home":
            self.off_pass_attempts = self.home_off_pass_attempts
            self.off_pass_completions = self.home_off_pass_completions
            self.sacks_allowed = self.home_sacks_allowed
            self.def_pass_attempts = self.home_def_pass_attempts
            self.def_pass_completions = self.home_def_pass_completions
            self.sacks_got = self.home_sacks_got
            self.int_thrown = self.home_int_thrown
            self.int_got = self.home_int_got
            self.fmbl = self.home_fmbl
            self.fmbl_got = self.home_fmbl_got
            self.tot_off_plays = self.home_tot_off_plays
            self.tot_def_plays = self.home_tot_def_plays
            #self.off_target_depth_data = np.array([self.off_target_depth_sheet["Short Att"][0], self.off_target_depth_sheet["Short Comp"][0], self.off_target_depth_sheet["Deep Att"][0], self.off_target_depth_sheet["Deep Comp"][0], self.off_target_depth_sheet["Short Int"][0], self.off_target_depth_sheet["Deep Int"][0]])
            #self.def_target_depth_data = np.array([self.def_target_depth_sheet["Short Att"][0], self.def_target_depth_sheet["Short Comp"][0], self.def_target_depth_sheet["Deep Att"][0], self.def_target_depth_sheet["Deep Comp"][0], self.def_target_depth_sheet["Short Int"][0], self.def_target_depth_sheet["Deep Int"][0]])
            self.off_target_depth_data = self.off_target_depth_sheet.values[0, 1:]   
            self.def_target_depth_data = self.def_target_depth_sheet.values[0, 1:]     
        else:
            self.off_pass_attempts = self.road_off_pass_attempts
            self.off_pass_completions = self.road_off_pass_completions
            self.sacks_allowed = self.road_sacks_allowed
            self.def_pass_attempts = self.road_def_pass_attempts
            self.def_pass_completions = self.road_def_pass_completions
            self.sacks_got = self.road_sacks_got
            self.int_thrown = self.road_int_thrown
            self.int_got = self.road_int_got
            self.fmbl = self.road_fmbl
            self.fmbl_got = self.road_fmbl_got
            self.tot_off_plays = self.road_tot_off_plays
            self.tot_def_plays = self.road_tot_def_plays
            #self.off_target_depth_data = np.array([self.off_target_depth_sheet["Short Att"][1], self.off_target_depth_sheet["Short Comp"][1], self.off_target_depth_sheet["Deep Att"][1], self.off_target_depth_sheet["Deep Comp"][1], self.off_target_depth_sheet["Short Int"][1], self.off_target_depth_sheet["Deep Int"][1]])
            #self.def_target_depth_data = np.array([self.def_target_depth_sheet["Short Att"][1], self.def_target_depth_sheet["Short Comp"][1], self.def_target_depth_sheet["Deep Att"][1], self.def_target_depth_sheet["Deep Comp"][1], self.def_target_depth_sheet["Short Int"][1], self.def_target_depth_sheet["Deep Int"][1]])
            self.off_target_depth_data = self.off_target_depth_sheet.values[1, 1:]   
            self.def_target_depth_data = self.def_target_depth_sheet.values[1, 1:]  
    def update_all_games_or_season_stats(self, opposition, stat_type):
        '''
        Method to update all_games_stats or all_season_stats of team at the end of a simulated game, depending on value of stat_type parameter.
        param opposition: the opponent from the most recently played game.
        param stat_type: "games" to update all_games_stats, otherwise update all_season_stats.
        '''
        if self.points > opposition.points:
            self.record[0] += 1 # Add 1 to number of wins
        elif self.points < opposition.points:
            self.record[1] += 1 # Add 1 to number of losses
        else:
            self.record[2] += 1 # Add 1 to number of ties
        if stat_type == "games":            
            for key in self.game_stats:
                if key != "PTS" and key != "PTSA" and key != "PTDsA" and key != "RTDsA" and key != "DefPTSA":
                    self.all_games_stats[key].append(self.game_stats[key])
            self.all_games_stats["PTS"].append(self.points)
            self.all_games_stats["PTSA"].append(opposition.points)
            self.all_games_stats["PTDsA"].append(opposition.game_stats["PTDs"])
            self.all_games_stats["RTDsA"].append(opposition.game_stats["RTDs"])
            # Update players stats
            for position in self.players:
                for player in self.players[position]:
                    player.update_fantasy_points()
                    player.update_all_games_or_season_stats("games")
        else:
            for key in self.season_stats:
                if key != "PTS" and key != "PTSA" and key != "PTDsA" and key != "RTDsA":
                    self.season_stats[key] += self.game_stats[key]
            self.season_stats["PTS"] += self.points
            self.season_stats["PTSA"] += opposition.points
            self.season_stats["PTDsA"] += opposition.game_stats["PTDs"]
            self.season_stats["RTDsA"] += opposition.game_stats["RTDs"]
            # Update players stats
            for position in self.players:
                for player in self.players[position]:
                    player.update_fantasy_points()
                    player.update_all_games_or_season_stats("season")
    def update_all_seasons_stats(self):
        '''
        Method to update all_seasons_stats at the end of a simulated season.
        '''
        for key in self.all_seasons_stats:
            if key == "WINS":
                self.all_seasons_stats[key].append(self.record[0])
            else:
                self.all_seasons_stats[key].append(self.season_stats[key])        
        for key in self.season_stats:
            self.season_stats[key] = 0 # Reset all season stats
        # update players stats
        for position in self.players:
            for player in self.players[position]:
                player.update_fantasy_points()
                player.update_all_seasons_stats()
    def reset_game_or_season_stats(self, stat_type):
        '''
        Method to reset game_stats or season_stats, depending on value of stat_type parameter.
        param stat_type: "game" to reset game_stats, else reset season_stats.
        '''
        if stat_type == "game":            
            for key in self.game_stats:
                self.game_stats[key] = 0
        else:
            for key in self.season_stats:
                self.season_stats[key] = 0
    def update_defensive_fantasy_points(self):
        '''
        Method to update defensive fantasy points for a team based on defensive points allowed.
        '''
        if self.game_stats["DefPTSA"] == 0:
            self.game_stats["FPTS"] += 10
        elif self.game_stats["DefPTSA"] < 21:
            self.game_stats["FPTS"] += 13 - 3 * (int(2 + self.game_stats["DefPTSA"] / 7))
        else:
            self.game_stats["FPTS"] += -(((self.game_stats["DefPTSA"] - 21) / 7) ** 2)
    def select_receiver(self, depth_index, yards_to_endzone):
        '''
        Method to select a receiver to catch a pass during a play in a simulation, based on the probabilities specified in self.receiver_probabilities.
        param depth_index: integer specifying if Short or Deep probabilities should be considered.
        param yards_to_endzone: integer specifiying the yardage left until the opposition endzone. If <= 20, use Redzone probabilities.
        '''
        x = rd.random() # Random float in [0, 1]
        lower_bound = 0
        upper_bound = 0
        player_index = len(self.receiver_probabilities[depth_index]) - 1 #if yards_to_endzone > 20 else len(self.receiver_probabilities[2]) - 1
        L = self.receiver_probabilities[depth_index] #if yards_to_endzone > 20 else self.receiver_probabilities[2]
        # Method to use x to get the receiver
        for i in range(0, len(L)):
            upper_bound = lower_bound + L[i]
            if x >= lower_bound and x < upper_bound:
                player_index = i
                break
            lower_bound = upper_bound
        return self.receivers[player_index]
    def select_rusher(self, down, yards_to_endzone):
        '''
        Method to select a rusher to run the ball during a play in a simulation, based on the probabilities specified in self.rushing_probabilities.
        param down: the current down, set to 3 if down == 3 or down == 4.
        param yards_to_endzone: integer specifiying the yardage left until the opposition endzone. If <= 20, use Redzone probabilities.
        '''
        x = rd.random() # Random float in [0, 1]
        lower_bound = 0
        upper_bound = 0
        if down == 4:
            down = 3
        player_index = len(self.rushing_probabilities[down - 1]) - 1 #if yards_to_endzone > 20 else len(self.rushing_probabilities[3]) - 1
        L = self.rushing_probabilities[down - 1] #if yards_to_endzone > 20 else self.rushing_probabilities[3]
        # Method to use x to get the rusher
        for i in range(0, len(self.rushing_probabilities[down - 1])):
            upper_bound = lower_bound + self.rushing_probabilities[down - 1][i]
            if x >= lower_bound and x < upper_bound:
                player_index = i
                break
            lower_bound = upper_bound
        return self.rushers[player_index]