from Simulate import simulate
import random as rd
import numpy as np

def simulate_season(teams, schedule, initial_records, start_week):
    '''
    Method to simulate part of a full season of the NFL.
    param teams: full list of all 32 NFL teams.
    param schedule: full regular season schedule, as a list of dictionaries.
    param initial_records: overall, divisional, and conference records for each team from the starting week. If start week is 1, all records are 0-0-0.
    param start_week: the week to start simulating from.
    '''
    for i in range(start_week - 1, len(schedule)): # loop through each week
        for game in schedule[i]: # loop through each game in each week
            road_team = game[0:game.index(" at")]
            home_team = game[game.index(" at") + 4:]
            simulate(teams[road_team], teams[home_team]) # simulate the game
            if teams[road_team].points > teams[home_team].points: # road team wins
                schedule[i][game] = road_team # value at this game in the schedule is winning team
                # update conference / divisional records
                if teams[road_team].conference == teams[home_team].conference: 
                    teams[road_team].conf_record[0] += 1
                    teams[home_team].conf_record[1] += 1
                    if teams[road_team].division == teams[home_team].division:
                        teams[road_team].div_record[0] += 1
                        teams[home_team].div_record[1] += 1
            elif teams[home_team].points > teams[road_team].points:
                schedule[i][game] = home_team
                if teams[road_team].conference == teams[home_team].conference:
                    teams[home_team].conf_record[0] += 1
                    teams[road_team].conf_record[1] += 1
                    if teams[road_team].division == teams[home_team].division:
                        teams[home_team].div_record[0] += 1
                        teams[road_team].div_record[1] += 1
            else: # game ended in a tie
                schedule[i][game] = "TIE"
                if teams[road_team].conference == teams[home_team].conference:
                    teams[road_team].conf_record[2] += 1
                    teams[home_team].conf_record[2] += 1
                    if teams[road_team].division == teams[home_team].division:
                        teams[road_team].div_record[2] += 1
                        teams[home_team].div_record[2] += 1
            # update team game and season stats stats
            teams[road_team].update_all_games_or_season_stats(teams[home_team], "season")
            teams[home_team].update_all_games_or_season_stats(teams[road_team], "season")
            teams[road_team].reset_game_or_season_stats("game")
            teams[home_team].reset_game_or_season_stats("game")
    # update team seasons stats
    for team in teams:        
        teams[team].update_all_seasons_stats()
        teams[team].reset_game_or_season_stats("season")
    # Sort conferences and divisions by record
    afc_sorted = sort_conference(teams, "AFC")
    nfc_sorted = sort_conference(teams, "NFC")
    afc_e_sorted = sort_division(teams, "AFC", "East", schedule)
    afc_n_sorted = sort_division(teams, "AFC", "North", schedule)
    afc_s_sorted = sort_division(teams, "AFC", "South", schedule)
    afc_w_sorted = sort_division(teams, "AFC", "West", schedule)
    nfc_e_sorted = sort_division(teams, "NFC", "East", schedule)
    nfc_n_sorted = sort_division(teams, "NFC", "North", schedule)
    nfc_s_sorted = sort_division(teams, "NFC", "South", schedule)
    nfc_w_sorted = sort_division(teams, "NFC", "West", schedule)
    # Sort top 4 seeds in each conference
    afc_division_winners = sort_division_winners([afc_e_sorted[0], afc_n_sorted[0], afc_s_sorted[0], afc_w_sorted[0]], schedule, teams)
    nfc_division_winners = sort_division_winners([nfc_e_sorted[0], nfc_n_sorted[0], nfc_s_sorted[0], nfc_w_sorted[0]], schedule, teams)
    # Remove top 4 seeds from sorted conference lists
    for team in afc_division_winners:
        afc_sorted.remove(team)
    for team in nfc_division_winners:
        nfc_sorted.remove(team)
    # Get wild card teams
    afc_wild_card_teams = get_wild_card_teams(afc_sorted, schedule, teams)  
    nfc_wild_card_teams = get_wild_card_teams(nfc_sorted, schedule, teams)
    afc_seeds = {}
    nfc_seeds = {}
    # Set seeds in each conference, and update some stats
    for team in afc_division_winners:
        afc_seeds[team.seed] = team
        team.division_wins += 1
        team.playoff_apps += 1
    for team in afc_wild_card_teams:
        afc_seeds[team.seed] = team
        team.playoff_apps += 1
    for team in nfc_division_winners:
        nfc_seeds[team.seed] = team
        team.division_wins += 1
        team.playoff_apps += 1
    for team in nfc_wild_card_teams:
        nfc_seeds[team.seed] = team 
        team.playoff_apps += 1
    # List of seeds left in each conference
    afc_seeds_left = [1, 2, 3, 4, 5, 6, 7]
    nfc_seeds_left = [1, 2, 3, 4, 5, 6, 7]
    wild_card_schedule = list()
    # Initialize wild card schedule
    wild_card_schedule.append(afc_seeds[7].name + " at " + afc_seeds[2].name)
    wild_card_schedule.append(afc_seeds[6].name + " at " + afc_seeds[3].name)
    wild_card_schedule.append(afc_seeds[5].name + " at " + afc_seeds[4].name)
    wild_card_schedule.append(nfc_seeds[7].name + " at " + nfc_seeds[2].name)
    wild_card_schedule.append(nfc_seeds[6].name + " at " + nfc_seeds[3].name)
    wild_card_schedule.append(nfc_seeds[5].name + " at " + nfc_seeds[4].name)
    # Perform wild card round, and get remaining teams
    afc_seeds_left, nfc_seeds_left = get_remaining_seeds(wild_card_schedule, teams, afc_seeds_left, nfc_seeds_left)
    divisional_schedule = list()
    # Initialize divisional round schedule, and update some stats
    divisional_schedule.append(afc_seeds[afc_seeds_left[3]].name + " at " + afc_seeds[1].name) # Top seed plays lowest seed remaining
    divisional_schedule.append(afc_seeds[afc_seeds_left[2]].name + " at " + afc_seeds[afc_seeds_left[1]].name) # Other 2 teams play each other
    divisional_schedule.append(nfc_seeds[nfc_seeds_left[3]].name + " at " + nfc_seeds[1].name)
    divisional_schedule.append(nfc_seeds[nfc_seeds_left[2]].name + " at " + nfc_seeds[nfc_seeds_left[1]].name)
    afc_seeds[afc_seeds_left[3]].division_round_apps += 1
    afc_seeds[1].division_round_apps += 1
    afc_seeds[afc_seeds_left[2]].division_round_apps += 1
    afc_seeds[afc_seeds_left[1]].division_round_apps += 1
    nfc_seeds[nfc_seeds_left[3]].division_round_apps += 1
    nfc_seeds[1].division_round_apps += 1
    nfc_seeds[nfc_seeds_left[2]].division_round_apps += 1
    nfc_seeds[nfc_seeds_left[1]].division_round_apps += 1
    # Perform divisional round, and get remaining teams
    afc_seeds_left, nfc_seeds_left = get_remaining_seeds(divisional_schedule, teams, afc_seeds_left, nfc_seeds_left)
    conference_schedule = list()
    # Initialize conference round schedule
    conference_schedule.append(afc_seeds[afc_seeds_left[1]].name + " at " + afc_seeds[afc_seeds_left[0]].name)
    conference_schedule.append(nfc_seeds[nfc_seeds_left[1]].name + " at " + nfc_seeds[nfc_seeds_left[0]].name)
    # Perform conference round, and get Super Bowl teams
    afc_seeds_left, nfc_seeds_left = get_remaining_seeds(conference_schedule, teams, afc_seeds_left, nfc_seeds_left)
    # Get Super Bowl matchup and update some stats
    super_bowl_match = afc_seeds[afc_seeds_left[0]].name + " at " + nfc_seeds[nfc_seeds_left[0]].name
    road_team = super_bowl_match[0:super_bowl_match.index(" at")]
    home_team = super_bowl_match[super_bowl_match.index(" at") + 4:]
    teams[road_team].conference_champions += 1
    teams[home_team].conference_champions += 1
    simulate(teams[road_team], teams[home_team], playoff_game=True) # Simulate Super Bowl
    winner = teams[road_team] if teams[road_team].points > teams[home_team].points else teams[home_team] # Get winning team
    winner.super_bowl_wins += 1 # Update Super Bowl wins for winner
    # Reset variables
    teams[road_team].reset_game_or_season_stats("game")
    teams[home_team].reset_game_or_season_stats("game")
    for team in teams:
        teams[team].record = [int(n) for n in initial_records[team][0].split("-")]
        teams[team].div_record = [int(n) for n in initial_records[team][1].split("-")]
        teams[team].conf_record = [int(n) for n in initial_records[team][2].split("-")]
        teams[team].seed = 0
        teams[team].division_position = 0
        teams[team].sov = 0
        teams[team].sos = 0
    return [afc_seeds, nfc_seeds]

