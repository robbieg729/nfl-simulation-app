from Simulate import simulate
from Simulate_Season_Functions import sort_division_winners, sort_division, sort_conference, get_wild_card_teams, get_remaining_seeds

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