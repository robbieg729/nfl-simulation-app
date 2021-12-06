import numpy as np
import scipy.stats as stat
import random as rd

def new_time_left(t, time_taken, after_snap=True):
    '''
    Method to get the new amount of time left after a time loss.
    param t: current time left.
    param time_taken: the time loss.
    param after_snap: boolean specifying if the time loss was pre-snap or post-snap. Important for 2 minute warning implications.
    '''
    if t > 2700 and t - time_taken < 2700: # time loss carries over into 2nd quarter
        return 2700 # set time to start of 2nd quarter
    elif t > 1920 and t - time_taken < 1920: # time loss carries over into first half 2 minute warning
        if after_snap == True: # time loss was after snap (during a play)
            return t - time_taken # set time to be time - time loss
        return 1920 # set time to be 1920 if time loss was pre-snap
    elif t > 1800 and t - time_taken < 1800: # end of first half
        return 1800
    elif t > 900 and t - time_taken < 900: # end of 3rd quarter
        return 900
    elif t > 120 and t - time_taken < 120: # carry over into second half 2 minute warning
        if after_snap == True:
            return t - time_taken
        return 120
    elif t >= 0 and t - time_taken < 0: # carry over to end of game
        return 0
    else:
        return t - time_taken # if there is no carry over, just return time - time loss