def winning_percentage(record):
    '''
    Method to calculate a winning percentage.
    param record: the win-loss-tie record.
    '''
    try:
        return (record[0] + 0.5 * record[2]) / (record[0] + record[1] + record[2])
    except: # if record is 0-0-0, exception will be thrown
        return 0

def bubble_sort_teams_by_records(teams, records):
    '''
    Method to bubble sort teams by records.
    param teams: the list of teams to sort.
    param records: the corresponding list of win-loss-tie records.
    '''
    # Perform standard bubble sort algorithm
    swapped = True
    while swapped == True:
        swapped = False
        for i in range(0, len(teams) - 1):
            if winning_percentage(records[i]) < winning_percentage(records[i + 1]):
                temp = teams[i + 1]
                teams[i + 1] = teams[i]
                teams[i] = temp
                temp = records[i + 1]
                records[i + 1] = records[i]
                records[i] = temp
                swapped = True
    return teams

def strength_of_victory(team, all_teams, schedule):
    '''
    Method to calculate the strength of victory (SOV) of a single team.
    param team: the team for which to calculate the SOV.
    param all_teams: a dictionary of all 32 teams in the league.
    param schedule: the full regular season schedule, given as a list of dictionaries.
    '''
    record = [0, 0, 0]
    opponents_beaten = list()
    for i in range(0, np.shape(team.opponents)[0]): # loop through opponents
        week = int(team.opponents[i][2])
        opponent = all_teams[team.opponents[i][0]]
        if opponent.name not in opponents_beaten: # checking for double counting a team, e.g. a divisional opponent would be played twice, but their record is only added once to the SOV            
            # Get winner of game and store in result
            result = ""
            if team.opponents[i][1] == "H":
                result = schedule[week - 1][opponent.name + " at " + team.name]
            else:
                result = schedule[week - 1][team.name + " at " + opponent.name]
            if result == team: # the team we want to calculate SOV for won
                opponents_beaten.append(opponent.name) # add opponent name to opponents_beaten list
                # add full record to SOV
                record[0] += opponent.record[0]
                record[1] += opponent.record[1]
                record[2] += opponent.record[2]
    return record

