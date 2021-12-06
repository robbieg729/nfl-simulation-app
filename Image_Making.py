import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_win_probabilities_image(matchups_data, week, img_number):
    '''
    Method to create an image displaying the win probabilities for each early Sunday matchup in a given week. Displays maximum of 8 matchups per image.
    param matchups_data: a list of lists, containing win probability data for each matchup.
    param week: the current week of the season.
    param img_number: 1 or 2. First image (img_number=1) displays first 8 matchups on the Sunday, second image (img_number=2) displays remaining matchups on the Sunday.
    '''
    img = Image.new("RGB", (1080, 1080), color=(1, 51, 105)) # Create 1080 x 1080 image with background specified by RGB color (1, 51, 105) 
    d = ImageDraw.Draw(img) # Create an object to be able to draw to the image with
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 90) # Set the font to be used for the next draw
    text = "WIN PROBABILITIES" # Next text to be displayed (this is the title)
    d.text((540 - (d.textlength(text, font=fnt) / 2), 0), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Add title to image
    text = "Week " + str(week) # Text showing week number
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 40) # Change font size
    d.text((540 - (d.textlength(text, font=fnt) / 2), 126), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Add week text to image
    i = -1 # Acts as an index. Could say for i in range(...) but this way is more readable
    for matchup in matchups_data: # loop through matchups
        i += 1 # Increase index (set to 0 on first loop)
        fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 60)
        road_img_coords = (25, 200 + 100 * i) # Coordinates for road team logo
        road_prob_coords = (146.875, 210.5 + 100 * i) # Coordinates for road team win probability
        road_rectangle_coords = [327.5, 221 + 100 * i, 0, 271 + 100 * i] # Coordinates for continuous bar showing the win probability
        road_fill = (0, 0, 0) # create color to fill road team text and bar with. Will be green if road team has a higher chance of winning, red if they have a lower chance of winning, yellow if it is the same.
        home_img_coords = (965, 200 + 100 * i)
        home_prob_coords = (786.875, 210.5 + 100 * i)
        home_fill = (0, 0, 0)
        base_rectangle_coords = [327.5, 221 + 100 * i, 752.5, 271 + 100 * i] # Underlying continuous bar coordinates. Road team bar is laid over this bar.
        tie_y_coord = 282.5 + 100 * i # Coordinates for text showing chance of a tie
        tie_rectangle_coords = [0, 221 + 100 * i, 0, 271 + 100 * i] # Coordinates for a thin white rectangle that will also be laid over the base, showing chances of a tie.
        road_img = Image.open("Base/Base/Team Logos/" + matchup[0] + ".png").resize((90, 90)) # Get road team image and resize to 90 x 90
        img.paste(road_img, road_img_coords, road_img.convert("RGBA")) # paste road team image onto main image, while maintaining transparency
        home_img = Image.open("Base/Base/Team Logos/" + matchup[2] + ".png").resize((90, 90))
        img.paste(home_img, home_img_coords, home_img.convert("RGBA"))        
        if matchup[1] > matchup[3]: # road team has a higher chance of winning
            road_fill = (77, 255, 12) # road fill set to a green color
            home_fill = (254, 11, 27) # home fill set to a red color
        elif matchup[3] > matchup[1]: # home team has a higher chance of winning
            road_fill = (254, 11, 27) # road fill set to a red color
            home_fill = (77, 255, 12) # home fill set to a green color
        else: # teams have equal chance of winning
            road_fill = (253, 252, 1) # road fill set to a yellow color
            home_fill = (253, 252, 1) # home fill set to a yellow color
        d.text(road_prob_coords, str(matchup[1]) + "%", font=fnt, align="center", fill=road_fill, stroke_width=1) # add road win probability text to image
        d.text(home_prob_coords, str(matchup[3]) + "%", font=fnt, align="center", fill=home_fill, stroke_width=1) # add home win probability text to image
        d.rectangle(base_rectangle_coords, fill=home_fill) # add base rectangle to image, with color set to home fill
        road_rectangle_coords[2] = round(332 + 425 * (matchup[1] / 100)) # reset road rectangle coordinates to match with the win probability of the road team
        d.rectangle(road_rectangle_coords, fill=road_fill) # draw road rectangle onto image
        # give tie rectangle a width of 3
        tie_rectangle_coords[0] = road_rectangle_coords[2] + 1
        tie_rectangle_coords[2] = road_rectangle_coords[2] + 4
        d.rectangle(tie_rectangle_coords, fill=(255, 255, 255))
        tie_text = "TIE - " + str(matchup[4]) + "%"
        fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 24)
        d.text((540 - (d.textlength(tie_text, font=fnt) / 2), tie_y_coord), tie_text, font=fnt, fill=(255, 255, 255), stroke_width=1)
    img.save("Instagram Posts/Week " + str(week) + "/Win Probabilities " + str(img_number) + ".png") # save image

