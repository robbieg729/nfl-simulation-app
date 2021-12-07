import pandas as pd
import numpy as np
import copy

def log_game(road_team, home_team, year, week, team_mnemonics):
    '''
    Method to update team data from a single game.
    param road_team: the road_team.
    param home_team: the home_team.
    param year: the year the game took place.
    param week: the week of the season the game took place.
    param team_mnemonics: abbreviations used in the gamebooks for the teams.
    '''
    directory = "Base/Gamebooks/" + str(year) + "/Week " + str(week) 
    game = road_team.name + " at " + home_team.name + ".txt" # filename   
    def edit_lines_into_correct_format(lines, road, home):
        '''
        Method to edit the text lines from the gamebook into a readable format for the program.
        param lines: the initial lines from the gamebook.
        param road: name of the road team.
        param home: name of the home team.
        '''
        def list_with_removed_lines(L, removing_lines):
            '''
            Method to remove lines from a list of lines.
            param L: the full list of lines.
            param removing_lines: the lines to be removed.
            '''
            for line in removing_lines:
                try:
                    L.remove(line)
                except:
                    None

            return L
        lines_copy = copy.copy(lines)
        lines_to_remove = []
        i = -1
        for line in lines_copy:
            lines_to_remove = []
            i += 1
            # Remove lines if they don't carry any data required to update the teams data
            if line[0] == " ":
                lines = list_with_removed_lines(lines, [line])            
            elif home in line and road in line:
                lines = list_with_removed_lines(lines, [line])
            elif " kneels " in line:
                lines = list_with_removed_lines(lines, [line])
            elif " spiked " in line:
                lines = list_with_removed_lines(lines, [line])
            elif "MUFFS" in line:
                lines = list_with_removed_lines(lines, [line])
            elif " kicks onside " in line:
                lines = list_with_removed_lines(lines, [line])
            elif "Play By Play" in line:
                lines = list_with_removed_lines(lines, [line])
            elif "punt is BLOCKED" in line:
                lines = list_with_removed_lines(lines, [line])
            elif "END OF QUARTER" in line:
                lines = list_with_removed_lines(lines, [l for l in lines_copy[i:i + 10]])
            elif " elects " in line:
                lines = list_with_removed_lines(lines, [line])
            elif "INJURY UPDATE" in line:
                lines = list_with_removed_lines(lines, [line])
            elif "PENALTY" in line:
                if "enforced between downs" in line:
                    lines = list_with_removed_lines(lines, [line])
                else:                
                    if ("False Start" not in line and "Offside" not in line and "Neutral Zone Infraction" not in line and "Encroachment" not in line and "Offensive Holding" not in line and "Defensive Holding" not in line and "Offensive Pass Interference" not in line and "Defensive Pass Interference" not in line and "Intentional Grounding" not in line):
                        lines_to_remove = [line]
                        if "No Play" in line:
                            if line[1] != "-":                        
                                lines_to_remove.append(lines_copy[i - 1])
                        lines = list_with_removed_lines(lines, lines_to_remove)
                    else:
                        if "False Start" not in line and "Offside" not in line and "Neutral Zone Infraction" not in line and "Encroachment" not in line:
                            if "No Play" in line:
                                lines[lines.index(line)] = lines_copy[i - 1][0:11] + " " + line
                                lines = list_with_removed_lines(lines, [lines_copy[i - 1]])
                            else:
                                lines[lines.index(line)] = "1-10 " + line
                        else:
                            if "No Play" in line:
                                if line[1] != "-":
                                    lines[lines.index(line)] = lines_copy[i - 1][0:11] + " " + line
                                    lines = list_with_removed_lines(lines, [lines_copy[i - 1]])
            elif "Penalty" in line:
                lines = list_with_removed_lines(lines, [line])
            elif line[1] == "-" and (line[2] == "1" or line[2] == "2" or line[2] == "3" or line[2] == "4" or line[2] == "5" or line[2] == "6" or line[2] == "7" or line[2] == "8" or line[2] == "9"):
                if len(line) < 20:
                    lines_to_remove = [line]
                    if lines_copy[i - 1][0] != "(":                   
                        try:                        
                            lines[lines.index(lines_copy[i - 2])] = line[0:11] + lines_copy[i - 2]
                            lines_to_remove.append(lines_copy[i - 1])
                        except:
                            None
                    else:
                        try:                        
                            lines[lines.index(lines_copy[i - 1])] = line[0:11] + lines_copy[i - 1]
                        except:
                            None
                    lines = list_with_removed_lines(lines, lines_to_remove)
            elif "The Replay Official" in line or "challenged" in line:
                lines_to_remove = [line]
                if "REVERSED" in line:
                    lines_to_remove.append(lines_copy[i - 1])
                    if lines_copy[i - 1][1] != "-" and lines_copy[i - 2][0] != "(":
                        lines_to_remove.append(lines_copy[i - 2])
                lines = list_with_removed_lines(lines, lines_to_remove)
        return lines

    def update_variables(team, down, distance, play_type, play_result, two_min, line):
        '''
        Method to update team variables based on a given play/line.
        param team: the team in possession.
        param down: the current down.
        param distance: the current yardage to gain for another first down.
        param play_type: string indicating the type of the play, e.g. "R" for run, "P" for pass, "KO" for kickoff.
        param play_result: the result of the play.
        param two_min: boolean specifying if the current time is under 2 minutes to go in either half.
        param line: the line from which the previous parameters are collected from.
        '''
        opposition = home_team if team.name == road_team.name else road_team
        if play_type == "PEN": # update team/opposition penalty variables if play type is a penalty
            # update total plays variables
            if team.name == road_team.name:
                team.road_tot_off_plays += 1
                opposition.home_tot_def_plays += 1
            else:
                team.home_tot_off_plays += 1
                opposition.road_tot_def_plays += 1
            if play_result == "FST": # false start
                team.fst += 1
            elif play_result == "OFFHOLD": # offensive hold
                team.off_hold += 1
            elif play_result == "OPI": # offensive pass interference
                team.opi += 1
            elif play_result == "INTG": # intentional grounding
                team.intg += 1
            elif play_result == "OFFS": # offside/encroachment/neutral zone infraction
                opposition.offs += 1
            elif play_result == "DEFHOLD": # defensive hold
                opposition.def_hold += 1
            elif play_result == "DPI": # defensive pass interference
                opposition.dpi += 1
        elif play_type == "PT": # update team/opposition punt variables if play is a punt
            team.pt += 1 # number of punts           
            team.ptd = np.append(team.ptd, int(play_result[0:play_result.index("D")])) # punt distance
            return_yardage = int(play_result[play_result.index("D") + 1:]) # return distance (0 if fair catch/not fielded)
            team.ptra = np.append(team.ptra, return_yardage) # add return_yardage to kicking team punt return allowed list
            opposition.ptrm = np.append(opposition.ptrm, return_yardage) # add return_yardage to return team punt return made list
        elif play_type == "KO": # update team/opposition kickoff variables if play is a kickoff
            team.ko += 1 # number of kickoffs
            if "TB" in play_result: # play result is a touchback
                team.kotb += 1 # number of touchbacks
            else:
                team.kod = np.append(team.kod, int(play_result[0:play_result.index("D")])) # kickoff distance
                return_yardage = int(play_result[play_result.index("D") + 1:]) # return distance
                team.kora = np.append(team.kora, return_yardage) # add return_yardage to kicking team kick return allowed list
                opposition.korm = np.append(opposition.korm, return_yardage) # add return_yardage to return team kick return made list
        elif play_type == "2P": # play type is a 2 point conversion
            team.two_pa += 1 # 2 pointers attempted
            if play_result == "2PS": # 2 point attempt converted
                team.two_pm += 1 # 2 pointers made
        elif "FG" in play_type: # play type is a field goal
            fg_distance = int(play_type[2:]) # field goal distance
            # update relevant variable
            if fg_distance < 40:
                team.fga_40 += 1 # field goals attempted
                if play_result == "FGS":
                    team.fgm_40 += 1 # field goals made
            elif fg_distance < 50:
                team.fga_50 += 1
                if play_result == "FGS":
                    team.fgm_50 += 1
            elif fg_distance < 60:
                team.fga_60 += 1
                if play_result == "FGS":
                    team.fgm_60 += 1
            elif fg_distance >= 60:
                team.fga_70 += 1
                if play_result == "FGS":
                    team.fgm_70 += 1
        elif play_type == "XP": # play type is an extra point
            team.xpa += 1 # extra point attempts
            if play_result == "XPS":
                team.xpm += 1 # extra points made
        if play_type == "R" or play_type == "P": # play type is a run or a pass
            distance_index = 0 # index indicating an interval for the yardage to go until a first down
            if distance <= 5:
                distance_index = 2
            elif distance > 5 and distance <= 10:
                distance_index = 1
            team_updating_list = list() # downs data list to update for team in possession
            opposition_updating_list = list() # downs data list to update for opposition
            if down == 1: # 1st down
                team_updating_list = team.off_fd
                opposition_updating_list = opposition.def_fd
            elif down == 2: # 2nd down
                team_updating_list = team.off_sd
                opposition_updating_list = opposition.def_sd
            elif down == 3: # 3rd down
                team_updating_list = team.off_td
                opposition_updating_list = opposition.def_td
            # no updating_list for 4th down, since 4th down is handled differently in the simulation algorithm
            if play_type == "P": # play type is a pass 
                player_targeted_index = 0 # index indicating the position of the player being targeted in the team players lists
                position_targeted = "" # string indicating the position being targeted
                found_receiver = False # boolean indicating if the receiver being targeted has been identified
                qb_index = 0 # same as player_targeted_index, but to identify the index of the quarterback throwing the ball                 
                #second_dash_index = line[line.index("-") + 1:].index("-")
                if "SACK" not in play_result: # there is a pass attempt
                    for j in range(0, len(team.players["QBs"])):
                        if team.players["QBs"][j].name in line: # find quarterback
                            qb_index = j
                            break                                 
                    for j in range(0, len(team.players["RBs"])):
                        if team.players["RBs"][j].name in line: # if a running back is being targeted, find the relevant variables
                            player_targeted_index = j
                            position_targeted = "RBs"
                            found_receiver = True
                            break
                    for j in range(0, len(team.players["WRs"])):
                        if team.players["WRs"][j].name in line: # if a wide receiver is being targeted, find the relevant variables
                            player_targeted_index = j
                            position_targeted = "WRs"
                            found_receiver = True
                            break
                    for j in range(0, len(team.players["TEs"])):
                        if team.players["TEs"][j].name in line: # if a tight end is being targeted, find the relevant variables
                            player_targeted_index = j
                            position_targeted = "TEs"
                            found_receiver = True
                            break
                    if team.name == road_team.name: # team in possession is the road team
                        team.road_off_pass_attempts += 1
                        opposition.home_def_pass_attempts += 1
                        if "DEEP" in play_result: # pass is a deep pass (>20 yards downfield)
                            if found_receiver == True: # receiver identified
                                if team_mnemonics[opposition.name] in line[0:11]: # team is in opposition half
                                    temp = line[0:11]
                                    mne_length = len(team_mnemonics[opposition.name])
                                    if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20: # team is in redzone
                                        team.players[position_targeted][player_targeted_index].receiving_data[4] += 1 # update redzone targets/comps if team in redzone
                                team.players[position_targeted][player_targeted_index].receiving_data[2] += 1
                            team.players["QBs"][qb_index].target_depth_data[1][2] += 1 # update target depth data of quarterback who is throwing
                            team.off_target_depth_data[1][2] += 1 # update team target depth data (offense)
                            opposition.def_target_depth_data[0][2] += 1 # update opposition target depth data (defense)
                        else: # pass is a short pass (<20 yards downfield)
                            if found_receiver == True:
                                if team_mnemonics[opposition.name] in line[0:11]:
                                    temp = line[0:11]
                                    mne_length = len(team_mnemonics[opposition.name])
                                    if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20:
                                        team.players[position_targeted][player_targeted_index].receiving_data[4] += 1
                                team.players[position_targeted][player_targeted_index].receiving_data[0] += 1
                            team.players["QBs"][qb_index].target_depth_data[1][0] += 1
                            team.off_target_depth_data[1][0] += 1
                            opposition.def_target_depth_data[0][0] += 1
                    else: # team in possession is home team
                        team.home_off_pass_attempts += 1
                        opposition.road_def_pass_attempts += 1
                        if "DEEP" in play_result:
                            if found_receiver == True:
                                if team_mnemonics[opposition.name] in line[0:11]:
                                    temp = line[0:11]
                                    mne_length = len(team_mnemonics[opposition.name])
                                    if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20:
                                        team.players[position_targeted][player_targeted_index].receiving_data[4] += 1
                                team.players[position_targeted][player_targeted_index].receiving_data[2] += 1
                            team.players["QBs"][qb_index].target_depth_data[0][2] += 1
                            team.off_target_depth_data[0][2] += 1
                            opposition.def_target_depth_data[1][2] += 1
                        else:
                            if found_receiver == True:
                                if team_mnemonics[opposition.name] in line[0:11]:
                                    temp = line[0:11]
                                    mne_length = len(team_mnemonics[opposition.name])
                                    if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20:
                                        team.players[position_targeted][player_targeted_index].receiving_data[4] += 1
                                team.players[position_targeted][player_targeted_index].receiving_data[0] += 1
                            team.players["QBs"][qb_index].target_depth_data[0][0] += 1
                            team.off_target_depth_data[0][0] += 1
                            opposition.def_target_depth_data[1][0] += 1
                    if "INT" not in play_result and "IC" not in play_result: # pass completion                        
                        if team.name == road_team.name:
                            team.road_off_pass_completions += 1
                            opposition.home_def_pass_completions += 1
                            if "DEEP" in play_result:
                                if found_receiver == True:
                                    if team_mnemonics[opposition.name] in line[0:11]:
                                        temp = line[0:11]
                                        mne_length = len(team_mnemonics[opposition.name])
                                        if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20:
                                            team.players[position_targeted][player_targeted_index].receiving_data[5] += 1
                                    team.players[position_targeted][player_targeted_index].receiving_data[3] += 1
                                team.players["QBs"][qb_index].target_depth_data[1][3] += 1
                                team.off_target_depth_data[1][3] += 1
                                opposition.def_target_depth_data[0][3] += 1
                            else:
                                if found_receiver == True:
                                    if team_mnemonics[opposition.name] in line[0:11]:
                                        temp = line[0:11]
                                        mne_length = len(team_mnemonics[opposition.name])
                                        if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20:
                                            team.players[position_targeted][player_targeted_index].receiving_data[5] += 1
                                    team.players[position_targeted][player_targeted_index].receiving_data[1] += 1
                                team.players["QBs"][qb_index].target_depth_data[1][1] += 1
                                team.off_target_depth_data[1][1] += 1
                                opposition.def_target_depth_data[0][1] += 1
                        else:
                            team.home_off_pass_completions += 1
                            opposition.road_def_pass_completions += 1
                            if "DEEP" in play_result:
                                if found_receiver == True:
                                    if team_mnemonics[opposition.name] in line[0:11]:
                                        temp = line[0:11]
                                        mne_length = len(team_mnemonics[opposition.name])
                                        if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20:
                                            team.players[position_targeted][player_targeted_index].receiving_data[5] += 1
                                    team.players[position_targeted][player_targeted_index].receiving_data[3] += 1
                                team.players["QBs"][qb_index].target_depth_data[0][3] += 1
                                team.off_target_depth_data[0][3] += 1
                                opposition.def_target_depth_data[1][3] += 1
                            else:
                                if found_receiver == True:
                                    if team_mnemonics[opposition.name] in line[0:11]:
                                        temp = line[0:11]
                                        mne_length = len(team_mnemonics[opposition.name])
                                        if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20:
                                            team.players[position_targeted][player_targeted_index].receiving_data[5] += 1
                                    team.players[position_targeted][player_targeted_index].receiving_data[1] += 1
                                team.players["QBs"][qb_index].target_depth_data[0][1] += 1
                                team.off_target_depth_data[0][1] += 1
                                opposition.def_target_depth_data[1][1] += 1
                    if "INT" in play_result: # pass thrown was intercepted
                        if team.name == road_team.name:
                            team.road_int_thrown += 1
                            opposition.home_int_got += 1
                            if "DEEP" in play_result:
                                team.players["QBs"][qb_index].target_depth_data[1][5] += 1
                                team.off_target_depth_data[1][5] += 1
                                opposition.def_target_depth_data[0][5] += 1
                            else:
                                team.players["QBs"][qb_index].target_depth_data[1][4] += 1
                                team.off_target_depth_data[1][4] += 1
                                opposition.def_target_depth_data[0][4] += 1
                        else:
                            team.home_int_thrown += 1
                            opposition.road_int_got += 1
                            if "DEEP" in play_result:
                                team.players["QBs"][qb_index].target_depth_data[0][5] += 1
                                team.off_target_depth_data[0][5] += 1
                                opposition.def_target_depth_data[1][5] += 1
                            else:
                                team.players["QBs"][qb_index].target_depth_data[0][4] += 1
                                team.off_target_depth_data[0][4] += 1
                                opposition.def_target_depth_data[1][4] += 1
                else: # play resulted in a sack
                    if team.name == road_team.name:
                        team.home_sacks_allowed += 1 
                        opposition.road_sacks_got += 1
                    else:
                        team.road_sacks_allowed += 1 
                        opposition.home_sacks_got += 1
                if down != 4: # 1st, 2nd, or 3rd down
                    team_updating_list[distance_index][1] += 1 # add pass attempt to downs data list for team (offense)
                    opposition_updating_list[distance_index][1] += 1 # add pass attempt to downs data list for opposition (defense)
                    if "INT" not in play_result and "IC" not in play_result and "SACK" not in play_result: # completed pass
                        yardage = int(play_result[0:play_result.index("Y")]) # yardage gained
                        team.pass_yards_list = np.append(team.pass_yards_list, yardage) # add yardage gained to team pass yards gained list
                        opposition.pass_yards_against_list = np.append(opposition.pass_yards_against_list, yardage) # add yardage allowed to opposition pass yards allowed list
                        team.players[position_targeted][player_targeted_index].rec_yards_list.append(yardage) # add yardage gained to targeted receiver's receiving yards gained list
            elif play_type == "R": # play type is a run
                player_index = 0
                position = ""
                found_player = False
                for j in range(0, len(team.players["QBs"])):
                    if team.players["QBs"][j].name in line:
                        player_index = j
                        position = "QBs"
                        found_player = True
                        break
                for j in range(0, len(team.players["RBs"])):
                    if team.players["RBs"][j].name in line:
                        player_index = j
                        position = "RBs"
                        found_player = True
                        break
                for j in range(0, len(team.players["WRs"])):
                    if team.players["WRs"][j].name in line:
                        player_index = j
                        position = "WRs"
                        found_player = True
                        break
                for j in range(0, len(team.players["TEs"])):
                    if team.players["TEs"][j].name in line:
                        player_index = j
                        position = "TEs"
                        found_player = True
                        break
                if down >= 3: # 3rd or 4th down
                    if found_player == True:
                        team.players[position][player_index].rushing_atts[2] += 1 # add 1 rushing attempt for player on 3rd/4th down
                else: # 1st or 2nd down
                    if found_player == True:
                        team.players[position][player_index].rushing_atts[down - 1] += 1 # add 1 rushing attempt for player on 1st/2nd down
                if team_mnemonics[opposition.name] in line[0:11]: # team is in inside opposition half
                        temp = line[0:11]
                        mne_length = len(team_mnemonics[opposition.name])
                        if int(temp[temp.index(team_mnemonics[opposition.name]) + mne_length + 1:temp.index(team_mnemonics[opposition.name]) + mne_length + 3]) <= 20: # team in redzone
                            team.players[position][player_index].rushing_atts[3] += 1 # add 1 redzone rushing attempt for player
                if down != 4:
                    yardage = int(play_result[0:play_result.index("Y")]) 
                    team.rush_yards_list = np.append(team.rush_yards_list, yardage)
                    opposition.rush_yards_against_list = np.append(opposition.rush_yards_against_list, yardage)
                    team.players[position][player_index].rush_yards_list.append(yardage) # add yardage gained to rusher's rush yards gained list
                    team_updating_list[distance_index][0] += 1 # add rush attempt to downs data list for team (offense)
                    opposition_updating_list[distance_index][0] += 1 # add pass attempt to downs data list for opposition (defense)
            if "FMBL" in play_result: # play resulted in a fumble
                if team.name == road_team.name:
                    team.road_fmbl += 1
                    opposition.home_fmbl_got += 1
                else:
                    team.home_fmbl += 1
                    opposition.road_fmbl_got += 1
            if down == 4: # 4th down
                team.ofod_a += 1 # add 4th down attempt for team (offense)
                opposition.dfod_a += 1 # add 4th down faced for opposition (defense)
                if "4DS" in play_result: # 4th down converted
                    team.ofod_m += 1 # add 4th down converted for team
                    opposition.dfod_m += 1 # add 4th down allowed for opposition
            # update total plays variables
            if team.name == road_team.name:
                team.road_tot_off_plays += 1
                opposition.home_tot_def_plays += 1
            else:
                team.home_tot_off_plays += 1
                opposition.road_tot_def_plays += 1

    two_min = False
    down = 0
    distance = 0
    play_type = ""
    play_result = ""
    team = ""
    file = open(directory + "/" + game) # gamebook file
    lines = edit_lines_into_correct_format(file.readlines(), road_team.name, home_team.name) # remove unneeded lines from gamebook
    for line in lines:
        #print(line) # uncommented if there is an error when logging to see what line is causing the error
        # line represents a 1st, 2nd, 3rd, or 4th down play being run
        if line[1] == "-" and (line[2] == "1" or line[2] == "2" or line[2] == "3" or line[2] == "4" or line[2] == "5" or line[2] == "6" or line[2] == "7" or line[2] == "8" or line[2] == "9"):
            down = int(line[0])
            try:
                distance = int(line[2:4])
            except:
                distance = int(line[2])
            if " PENALTY " in line: # play was an accepted penalty in line
                play_type = "PEN"
                if "False Start" in line:
                    play_result = "FST"
                elif "Neutral Zone Infraction" in line or "Offside" in line or "Encroachment" in line:
                    play_result = "OFFS"
                elif "Defensive Pass Interference" in line:
                    play_result = "DPI"
                elif "Offensive Pass Interference" in line:
                    play_result = "OPI"
                elif "Intentional Grounding" in line:
                    play_result = "INTG"
                elif "Offensive Holding" in line:
                    play_result = "OFFHOLD"
                elif "Defensive Holding" in line:
                    play_result = "DEFHOLD"
            elif " pass " in line: # play was a pass
                play_type = "P"
                if "pass incomplete" in line:
                    if " deep " in line:
                        play_result = "IC DEEP" # incomplete deep pass
                    elif " short " in line:
                        play_result = "IC SHORT"
                    else:
                        play_result = "IC" # incomplete if target depth not specified
                else:
                    if "INTERCEPTED" in line: # play was an interception
                        if " deep " in line:
                            play_result = "INT DEEP" # deep interception
                        elif " short " in line:
                            play_result = "INT SHORT"
                    else: # play was a pass completion
                        try:
                            yardage = int(line[line.index(" yard") - 2:line.index(" yard")]) # yardage gained
                            play_result = str(yardage) + "YDS"
                            if yardage < 20:
                                play_result += " SHORT" # short gain
                            else:
                                play_result += " DEEP" # deep gain
                        except:
                            play_result = "0YDS SHORT" # if line says "no gain" rather than "0 yards", for example
                        if "FUMBLES" in line: # play resulted in a fumble
                            play_result += "FMBL"
            elif " sacked " in line: # play resulted in a sack
                play_type = "P"
                play_result = "SACK"
                if "FUMBLES" in line:
                    play_result += "FMBL" # sack fumble
            elif " punts " in line: # play was a punt
                play_type = "PT"
                play_result = str(int(line[line.index(" yard") - 2:line.index(" yard")])) + "D" # punt distance
                try:
                    substring = line[line.index(" yard") + 1:]
                    play_result += str(int(substring[substring.index(" yard") - 2:substring.index(" yard")])) # added punt return
                except:
                    play_result += "0" # if "fair catch" or "no gain" in line
            elif "field goal" in line: # play was a field goal
                play_type = "FG" + str(int(line[line.index(" yard") - 2:line.index(" yard")])) # field goal distance
                play_result = "FGS" if "is GOOD" in line else "FGF" # field goal made/missed
            else:
                play_type = "R" # play was a run (gamebook does not explicitly state when a run play occurs)              
                try:                        
                    play_result = str(int(line[line.index(" yard") - 2:line.index(" yard")])) + "YDS"
                except:
                    play_result = "0YDS"
                if "FUMBLES" in line:                    
                    if "no gain" in line:
                        if line.index("no gain") > line.index("FUMBLES"): # no gain was on the rush, not on the fumble return
                            play_result = "0YDS"
                        else:
                            try:                        
                                play_result = str(int(line[0:line.index("FUMBLES")][line[0:line.index("FUMBLES")].index(" yard") - 2:line[0:line.index("FUMBLES")].index(" yard")])) + "YDS"
                            except:
                                play_result = "0YDS"                                
                    play_result += "FMBL"
            if down == 4 and (play_type == "R" or play_type == "P"): # team went for a 4th down attempt
                if "FMBL" in play_result or "INT" in play_result or "IC" in play_result or "SACK" in play_result:
                    play_result += " 4DF" # failed to convert
                else:
                    if int(play_result[0:play_result.index("Y")]) >= distance: # yardage gained was enough to gain a 1st down/touchdown
                        play_result += " 4DS" # converted
                    else:
                        play_result += " 4DF"
            if team == home_team.name: # team in possession is the home team
                update_variables(home_team, down, distance, play_type, play_result, two_min, line) # update home team variables
            else:
                update_variables(road_team, down, distance, play_type, play_result, two_min, line) # update road team variables
        elif home_team.name in line: # if name of home team is in line, change the team variable
            if home_team.name == "Rams" and "Ramsey" not in line: # exception since J.Ramsey, a member of the LA Rams, appears in several lines in gamebook - don't want a "false change"
                team = home_team.name
            else:
                team = home_team.name
        elif road_team.name in line:
            if road_team.name == "Rams" and "Ramsey" not in line:
                team = road_team.name
            else:
                team = road_team.name
        elif ("2M" in line and len(line) == 3) or "Two-Minute Warning" in line: # under the 2 minute warning (previously used "2M" as an indicator for this, so some gamebooks have it)
            two_min = True
        elif "2Mend" in line:
            two_min = False
        elif "Timeout" in line: # timeout
            continue # ignore it, next line           
        else: # no 1st, 2nd, 3rd, or 4th down specified, so it is a kickoff/points after play
            down = 1
            distance = 10
            if " kicks " in line: # kickoff
                play_type = "KO"
                if "Touchback" in line:
                    play_result = "TB"
                else:
                    play_result = str(int(line[line.index("yards") - 3:line.index("yards")])) + "D" # kickoff distance
                    try:
                        substring = line[line.index("yards") + 1:]
                        play_result += str(int(substring[substring.index("yards") - 3:substring.index("yards")])) # kickoff return yardage
                    except:
                        play_result += "0" # no return
            if "extra point" in line: # extra point
                play_type = "XP"
                play_result = "XPS" if "is GOOD" in line else "XPF"
            if "TWO-POINT CONVERSION ATTEMPT" in line: # 2 point conversion
                play_type = "2P"
                play_result = "2PS" if "ATTEMPT FAILS" not in line else "2PF"
            if team == home_team.name:
                update_variables(home_team, down, distance, play_type, play_result, two_min, line)
            else:
                update_variables(road_team, down, distance, play_type, play_result, two_min, line)

    file.close() # close gamebook once looped through its lines