def strength_of_schedule(team, all_teams):
    '''
    Method to calculate the strength of schedule (SOS) of a single team.
    param team: the team for which to calculate the SOV.
    param all_teams: a dictionary of all 32 teams in the league.
    '''
    record = [0, 0, 0]
    opponents_played = list()
    for i in range(0, np.shape(team.opponents)[0]):
        opponent = all_teams[team.opponents[i][0]]
        if opponent.name not in opponents_played: # checking for double counting in case of divisional opponents being played
            record[0] += opponent.record[0]
            record[1] += opponent.record[1]
            record[2] += opponent.record[2]
            opponents_played.append(opponent)
    return record

def sorted_teams_after_multi_hth(teams, schedule):
    '''
    Method to sort teams after a multi-team head-to-head record check.
    param teams: the teams to sort.
    param schedule: the full regular season schedule.
    '''
    if check_within_division(teams) == False:
        teams_beaten = np.zeros((len(teams), len(teams) + 1))
        for i in range(0, len(teams)):
            for j in range(0, len(teams)):
                hth_weeks = np.where(teams[i].opponents[:, 0] == teams[j].name)[0]
                if teams[i].opponents[hth_weeks] != []:
                    for k in range(0, len(hth_weeks)):
                        result = ""
                        game = teams[i].opponents[hth_weeks[k]]
                        if game[1] == "H":
                            result = schedule[int(game[2]) - 1][teams[j].name + " at " + teams[i].name]
                        else:
                            result = schedule[int(game[2]) - 1][teams[i].name + " at " + teams[j].name]                  
                        if result == teams[i].name:                            
                            teams_beaten[i][j] += 1   
                        teams_beaten[i][len(teams)] += 1
                        teams_beaten[j][len(teams)] += 1
        teams_sweep = list()
        teams_swept = list()
        for i in range(0, len(teams)):
            teams_beaten[i][i] = 1
            y = np.where(teams_beaten[i] == 0)[0]
            try:
                z = y[0]
            except:
                teams_sweep.append(teams[i])
            teams_beaten[i][i] = 0
            y = np.where(teams_beaten[i] == 0)[0]
            if len(y) == len(teams) and len(teams) not in y:
                teams_swept.append(teams[i])

        if len(teams_sweep) != 0:
            return teams_sweep
        if len(teams_swept) != 0:
            for i in range(0, len(teams_swept)):
                teams.remove(teams_swept[i])
        return teams
    else:
        hth_records = list()
        for i in range(0, len(teams)):
            hth_records.append([0, 0, 0, teams[i].name])
        for i in range(0, len(teams) - 1):
            for j in range(0, np.shape(teams[i].opponents)[0]):
                for k in range(i + 1, len(teams)):
                    if teams[k].name in teams[i].opponents[j][0]:
                        week = int(teams[i].opponents[j][2])
                        result = ""
                        if teams[i].opponents[j][1] == "H":
                            result = schedule[week - 1][teams[k].name + " at " + teams[i].name]
                        else:
                            result = schedule[week - 1][teams[i].name + " at " + teams[k].name]
                        if result == teams[i].name:
                            hth_records[i][0] += 1
                            hth_records[k][1] += 1
                        elif result == teams[k].name:
                            hth_records[k][0] += 1
                            hth_records[i][1] += 1
                        else:
                            hth_records[i][2] += 1
                            hth_records[k][2] += 1
        sorted_hth_percentages = list()
        teams = bubble_sort_teams_by_records(teams, hth_records)
        for i in range(0, len(teams)):
            for j in range(0, len(hth_records)):
                if hth_records[j][3] == teams[i].name:
                    sorted_hth_percentages.append(winning_percentage(hth_records[j]))
        count = 1
        if sorted_hth_percentages[0] > sorted_hth_percentages[1]:
            return [teams[0]]
        else:
            for i in range(0, len(sorted_hth_percentages) - 1):
                j = i + 1
                if sorted_hth_percentages[i] == sorted_hth_percentages[j]:
                    count += 1
                else:
                    break
            return teams[0:count]

