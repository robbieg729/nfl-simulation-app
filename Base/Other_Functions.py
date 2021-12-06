import numpy as np

def bubble_sort_by_fpts(players, scoring_format="PPR"):
    '''
    Method to sort a list of players/teams by fantasy points.
    param players: the list of players/teams to sort.
    param scoring_format: "PPR" or "Non-PPR", based on what type of scoring system the user wants to use. Defaults to standard PPR.
    '''
    # Applies standard bubble sort algorithm
    swapped = True
    while swapped == True:
        swapped = False
        for i in range(0, len(players) - 1):
            if scoring_format == "Non-PPR":
                if np.mean(players[i].all_games_stats["FPTS"]) - np.mean(players[i].all_games_stats["Rec"]) < np.mean(players[i + 1].all_games_stats["FPTS"]) - np.mean(players[i + 1].all_games_stats["Rec"]):
                    temp = players[i + 1]
                    players[i + 1] = players[i]
                    players[i] = temp
                    swapped = True 
            else:
                if np.mean(players[i].all_games_stats["FPTS"]) < np.mean(players[i + 1].all_games_stats["FPTS"]):
                    temp = players[i + 1]
                    players[i + 1] = players[i]
                    players[i] = temp
                    swapped = True
    return players

def return_best_fit_in_str_format(best_fit):
    '''
    Method to return the best fit to a statistical distribution in string format, to write to Excel.
    param best_fit: the best fit to a statistical distribution for some data, as a tuple.
    '''
    def generate_params_string(params_tuple):
        '''
        Method to get the parameters in string format.
        param params_tuple: the parameters, as a tuple.
        '''
        params_str = ""
        for p in params_tuple:
            if params_str == "":
                params_str = str(p) + ", "
            else:
                params_str += str(p) + ", "
        return "(" + params_str[0:len(params_str) - 2] + ")"
    dist = ""
    params_tuple = tuple()
    params_str = ""
    if (best_fit.get("f") is not None): # distribution of best fit is the F distribution
        dist = "F" # distribution
        params_tuple = best_fit["f"] # parameters of the best fit
        params_str = generate_params_string(params_tuple) # parameters in string format
    elif (best_fit.get("johnsonsu") is not None): # Johnson SU distribution
        dist = "JSU"
        params_tuple = best_fit["johnsonsu"]
        params_str = generate_params_string(params_tuple)
    elif (best_fit.get("johnsonsb") is not None): # Johnson SB distribution
        dist = "JSB"
        params_tuple = best_fit["johnsonsb"]
        params_str = generate_params_string(params_tuple)
    elif (best_fit.get("norm") is not None): # Normal distribution
        dist = "N"
        params_tuple = best_fit["norm"]
        params_str = generate_params_string(params_tuple)
    elif (best_fit.get("norminvgauss") is not None): # Normal-inverse Gaussian
        dist = "NIG"
        params_tuple = best_fit["norminvgauss"]
        params_str = generate_params_string(params_tuple)
    elif (best_fit.get("nct") is not None): # NCT distribution
        dist = "NCT"
        params_tuple = best_fit["nct"]
        params_str = generate_params_string(params_tuple)
    elif (best_fit.get("exponnorm") is not None): # Exponential normal distribution
        dist = "EXN"
        params_tuple = best_fit["exponnorm"]
        params_str = generate_params_string(params_tuple)
    elif (best_fit.get("mielke") is not None): # Mielke distribution
        dist = "MIE"
        params_tuple = best_fit["mielke"]
        params_str = generate_params_string(params_tuple)
    elif (best_fit.get("fatiguelife") is not None): # Fatigue life distribution
        dist = "FTL"
        params_tuple = best_fit["fatiguelife"]
        params_str = generate_params_string(params_tuple)
    elif (best_fit.get("gamma") is not None): # Gamma distribution
        dist = "GAM"
        params_tuple = best_fit["gamma"]
        params_str = generate_params_string(params_tuple)
    return (dist + params_str) # return best fit as string, in format "distribution_name(parameter_1,...,parameter_n)"

