import random as rd
from Simulate_Functions import new_time_left, get_play, get_play_result, get_updated_variables, return_pre_snap_time_loss

def simulate(road_team, home_team, initial_variables={"t": 3600, "down": 1, "distance": 10, "yards_to_endzone": 65, "ko_team": None, "team_in_poss": None, "opposition": None, "road_team_timeouts": 3, "home_team_timeouts": 3, "road_team_points": 0, "home_team_points": 0, "clock_running": "N", "td_play": "N", "kickoff": "Y", "safety_kick": "N", "hurry_up": "N", "overtime": "N", "sudden_death": "N"}, playoff_game=False):
    '''
    Method to simulate an entire game.
    param road_team: the road team playing.
    param home_team: the home team playing.
    param initial_variables: the starting point of the game. If unspecified, defaults to the beginning of a game.
    param playoff_game: boolean specifying whether or not the game is a playoff game, for tie implications. If unspecified, defaults to False.
    '''
    t = initial_variables["t"] # time left in seconds
    down = initial_variables["down"] # current down
    distance = initial_variables["distance"] # current distance
    yards_to_endzone = initial_variables["yards_to_endzone"] # yards for team in possession to go until the endzone
    ko_team = initial_variables["ko_team"] # team that kicked off first
    if ko_team == None: # beginning of the game
        ko_team = home_team if rd.random() <= 0.5 else road_team # coin toss          
    team_in_poss = initial_variables["team_in_poss"] # current team in possession
    opposition = initial_variables["opposition"] # current opposition (defense)
    if team_in_poss == None: # beginning of the game
        team_in_poss = ko_team # team in possession is kicking team
        opposition = home_team if team_in_poss.name == road_team.name else road_team # opposition is return team
    team_in_poss.timeouts = initial_variables["home_team_timeouts"] if team_in_poss.name == home_team.name else initial_variables["road_team_timeouts"]
    opposition.timeouts = initial_variables["home_team_timeouts"] if opposition.name == home_team.name else initial_variables["road_team_timeouts"]
    team_in_poss.points = initial_variables["home_team_points"] if team_in_poss.name == home_team.name else initial_variables["road_team_points"]
    opposition.points = initial_variables["home_team_points"] if opposition.name == home_team.name else initial_variables["road_team_points"]
    clock_running = True if initial_variables["clock_running"] == "Y" else False # boolean specifying if clock currently running
    td_play = True if initial_variables["td_play"] == "Y" else False # boolean specifying if a touchdown just occurred
    kickoff = True if initial_variables["kickoff"] == "Y" else False # boolean specifying if it is a kikcoff
    safety_kick = True if initial_variables["safety_kick"] == "Y" else False # boolean specifying if a safety just occurred
    hurry_up = True if initial_variables["hurry_up"] == "Y" else False # boolean specifying if a team is in hurry-up mode
    overtime = True if initial_variables["overtime"] == "Y" else False # boolean specifying if the game is in overtime
    sudden_death = True if initial_variables["sudden_death"] == "Y" else False # boolean specifying if the game is in sudden death (overtime only)
    play_result = ""
    untimed_down = False # boolean specifying if an untimed down should be run
    if overtime == False: # in regulation
        while t > 0 or untimed_down == True: # time left on the clock, or an untimed down should be run
            # get pre-snap time loss
            pre_snap_time_loss = return_pre_snap_time_loss(t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, hurry_up, play_result)
            if pre_snap_time_loss == 0:
                clock_running = False
            else:            
                t = new_time_left(t, pre_snap_time_loss, after_snap=False) # new time left after pre-snap time loss
            if t != 0 or untimed_down == True: # time is still left on the clock after pre-snap time loss
                if t == 1800 and "KOTB" not in play_result: # second half kickoff
                    clock_running = False # clock stopped
                    kickoff = True # next play should be a kickoff
                    # team_in_poss (kicking team) becomes the team that did not initially kickoff
                    team_in_poss = home_team if ko_team.name == road_team.name else road_team
                    opposition = home_team if team_in_poss.name == road_team.name else road_team
                # get the next play (e.g. run/pass/field goal etc.)
                play = get_play(t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, td_play, kickoff, safety_kick, hurry_up)
                # get the result of the play 
                play_result = get_play_result(play, t, down, distance, yards_to_endzone, team_in_poss, opposition)                
                # get the new variables from the play result
                updated_variables = get_updated_variables(play_result, t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, td_play, kickoff, safety_kick, hurry_up)
                t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, td_play, kickoff, safety_kick, hurry_up = updated_variables["t"], updated_variables["down"], updated_variables["distance"], updated_variables["yards_to_endzone"], updated_variables["team_in_poss"], updated_variables["opposition"], updated_variables["clock_running"], updated_variables["td_play"], updated_variables["kickoff"], updated_variables["safety_kick"], updated_variables["hurry_up"]
                if (t == 1800) and ("DPI" in play_result or "DEFHOLD" in play_result or "OFFS" in play_result): # defensive penalty at end of first half
                    t += 1 # add 1 more second to the clock (just to simulate an untimed down)
                if untimed_down == True: # previous play was an untimed down
                    untimed_down = False # set it back
            if (t == 0) and (("DPI" in play_result or "DEFHOLD" in play_result or "OFFS" in play_result) or td_play == True): # defensive penalty or touchdown at end of game
                untimed_down = True # should be 1 more play
    if home_team.points == road_team.points or overtime == True: # overtime required
        game_over = False 
        overtime = True
        if initial_variables["overtime"] == "N": # regulation was simulated, so overtime = True was not an initial variable
            t = 600 if playoff_game == False else 900 # time left
            team_in_poss = home_team if rd.random() <= 0.5 else road_team # coin toss
            opposition = home_team if team_in_poss.name == road_team.name else road_team
            team_in_poss.timeouts = 2 # reset timeouts for each team
            opposition.timeouts = 2
            clock_running = False
            td_play = False
            kickoff = True
            safety_kick = False
            td_play = False
            hurry_up = False
        else:
            if team_in_poss == None: # overtime = True was an initial variable, but wanted to simulate from the start of overtime and before coin toss
                team_in_poss = home_team if rd.random() <= 0.5 else road_team
                opposition = home_team if team_in_poss.name == road_team.name else road_team
        play_result = ""
        plays = 0
        # same algorithm as before, with a few tweaks
        while (game_over == False) and (t > 0):
            pre_snap_time_loss = return_pre_snap_time_loss(t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, hurry_up, play_result)
            if pre_snap_time_loss == 0:
                clock_running = False
            else:            
                t = new_time_left(t, pre_snap_time_loss, after_snap=False)
            if t != 0:
                play = get_play(t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, td_play, kickoff, safety_kick, hurry_up, overtime=True, sudden_death=sudden_death)
                play_result = get_play_result(play, t, down, distance, yards_to_endzone, team_in_poss, opposition)
                updated_variables = get_updated_variables(play_result, t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, td_play, kickoff, safety_kick, hurry_up)           
                plays += 1
                if updated_variables["team_in_poss"] != team_in_poss and plays != 1: # change of possession not from opening kickoff
                    sudden_death = True # now in sudden death
                    if team_in_poss.points < opposition.points:
                        game_over = True
                t, down, distance, yards_to_endzone, team_in_poss, opposition, clock_running, td_play, kickoff, safety_kick, hurry_up = updated_variables["t"], updated_variables["down"], updated_variables["distance"], updated_variables["yards_to_endzone"], updated_variables["team_in_poss"], updated_variables["opposition"], updated_variables["clock_running"], updated_variables["td_play"], updated_variables["kickoff"], updated_variables["safety_kick"], updated_variables["hurry_up"]
                if "TD" in play_result or "SAFETY" in play_result: # score to end the game
                    game_over = True # game over
                elif "FGS" in play_result:
                    if sudden_death == True and team_in_poss.points > opposition.points: # score to end the game
                        game_over = True # game over
            if t == 0 and game_over == False and playoff_game == True: # another overtime period if playoff game is tied at end of overtime period 
                t = 900
    # update team defensive fantasy points
    road_team.update_defensive_fantasy_points()
    home_team.update_defensive_fantasy_points()