def get_play(t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, td_play, kickoff, safety_kick, hurry_up, overtime=False, sudden_death=False):        
    '''
    Method to get the play type of the next play.
    param t: time left.
    param down: the current down.
    param distance: the current distance.
    param yards_to_endzone: the yards to go until the endzone for the offense.
    param team_in_poss: the team in possession.
    param opposition: the defense.
    param clock_running: boolean specifying if game clock is running or not.
    param td_play: boolean specifying if a touchdown just occurred.
    param kickoff: boolean specifying if the play should be a kickoff.
    param safety_kick: boolean specifying if a safety just occurred.
    param hurry_up: boolean specifying if offense is in hurry-up.
    param overtime: boolean specifying if game is in overtime. Defaults to False.
    param sudden_death: boolean specifying if game is in sudden_death. Defaults to False.
    '''
    def check_kneel_scenario(t, team_in_poss, opposition):
        '''
        Method to check if offense can go into victory formation.
        param t: time left.
        param team_in_poss: the offense.
        param opposition: the defense.
        '''
        if (team_in_poss.points - opposition.points > 0) and opposition.timeouts == 0:
            if (t - 40 * (4 - down)) <= 5:                            
                return True
        elif (team_in_poss.points - opposition.points > 0) and opposition.timeouts == 1:
            if down == 1:
                if t <= 83:
                    return True
            elif down == 2:
                if t <= 41:
                    return True
        elif (team_in_poss.points - opposition.points > 0) and opposition.timeouts == 2:
            if down == 1 and t <= 42:
                return True
        elif (t <= 1805 and t > 1800) and yards_to_endzone >= 75:
            return True
        return False

    def get_fourth_down_play(team_in_poss, opposition):
        '''
        Method to get a 4th down attempt (run or pass) play
        '''
        if team_in_poss.ofod_a > 10: # offense has more than 10 4th down attempts logged
            return team_in_poss.name + " 4DA" # just return a 4th down attempt for the offense (play result will consider how many 4th downs the offense has converted)
        else:
            data_list_off = team_in_poss.off_td[2]
            data_list_def = opposition.def_td[2]
            rush_ratio = (data_list_off[0] + data_list_def[0]) / (data_list_off[0] + data_list_def[0] + data_list_off[1] + data_list_def[1]) # proportion of rushes on 4th down
            if rd.random() <= rush_ratio: # random float in [0, 1] is <= rush probability (so play will be a rush essentially)
                return team_in_poss.name + " R" # rush attempt
            else:
                return team_in_poss.name + " P" # pass attempt

    def choose_punt_or_fourth_down(team_in_poss, per):
        '''
        Method to choose between a punt or 4th down.
        param team_in_poss: the offense.
        param per: approximate proportion that the offense will go for a 4th down attempt in this spot.
        '''
        play = ""
        if rd.random() <= per:
            play = get_fourth_down_play(team_in_poss, opposition)
        else:
            play = team_in_poss.name + " PT"
        return play
    play = ""
    if kickoff == True: # play should be a kickoff
        # Check if team should go for an onside kick or a regular kickoff
        if opposition.points - team_in_poss.points <= 8 and opposition.points - team_in_poss.points > 0 and check_kneel_scenario(t, opposition, team_in_poss) == True:
            play = team_in_poss.name + " ONSIDE KICK"
        elif opposition.points - team_in_poss.points > 8 and t <= 180:
            play = team_in_poss.name + " ONSIDE KICK"
        else:                
            play = team_in_poss.name + " KO"
            if t == 1800: # beginning of the second half
                # reset timeouts
                team_in_poss.timeouts = 3
                opposition.timeouts = 3
    elif (t <= 1806 and t > 1800) and (yards_to_endzone > 10 and yards_to_endzone <= 50): # Going for a score at the end of the half in bad field position
        if yards_to_endzone >= 43: # Not in field goal range
            play = team_in_poss.name + " HAILMARY"
        else:
            play = team_in_poss.name + " FG"
    elif (t <= 5) and (yards_to_endzone > 10 and yards_to_endzone <= 50) and (opposition.points - team_in_poss.points <= 3) and (opposition.points - team_in_poss.points >= 0): # Need a score at the end of the game
        if yards_to_endzone >= 43:
            play = team_in_poss.name + " HAILMARY"
        else:
            play = team_in_poss.name + " FG"
    else:
        if down <= 3: # 1st, 2nd, or 3rd down (any miscellaneous play is denoted as a 1st down)
            if td_play == True: # touchdown just occurred
                if t > 600: # Enough time left that you don't need to go for 2 regardless
                    play = team_in_poss.name + " XPA" # Extra point attempt
                else:
                    # Estimated increase in win probability when going for extra point/2 point conversion for point differentials between -15 and 15
                    decision_chart = {-15:1, -14:1, -13:[0.4, 1.1], -12:[1.1, 1.1], -11:[1.3, 2.2], -10:2, -9:[2.9, 3.3], -8:[3.3, 5.2], -7:1, -6:1, -5:2, -4:1, -3:1, -2:2, -1:1, 0:1, 1:2, 2:1, 3:1, 4:2, 5:2, 6:1, 7:[3.3, 2.9], 8:1, 9:1, 10:1, 11:1, 12:[0.4, 1], 13:1, 14:1, 15:[0.4, 1]}
                    if abs(team_in_poss.points - opposition.points) <= 15: # need decision_chart
                        deficit = team_in_poss.points - opposition.points
                        xpa_per = 0
                        try:
                            if decision_chart[deficit][0] < decision_chart[deficit][1]:
                                xpa_per = 1 - (0.5 + (decision_chart[deficit][1] - decision_chart[deficit][0]) * 0.15) # Subjective method to determine play type
                            else:
                                xpa_per = 0.5 + (decision_chart[deficit][0] - decision_chart[deficit][1]) * 0.15
                            play = team_in_poss.name + " XPA" if rd.random() <= xpa_per else team_in_poss.name + " 2PA"
                        except:
                            if decision_chart[deficit] == 1:
                                play = team_in_poss.name + " XPA"
                            else:
                                play = team_in_poss.name + " 2PA"
                    else:
                        if opposition.points - team_in_poss.points >= 17:
                            play = team_in_poss.name + " 2PA" # Go for 2 when down a lot
                        else:
                            play = team_in_poss.name + " XPA"
            elif safety_kick == True: # safety just occurred
                play = team_in_poss.name + " SAFETY KICK" # next play should be a safety kick
            else:                    
                data_list_off = list() # downs data list for offense
                data_list_def = list() # downs data list for defense
                distance_index = 0
                if distance <= 10 and distance > 5:
                    distance_index = 1
                elif distance <= 5:
                    distance_index = 2
                if down == 1:
                    data_list_off = team_in_poss.off_fd[distance_index]
                    data_list_def = opposition.def_fd[distance_index]
                elif down == 2:
                    data_list_off = team_in_poss.off_sd[distance_index]
                    data_list_def = opposition.def_sd[distance_index]
                else:
                    data_list_off = team_in_poss.off_td[distance_index]
                    data_list_def = opposition.def_td[distance_index]
                rush_ratio = (data_list_off[0] + data_list_def[0]) / (data_list_off[0] + data_list_def[0] + data_list_off[1] + data_list_def[1]) # chance of rushing in this spot
                if team_in_poss.points > opposition.points and (t < 180): # in a run-first situation
                    # Subjectively update chance of rushing based on situation                                        
                    if down == 1:
                        rush_ratio = 0.9
                    elif down == 2:
                        if distance > 10:
                            rush_ratio *= 1.3
                        else:
                            if distance <= 5:
                                rush_ratio = 1
                            else:
                                rush_ratio = 0.9
                    elif down == 3:
                        if distance <= 3:
                            rush_ratio = 1
                        else:
                            if t < 60 and opposition.timeouts == 0:
                                if yards_to_endzone <= 65:
                                    rush_ratio = 1
                                else:
                                    rush_ratio = 0.8
                            else:
                                rush_ratio *= 0.8
                elif opposition.points - team_in_poss.points > 16: # in a pass-first situation
                    # Subjectively update chance of running based on situation
                    if t >= 900:
                        rush_ratio *= 0.5
                    else:
                        if t >= 420:
                            rush_ratio *= 0.2
                        else:
                            if t <= 240:
                                if distance >= 2:
                                    rush_ratio = 0
                                else:
                                    if yards_to_endzone != 1:                                            
                                        rush_ratio *= 0.1
                            else:
                                rush_ratio *= 0.1
                elif opposition.points - team_in_poss.points > 8 and opposition.points - team_in_poss.points <= 16: # Virtually have to pass
                    if t <= 180:
                        if distance >= 2:
                            rush_ratio = 0
                        else:
                            if yards_to_endzone != 1:
                                rush_ratio *= 0.1
                if rd.random() <= rush_ratio: # will run the ball
                    play = team_in_poss.name + " R"
                else:
                    play = team_in_poss.name + " P"
                if check_kneel_scenario(t, team_in_poss, opposition) == True: # offense can kneel
                    if yards_to_endzone == 99: # on own 1 yard line
                        play = team_in_poss.name + " SNEAK" # have to sneak (can't kneel, would be a safety)
                    else:
                        play = team_in_poss.name + " KNEEL" # can kneel
                if (hurry_up == True) and (clock_running == True): # may need to spike
                    # play should be a spike depending on time left and timeouts
                    if (t <= 45) or (t <= 1845):
                        if down == 1:
                            if team_in_poss.timeouts == 0:
                                play = team_in_poss.name + " SPIKE"
                            elif team_in_poss.timeouts == 1:
                                if rd.random() <= 0.5:
                                    play = team_in_poss.name + " SPIKE"
                        elif down == 2 or down == 3:
                            if team_in_poss.timeouts == 0:
                                if t <= 10:
                                    play = team_in_poss.name + " SPIKE"
        else: # 4th down                
            if yards_to_endzone >= 65: # well inside own half
                if t >= 600: # more than 10 minutes left
                    play = team_in_poss.name + " PT" # have to punt
                else: # less than 10 minutes left
                    if t >= 360:
                        if distance <= 5 and opposition.points - team_in_poss.points >= 14 and yards_to_endzone <= 75:
                            play = get_fourth_down_play(team_in_poss, opposition)
                        else:
                            play = team_in_poss.name + " PT"
                    else:
                        if team_in_poss.points >= opposition.points:
                            play = team_in_poss.name + " PT"
                        else:                                
                            if distance <= 5 and opposition.points - team_in_poss.points >= 14 and yards_to_endzone <= 75:
                                play = get_fourth_down_play(team_in_poss, opposition)
                            elif t <= 120 and team_in_poss.timeouts < 3:
                                play = get_fourth_down_play(team_in_poss, opposition)
                            elif team_in_poss.timeouts == 3 and (t <= 120 and t >= 60) and distance > 10 and opposition.points - team_in_poss.points <= 8:
                                play = team_in_poss.name + " PT"
                            else:
                                play = get_fourth_down_play(team_in_poss, opposition)
            elif (yards_to_endzone >= 43 and yards_to_endzone < 65): # in range to potentially go for it on 4th down
                if t >= 600:
                    if yards_to_endzone <= 50 and distance <= 6:
                        play = choose_punt_or_fourth_down(team_in_poss, 0.1 + (6 - distance) * 0.02)
                    else:                            
                        play = team_in_poss.name + " PT"
                else:
                    if t >= 360:                            
                        if team_in_poss.points - opposition.points >= 0:
                            if distance <= 2:                
                                play = choose_punt_or_fourth_down(team_in_poss, 0.01 + (2 - distance) * 0.01)
                            else:
                                play = team_in_poss.name + " PT"
                        else:
                            if opposition.points - team_in_poss.points <= 8:
                                play = team_in_poss.name + " PT"
                            else:                                    
                                if distance <= 6:
                                    play = choose_punt_or_fourth_down(team_in_poss, 0.3 + (6 - distance) * 0.02)
                                else:
                                    if opposition.points - team_in_poss.points >= 16:
                                        play = choose_punt_or_fourth_down(team_in_poss, 0.4 + (10 - distance) * 0.02)
                                    else:
                                        play = team_in_poss.name + " PT"
                    else:
                        if team_in_poss.points - opposition.points >= 0:
                            if distance <= 2:
                                per = 0.3 + (2 - distance) * 0.1 if (opposition.timeouts == 0 and t <= 160) else 0.01 + (2 - distance) * 0.01
                                play = choose_punt_or_fourth_down(team_in_poss, per)
                            else:
                                play = team_in_poss.name + " PT"
                        else:
                            if ((t >= 300 and team_in_poss.timeouts >= 2) or (t >= 120 and team_in_poss.timeouts == 3)) and opposition.points - team_in_poss.points <= 8 and opposition.points - team_in_poss.points >= 0:
                                if distance <= 3:
                                    per = 0.4 + (3 - distance) * 0.05
                                    play = choose_punt_or_fourth_down(team_in_poss, per)
                                else:
                                    play = team_in_poss.name + " PT"
                            else:
                                play = get_fourth_down_play(team_in_poss, opposition)
            else: # in field goal range
                if t >= 600:
                    if yards_to_endzone >= 40:
                        if distance <= 5:
                            if rd.random() <= 0.3 + (5 - distance) * 0.02:
                                play = get_fourth_down_play(team_in_poss, opposition)
                            else:
                                play = team_in_poss.name + " FG"
                        else:
                            play = team_in_poss.name + " FG"
                    else:
                        if yards_to_endzone == 1:
                            play = get_fourth_down_play(team_in_poss, opposition)
                        else:
                            play = team_in_poss.name + " FG"
                else:
                    if t >= 360:
                        if distance <= 5:
                            if opposition.points - team_in_poss.points <= 11 and opposition.points - team_in_poss.points >= 0:
                                if rd.random() <= 0.4 + (5 - distance) * 0.02:
                                    play = get_fourth_down_play(team_in_poss, opposition)
                                else:
                                    play = team_in_poss.name + " FG"
                            elif yards_to_endzone == 1:
                                if opposition.points - team_in_poss.points > 16:
                                    play = get_fourth_down_play(team_in_poss, opposition)
                                elif team_in_poss.points == opposition.points:
                                    if rd.random() <= 0.35:
                                        play = get_fourth_down_play(team_in_poss, opposition)
                                    else:
                                        play = team_in_poss.name + " FG"
                                elif opposition.points - team_in_poss.points == 3:
                                    play = team_in_poss.name + " FG"
                                else:
                                    play = get_fourth_down_play(team_in_poss, opposition)
                            else:
                                play = get_fourth_down_play(team_in_poss, opposition)
                        else:
                            play = team_in_poss.name + " FG"
                    else:
                        if distance <= 3 and yards_to_endzone >= 40 and t >= 30:
                            if rd.random() <= 0.5:
                                play = get_fourth_down_play(team_in_poss, opposition)
                            else:
                                play = team_in_poss.name + " FG"
                        else:
                            if opposition.points - team_in_poss.points <= 3 and opposition.points - team_in_poss.points > 0:
                                if yards_to_endzone != 1:
                                    play = team_in_poss.name + " FG"
                                else:
                                    if rd.random() <= 0.05:
                                        play = get_fourth_down_play(team_in_poss, opposition)
                                    else:
                                        play = team_in_poss.name + " FG"
                            else:
                                if opposition.points - team_in_poss.points <= 8 and opposition.points > team_in_poss.points:
                                    if t <= 120:
                                        play = get_fourth_down_play(team_in_poss, opposition)
                                    else:
                                        if team_in_poss.timeouts >= 2:
                                            per = 0.5 + (5 - distance) * 0.05 if distance <= 10 else 0 
                                            if rd.random() <= per:
                                                play = get_fourth_down_play(team_in_poss, opposition)
                                            else:
                                                play = team_in_poss.name + " FG"
                                        else:
                                            play = get_fourth_down_play(team_in_poss, opposition)
                                elif team_in_poss.points >= opposition.points:
                                    play = team_in_poss.name + " FG"
                                else:
                                    play = get_fourth_down_play(team_in_poss, opposition)
        if overtime == True: # game in overtime
            if sudden_death == True: # game in sudden death
                if down == 4 and team_in_poss.points < opposition.points: # offense is losing, and its 4th down
                    if yards_to_endzone > 45: # not in field goal range
                        play = get_fourth_down_play(team_in_poss, opposition) # have to go for it on 4th down
                    else:
                        # don't need to check if points deficit is 3 points - it must be if game is still in play
                        if distance >= 8:
                            if yards_to_endzone >= 43:
                                play = team_in_poss.name + " FG" if rd.random() <= 0.5 else get_fourth_down_play(team_in_poss, opposition)
                            else:
                                play = team_in_poss.name + " FG"
                        else:
                            if distance <= 3 and yards_to_endzone >= 43:
                                play = team_in_poss.name + " FG" if rd.random() <= 0.3 else get_fourth_down_play(team_in_poss, opposition)
                            else:
                                play = team_in_poss.name + " FG"
                elif down == 4 and team_in_poss.points == opposition.points: # game tied and its 4th down
                    if yards_to_endzone <= 45:
                        if distance >= 8:
                            if yards_to_endzone >= 43:                                
                                play = team_in_poss.name + " FG" if rd.random() <= 0.5 else team_in_poss.name + " PT" # 50-50 field goal or punt
                            else:
                                play = team_in_poss.name + " FG"
                        else:
                            if yards_to_endzone >= 40:
                                if distance <= 2:                                        
                                    play = get_fourth_down_play(team_in_poss, opposition) if rd.random() <= 0.3 else team_in_poss.name + " FG"
                                else:
                                    play = team_in_poss.name + " FG" if rd.random() <= 0.5 else team_in_poss.name + " PT"
                            else:
                                play = team_in_poss.name + " FG"
                    else:
                        play = team_in_poss.name + " PT"
                elif down <= 3 and team_in_poss.points == opposition.points: # 1st, 2nd, or 3rd down, game is tied
                    if yards_to_endzone < 43: # in field goal range
                        if yards_to_endzone >= 35:
                            play = team_in_poss.name + " R" if t >= 30 else team_in_poss.name + " FG"
                        else:
                            if down <= 2 and yards_to_endzone >= 30:
                                play = team_in_poss.name + " R" if t >= 30 else team_in_poss.name + " FG"
                            else:                                
                                play = team_in_poss.name + " FG"
    return play
        