def sorted_teams_after_multi_record(teams, record_type):
    '''
    Method to sort multiple teams by record.
    param teams: the teams to be sorted.
    param record_type: the type of record to sort by. Could be divisional, conference, strength of victory (SOV), or strength of schedule (SOS).
    '''
    records = list()
    for team in teams:
        if record_type == "div":
            records.append(team.div_record)
        elif record_type == "conf":
            records.append(team.conf_record)
        elif record_type == "sov":
            records.append(team.sov)
        elif record_type == "sos":
            records.append(team.sos)
    teams = bubble_sort_teams_by_records(teams, records)
    percentages = list()
    for team in teams:
        if record_type == "div":            
            percentages.append(winning_percentage(team.div_record))
        elif record_type == "conf":
            percentages.append(winning_percentage(team.conf_record))
        elif record_type == "sov":
            percentages.append(winning_percentage(team.sov))
        elif record_type == "sos":
            percentages.append(winning_percentage(team.sos))
    count = 1
    if percentages[0] > percentages[1]:
        return [teams[0]]
    else:
        for i in range(0, len(percentages) - 1):
            j = i + 1
            if percentages[i] == percentages[j]:
                count += 1
            else:
                break
        return teams[0:count]

def check_within_division(teams):
    '''
    Method to check if a list of teams are in the same division. Important for tie-breaking wild-card teams, as divisional rules could apply.
    param teams: the teams to check.
    '''
    within_division = True
    division = teams[0].division
    for team in teams[1:]:
        if team.division != division:
            within_division = False
            break
    return within_division 

