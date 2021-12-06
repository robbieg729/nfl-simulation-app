from Simulate import simulate
import random as rd

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
    for i in range(0, len(team.opponents)): # loop through opponents
        week = team.opponents[i][2]
        opponent = all_teams[team.opponents[i][0]]
        if opponent.name not in opponents_beaten: # checking for double counting a team, e.g. a divisional opponent would be played twice, but their record is only added once to the SOV            
            result = schedule[week - 1][opponent.name + " at " + team.name] if team.opponents[i][1] == "H" else schedule[week - 1][team.name + " at " + opponent.name] # winner of the game
            if result == team: # the team we want to calculate SOV for won
                opponents_beaten.append(opponent.name) # add opponent name to opponents_beaten list
                # add full record to SOV
                record[0] += opponent.record[0]
                record[1] += opponent.record[1]
                record[2] += opponent.record[2]
    return record

def strength_of_schedule(team, all_teams, schedule):
    '''
    Method to calculate the strength of schedule (SOS) of a single team.
    param team: the team for which to calculate the SOV.
    param all_teams: a dictionary of all 32 teams in the league.
    '''
    record = [0, 0, 0]
    opponents_played = list()
    for i in range(0, len(team.opponents)):
        opponent = all_teams[team.opponents[i][0]]
        if opponent.name not in opponents_played: # checking for double counting in case of divisional opponents being played
            record[0] += opponent.record[0]
            record[1] += opponent.record[1]
            record[2] += opponent.record[2]
    return record

def sorted_teams_after_multi_hth(teams, schedule, all_teams):
    hth_records = list()
    for i in range(0, len(teams)):
        hth_records.append([0, 0, 0, teams[i].name])
    for i in range(0, len(teams) - 1):
        for j in range(0, len(teams[i].opponents)):
            for k in range(i + 1, len(teams)):
                if teams[k].name in teams[i].opponents[j][0]:
                    week = teams[i].opponents[j][2]
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

def sorted_teams_after_multi_record(teams, schedule, all_teams, record_type):
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
        for i in range(0, len(teams[0].opponents)):
            count = 0
            if teams[1].name in teams[0].opponents[i][0]:
                count += 1
                week = teams[0].opponents[i][2]
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
            if winning_percentage(teams[0].conf_record) > winning_percentage(teams[1].conf_record):
                return teams[0]
            elif winning_percentage(teams[1].conf_record) > winning_percentage(teams[0].conf_record):
                return teams[1]
            else:
                if winning_percentage(strength_of_victory(teams[0], all_teams, schedule)) > winning_percentage(strength_of_victory(teams[1], all_teams, schedule)):
                    return teams[0]
                elif winning_percentage(strength_of_victory(teams[1], all_teams, schedule)) > winning_percentage(strength_of_victory(teams[0], all_teams, schedule)):
                    return teams[1]
                else:
                    if winning_percentage(strength_of_schedule(teams[0], all_teams, schedule)) > winning_percentage(strength_of_victory(teams[1], all_teams, schedule)):
                        return teams[0]
                    elif winning_percentage(strength_of_schedule(teams[1], all_teams, schedule)) > winning_percentage(strength_of_victory(teams[0], all_teams, schedule)):
                        return teams[1]
                    else:                        
                        if (teams[0].season_stats["PTS"] - teams[0].season_stats["PTSA"]) > (teams[1].season_stats["PTS"] - teams[1].season_stats["PTSA"]):
                            return teams[0]
                        elif (teams[1].season_stats["PTS"] - teams[1].season_stats["PTSA"]) > (teams[0].season_stats["PTS"] - teams[0].season_stats["PTSA"]):
                            return teams[1]
                        else:
                            return teams[0] if rd.random() <= 0.5 else teams[1]
    else:
        teams = sorted_teams_after_multi_hth(teams, schedule, all_teams)
        if len(teams) == 1:
            return teams[0]
        if within_division == True or check_within_division(teams) == True:
            teams = sorted_teams_after_multi_record(teams, schedule, all_teams, "div")
            if len(teams) == 1:
                return teams[0]
        teams = sorted_teams_after_multi_record(teams, schedule, all_teams, "conf")
        if len(teams) == 1:
            return teams[0]
        for team in teams:
            team.sov = strength_of_victory(team, all_teams, schedule)
        teams = sorted_teams_after_multi_record(teams, schedule, all_teams, "sov")
        if len(teams) == 1:
            return teams[0]
        for team in teams:
            team.sos = strength_of_schedule(team, all_teams, schedule)
        teams = sorted_teams_after_multi_record(teams, schedule, all_teams, "sos")
        if len(teams) == True:
            return teams[0]
        return teams[rd.randint(0, len(teams) - 1)]           

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
            k = 0
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