def get_play_result(play, t, down, distance, yards_to_endzone, team_in_poss, opposition):
    '''
    Method to get the play result from a play.
    param play: the play type.
    param down: the current down.
    param distance: yardage needed for a 1st down/touchdown.
    param yards_to_endzone: yardage needed for a touchdown.
    param team_in_poss: the offense.
    param opposition: the defense.
    '''
    def check_pre_snap_penalty(team_in_poss, opposition):
        '''
        Method to check for a pre-snap penalty, and return the penalty.
        param team_in_poss: the offense.
        param opposition: the offense.
        '''
        if rd.random() <= team_in_poss.fst_per: # random float in [0, 1] is less than proportion of false starts by offense
            return "FST" # false start penalty
        if rd.random() <= opposition.offs_per: # random float in [0, 1] is less than proportion of offsides by defense
            return "OFFS" # offside penalty
        return None # no penalty
    def check_after_snap_penalty(team_in_poss, opposition, play_type):
        '''
        Method to check for a post-snap penalty.
        param team_in_poss: the offense.
        param opposition: the defense.
        param play_type: the type of play. Important as some penalties are not possible with some play types.
        '''
        asp = "OFFHOLD " if rd.random() <= team_in_poss.off_hold_per else "" # offensive hold can be on a run or pass
        asp = asp + "DEFHOLD " if rd.random() <= opposition.def_hold_per else asp # defensive hold can be on a run or pass
        if "P " in play_type: # pass play                
            if "SACK" not in play_type:
                asp = asp + "DPI " if rd.random() <= opposition.dpi_per else asp
                asp = asp + "OPI " if rd.random() <= team_in_poss.opi_per else asp
            if "IC" in play_type:
                asp = asp + "INTG " if rd.random() <= team_in_poss.intg_per else asp
        return asp # Return sequence of post-snap penalties, or "" if there were none

    def get_random_variate(distribution_data, play_type):
        '''
        Method to get a random variable from a distribution, primarily for a yardage gain.
        param distribution_data: the name of the distribution, along with its parameters.
        play_type: pass or a run
        '''
        # Get average of 5 random variables sampled from the distribution for a pass play. Gives more accurate results for game stats.
        # Get 1 random variable sampled from the distribution for a run play.        
        if distribution_data[0] == "F":
            return np.mean(stat.f.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3], size=5)) if play_type == "P" else stat.f.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3])
        elif distribution_data[0] == "JSB":
            return np.mean(stat.johnsonsb.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3], size=5)) if play_type == "P" else stat.johnsonsb.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3]) 
        elif distribution_data[0] == "JSU":
            return np.mean(stat.johnsonsu.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3], size=5)) if play_type == "P" else stat.johnsonsu.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3])
        elif distribution_data[0] == "N":
            return np.mean(stat.norm.rvs(loc=distribution_data[1][0], scale=distribution_data[1][1], size=5)) if play_type == "P" else stat.norm.rvs(loc=distribution_data[1][0], scale=distribution_data[1][1])
        elif distribution_data[0] == "NIG":
            return np.mean(stat.norminvgauss.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3], size=5)) if play_type == "P" else stat.norminvgauss.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3])
        elif distribution_data[0] == "NCT":
            return np.mean(stat.nct.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3], size=5)) if play_type == "P" else stat.nct.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3])
        elif distribution_data[0] == "EXN":
            return np.mean(stat.exponnorm.rvs(distribution_data[1][0], loc=distribution_data[1][1], scale=distribution_data[1][2], size=5)) if play_type == "P" else stat.exponnorm.rvs(distribution_data[1][0], loc=distribution_data[1][1], scale=distribution_data[1][2])
        else:
            return np.mean(stat.mielke.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3], size=5)) if play_type == "P" else stat.mielke.rvs(distribution_data[1][0], distribution_data[1][1], loc=distribution_data[1][2], scale=distribution_data[1][3])
    
    play_result = ""
    if "KO" in play: # play was a kickoff            
        if rd.random() <= team_in_poss.kotb_per: # result should be a touchback
            play_result = team_in_poss.name + " KOTB" 
        else: # result should be a kickoff return
            ko_distance = team_in_poss.kod[rd.randint(0, len(team_in_poss.kod) - 1)]
            return_yards = int((opposition.korm[rd.randint(0, len(opposition.korm) - 1)] + team_in_poss.kora[rd.randint(0, len(team_in_poss.kora) - 1)]) / 2)
            play_result = team_in_poss.name + " KO " + str(ko_distance) + "YDS " + str(return_yards) + "RET"
            if 100 - (65 - ko_distance + return_yards) <= 0: # return went for a touchdown
                play_result += " DEF TD" # defensive touchdown
                opposition.game_stats["FPTS"] += 6
                team_in_poss.game_stats["DefPTSA"] += 6
    elif " P" in play and " PT" not in play: # play was a pass
        psp = check_pre_snap_penalty(team_in_poss, opposition) # get any pre-snap penalties
        if psp == None: # no pre-snap penalties
            touchdown = False
            sack_per = ((team_in_poss.sacks_allowed / team_in_poss.off_pass_attempts) + (opposition.sacks_got / opposition.def_pass_attempts)) / 2 # chance of a sack
            sack = True if rd.random() <= sack_per else False # play result is a sack if sack is True
            fmbl_per = ((team_in_poss.fmbl / team_in_poss.tot_off_plays) + (opposition.fmbl_got / opposition.tot_def_plays)) / 2 # chance of a fumble
            if sack == True: # there was a sack
                asp = check_after_snap_penalty(team_in_poss, opposition, "P SACK") # get any post-snap penalties
                yardage_lost = int(get_random_variate(["N", [6.5, 2]], "SACK")) # yardage lost from sack
                fmbl = True if rd.random() <= fmbl_per else False # play result is a sack fumble if fmbl is True
                if asp == "": # no post-snap penalties
                    if yardage_lost >= (100 - yards_to_endzone): # play ended in own endzone
                        if fmbl == True:
                            play_result = team_in_poss.name + " P SACK FMBL DEF TD" # fumble recovered by defense in the endzone
                        else:                                
                            play_result = team_in_poss.name + " P SACK SAFETY" # sack in the endzone, safety
                    else: # play ended on the field of play
                        if fmbl == True:
                            play_result = team_in_poss.name + " P SACK " + str(yardage_lost) + "YDS FMBL" # sack fumble
                        else:
                            play_result = team_in_poss.name + " P SACK " + str(yardage_lost) + "YDS" # regular sack
                else: # there was at least 1 post-snap penalty
                    # offensive and defensive hold are the only 2 penalties the algorithm considers that can occur on a sack
                    if "OFFHOLD" in asp and "DEFHOLD" in asp: # offsetting penalties
                        play_result = "PEN OFFSETTING"
                    else:
                        if "DEFHOLD" in asp:                                
                            play_result = "PEN DEFHOLD"
                        elif "OFFHOLD" in asp:
                            if down == 4 or yardage_lost > 5 or fmbl == True: # penalty should be declined
                                play_result = team_in_poss.name + " P SACK " + str(yardage_lost) + "YDS" if fmbl == False else team_in_poss.name + " P SACK " + str(yardage_lost) + "YDS FMBL"
                            else: # penalty accepted
                                play_result = "PEN OFFHOLD"
                # update some game stats
                if "SACK" in play_result:
                    opposition.game_stats["FPTS"] += 1
                if "SAFETY" in play_result:
                    opposition.game_stats["FPTS"] += 2
                if "FMBL" in play_result:
                    opposition.game_stats["FPTS"] += 2
                    team_in_poss.players["QBs"][0].game_stats["FMBLs"] += 1
                if "DEF TD" in play_result:
                    opposition.game_stats["FPTS"] += 6
            else: # there was a pass attempt
                yardage = round(get_random_variate(team_in_poss.pass_yards_dist, "P")) # yardage gained
                depth = 0 # integer indicating the depth index needed to select a receiver, default to a "short" pass play
                if yardage >= 20: # deep pass play
                    depth = 2
                receiver = team_in_poss.select_receiver(int(0.5 * depth), yards_to_endzone) # select the targeted receiver based on pre-defined probabilities
                comp_per = ((team_in_poss.off_target_depth_data[depth + 1] / team_in_poss.off_target_depth_data[depth]) + (opposition.def_target_depth_data[depth + 1] / opposition.def_target_depth_data[depth])) / 2 # chance of a completion
                completion = True if rd.random() <= comp_per else False
                if completion == True: # pass completion
                    asp = check_after_snap_penalty(team_in_poss, opposition, "P C") # get any post-snap penalties
                    fmbl = True if rd.random() <= fmbl_per else False
                    if fmbl == True and yardage < yards_to_endzone: # fumble occurred on the field of play                            
                        if yardage + 100 - yards_to_endzone <= 0:
                            play_result = team_in_poss.name + " P " + str(yards_to_endzone - 100) + "YDS DEF TD"
                        else:
                            if yardage >= yards_to_endzone:
                                yardage = yards_to_endzone - 1
                            play_result = team_in_poss.name + " P " + str(yardage) + "YDS FMBL"
                        if asp != "": # there were some post-snap penalties
                            if ("DEFHOLD" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)) or ("DPI" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)):
                                play_result = "PEN OFFSETTING"
                            elif "DPI" in play_result:
                                play_result = "PEN DPI " + str(yardage) + "YDS"
                            elif "DEFHOLD" in play_result:
                                play_result = "PEN DEFHOLD"
                        # update some game stats
                        if "FMBL" in play_result:                            
                            receiver.game_stats["FMBLs"] += 1
                            receiver.game_stats["RecYDs"] += yardage
                            team_in_poss.players["QBs"][0].game_stats["PATTs"] += 1
                            team_in_poss.players["QBs"][0].game_stats["PCOMPs"] += 1
                            team_in_poss.players["QBs"][0].game_stats["PYDs"] += yardage
                        if "DEF TD" in play_result:
                            opposition.game_stats["FPTS"] += 6
                    else: # fumble did not occur (fumble in the endzone not counted as a fumble)                            
                        if yardage >= yards_to_endzone: # yardage gained was greater than that needed for a touchdown
                            yardage = yards_to_endzone # set yardage gained to yards_to_endzone
                            touchdown = True # touchdown scored
                        play_result = team_in_poss.name + " P " + str(yardage) + "YDS" if touchdown == False else team_in_poss.name + " P " + str(yardage) + "YDS TD"
                        if asp != "": # post-snap penalties
                            if ("DEFHOLD" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)) or ("DPI" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)):
                                play_result = "PEN OFFSETTING"
                            elif "OPI" in asp:
                                play_result = "PEN OPI"
                            elif "OFFHOLD" in asp:
                                if down != 4:
                                    play_result = "PEN OFFHOLD"
                        if yardage + 100 - yards_to_endzone <= 0:
                            play_result = team_in_poss.name + " P " + str(yards_to_endzone - 100) + "YDS SAFETY"
                            if asp != "":
                                if ("DEFHOLD" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)) or ("DPI" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)):
                                    play_result = "PEN OFFSETTING"
                                elif "DPI" in play_result:
                                    play_result = "PEN DPI " + str(yardage) + "YDS"
                                elif "DEFHOLD" in play_result:
                                    play_result = "PEN DEFHOLD"
                        if "PEN" not in play_result: # no penalty, update some game stats
                            receiver.game_stats["RecYDs"] += yardage
                            team_in_poss.players["QBs"][0].game_stats["PATTs"] += 1
                            team_in_poss.players["QBs"][0].game_stats["PCOMPs"] += 1
                            team_in_poss.players["QBs"][0].game_stats["PYDs"] += yardage
                            if "TD" in play_result:
                                receiver.game_stats["RecTDs"] += 1
                                team_in_poss.players["QBs"][0].game_stats["PTDs"] += 1
                                opposition.game_stats["DefPTSA"] += 6
                    if "PEN" not in play_result:
                        receiver.game_stats["Rec"] += 1
                else: # incomplete pass
                    int_per = ((team_in_poss.off_target_depth_data[int(0.5 * depth + 4)] / team_in_poss.off_target_depth_data[depth]) + (opposition.def_target_depth_data[int(0.5 * depth + 4)] / opposition.def_target_depth_data[depth]))
                    interception = True if rd.random() <= int_per else False
                    if interception == True:
                        asp = check_after_snap_penalty(team_in_poss, opposition, "P INT")
                        if yardage >= yards_to_endzone:
                            play_result = team_in_poss.name + " P INT TB"
                        else:
                            if yards_to_endzone - yardage >= 100:                                    
                                play_result = team_in_poss.name + " P " + str(yardage) + "YDS INT DEF TD"
                            else:
                                play_result = team_in_poss.name + " P " + str(yardage) + "YDS INT"
                        if asp != "":
                            if ("DEFHOLD" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)) or ("DPI" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)):
                                play_result = "PEN OFFSETTING"                                                                                                        
                            elif "DEFHOLD" in asp:
                                play_result = "PEN DEFHOLD"
                            elif "DPI" in asp:
                                play_result = "PEN DPI " + str(yardage) + "YDS"
                        if "INT" in play_result:
                            team_in_poss.players["QBs"][0].game_stats["INTs"] += 1
                            team_in_poss.players["QBs"][0].game_stats["PATTs"] += 1
                            opposition.game_stats["FPTS"] += 2
                            if "DEF TD" in play_result:
                                opposition.game_stats["FPTS"] += 6
                    else:
                        asp = check_after_snap_penalty(team_in_poss, opposition, "P IC")                
                        play_result = team_in_poss.name + " P IC"
                        if asp != "":
                            if ("DEFHOLD" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)) or ("DPI" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)):
                                play_result = "PEN OFFSETTING"                                                                                                
                            elif "OFFHOLD" in asp:
                                if down != 4:
                                    if yards_to_endzone < 90:
                                        play_result = "PEN OFFHOLD"
                            elif "OPI" in asp:
                                if down != 4:
                                    if yards_to_endzone < 90:
                                        play_result = "PEN OPI"
                            elif "INTG" in asp:
                                play_result = "PEN INTG"
                            elif "DEFHOLD" in asp:
                                play_result = "PEN DEFHOLD"                                
                            elif "DPI" in asp:
                                play_result = "PEN DPI " + str(yardage) + "YDS" if yardage < yards_to_endzone else "PEN DPI " + str(yards_to_endzone - 1) + "YDS"                               
                        if "P IC" in play_result:
                            team_in_poss.players["QBs"][0].game_stats["PATTs"] += 1
        else: # pre-snap penalty occurred
            play_result = "PEN " + psp
    elif " R" in play: # play was a run play
        psp = check_pre_snap_penalty(team_in_poss, opposition)
        rusher = team_in_poss.select_rusher(down, yards_to_endzone)
        if psp == None:
            touchdown = False
            fmbl_per = ((team_in_poss.fmbl / team_in_poss.tot_off_plays) + (opposition.fmbl_got / opposition.tot_def_plays)) / 2
            yardage = round(get_random_variate(team_in_poss.rush_yards_dist, "R") * (1 - 0.1 * (team_in_poss.avg_rush_yards - opposition.avg_rush_yards_against)))
            fmbl = True if rd.random() <= fmbl_per else False
            if fmbl == True:
                asp = check_after_snap_penalty(team_in_poss, opposition, "R FMBL")                                                                                                            
                if yardage >= yards_to_endzone:
                    yardage = yards_to_endzone - 1
                play_result = team_in_poss.name + " R " + str(yardage) + "YDS FMBL"
                if yardage + 100 - yards_to_endzone <= 0:
                    play_result = team_in_poss.name + " R " + str(yards_to_endzone - 100) + "YDS DEF TD"
                if asp != "":
                    if "OFFHOLD" in asp and "DEFHOLD" in asp:
                        play_result = "PEN OFFSETTING"                                                                                                        
                    elif "DEFHOLD" in asp:
                        play_result = "PEN DEFHOLD"
                if "PEN" not in play_result:
                    opposition.game_stats["FPTS"] += 2
                    rusher.game_stats["FMBLs"] += 1
                    rusher.game_stats["RYDs"] += yardage
                    if "DEF TD" in play_result:
                        opposition.game_stats["FPTS"] += 6
            else:
                asp = check_after_snap_penalty(team_in_poss, opposition, "R")                                                                                                                
                if yardage >= yards_to_endzone:
                    yardage = yards_to_endzone
                    touchdown = True
                play_result = team_in_poss.name + " R " + str(yardage) + "YDS" if touchdown == False else team_in_poss.name + " R " + str(yardage) + "YDS TD"                    
                if asp != "":
                    if "OFFHOLD" in asp and "DEFHOLD" in asp:
                        play_result = "PEN OFFSETTING"                                                                                                        
                    elif "OFFHOLD" in asp:
                        if down != 4:                                                                                                                                    
                            play_result = "PEN OFFHOLD"
                        else:
                            if yardage >= distance:
                                play_result = "PEN OFFHOLD"
                if yardage + 100 - yards_to_endzone <= 0:
                    play_result = team_in_poss.name + " R " + str(yards_to_endzone - 100) + "YDS SAFETY"
                    if asp != "":
                        if asp != "":
                            if ("DEFHOLD" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)) or ("DPI" in asp and ("OFFHOLD" in asp or "OPI" in asp or "INTG" in asp)):
                                play_result = "PEN OFFSETTING"
                            elif "DPI" in play_result:
                                play_result = "PEN DPI " + str(yardage) + "YDS"
                            elif "DEFHOLD" in play_result:
                                play_result = "PEN DEFHOLD"
                if "PEN" not in play_result:
                    rusher.game_stats["RYDs"] += yardage
                    if "TD" in play_result:
                        rusher.game_stats["RTDs"] += 1
                        opposition.game_stats["DefPTSA"] += 6
                    if "SAFETY" in play_result:
                        opposition.game_stats["FPTS"] += 2
            if "PEN" not in play_result:
                rusher.game_stats["RATTs"] += 1
        else:
            play_result = "PEN " + psp
    elif "2PA" in play: # play was a 2 point try
        play_type = "P" if rd.random() <= 0.7 else "R" # league proportion of pass play vs. rush play on 2 point try
        player = team_in_poss.select_receiver(0, 2) if play_type == "P" else team_in_poss.select_rusher(3, 2) # get receiver/rusher
        play_result = team_in_poss.name + " 2PS" if rd.random() <= team_in_poss.two_pm_per else team_in_poss.name + " 2PF" # 2 point try sucessful if random float in [0, 1] in correct range
        if "2PS" in play_result:
            opposition.game_stats["DefPTSA"] += 2
            if play_type == "P":
                team_in_poss.players["QBs"][0].game_stats["2PCs"] += 1
            player.game_stats["2PCs"] += 1
    elif "XPA" in play: # play was an extra point
        team_in_poss.players["Ks"][0].game_stats["XPA"] += 1
        play_result = team_in_poss.name + " XPS" if rd.random() <= team_in_poss.xpm_per else team_in_poss.name + " XPF"
        if "XPS" in play_result:
            team_in_poss.players["Ks"][0].game_stats["XPM"] += 1
            opposition.game_stats["DefPTSA"] += 1
    elif "HAILMARY" in play: # play was a hail mary
        # 1% chance of converting a hail mary in general
        play_result = team_in_poss.name + " P " + str(yards_to_endzone) + "YDS TD" if rd.random() <= 0.01 else team_in_poss.name + " P IC" 
        team_in_poss.players["QBs"][0].game_stats["PATTs"] += 1
        if "TD" in play_result:
            team_in_poss.players["QBs"][0].game_stats["PCOMPs"] += 1
            team_in_poss.players["QBs"][0].game_stats["PYDs"] += yards_to_endzone
            team_in_poss.players["QBs"][0].game_stats["PTDs"] += 1
            receiver = team_in_poss.select_receiver(1, yards_to_endzone)
            receiver.game_stats["Rec"] += 1
            receiver.game_stats["RecYDs"] += yards_to_endzone
            receiver.game_stats["RecTDs"] += 1
            opposition.game_stats["DefPTSA"] += 6
    elif "PT" in play or "SAFETY KICK" in play: # punt or a safety kick
        punt_distance = int(team_in_poss.ptd[rd.randint(0, len(team_in_poss.ptd) - 1)]) # random punt distance from punt distance list
        if punt_distance >= yards_to_endzone:
            play_result = team_in_poss.name + " PT TB"
        else:
            punt_return = round((int(team_in_poss.ptra[rd.randint(0, len(team_in_poss.ptra) - 1)]) + int(opposition.ptrm[rd.randint(0, len(opposition.ptrm) - 1)])) / 2) # random punt return from offense and defense lists
            play_result = team_in_poss.name + " PT " + str(punt_distance) + "YDS " + str(punt_return) + "RET"
            if 100 - (yards_to_endzone - punt_distance + punt_return) <= 0: # return went for a touchdown
                play_result += " DEF TD"
                opposition.game_stats["FPTS"] += 6
                team_in_poss.game_stats["DefPTSA"] += 6
        if "SAFETY KICK" in play:
            play_result += " SAFETY KICK" # program knows punt was from a safety kick, so that it sets safety_kick variable to False
    elif "4DA" in play: # 4th down attempts
        per = (team_in_poss.ofod_m / team_in_poss.ofod_a) + (5 - distance) * 0.02 # subjective probability of converting, changes with distance
        if rd.random() <= per: # 4th down converted                    
            if distance == 1: # needed 1 yard - make it a rushing play
                rusher = team_in_poss.select_rusher(3, yards_to_endzone)
                play_result = team_in_poss.name + " R 1YDS TD" if distance == yards_to_endzone else team_in_poss.name + " R 1YDS" 
                rusher.game_stats["RATTs"] += 1
                rusher.game_stats["RYDs"] += 1
                if "TD" in play_result:
                    rusher.game_stats["RTDs"] += 1
                    opposition.game_stats["DefPTSA"] += 6
            else: # needed more than 1 yard - make it a passing play
                depth_index = 0 if distance < 20 else 1
                receiver = team_in_poss.select_receiver(depth_index, yards_to_endzone)
                play_result = team_in_poss.name + " P " + str(distance) + "YDS TD" if distance == yards_to_endzone else team_in_poss.name + " P " + str(distance) + "YDS"
                receiver.game_stats["Rec"] += 1
                receiver.game_stats["RecYDs"] += distance
                team_in_poss.players["QBs"][0].game_stats["PCOMPs"] += 1
                team_in_poss.players["QBs"][0].game_stats["PATTs"] += 1
                team_in_poss.players["QBs"][0].game_stats["PYDs"] += distance
                if "TD" in play_result:
                    receiver.game_stats["RecTDs"] += 1
                    team_in_poss.players["QBs"][0].game_stats["PTDs"] += 1
                    opposition.game_stats["DefPTSA"] += 6
        else: # 4th down not converted
            if distance == 1:
                rusher = team_in_poss.select_rusher(3, yards_to_endzone)
                rusher.game_stats["RATTs"] += 1
                play_result = team_in_poss.name + " R 0YDS"
            else:
                team_in_poss.players["QBs"][0].game_stats["PATTs"] += 1
                play_result = team_in_poss.name + " P IC"
    elif "FG" in play: # field goal
        fg_distance = yards_to_endzone + 18 # get field goal distance
        # get relevant probability, and test it
        if fg_distance < 40:
            play_result = team_in_poss.name + " FGS" if rd.random() <= team_in_poss.fgm_40_per else team_in_poss.name + " FGF"
            team_in_poss.players["Ks"][0].game_stats["FG50-A"] += 1
            if "FGS" in play_result:
                team_in_poss.players["Ks"][0].game_stats["FG50-M"] += 1
        elif fg_distance >= 40 and fg_distance <= 49:
            play_result = team_in_poss.name + " FGS" if rd.random() <= team_in_poss.fgm_50_per else team_in_poss.name + " FGF"
            team_in_poss.players["Ks"][0].game_stats["FG50-A"] += 1
            if "FGS" in play_result:
                team_in_poss.players["Ks"][0].game_stats["FG50-M"] += 1
        elif fg_distance >= 50 and fg_distance <= 59:
            play_result = team_in_poss.name + " FGS" if rd.random() <= team_in_poss.fgm_60_per else team_in_poss.name + " FGF"
            team_in_poss.players["Ks"][0].game_stats["FG50+A"] += 1
            if "FGS" in play_result:
                team_in_poss.players["Ks"][0].game_stats["FG50+M"] += 1
        else:
            play_result = team_in_poss.name + " FGS" if rd.random() <= team_in_poss.fgm_70_per else team_in_poss.name + " FGF"
            team_in_poss.players["Ks"][0].game_stats["FG50+A"] += 1
            if "FGS" in play_result:
                team_in_poss.players["Ks"][0].game_stats["FG50+M"] += 1
        if "FGS" in play_result:
            opposition.game_stats["DefPTSA"] += 3
    elif "SPIKE" in play: # QB spiked the ball
        play_result = team_in_poss.name + " P IC"
        team_in_poss.players["QBs"][0].game_stats["PATTs"] += 1
    elif " KNEEL" in play: # QB knelt
        play_result = team_in_poss.name + " R -1YDS"
        team_in_poss.players["QBs"][0].game_stats["RATTs"] += 1
        team_in_poss.players["QBs"][0].game_stats["RYDs"] -= 1
    elif " ONSIDE KICK" in play: # onside kick
        # league proportion of onside kicks converted
        play_result = team_in_poss.name + " ONSIDE KICK FAIL" if rd.random() > (3 / 71) else team_in_poss.name + " ONSIDE KICK RECOVERED"
    elif "SNEAK" in play: # QB sneaked
        play_result = team_in_poss.name + " R 1YDS"
        team_in_poss.players["QBs"][0].game_stats["RATTs"] += 1
        team_in_poss.players["QBs"][0].game_stats["RYDs"] += 1
    return play_result