def tiebreak_teams(teams, within_division, schedule, all_teams):
    '''
    Method to tiebreak multiple teams.
    param teams: the teams to tiebreak.
    param within_division: boolean specifying if the teams are all part of the same division.
    param schedule: the full regular season schedule.
    param all_teams: all 32 NFL teams.
    '''
    if len(teams) == 2:
        team_zero_hth_wins = 0
        team_one_hth_wins = 0
        for i in range(0, np.shape(teams[0].opponents)[0]):
            count = 0
            if teams[1].name in teams[0].opponents[i][0]:
                count += 1
                week = int(teams[0].opponents[i][2])
                result = ""
                if teams[0].opponents[i][1] == "H":
                    result = schedule[week - 1][teams[1].name + " at " + teams[0].name]
                else:
                    result = schedule[week - 1][teams[0].name + " at " + teams[1].name]
                if result == teams[0].name:
                    team_zero_hth_wins += 1
                elif result == teams[1].name:
                    team_one_hth_wins += 1
                if within_division == True:
                    if count == 2:
                        break
                else:
                    break
        if team_zero_hth_wins > team_one_hth_wins:
            return teams[0]
        elif team_one_hth_wins > team_zero_hth_wins:
            return teams[1]
        else:
            if within_division == True:
                if winning_percentage(teams[0].div_record) > winning_percentage(teams[1].div_record):
                    return teams[0]
                elif winning_percentage(teams[1].div_record) > winning_percentage(teams[0].div_record):
                    return teams[1]
                teams = sorted_teams_after_common_games(teams, schedule)
                if len(teams) == 1:
                    return teams[0]
                else:
                    if winning_percentage(teams[0].conf_record) > winning_percentage(teams[1].conf_record):
                        return teams[0]
                    elif winning_percentage(teams[1].conf_record) > winning_percentage(teams[0].conf_record):
                        return teams[1]
            else:
                if winning_percentage(teams[0].conf_record) > winning_percentage(teams[1].conf_record):
                    return teams[0]
                elif winning_percentage(teams[1].conf_record) > winning_percentage(teams[0].conf_record):
                    return teams[1]
                else:
                    teams = sorted_teams_after_common_games(teams, schedule)
                    if len(teams) == 1:
                        return teams[0]
            if winning_percentage(strength_of_victory(teams[0], all_teams, schedule)) > winning_percentage(strength_of_victory(teams[1], all_teams, schedule)):
                return teams[0]
            elif winning_percentage(strength_of_victory(teams[1], all_teams, schedule)) > winning_percentage(strength_of_victory(teams[0], all_teams, schedule)):
                return teams[1]
            else:
                if winning_percentage(strength_of_schedule(teams[0], all_teams)) > winning_percentage(strength_of_schedule(teams[1], all_teams)):
                    return teams[0]
                elif winning_percentage(strength_of_schedule(teams[1], all_teams)) > winning_percentage(strength_of_schedule(teams[0], all_teams)):
                    return teams[1]
                else:                        
                    if (teams[0].season_stats["PTS"] - teams[0].season_stats["PTSA"]) > (teams[1].season_stats["PTS"] - teams[1].season_stats["PTSA"]):
                        return teams[0]
                    elif (teams[1].season_stats["PTS"] - teams[1].season_stats["PTSA"]) > (teams[0].season_stats["PTS"] - teams[0].season_stats["PTSA"]):
                        return teams[1]
                    else:
                        return teams[0] if rd.random() <= 0.5 else teams[1]
    else:
        teams = sorted_teams_after_multi_hth(teams, schedule)
        if len(teams) == 1:
            return teams[0]
        if within_division == True or check_within_division(teams) == True:
            teams = sorted_teams_after_multi_record(teams, "div")
            if len(teams) == 1:
                return teams[0]
            teams = sorted_teams_after_common_games(teams, schedule)
            if len(teams) == 1:
                return teams[0]
            teams = sorted_teams_after_multi_record(teams, "conf")
            if len(teams) == 1:
                return teams[0]
        else:
            teams = sorted_teams_after_multi_record(teams, "conf")
            if len(teams) == 1:
                return teams[0]
            teams = sorted_teams_after_common_games(teams, schedule)
            if len(teams) == 1:
                return teams[0]
        for team in teams:
            team.sov = strength_of_victory(team, all_teams, schedule)
        teams = sorted_teams_after_multi_record(teams, "sov")
        if len(teams) == 1:
            return teams[0]
        for team in teams:
            team.sos = strength_of_schedule(team, all_teams)
        teams = sorted_teams_after_multi_record(teams, "sos")
        if len(teams) == 1:
            return teams[0]
        return teams[rd.randint(0, len(teams) - 1)]           