def create_fantasy_rankings_image(objects_list, object_team_names_list, team_colors, team_mnemonics, position, week, img_number, scoring_format="", schedule={}, starting_num=1):
    '''
    Method to create an image displaying at most 32 players/teams in order of their respective simulated fantasy points.
    param objects_list: the players/teams to display, already in sorted order.
    param object_team_names_list: the team names of the players/teams to display, in the same order as objects_list. Necessary because team name property of Player and Team objects don't have the same name.
    param team_colors: base colors for all 32 NFL teams.
    param team_mnemonics: 2/3 letter abbreviations for all 32 NFL teams. E.g. Chiefs = KC.
    param position: the position of the players.
    param week: the simulated week of the season from which the fantasy points data has been collected.
    param img_number: 1 or 2, depending on whether or not to display players/teams 1-32, or players/teams 33-64.
    param scoring_format: "PPR" or "Non-PPR", based on what scoring system the user wants. Default is standard PPR.
    param schedule: the schedule of the simulated week, to add player matchups to the image.
    param start_num: 1 or 33 depending on which rank to start from. 
    '''
    img = Image.new("RGB", (1080, 1080), color=(1, 51, 105)) # Create 1080 x 1080 image with background color (1, 51, 105) in RGB form
    d = ImageDraw.Draw(img) # Create object to draw to image
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 90) # Set font type and size
    text = "TOP FANTASY " + position + "s " + "(" + scoring_format + ")" if scoring_format != "" else "TOP FANTASY " + position + "s" # Title
    d.text((540 - (d.textlength(text, font=fnt) / 2), 0), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw title to image
    text = "Week " + str(week) # Week text
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 40) # Change font size
    d.text((540 - (d.textlength(text, font=fnt) / 2), 126), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw week text to image
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 36) # Change font size
    current_num = starting_num # current rank for the next player
    for i in range(0, len(objects_list)): # Loop through players / teams
        rectangle_coords = [0, 221 + 50 * i, 540, 271 + 50 * i] if i < 16 else [540, 221 + 50 * (i - 16), 1080, 271 + 50 * (i - 16)] # Position of current player/team rectangle
        x_coord_addon = 15 if (current_num > 9) else 0 # Add-on for x coordinates of some textual objects, if the current rank is 2 digits long
        numbers_coords = (5, 225 + 50 * i) if i < 16 else (545, 225 + 50 * (i - 16)) # Coordinates for rank
        name_coords = (108 + x_coord_addon, 225 + 50 * i) if i < 16 else (648 + x_coord_addon, 225 + 50 * (i - 16)) # Coordinates for current player/team name
        img_coords = (45 + x_coord_addon, 225 + 50 * i) if i < 16 else (585 + x_coord_addon, 225 + 50 * (i - 16)) # Team image coordinates for current player/team
        d.rectangle(rectangle_coords, fill=team_colors[object_team_names_list[i]], outline=(255, 255, 255), width=3) # Draw player/team rectangle, with color of base team color
        d.text(numbers_coords, str(current_num) + ".", font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw player/team rank
        # Get player/team team logo, and appropriately resize (some team logos look better of resized differently)
        team_img = Image.open("Base/Team Logos/" + object_team_names_list[i] + ".png").resize((40, 40)) if (object_team_names_list[i] != "Panthers" and object_team_names_list[i] != "Ravens" and object_team_names_list[i] != "Patriots" and object_team_names_list[i] != "Seahawks" and object_team_names_list[i] != "Broncos" and object_team_names_list[i] != "Football Team" and object_team_names_list[i] != "Jets" and object_team_names_list[i] != "49ers") else Image.open("Base/Team Logos/" + object_team_names_list[i] + ".png").resize((48, 48))
        img.paste(team_img, img_coords, team_img.convert("RGBA")) # Paste team logo to image, maintaining transparency
        name_text = objects_list[i].name
        if "." in name_text: # player name
            if name_text.index(".") >= 2: # have 2 letters before the surname
                name_text = name_text[0] + name_text[name_text.index("."):] # change it so that only their first initial appears in the display
        # Shorten some player names for display aesthetics
        if name_text == "C.Edwards-Helaire":
            name_text = "C.Edwards-Hel."
        elif name_text == "M.Valdes-Scantling":
            name_text = "M.Valdes-Scan."
        elif name_text == "J.Smith-Schuster":
            name_text = "J.Smith-Schus."
        elif name_text == "J.O'Shaughnessy":
            name_text = "J.O'Shaughn."
        elif name_text == "A.Okwuegbunam":
            name_text = "A.Okwuegbun."
        elif name_text == "B.Roethlisberger":
            name_text = "B.Roethlisberg."
        elif name_text == "E.St. Brown":
            name_text = "E.St.Brown"
        elif name_text == "A.St. Brown":
            name_text = "A.St.Brown"
        if schedule != {}: # schedule parameter not empty
            # Find opponent for current player/team, and add it to the text of the player/team name
            for game in schedule:
                if object_team_names_list[i] in game:
                    if game.index(object_team_names_list[i]) < game.index(" at "):
                        name_text += " @ " + team_mnemonics[game[game.index(" at") + 4:]]
                    else:
                        name_text += " vs. " + team_mnemonics[game[0:game.index(" at")]]
                    break
        d.text(name_coords, name_text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw player/team text onto image
        # Get fantasy points for player/team
        fantasy_points = ""
        if scoring_format == "" or scoring_format == "PPR":
            fantasy_points = str(round(np.mean(objects_list[i].all_games_stats["FPTS"]), 2))
        else:
            fantasy_points = str(round(np.mean(objects_list[i].all_games_stats["FPTS"]) - np.mean(objects_list[i].all_games_stats["Rec"]), 2))
        # Ensure 2 decimal places will be displayed
        if len(fantasy_points[fantasy_points.index(".") + 1:]) == 1:
            fantasy_points += "0"
        points_coords = tuple()
        # Set fantasy points coordinates depending on how long the string is
        if len(fantasy_points) == 5:
            points_coords = (451, 225 + 50 * i) if i < 16 else (991, 225 + 50 * (i - 16))
        else:
            points_coords = (471, 225 + 50 * i) if i < 16 else (1011, 225 + 50 * (i - 16))
        d.text(points_coords, str(fantasy_points), font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw player/team fantasy points on image
        current_num += 1 # Increment rank
    img.save("Instagram Posts/Week " + str(week) + "/" + position + " Fantasy Projections " + scoring_format + " " + str(img_number) + ".png") # Save image

def create_power_rankings_image(teams, team_colors, week):
    '''
    Method to create an image of the current power rankings in the NFL.
    param teams: the teams in order.
    param team_colors: base colors for each team.
    param week: the week the power rankings are for.
    '''
    img = Image.new("RGB", (1080, 1080), color=(1, 51, 105)) # Create 1080 x 1080 image with background (1, 51, 105) in RGB form
    d = ImageDraw.Draw(img) # Create object to draw to image
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 90) # Set font type and font size
    text = "POWER RANKINGS" # Title
    d.text((540 - (d.textlength(text, font=fnt) / 2), 0), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw title
    text = "Week " + str(week) # Week text
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 40) # Change font size
    d.text((540 - (d.textlength(text, font=fnt) / 2), 126), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw week text
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 36) # Change font size
    for i in range(0, len(teams)): # Loop through teams
        rectangle_coords = [0, 221 + 50 * i, 540, 271 + 50 * i] if i < 16 else [540, 221 + 50 * (i - 16), 1080, 271 + 50 * (i - 16)] # Rectangle for current team
        x_coord_addon = 15 if (i > 8) else 0 # Add on for x coordinates of some textual objects if rank (i + 1) is 2 digits long
        numbers_coords = (5, 225 + 50 * i) if i < 16 else (545, 225 + 50 * (i - 16)) # Coordinates for rank
        name_coords = (108 + x_coord_addon, 225 + 50 * i) if i < 16 else (648 + x_coord_addon, 225 + 50 * (i - 16)) # Coordinates for team name
        img_coords = (45 + x_coord_addon, 225 + 50 * i) if i < 16 else (585 + x_coord_addon, 225 + 50 * (i - 16)) # Coordinates for team logo
        d.rectangle(rectangle_coords, fill=team_colors[teams[i]], outline=(255, 255, 255), width=3) # Draw team rectangle with white outline on image
        d.text(numbers_coords, str(i + 1) + ".", font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw rank text
        # Get team logo
        team_img = Image.open("Base/Team Logos/" + teams[i] + ".png").resize((40, 40)) if (teams[i] != "Panthers" and teams[i] != "Ravens" and teams[i] != "Patriots" and teams[i] != "Seahawks" and teams[i] != "Broncos" and teams[i] != "Football Team" and teams[i] != "Jets" and teams[i] != "49ers") else Image.open("Base/Team Logos/" + teams[i] + ".png").resize((48, 48))
        img.paste(team_img, img_coords, team_img.convert("RGBA")) # Paste team logo onto image, maintaining transparency
        d.text(name_coords, teams[i], font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw team text
    img.save("Instagram Posts/Week " + str(week) + "/Power Rankings.png") # Save image

def create_primetime_opener_image(road_team, home_team, week, bets, n):
    '''
    Method to create an image to display simulated data about a primetime matchup. Displayed data includes win probabilities, average spread, average total points, and bets.
    param road_team: the road team.
    param home_team: the home team.
    param week: the week of the season that this matchup occurs.
    param bets: bets given by Fanduel Sportsbook, as a list, in the form [road_team spread, total points over/under].
    param n: the number of times the matchup was simulated.
    '''
    img = Image.new("RGB", (1080, 1080), color=(1, 51, 105)) # Create 1080 x 1080 image with background color (1, 51, 105) in RGB form
    d = ImageDraw.Draw(img) # Create object to be able to draw to image
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 96) # Set font type and font size
    text = road_team.name.upper() if road_team.name != "Football Team" else "WASHINGTON" # Road team name text (special case for Washington, since Football Team is too long)
    d.text((270 - (d.textlength(text, font=fnt) / 2), 0), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw road team name text
    text = home_team.name.upper() if home_team.name != "Football Team" else "WASHINGTON" # Home team name text
    d.text((810 - (d.textlength(text, font=fnt) / 2), 0), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw home team name text
    text = str(round(np.mean(road_team.all_games_stats["PTS"]) + np.mean(home_team.all_games_stats["PTS"]), 1)) # Average total points 
    d.text((908.5 - (d.textlength(text, font=fnt) / 2), 784), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw average total points
    field_img = Image.open("Base/Football Field.jpg").resize((1080, 507)) # Image of football field to display team logos on
    img.paste(field_img, (0, 125)) # Paste football field image onto main image
    road_team_img = Image.open("Base/Team Logos/" + road_team.name + ".png").resize((300, 300)) # Road team logo
    img.paste(road_team_img, (121, 213), road_team_img.convert("RGBA")) # Paste road team logo onto image
    home_team_img = Image.open("Base/Team Logos/" + home_team.name + ".png").resize((300, 300)) # Home team logo
    img.paste(home_team_img, (663, 213), home_team_img.convert("RGBA")) # Paste home team logo onto image
    text = "WIN PROBABILITY" 
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 48) # Change font size 
    d.text((189.5 - (d.textlength(text, font=fnt) / 2), 655), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw "WIN PROBABILITY"
    text = "AVERAGE SPREAD"
    d.text((556 - (d.textlength(text, font=fnt) / 2), 655), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw "AVERAGE SPREAD"
    text = "AVG. TOTAL PTS" 
    d.text((908 - (d.textlength(text, font=fnt) / 2), 655), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw "AVG. TOTAL PTS"
    text = "BET"
    d.text((56.5 - (d.textlength(text, font=fnt) / 2), 963), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw "BET"
    text = "-" # Used to display chances of a tie
    d.text((213.5 - (d.textlength(text, font=fnt) / 2), 963), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw "-"
    # Resize team images
    road_team_img = road_team_img.resize((75, 75))
    home_team_img = home_team_img.resize((75, 75))
    # Paste team images again, but lower down
    img.paste(road_team_img, (15, 732), road_team_img.convert("RGBA"))
    img.paste(home_team_img, (15, 851), home_team_img.convert("RGBA"))
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 60) # Change font size
    # Get road and home text colors (Green or Red or Yellow, depending on who has a higher chance of winning)
    road_team_text_color = (77, 255, 12) if road_team.record[0] > home_team.record[0] else ((254, 11, 27) if road_team.record[0] < home_team.record[0] else (253, 252, 1))
    home_team_text_color = (77, 255, 12) if road_team_text_color == (254, 11, 27) else ((254, 11, 27) if road_team_text_color == (77, 255, 12) else (253, 252, 1))
    text = str(round(100 * road_team.record[0] / n, 1)) + "%" # Road win probability
    d.text((212.5 - (d.textlength(text, font=fnt) / 2), 729), text, font=fnt, fill=road_team_text_color, stroke_width=1) # Draw road win probability
    text = str(round(100 * home_team.record[0] / n, 1)) + "%" # Home win probability
    d.text((212.5 - (d.textlength(text, font=fnt) / 2), 848), text, font=fnt, fill=home_team_text_color, stroke_width=1) # Draw home win probability
    avg_spread = -1 * round(np.mean(road_team.all_games_stats["PTS"]) - np.mean(home_team.all_games_stats["PTS"]), 1) # Average simulated spread for road team (negative spread indicates a win)
    text = "+" + str(avg_spread) if avg_spread >= 0 else str(avg_spread) # Road team simulated spread as a string, with "+" added if positive
    d.text((542.5 - (d.textlength(text, font=fnt) / 2), 724), text, font=fnt, fill=road_team_text_color, stroke_width=1)
    text = "+" + str(-1 * avg_spread) if -1 * avg_spread >= 0 else str(-1 * avg_spread) # Home team simulated spread as a string
    d.text((542.5 - (d.textlength(text, font=fnt) / 2), 843), text, font=fnt, fill=home_team_text_color, stroke_width=1)
    # Over/Under total points bet as a string - "U X" if X < points given by Fanduel Sportsbook, otherwise "O X"
    text = "U " + str(bets[1]) if np.mean(road_team.all_games_stats["PTS"]) + np.mean(home_team.all_games_stats["PTS"]) < bets[1] else "O " + str(bets[1])
    d.text((909 - (d.textlength(text, font=fnt) / 2), 963), text, font=fnt, fill=(255, 255, 255), stroke_width=1)
    spread_team = road_team if avg_spread < bets[0] else home_team # Which team to bet spread for
    spread_string = str(bets[0]) if spread_team.name == road_team.name else str(-1 * bets[0]) # Spread text for team to bet spread for
    if spread_string[0] != "-":
        spread_string = "+" + spread_string # Add "+" if spread is positive
    text = spread_string
    d.text((582 - (d.textlength(text, font=fnt) / 2), 963), text, font=fnt, fill=(255, 255, 255), stroke_width=1)
    if spread_team == road_team: # Should bet on road team spread
        img.paste(road_team_img, (433, 971), road_team_img.convert("RGBA")) # Paste road team logo next to spread_string
    else: # Should bet on home team spread
        img.paste(home_team_img, (433, 971), home_team_img.convert("RGBA")) # Paste home team logo next to spread_string 
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 24)
    text = "TIE"
    d.text((52 - (d.textlength(text, font=fnt) / 2), 812), text, font=fnt, fill=(255, 255, 255), stroke_width=1)
    text = str(round(100 - 100 * road_team.record[0] / n - 100 * home_team.record[0] / n, 1)) + "%" # Chance of a tie
    d.text((212.5 - (d.textlength(text, font=fnt) / 2), 812), text, font=fnt, fill=(255, 255, 255), stroke_width=1)
    img.save("Instagram Posts/Week " + str(week) + "/" + road_team.name + " at " + home_team.name + " Opener.png") # Save image

def create_primetime_stat_projections_image(road_team, home_team, week):
    '''
    Method to create an image displaying stat projections for a primetime matchup.
    param road_team: the road team.
    param home_team: the home team.
    param week: the week of the season that this matchup occurs.
    '''
    img = Image.new("RGB", (1080, 1080), color=(1, 51, 105)) # Create a 1080 x 1080 image with background color (1, 51, 105) in RGB form
    d = ImageDraw.Draw(img) # Create an object to draw to the image
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 96) # Set font type and font size
    text = "STAT PROJECTIONS" # Title
    d.text((540 - (d.textlength(text, font=fnt) / 2), 0), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw title
    # Get team logos and paste them onto image
    road_team_img = Image.open("Base/Team Logos/" + road_team.name + ".png").resize((125, 125))
    home_team_img = Image.open("Base/Team Logos/" + home_team.name + ".png").resize((125, 125))
    img.paste(road_team_img, (478, 135), road_team_img.convert("RGBA"))
    img.paste(home_team_img, (781, 135), home_team_img.convert("RGBA"))
    fnt = ImageFont.truetype("Base/Fonts/Abel-regular.ttf", 60) # Change font size
    # Add simulated average completion percentage to image
    text = "COMP. %"
    d.text((15, 391), text, font=fnt, fill=(255, 255, 255), stroke_width=1)
    text = str(round(100 * np.mean(road_team.all_games_stats["PCOMPs"]) / np.mean(road_team.all_games_stats["PATTs"]), 1))
    d.text((540.5 - (d.textlength(text, font=fnt) / 2), 391), text, font=fnt, fill=(255, 255, 255), stroke_width=1)
    text = str(round(100 * np.mean(home_team.all_games_stats["PCOMPs"]) / np.mean(home_team.all_games_stats["PATTs"]), 1))
    d.text((844.5 - (d.textlength(text, font=fnt) / 2), 391), text, font=fnt, fill=(255, 255, 255), stroke_width=1)
    stats = ["PTS", "PYDs", "PTDs", "INTs", "RYDs", "RTDs"] # Stats to display
    texts = ["POINTS", "PASS YARDS", "PASS TDS", "INTS", "RUSH YARDS", "RUSH TDS"] # Texts to display
    y_coord = 281 # y coordinate for next row
    for i in range(0, len(stats)): # Loop through stats
        text = texts[i] # Text for next stat to display
        d.text((15, y_coord), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw text
        text = str(round(np.mean(road_team.all_games_stats[stats[i]]), 1)) # Simulated average stat for road team
        d.text((540.5 - (d.textlength(text, font=fnt) / 2), y_coord), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw road team stat
        text = str(round(np.mean(home_team.all_games_stats[stats[i]]), 1)) # Simulated average stat for home team
        d.text((844.5 - (d.textlength(text, font=fnt) / 2), y_coord), text, font=fnt, fill=(255, 255, 255), stroke_width=1) # Draw home team stat
        y_coord = 501 if i == 0 else y_coord + 110 # Update y coordinate for next row
    img.save("Instagram Posts/Week " + str(week) + "/" + road_team.name + " at " + home_team.name + " Matchup Projections.png") # Save image           