def get_updated_variables(play_result, t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, td_play, kickoff, safety_kick, hurry_up):
    '''
    Method to update variables based on a play result.
    param play_result: the result of the play.
    param t: time left.
    param down: the current down.
    param distance: the yardage needed for a 1st down/touchdown.
    param yards_to_endzone: the yardage needed for a touchdown.
    param team_in_poss: the offense.
    param opposition: the defense.
    param clock_running: boolean specifying if game clock is running or not.
    param td_play: boolean specifying if a touchdown just occurred.
    param kickoff: boolean specifying if the play should be a kickoff.
    param safety_kick: boolean specifying if a safety just occurred.
    param hurry_up: boolean specifying if offense is in hurry-up.
    '''
    def update_variables_after_turnover(play_result, updated_variables, yardage=0): 
        '''
        Method to update variables after a turnover.
        param play_result: the result of the play.
        param updated_variables: a dictionary containing the base variables needing to be updated.
        param yardage: yardage gained on the play by current offense (team that turned the ball over). Defaults to 0.
        '''          
        updated_variables["yards_to_endzone"] = 100 - yards_to_endzone + yardage # swap field position
        if "INT" in play_result:
            team_in_poss.game_stats["INTs"] += 1
        elif "FMBL" in play_result:
            team_in_poss.game_stats["FMBLs"] += 1
            if " P " in play_result and "SACK" not in play_result:
                team_in_poss.game_stats["PCOMPs"] += 1
                team_in_poss.game_stats["PYDs"] += yardage
            if " R " in play_result:
                team_in_poss.game_stats["RYDs"] += yardage
        elif " P " in play_result and "IC" not in play_result and "SACK" not in play_result:
            team_in_poss.game_stats["PYDs"] += yardage
            team_in_poss.game_stats["PCOMPs"] += 1
        updated_variables["opposition"] = team_in_poss # swap opposition and team_in_poss
        updated_variables["team_in_poss"] = opposition 
        updated_variables["down"] = 1
        updated_variables["distance"] = 10 if updated_variables["yards_to_endzone"] >= 10 else updated_variables["yards_to_endzone"] # 1st and 10 if not within 10 yards of opposition endzone, else 1st and 6 e.g.
        updated_variables["clock_running"] = False # clock stops
        return updated_variables
    def update_variables_after_successful_run_or_pass_play(yardage, updated_variables):
        '''
        Method to update variables after a successful run or pass play. Successful means no turnover.
        param yardage: the yardage gained on the play.
        pparam updated_variables: a dictionary containing the base variables needing to be updated.
        '''
        updated_variables["yards_to_endzone"] -= yardage # adjust yards to endzone
        if yardage >= distance: # yardage gained was enough for a 1st down
            updated_variables["down"] = 1 # 1st down
            if updated_variables["yards_to_endzone"] < 10: # inside opponents 10 yard line
                updated_variables["distance"] = updated_variables["yards_to_endzone"] # 1st and goal
            else: # outside opponents 10 yard line
                updated_variables["distance"] = 10 # 1st and 10
        else: # yardage gained not enough for a 1st down
            updated_variables["down"] += 1 # down increases
            updated_variables["distance"] -= yardage # adjust distance until first down
        if " P " in play_result: # pass play
            team_in_poss.game_stats["PCOMPs"] += 1
            team_in_poss.game_stats["PYDs"] += yardage
        else: # run play
            team_in_poss.game_stats["RYDs"] += yardage        
        updated_variables["clock_running"] = True # keep clock running            
        return updated_variables
    def update_variables_after_score(play_result, updated_variables, yardage=0):
        '''
        Method to update variables after a score.
        param play_result: the result of the play.
        param updated_variables: a dictionary containing the base variables needing to be updated.
        param yardage: yardage gained on the play by current offense (team that turned the ball over). Defaults to 0.
        '''
        updated_variables["down"] = 1 # reset down
        updated_variables["distance"] = 10 # reset distance
        updated_variables["clock_running"] = False # clock stops after score
        updated_variables["yards_to_endzone"] = 65 # kickoff line
        if "TD" in play_result: # score was a touchdown
            if "DEF TD" in play_result: # score was a defensive touchdown
                opposition.points += 6
                updated_variables["team_in_poss"] = opposition
                updated_variables["opposition"] = team_in_poss
            else: # score was an offensive touchdowns
                team_in_poss.points += 6
                if " P " in play_result:
                    team_in_poss.game_stats["PCOMPs"] += 1
                    team_in_poss.game_stats["PTDs"] += 1                        
                elif " R " in play_result:
                    team_in_poss.game_stats["RTDs"] += 1
            if " P " in play_result:                    
                team_in_poss.game_stats["PYDs"] += yardage
            elif " R " in play_result:                    
                team_in_poss.game_stats["RYDs"] += yardage        
            updated_variables["td_play"] = True # touchdown scored
        elif "FGS" in play_result: # score was a field goal
            team_in_poss.points += 3
            updated_variables["kickoff"] = True # next play should be a kickoff
        elif "XPS" in play_result: # score was an extra point
            team_in_poss.points += 1
            updated_variables["kickoff"] = True
        elif "2PS" in play_result: # score was a 2 point conversion
            team_in_poss.points += 2
            updated_variables["kickoff"] = True
        elif "SAFETY" in play_result: # score was a safety
            opposition.points += 2
            updated_variables["yards_to_endzone"] = 80 # spot of safety kick
            updated_variables["safety_kick"] = True # next play should be a safety kick
            if " R " in play_result:
                team_in_poss.game_stats["RYDs"] += yardage  
        return updated_variables
    # base variables that need to be updated
    updated_variables = {"t": t, "down": down, "distance": distance, "yards_to_endzone": yards_to_endzone, "team_in_poss": team_in_poss, "opposition": opposition, "clock_running": clock_running, "td_play": td_play, "kickoff": kickoff, "safety_kick": safety_kick, "hurry_up": hurry_up}
    time_taken = 0 # time taken for play
    if "KO" in play_result: # play was a kickoff
        updated_variables["kickoff"] = False
        updated_variables["clock_running"] = False    
        updated_variables["opposition"] = team_in_poss # swap teams around
        updated_variables["team_in_poss"] = opposition
        updated_variables["down"] = 1
        updated_variables["distance"] = 10
        if "KOTB" in play_result: # touchback                
            updated_variables["yards_to_endzone"] = 75 # play starts on offense 25
        else:
            ko_distance = int(play_result[play_result.index("YDS") - 2:play_result.index("YDS")])
            ko_return = int(play_result[play_result.index("RET") - 2:play_result.index("RET")])
            if "DEF TD" in play_result: # defensive touchdown
                updated_variables = update_variables_after_score(play_result, updated_variables)
            else: # standard kick return                    
                updated_variables["yards_to_endzone"] = 100 - (65 - ko_distance + ko_return)
            time_taken = round((11 / 40) * ko_return) if ko_return < 40 else round((3 / 20) * ko_return) # Subjective time it takes for the return
            updated_variables["t"] = new_time_left(t, time_taken) # update time left
    elif " P" in play_result and "PT" not in play_result: # play was a pass or a run
        yardage = 0
        try:
            yardage = int(play_result[play_result.index("YDS") - 2:play_result.index("YDS")])
        except:
            yardage = 0
        if "SACK" not in play_result: # pass attempt occurred             
            team_in_poss.game_stats["PATTs"] += 1
            if ("IC" in play_result or "INT" in play_result or "FMBL" in play_result) and "TD" not in play_result:
                updated_variables["clock_running"] = False # incomplete pass or turnover stops clock                                                                                                                    
                if down == 4 or "INT" in play_result or "FMBL" in play_result: # there was a turnover
                    updated_variables = update_variables_after_turnover(play_result, updated_variables, yardage=yardage)
                else:
                    updated_variables["down"] += 1
            elif "TD" in play_result: # there was a touchdown
                updated_variables = update_variables_after_score(play_result, updated_variables, yardage=yardage)                
            else: # standard completion
                if down == 4 and yardage < distance: # turnover on downs
                    updated_variables = update_variables_after_turnover(play_result, updated_variables, yardage=yardage)
                else:
                    updated_variables = update_variables_after_successful_run_or_pass_play(yardage, updated_variables) 
        else:
            yardage *= -1 # yardage becomes negative as there is a loss
            if down == 4 and "SAFETY" not in play_result:
                updated_variables = update_variables_after_turnover(play_result, updated_variables, yardage=yardage)
            elif "SAFETY" in play_result:
                updated_variables = update_variables_after_score(play_result, updated_variables)
            else:
                updated_variables["down"] += 1
                updated_variables["distance"] -= yardage
                updated_variables["yards_to_endzone"] -= yardage
                updated_variables["clock_running"] = True            
        updated_variables["t"] = new_time_left(t, int(stat.norm.rvs(loc=9, scale=1.5))) # Subjective time taken for a pass play
    elif "R " in play_result: # run play
        yardage = int(play_result[play_result.index("YDS") - 2:play_result.index("YDS")])
        team_in_poss.game_stats["RATTs"] += 1
        if "FMBL" in play_result: # fumble
            updated_variables = update_variables_after_turnover(play_result, updated_variables, yardage=yardage)
        elif "TD" in play_result or "SAFETY" in play_result: # scoring play
            updated_variables = update_variables_after_score(play_result, updated_variables, yardage=yardage)
        else:
            if down == 4 and yardage < distance: # turnover on downs
                updated_variables = update_variables_after_turnover(play_result, updated_variables, yardage=yardage)
            else:
                updated_variables = update_variables_after_successful_run_or_pass_play(yardage, updated_variables)
        updated_variables["t"] = new_time_left(t, int(stat.norm.rvs(loc=7.5, scale=1.4989708403591155))) # Subjective time taken for a run play
    elif "PEN" in play_result: # penalty occurred
        updated_variables["clock_running"] = False # clock stops after a penalty
        if "FST" in play_result: # false start
            if yards_to_endzone > 90: # inside own 10 yard line
                updated_variables["distance"] += int((100 - yards_to_endzone) / 2) # penalty yardage is half the distance to the goal line
                updated_variables["yards_to_endzone"] += int((100 - yards_to_endzone) / 2)
            else: # outside own 10 yard line                 
                updated_variables["distance"] += 5 # penalty is 5 yards
                updated_variables["yards_to_endzone"] += 5
        elif "OFFS" in play_result: # offside
            pen_yardage = 0
            if yards_to_endzone < 10: # inside opponents 10 yard line
                pen_yardage = int(yards_to_endzone / 2) # penalty is half the distance to the goal line
            else: # outside opponents 10 yard line
                pen_yardage = 5 # penalty is 5 yards
            updated_variables["yards_to_endzone"] -= pen_yardage 
            if pen_yardage >= distance: # penalty yardage enough for a 1st down
                updated_variables["down"] = 1
                updated_variables["distance"] = 10 if updated_variables["yards_to_endzone"] >= 10 else updated_variables["yards_to_endzone"]
            else:
                updated_variables["distance"] -= pen_yardage
        elif "OFFHOLD" in play_result or "OPI" in play_result: # offensive hold or offensive pass interference
            # half the distance to the goal line penalty, or 10 yards, depending on the field position.
            if yards_to_endzone > 80:
                updated_variables["distance"] += int((100 - yards_to_endzone) / 2)
                updated_variables["yards_to_endzone"] += int((100 - yards_to_endzone) / 2)
            else:
                updated_variables["distance"] += 10
                updated_variables["yards_to_endzone"] += 10
            updated_variables["t"] = new_time_left(t, int(stat.norm.rvs(loc=8.25, scale=1.5))) # post-snap penalty, so time needs to be taken off
        elif "DEFHOLD" in play_result: # defensive hold
            pen_yardage = 0
            if yards_to_endzone < 10:
                    pen_yardage = int(yards_to_endzone / 2)
            else:
                pen_yardage = 5
            updated_variables["yards_to_endzone"] -= pen_yardage
            updated_variables["down"] = 1 # automatic first down
            updated_variables["distance"] = 10 if updated_variables["yards_to_endzone"] >= 10 else updated_variables["yards_to_endzone"]
            updated_variables["t"] = new_time_left(t, int(stat.norm.rvs(loc=8.25, scale=1.5)))
        elif "DPI" in play_result: # defensive pass interference
            pen_yardage = int(play_result[play_result.index("YDS") - 2:play_result.index("YDS")])
            updated_variables["yards_to_endzone"] -= pen_yardage
            updated_variables["down"] = 1 # automatic first down
            updated_variables["distance"] = 10 if updated_variables["yards_to_endzone"] >= 10 else updated_variables["yards_to_endzone"]
            updated_variables["t"] = new_time_left(t, int(stat.norm.rvs(loc=8.25, scale=1.5)))
        elif "INTG" in play_result: # intentional grounding
            if down == 4: # turnover on downs, since it is 4th down and there is a loss of down
                updated_variables = update_variables_after_turnover(play_result, updated_variables)
            else:
                updated_variables["down"] += 1 # loss of down
                if yards_to_endzone > 80:
                    updated_variables["distance"] += int((100 - yards_to_endzone) / 2)
                    updated_variables["yards_to_endzone"] += int((100 - yards_to_endzone) / 2)
                else:
                    updated_variables["distance"] += 10
                    updated_variables["yards_to_endzone"] += 10
            updated_variables["t"] = new_time_left(t, int(stat.norm.rvs(loc=8.25, scale=1.5)))
    elif "XP" in play_result or "2P" in play_result: # play was a points after try
        updated_variables["td_play"] = False # previous play no longer a touchdown
        if "XPS" in play_result or "2PS" in play_result:
            updated_variables = update_variables_after_score(play_result, updated_variables)
        else:
            updated_variables["kickoff"] = True # next play should be a kickoff
        # no time loss on points after try
    elif "FG" in play_result: # play was a field goal
        time_taken = int((6 / 39) * (yards_to_endzone + 18)) # subjective time loss from a field goal
        updated_variables["t"] = new_time_left(updated_variables["t"], time_taken)
        if "FGS" in play_result:
            updated_variables = update_variables_after_score(play_result, updated_variables)
        else:
            updated_variables = update_variables_after_turnover(play_result, updated_variables)
            if yards_to_endzone <= 20: # attempt was inside opponents 20 yard line
                updated_variables["yards_to_endzone"] = 80 # results in a touchback
            else: # attempt was outside opponents 20 yard line
                updated_variables["yards_to_endzone"] -= 8 # play starts from spot of the hold
    elif "PT" in play_result: # play was a punt
        updated_variables["clock_running"] = False # clock stops
        updated_variables["opposition"] = team_in_poss # swap teams around
        updated_variables["team_in_poss"] = opposition
        updated_variables["down"] = 1 # 1st and 10
        updated_variables["distance"] = 10
        if "TB" in play_result:
            time_taken = int((7763 / 51040) * yards_to_endzone) # subjective time taken for punt
            updated_variables["yards_to_endzone"] = 80
        else:
            punt_distance = int(play_result[play_result.index("YDS") - 2:play_result.index("YDS")])
            punt_return = int(play_result[play_result.index("RET") - 2:play_result.index("RET")])
            time_taken = int((7763 / 51040) * punt_distance)
            if punt_return != 0:
                time_taken = time_taken + round((11 / 40) * punt_return) if punt_return < 40 else time_taken + round((3 / 20) * punt_return)
            if "DEF TD" in play_result:
                updated_variables = update_variables_after_score(play_result, updated_variables)
            else:                    
                updated_variables["yards_to_endzone"] = 100 - (yards_to_endzone - punt_distance + punt_return)
        updated_variables["t"] = new_time_left(t, time_taken)
        if "SAFETY KICK" in play_result: # play was a safety kick
            updated_variables["safety_kick"] = False # reset safety kick to False
    elif "ONSIDE KICK" in play_result: # play was an onside kick
        updated_variables["clock_running"] = False
        updated_variables["kickoff"] = False # no longer a kickoff
        if "RECOVERED" in play_result: # offense recovered
            updated_variables["yards_to_endzone"] = 55 # assume no advance, so play starts at own 45 yard line
        else: # defense recovered
            updated_variables["yards_to_endzone"] = 45 # assume no advance, so play starts on opponents 45 yard line
            updated_variables["opposition"] = team_in_poss
            updated_variables["team_in_poss"] = opposition
    if t == 1800: # halftime
        updated_variables["clock_running"] = False # stop the clock
    elif t > 120 and updated_variables["t"] <= 120: # 2 minute warning
        updated_variables["clock_running"] = False
    elif t > 1920 and updated_variables["t"] <= 1920: # 2 minute warning
        updated_variables["clock_running"] = False
    # check if current scenario meets the criteria for hurry up
    if (updated_variables["t"] <= 1920 and updated_variables["t"] > 1800):
        updated_variables["hurry_up"] = True
    elif (updated_variables["t"] <= 600 and updated_variables["opposition"].points - updated_variables["team_in_poss"].points > 16):
        updated_variables["hurry_up"] = True
    elif (updated_variables["t"] <= 240 and updated_variables["t"] > 120 and updated_variables["opposition"].points - updated_variables["team_in_poss"].points > 8 and yards_to_endzone >= 40):
        updated_variables["hurry_up"] = True
    elif (updated_variables["t"] <= 120 and updated_variables["opposition"].points - updated_variables["team_in_poss"].points > 8):
        updated_variables["hurry_up"] = True
    elif (updated_variables["t"] <= 120 and updated_variables["team_in_poss"].points - updated_variables["opposition"].points <= 0):
        updated_variables["hurry_up"] = True
    else:
        updated_variables["hurry_up"] = False
    if (t > 1920 and updated_variables["t"] <= 1920) or (t > 120 and updated_variables["t"] <= 120): # time went below 2 minute warning
        updated_variables["clock_running"] = False # clock stops
    return updated_variables