def change_data_list_if_needed(data_list, team, down, distance, two_min, list_type):
    '''
    Method to change a downs data list if there are not enough data points in it, based on similarities between down and distance situations.
    param data_list: the downs data list that may be changed.
    param team: the team containing the data list that may be changed.
    param down: the down of the data list to potentially change.
    param distance: the distance of the data list to change. Given as 1, 6, or 11 for (1<=d<=5, 6<=d<=10, d>=11).
    param two_min: boolean specifying if the data list to be changed is a 2-minute list.
    param list_type: "OFF" or "DEF" for offense list or defense list.
    '''
    if data_list[0] + data_list[1] <= 20: # sum of rush attempts and pass attempts is less than 20.
        if list_type == "OFF": # offense list type                     
            if down == 1: # 1st down
                if distance == 11 or distance == 1: # 1st and 11+ or 1st and 1-5
                    return team.off_fd[1] if two_min == False else team.two_min_off_fd[1] # change data list to 1st and 6-10 as it is most similar to 1st and 11+ or 1st and 1-5
                elif distance == 6: # 1st and 6-10
                    return team.off_sd[1] if two_min == False else team.two_min_off_sd[1] # change data list to 2nd and 6-10
            # apply same ideas for other downs and distances
            elif down == 2:
                if distance == 11:
                    return team.off_td[1] if two_min == False else team.two_min_off_td[1]
                elif distance == 6 or distance == 1:
                    return team.off_fd[1] if two_min == False else team.two_min_off_fd[1]
            elif down == 3:
                if distance == 11 or distance == 6:
                    return team.off_sd[1] if two_min == False else team.two_min_off_sd[1]
                elif distance == 1:
                    return team.off_sd[1] if two_min == False else team.two_min_off_sd[1]
        elif list_type == "DEF": # defense list type
            if down == 1:
                if distance == 11 or distance == 1:
                    return team.def_fd[1] if two_min == False else team.two_min_def_fd[1]
                elif distance == 6:
                    return team.def_sd[1] if two_min == False else team.two_min_def_sd[1]
            elif down == 2:
                if distance == 11:
                    return team.def_td[1] if two_min == False else team.two_min_def_td[1]
                elif distance == 6 or distance == 1:
                    return team.def_fd[1] if two_min == False else team.two_min_def_fd[1]
            elif down == 3:
                if distance == 11 or distance == 6:
                    return team.def_sd[1] if two_min == False else team.two_min_def_sd[1]
                elif distance == 1:
                    return team.def_sd[1] if two_min == False else team.two_min_def_sd[1]                    
    return data_list # return data_list in its original form if no changes were made 

def change_team_data_lists(team):
    '''
    Method to check all downs data lists for a team, and change them if needed.
    param team: the team that needs checking.
    '''
    for i in range(0, len(team.off_fd)): # loop through offense first down data lists, change if needed
        team.off_fd[i] = change_data_list_if_needed(team.off_fd[i], team, 1, -5 * i + 11, False, "OFF")
    for i in range(0, len(team.off_sd)):
        team.off_sd[i] = change_data_list_if_needed(team.off_sd[i], team, 2, -5 * i + 11, False, "OFF")
    for i in range(0, len(team.off_td)):
        team.off_td[i] = change_data_list_if_needed(team.off_td[i], team, 3, -5 * i + 11, False, "OFF")
    for i in range(0, len(team.two_min_off_fd)):
        team.two_min_off_fd[i] = change_data_list_if_needed(team.two_min_off_fd[i], team, 1, -5 * i + 11, True, "OFF")
    for i in range(0, len(team.two_min_off_sd)):
        team.two_min_off_sd[i] = change_data_list_if_needed(team.two_min_off_sd[i], team, 2, -5 * i + 11, True, "OFF")
    for i in range(0, len(team.two_min_off_td)):
        team.two_min_off_td[i] = change_data_list_if_needed(team.two_min_off_td[i], team, 3, -5 * i + 11, True, "OFF")
    for i in range(0, len(team.def_fd)):
        team.def_fd[i] = change_data_list_if_needed(team.def_fd[i], team, 1, -5 * i + 11, False, "DEF")
    for i in range(0, len(team.def_sd)):
        team.def_sd[i] = change_data_list_if_needed(team.def_sd[i], team, 2, -5 * i + 11, False, "DEF")
    for i in range(0, len(team.def_td)):
        team.def_td[i] = change_data_list_if_needed(team.def_td[i], team, 3, -5 * i + 11, False, "DEF")
    for i in range(0, len(team.two_min_def_fd)):
        team.two_min_def_fd[i] = change_data_list_if_needed(team.two_min_def_fd[i], team, 1, -5 * i + 11, True, "DEF")
    for i in range(0, len(team.two_min_def_sd)):
        team.two_min_def_sd[i] = change_data_list_if_needed(team.two_min_def_sd[i], team, 2, -5 * i + 11, True, "DEF")
    for i in range(0, len(team.two_min_def_td)):
        team.two_min_def_td[i] = change_data_list_if_needed(team.two_min_def_td[i], team, 3, -5 * i + 11, True, "DEF")