def sorted_teams_after_common_games(teams, schedule):
    '''
    Method to sort teams in a common-games tiebreaking procedure.
    param teams: the teams involved in the tiebreak.
    param schedule: the full regular season schedule.
    '''
    all_opponents = list()
    team_records = list()
    common_opponents = list()
    for i in range(0, len(teams)):
        team_records.append([0, 0, 0, teams[i].name])
        all_opponents.append(teams[i].opponents[:, 0])

    for i in range(0, 17):
        common_opponent = True
        opponent = teams[0].opponents[i][0]
        for j in range(1, len(teams)):
            if opponent not in all_opponents[j]:
                common_opponent = False
                break
        if common_opponent == True:
            common_opponents.append(opponent)

    if len(common_opponents) < 4:
        return teams
    else:
        for i in range(0, len(teams)):
            for j in range(0, len(common_opponents)):
                indexes = np.where(teams[i].opponents[:, 0] == common_opponents[j])[0]
                #print(teams[i].name)
                #print(common_opponents[j])
                #print(indexes)
                for k in range(0, len(indexes)):
                    #print(teams[i].opponents[k, 2])
                    week = int(teams[i].opponents[indexes[k], 2])
                    #print(week)
                    result = ""
                    #print(teams[i].opponents[k, 1])
                    if teams[i].opponents[indexes[k], 1] == "H":
                        result = schedule[week - 1][common_opponents[j] + " at " + teams[i].name]
                    else:
                        result = schedule[week - 1][teams[i].name + " at " + common_opponents[j]]
                    if result == teams[i]:
                        team_records[i][0] += 1
                    elif result == common_opponents[j]:
                        team_records[i][1] += 1
                    else:
                        team_records[i][2] += 1
        teams = bubble_sort_teams_by_records(teams, team_records)
        sorted_percentages = list()
        for i in range(0, len(teams)):
            for j in range(0, len(team_records)):
                if team_records[j][3] == teams[i].name:
                    sorted_percentages.append(winning_percentage(team_records[j]))
        count = 1
        if sorted_percentages[0] > sorted_percentages[1]:
            return [teams[0]]
        else:
            for i in range(0, len(sorted_percentages) - 1):
                j = i + 1
                if sorted_percentages[i] == sorted_percentages[j]:
                    count += 1
                else:
                    break
            return teams[0:count]
            

def sort_division_winners(teams, schedule, all_teams):
    '''
    Method to sort the division winners in a conference, and set their seeds.
    param teams: the teams to sort.
    param schedule: the full regular season schedule.
    param all_teams: all 32 NFL teams.
    '''
    records = list()
    for team in teams:
        records.append(team.record)
    teams = bubble_sort_teams_by_records(teams, records)
    for i in range(0, len(teams) - 1):
        if winning_percentage(teams[i].record) > winning_percentage(teams[i + 1].record):
            teams[i].seed = i + 1
        else:
            j = i + 1
            tiebreaking_teams = [teams[i]]
            while winning_percentage(teams[i].record) == winning_percentage(teams[j].record):
                tiebreaking_teams.append(teams[j])
                if j == len(teams) - 1:
                    break
                else:
                    j += 1
            tiebreak = list() 
            tiebreak = tiebreak_teams(tiebreaking_teams, False, schedule, all_teams)
            index = teams.index(tiebreak)
            temp = teams[i]
            teams[i] = tiebreak
            teams[index] = temp
    for i in range(0, 4):
        teams[i].seed = i + 1
    return teams      