def return_pre_snap_time_loss(t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, hurry_up, prev_play_result):
    '''
    Method to determine time loss before the snap.
    param t: time left in game.
    param down: the current down.
    param distance: yardage needed for a 1st down/touchdown.
    param yards_to_endzone: yardage needed for a touchdown.
    param team_in_poss: the offense.
    param opposition: the defense.
    param clock_running: boolean specifying if the clock is running.
    param hurry_up: boolean specifying if the offense is in hurry up.
    param prev_play_result: the previous play result.
    '''
    if clock_running == False: # clock stopped
        if "PEN" in prev_play_result: # penalty on the previous play
            if t > 1920 or (t > 300 and t < 1800): # time left meets criteria for game clock to restart once ball is spotted
                time_loss = int(stat.loglaplace.rvs(6.706365134598226, loc=-0.08562374476019619, scale=30.08562363884087))
                if time_loss > 15:
                    return time_loss - 15
                else:
                    return 15
        return 0 # no pre-snap time loss
    else: # clock running
        # check for various scenarios in which teams may take a timeout
        if t < 120 and team_in_poss.points > opposition.points and abs(team_in_poss.points - opposition.points <= 16):
            if opposition.timeouts > 0:
                opposition.timeouts -= 1
                return 0
            return 40
        elif opposition.points - team_in_poss.points <= 3 and opposition.points - team_in_poss.points >= 0 and t <= 20:
            if opposition.timeouts > 0:
                opposition.timeouts -= 1
                return 0
            else:
                if team_in_poss.timeouts > 0:
                    team_in_poss.timeouts -= 1
                    return t - 4 if t > 4 else 0
        elif (t < 1920) and (t > 1800):
            if down == 3 and t >= 1820:
                if opposition.timeouts > 1:
                    opposition.timeouts -= 1
                    return 0
            if down == 4 and t >= 1820:
                if opposition.timeouts > 0:
                    opposition.timeouts -= 1
                    return 0
        if hurry_up == False: # offense not in hurry up
            return int(stat.loglaplace.rvs(6.706365134598226, loc=-0.08562374476019619, scale=30.08562363884087)) # take 30-40 seconds off clock
        else: # offense in hurry up
            # check if teams can take timeouts
            if ((t < 60) and (t >= 40)) or ((t < 1860) and t >= 1840):
                yardage = 0
                try:
                    yardage = int(prev_play_result[prev_play_result.index("YDS") - 2:prev_play_result.index("YDS")])
                except:
                    yardage = 0
                if yardage <= 10: # yardage gained on previously play was small
                    return rd.randint(6, 8) + 5 # offense can get to the line quickly, so short time to next snap
                else:
                    if team_in_poss.timeouts > 0:
                        team_in_poss.timeouts -= 1
                        return 0
            elif (t < 40) or ((t < 1840) and (t > 1800)):
                if team_in_poss.timeouts > 0:
                    team_in_poss.timeouts -= 1
                    return 0
            return rd.randint(8, 13) + 7