def write_team_data_to_excel_files(team, year="", include_players_data=True):
    '''
    Method to write the updated team data to Excel files.
    param team: the team that will gets its Excel files updated.
    param year: the year of the team. If not specified, defaults to current and previous year.
    param include_players_data: boolean indicating whether or not to write players data to Excel.
    '''
    team.kod = ["n"] if team.kod == [] else team.kod # empty lists are initialized to ["n"] instead of [] so that exception is not thrown when loading data
    team.kora = ["n"] if team.kora == [] else team.kora
    team.korm = ["n"] if team.korm == [] else team.korm
    team.ptd = ["n"] if team.ptd == [] else team.ptd
    team.ptra = ["n"] if team.ptra == [] else team.ptra
    team.ptrm = ["n"] if team.ptrm == [] else team.ptrm

    # Create data frames for each sheet in general team data sheet
    yards_df = pd.DataFrame([[" ".join([str(num) for num in team.rush_yards_list]), " ".join([str(num) for num in team.rush_yards_against_list])], [" ".join([str(num) for num in team.pass_yards_list]), " ".join([str(num) for num in team.pass_yards_against_list])]], index=["R", "P"], columns=["OFF", "DEF"])
    off_df = pd.DataFrame([[team.off_fd[0][0], team.off_fd[1][0], team.off_fd[2][0], team.off_sd[0][0], team.off_sd[1][0], team.off_sd[2][0], team.off_td[0][0], team.off_td[1][0], team.off_td[2][0], "Home", team.home_off_pass_attempts, team.home_off_pass_completions, team.home_sacks_allowed, team.ofod_a, team.ofod_m, team.home_tot_off_plays], [team.off_fd[0][1], team.off_fd[1][1], team.off_fd[2][1], team.off_sd[0][1], team.off_sd[1][1], team.off_sd[2][1], team.off_td[0][1], team.off_td[1][1], team.off_td[2][1], "Road", team.road_off_pass_attempts, team.road_off_pass_completions, team.road_sacks_allowed, " ", " ", team.road_tot_off_plays]], index=["RATT", "PATT"], columns=["1N11+", "1N10-6", "1N5-", "2N11+", "2N10-6", "2N5-", "3N11+", "3N10-6", "3N5-", " ", "PATT", "PCOMP", "SACKS", "4DA", "4DM", "TOTPLAYS"])
    two_min_off_df = pd.DataFrame([[team.two_min_off_fd[0][0], team.two_min_off_fd[1][0], team.two_min_off_fd[2][0], team.two_min_off_sd[0][0], team.two_min_off_sd[1][0], team.two_min_off_sd[2][0], team.two_min_off_td[0][0], team.two_min_off_td[1][0], team.two_min_off_td[2][0]], [team.two_min_off_fd[0][1], team.two_min_off_fd[1][1], team.two_min_off_fd[2][1], team.two_min_off_sd[0][1], team.two_min_off_sd[1][1], team.two_min_off_sd[2][1], team.two_min_off_td[0][1], team.two_min_off_td[1][1], team.two_min_off_td[2][1]]], index=["RATT", "PATT"], columns=["1N11+", "1N10-6", "1N5-", "2N11+", "2N10-6", "2N5-", "3N11+", "3N10-6", "3N5-"])
    def_df = pd.DataFrame([[team.def_fd[0][0], team.def_fd[1][0], team.def_fd[2][0], team.def_sd[0][0], team.def_sd[1][0], team.def_sd[2][0], team.def_td[0][0], team.def_td[1][0], team.def_td[2][0], "Home", team.home_def_pass_attempts, team.home_def_pass_completions, team.home_sacks_got, team.dfod_a, team.dfod_m, team.home_tot_def_plays], [team.def_fd[0][1], team.def_fd[1][1], team.def_fd[2][1], team.def_sd[0][1], team.def_sd[1][1], team.def_sd[2][1], team.def_td[0][1], team.def_td[1][1], team.def_td[2][1], "Road", team.road_def_pass_attempts, team.road_def_pass_completions, team.road_sacks_got, " ", " ", team.road_tot_def_plays]], index=["RATT", "PATT"], columns=["1N11+", "1N10-6", "1N5-", "2N11+", "2N10-6", "2N5-", "3N11+", "3N10-6", "3N5-", " ", "PATT", "PCOMP", "SACKS", "4DA", "4DM", "TOTPLAYS"])
    two_min_def_df = pd.DataFrame([[team.two_min_def_fd[0][0], team.two_min_def_fd[1][0], team.two_min_def_fd[2][0], team.two_min_def_sd[0][0], team.two_min_def_sd[1][0], team.two_min_def_sd[2][0], team.two_min_def_td[0][0], team.two_min_def_td[1][0], team.two_min_def_td[2][0]], [team.two_min_def_fd[0][1], team.two_min_def_fd[1][1], team.two_min_def_fd[2][1], team.two_min_def_sd[0][1], team.two_min_def_sd[1][1], team.two_min_def_sd[2][1], team.two_min_def_td[0][1], team.two_min_def_td[1][1], team.two_min_def_td[2][1]]], index=["RATT", "PATT"], columns=["1N11+", "1N10-6", "1N5-", "2N11+", "2N10-6", "2N5-", "3N11+", "3N10-6", "3N5-"])
    special_teams_df = pd.DataFrame([[team.ko, "#", team.pt, " ", team.xpa, team.xpm, team.two_pa, team.two_pm, team.fga_40, team.fgm_40, team.fga_50, team.fgm_50, team.fga_60, team.fgm_60, team.fga_70, team.fgm_70], [team.kotb, "D", " ".join([str(num) for num in team.ptd])], [" ".join([str(num) for num in team.kod]), "RA", " ".join([str(num) for num in team.ptra])], [" ".join([str(num) for num in team.kora]), "RM", " ".join([str(num) for num in team.ptrm])], [" ".join([str(num) for num in team.korm])]], index=["#", "TB", "D", "RA", "RM"], columns=["KO", " ", "PT", " ", "XPA", "XPM", "2PA", "2PM", "FG40-A", "FG40-M", "FG50-A", "FG50-M", "FG60-A", "FG60-M", "FG70-A", "FG70-M"])
    turnovers_df = pd.DataFrame([[team.home_int_thrown, team.home_int_got, team.home_fmbl, team.home_fmbl_got], [team.road_int_thrown, team.road_int_got, team.road_fmbl, team.road_fmbl_got]], columns=["INT", "INTg", "FMBL", "FMBLg"], index=["Home", "Road"])
    penalties_df = pd.DataFrame([[team.fst, "Offside", team.offs], [team.off_hold, "Holding", team.def_hold], [team.opi, "Pass interference", team.dpi], [team.intg]], index=["False start", "Holding", "Pass interference", "Intentional grounding"], columns=["OFF", " ", "DEF"])
 
    with pd.ExcelWriter("Base/Teams/" + team.name + "/" + year + "Team Data.xlsx") as writer: # write data frames to excel simultaneously
        yards_df.to_excel(writer, sheet_name="YDS")
        off_df.to_excel(writer, sheet_name="OFF")
        two_min_off_df.to_excel(writer, sheet_name="2minOFF")
        def_df.to_excel(writer, sheet_name="DEF")
        two_min_def_df.to_excel(writer, sheet_name="2minDEF")
        special_teams_df.to_excel(writer, sheet_name="ST")
        turnovers_df.to_excel(writer, sheet_name="TURNS")                                                      
        penalties_df.to_excel(writer, sheet_name="PEN")

    # Create team target depth data frames
    targ_dep_off_df = pd.DataFrame([[int(d) for d in team.off_target_depth_data[0]], [int(d) for d in team.off_target_depth_data[1]]], columns=["Short Att", "Short Comp", "Deep Att", "Deep Comp", "Short Int", "Deep Int"], index=["H", "R"])
    targ_dep_def_df = pd.DataFrame([[int(d) for d in team.def_target_depth_data[0]], [int(d) for d in team.def_target_depth_data[1]]], columns=["Short Att", "Short Comp", "Deep Att", "Deep Comp", "Short Int", "Deep Int"], index=["H", "R"])
    
    with pd.ExcelWriter("Base/Teams/" + team.name + "/" + year + "Target Depth Data.xlsx") as writer:
        targ_dep_off_df.to_excel(writer, sheet_name="OFF")
        targ_dep_def_df.to_excel(writer, sheet_name="DEF")

    if include_players_data == True:
        rushing_players = list()
        receiving_players = list()   
        # loop through players     
        for position in team.players:
            for player in team.players[position]:
                if np.any(player.rushing_atts) != 0: # player has at least 1 rushing attempt
                    rushing_players.append(player) # add them to rushing_players
                if np.any(player.receiving_data) != 0: # player has at least 1 target
                    receiving_players.append(player) # add them to receiving_players
        players_rushing_df = pd.DataFrame([[player.name, player.rushing_atts[0], player.rushing_atts[1], player.rushing_atts[2], player.rushing_atts[3]] for player in rushing_players], columns=["Name", "1DATT", "2DATT", "3DATT", "RZATT"])
        players_receiving_df = pd.DataFrame([[player.name, player.receiving_data[0], player.receiving_data[1], player.receiving_data[2], player.receiving_data[3], player.receiving_data[4], player.receiving_data[5]] for player in receiving_players], columns=["Name", "Short Target", "Short Comp", "Deep Target", "Deep Comp", "RZ Target", "RZ Comp"])
        with pd.ExcelWriter("Base/Teams/" + team.name + "/Players Data.xlsx") as writer:
            players_rushing_df.to_excel(writer, sheet_name="Rushing")
            players_receiving_df.to_excel(writer, sheet_name="Receiving")
        

        ## Work in progress
        
        # with pd.ExcelWriter(team.name + "/QBs Target Depth Data.xlsx") as writer:            
        #     for qb in team.players["QBs"]:
        #         targ_dep_df = pd.DataFrame([[int(d) for d in qb.target_depth_data[0]], [int(d) for d in qb.target_depth_data[1]]], columns=["Short Att", "Short Comp", "Deep Att", "Deep Comp", "Short Int", "Deep Int"], index=["H", "R"])
        #         targ_dep_df.to_excel(writer, sheet_name=qb.name)
        
        # players_rush_yards_lists = list()
        # players_rec_yards_lists = list()
        # rush_players = list()
        # rec_players = list()
        # for position in team.players:
        #     if position != "Ks":
        #         for player in team.players[position]:
        #             rush_players.append(player)
        #             rec_players.append(player)
        #             if player.rush_yards_list != []:                        
        #                 players_rush_yards_lists.append(" ".join([str(d) for d in player.rush_yards_list]))
        #             else:
        #                 players_rush_yards_lists.append("n")
        #             if player.rec_yards_list != []:                        
        #                 players_rec_yards_lists.append(" ".join([str(d) for d in player.rec_yards_list]))
        #             else:
        #                 players_rec_yards_lists.append("n")
        # players_rush_yards_df = pd.DataFrame([players_rush_yards_lists], columns=[player.name for player in rush_players])
        # players_rec_yards_df = pd.DataFrame([players_rec_yards_lists], columns=[player.name for player in rec_players])
        # with pd.ExcelWriter(team.name + "/Players Yards Data.xlsx") as writer:
        #     players_rush_yards_df.to_excel(writer, sheet_name="Rushing")
        #     players_rec_yards_df.to_excel(writer, sheet_name="Receiving")