def sort_division(teams, conference, division, schedule):
    '''
    Method to sort a division
    param teams: the teams to sort.
    param conference: the conference the teams are in.
    param division: the division the teams are in.
    param schedule: the full regular season schedule.
    '''
    div_teams = list()
    for key in teams:
        if teams[key].conference == conference:
            if teams[key].division == division:
                div_teams.append(teams[key])
    records = list()
    for team in div_teams:
        records.append(team.record)
    div_teams = bubble_sort_teams_by_records(div_teams, records)
    for i in range(0, len(div_teams) - 1):
        if winning_percentage(div_teams[i].record) > winning_percentage(div_teams[i + 1].record):
            div_teams[i].division_position = i + 1
        else:
            j = i + 1
            tiebreaking_teams = [div_teams[i]]
            while winning_percentage(div_teams[i].record) == winning_percentage(div_teams[j].record):
                tiebreaking_teams.append(div_teams[j])
                if j == len(div_teams) - 1:
                    break
                else:
                    j += 1
            tiebreak = list()
            tiebreak = tiebreak_teams(tiebreaking_teams, True, schedule, teams)
            index = div_teams.index(tiebreak)
            temp = div_teams[i]
            div_teams[i] = tiebreak
            div_teams[index] = temp
    for i in range(0, 4):
        div_teams[i].division_position = i + 1
    return div_teams

def sort_conference(teams, conference):
    '''
    Method to sort an entire conference by records.
    param team: the teams to sort.
    param conference: the conference to be sorted.
    '''
    sorting_list = list()
    records = list()
    for key in teams:
        if teams[key].conference == conference:
            sorting_list.append(teams[key])
            records.append(teams[key].record)
    return bubble_sort_teams_by_records(sorting_list, records)

def get_wild_card_teams(teams, schedule, all_teams):
    '''
    Method to get the 3 wild card teams from the remaining teams in the conference.
    param teams: all teams left in the conference (excluding division winners).
    param schedule: the full regular season schedule.
    param all_teams: all 32 NFL teams.
    '''
    teams_fixed = 0
    for i in range(0, len(teams) - 1):
        if teams_fixed >= 3:
            break
        tiebreaking_teams = list()
        if winning_percentage(teams[i].record) == winning_percentage(teams[i + 1].record):              
            j = i + 1
            tiebreaking_teams.append(teams[i])
            while winning_percentage(teams[i].record) == winning_percentage(teams[j].record):
                tiebreaking_teams.append(teams[j])
                if j == len(teams) - 1:
                    break
                else:
                    j += 1
            within_division = check_within_division(tiebreaking_teams)
            teams_fixed += len(tiebreaking_teams)
            tiebreak = tiebreak_teams(tiebreaking_teams, within_division, schedule, all_teams)
            index = teams.index(tiebreak)
            temp = teams[i]
            teams[i] = tiebreak
            teams[index] = temp
        else:
            teams_fixed += 1
    wild_card_teams = teams[0:3]
    for j in range(0, len(wild_card_teams)):
        wild_card_teams[j].seed = j + 5
    return wild_card_teams

def get_remaining_seeds(schedule, teams, afc_seeds_left, nfc_seeds_left):
    '''
    Method to perform a full week of the playoff schedule and get the remaining seeds.
    param schedule: the games in the current week of the playoff schedule.
    param teams: the teams remaining in the playoffs.
    param afc_seeds_left: a list of the remaining AFC seeds.
    param nfc_seeds_left: a list of the remaining NFC seeds.
    '''
    for game in schedule:
        road_team = game[0:game.index(" at")]
        home_team = game[game.index(" at") + 4:]
        simulate(teams[road_team], teams[home_team], playoff_game=True)
        loser = teams[home_team] if teams[road_team].points > teams[home_team].points else teams[road_team]
        if loser.conference == "AFC":
            afc_seeds_left.remove(loser.seed)
        else:
            nfc_seeds_left.remove(loser.seed)
        teams[road_team].reset_game_or_season_stats("game")
        teams[home_team].reset_game_or_season_stats("game")
    return afc_seeds_left, nfc_seeds_left