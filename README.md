## Table of Contents
1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [.py files](#.py-files)
4. [.ipynb files](#.ipynb-files)
5. [Sub-directories](#sub-directories)

## General Info
***
This project uses real, current data from all 32 teams in the National Football League (NFL), that can be used to simulate NFL games and create various results such as win probabilities, playoff chances, fantasy rankings, and win probability charts. The results are then stored into Excel files, or in some cases, manipulated and displayed through graphics which are then posted on an Instagram page, @nflstatguy. Programs are coded fully using Python, with the help of several packages such as NumPy and Pandas.
***

## Technologies
***
The technologies used in this project are:
* [Python](https://www.python.org/): Version 3.8.5
* [NumPy](https://numpy.org/): Version 1.19.2
* [Pandas](https://pandas.pydata.org/): Version 1.1.3
* [SciPy](https://scipy.org/): Version 1.5.2
* [Matplotlib](https://matplotlib.org/): Version 3.3.2
* [Fitter](https://fitter.readthedocs.io/en/latest/): Version 1.2.3
* [Pillow](https://pypi.org/project/Pillow/): Version 8.0.1
* [Jupyter Notebook](https://jupyter.org/): Version 6.4.6
***

## .py files
***
The .py files are intended to be viewed only, not used. They have no options for user input, contain only functions, and are simply imported into the .ipynb files for simulation.
1. [Classes](#classes)
2. [Gamelog](#gamelog)
3. [Image_Making](#image_making)
4. [Other_Functions](#other_functions)
5. [Simulate](#simulate)
6. [Simulate_Season](#simulate_season)

### Classes
Classes.py contains the class definitions needed for simulations. It contains a class Team, which is only used for logging data, a class Player, which is used when logging data and during simulations, and a class SimulationTeam, which is a sub-class of Team, and is used only during simulations.

### Gamelog
Gamelog.py contains functions necessary for logging data. The log_game function takes two Team variables and the gamebook from their matchup, and reads each line from the gamebook to update class variables in each Team object. The function write_team_data_to_excel_files then writes the updated data back into an Excel Spreadsheet.

### Image_Making
Image_Making.py contains various functions which create graphics for social media, based on inputted data. The functions make use of the Python Imaging Library (PIL) to create and draw to images.

### Other_Functions
Other_Functions.py contains functions that need to be accessed by multiple .py or .ipynb files, such as return_best_fit_in_str_format, and bubble_sort_by_fpts.

### Simulate
Simulate.py contains the base simulate() function, which describes the algorithm for simulating games. All of the .ipynb files and any .py files that involve simulation make use of this file. The file contains other functions which continuously update stats for the teams and players involved in the simulation.

### Simulate_Season
Simulate_Season.py uses the simulate() function from Simulate.py to simulate an entire season of the NFL (or from a given starting point). The file contains other functions which continuously update stats for the teams and players involved in the simulation.
***

## .ipynb files
***
The .ipynb files are intended to be used as well as viewed. Each of them perform a specific task which is described by the filename, and involve user input of some form.
1. [Distribution_Getter](#distribution_getter)
2. [Log_Week](#log_week)
3. [Power_Rankings_Image](#power_rankings_image)
4. [Simulate_Single_Game](#simulate_single_game)
5. [Simulate_Single_Season](#simulate_single_season)
6. [Simulate_Single_Week](#simulate_single_week)
7. [Single_Game_Win_Probability_Chart_Maker](#single_game_win_probability_chart_maker)
8. [Situational_Win_Probability_Calculator](#situational_win_probability_calculator)
9. [Playoffs_Simulator](#playoffs_simulator)

### Distribution_Getter
Distribution_Getter.ipynb calculates the best fit to a statistical distribution for every team's offensive and defensive rush and pass yards. These best fits are used in the simulate() function to generate random variables corresponding to a yardage gain on a single play. The best fits are written into Excel spreadsheets, so that they can be accessed by Simulate.py.

### Log_Week
Log_Week.ipynb updates team and player data for every team from a single week, and re-writes it back to Excel. All the user would need to do is specify the year and week before run-time, and the program will take care of the rest.

### Power_Rankings_Image
Power_Rankings_Image.ipynb creates and saves a graphic displaying the user-given power rankings of all 32 NFL teams. Before run-time, the user must specify the week of the season which the power rankings are for (usually the number of the week after the one that has just been played). Once the program is run, the user will be prompted to enter their power rankings, from 1 to 32, but their input must obey the format given in the team_mnemonics variable. So if they wanted to enter the Arizona Cardinals for a certain rank, they would type "ARI" and hit Enter. The user would then automatically be prompted to enter the next team, and so on.

### Simulate_Single_Game
Simulate_Single_Game.ipynb prompts the user to input a road team and a home team, and proceeds to simulate that matchup for a certain number of times, which is controlled by the variable n. The program then prints various statistics from the simulations, including the overall number of wins for each team from n simulations. Note that simulating a matchup 1,000 times will take around 20 seconds, so the user should not go too big on the variable n, especially considering that the results do not change that much when n = 10,000 compared to n = 1,000.

### Simulate_Single_Season
Simulate_Single_Season.ipynb simulates a single season of the NFL, including playoffs, and writes results such as Super Bowl chances and playoff chances for each team to a single Excel file in the "Season Simulations" sub-directory. The user can specify the week to start simulating from, and the number of times to simulate the season, before run-time.

### Simulate_Single_Week
Simulate_Single_Week.ipynb simulates a full week of the NFL season, and outputs results of game simulations to Excel files, as well as calculating fantasy projections for players which are displayed via graphics and saved to the "Instagram Posts" sub-directory. User input can get a little tricky here and I am currently working on a better solution, but the variables that the user needs to specify before run-time are the schedule of the week, the week of the year being simulated, the number of times to simulate each game, and bets given by [FanDuel Sportsbook](https://sportsbook.fanduel.com/). Comments in the actual code explain this further.

### Single_Game_Win_Probability_Chart_Maker
Single_Game_Win_Probability_Chart_Maker.ipynb simulates a game n times, from the beginning of every play in the game, saves the win probabilities at each time for one of the teams, and generates a line graph showing win probability against time. User input for this program is also a bit tricky, as there is no option to just specify a game from the season, because the program requires an Excel spreadsheet with the initial_variables (see simulate() function in Simulate.py) at the beginning of every play, which is difficult to generate for a game. The example given in the code currently is the Chiefs-Bengals game from Week 17, 2021, where the Bengals were down 14-0, 21-7, and 28-14, but came back to win 34-31. For now, the user can just run this program and see the kind of input it generates, though it can take a while for all the simulations to complete (the user can again specify the variable n to control the number of simulations at each play).

### Situational_Win_Probability_Calculator
Situational_Win_Probability_Calculator.ipynb allows evaluation of in-game decisions by Head Coaches, by calculating a teams win probability by attempting a certain play in a certain situation. For example, if a team was deciding whether or not to go for a touchdown on 4th and Goal at the 1 in a tied game late in the fourth quarter, the win probabilities for a run, pass, or field goal attempt could be calculated. The example that currently runs in the code is just that, involving Bengals Head Coach Zac Taylor's late decisions to go for it on 4th down against the Chiefs in Week 17 of the 2021 season. Currently working on a way to involve more user input.

### Playoff_Simulator
Playoff_Simulator.ipynb is a program which can simulate the playoffs once the regular season is finished. It is able to calculate results such as Super Bowl probabilities for each team, and most likely Super Bowl matchups, at a given point in the playoffs. Currently set to the beginning of the 2021 Conference Championship round.
*** 

## Sub-directories
***
1. [Base](#base)
2. [Game Simulations](#game-simulations)
3. [Instagram Posts](#instagram-posts)
4. [Season Simulations](#season-simulations)

### Base
The Base sub-directory contains a single .jpg file which is needed for one of the functions in Image_Making.py, and several other directories. "Excel Files" contains templates of various spreadsheets used to store some of the data for each team. "Fonts" contains over 500 font styles, used in Image_Making.py. "Gamebooks" contains .txt files sorted into directories by year and week, which contain the play result for every play from the game specified by the name of the .txt file. The .txt files are a partial match to the PDF Gamebooks from the [NFL Website](https://nfl.com), and are used to log and write data for each team to Excel files. "Team Logos" contains the franchise logos for all 32 NFL teams, used in Image_Making.py. Finally, "Teams" contains a directory for each NFL team, which in turn contains multiple Excel files which store data necessary to simulate games and obtain desired results.

### Game Simulations
This sub-directory contains Excel spreadsheets, storing results from simulations for every game during the 2021 NFL season. For each week, it also includes a file "Fantasy Projections.xlsx", which contains a list of players sorted by simulated fantasy points for each position.

### Instagram Posts
This sub-directory contains .png files for each week, which display and visualize various results from simulations.

### Season Simulations
This sub-directory contains Excel spreadsheets which store results from simulations such as playoff chances and Super Bowl chances for every NFL team, from different starting points in the season.
***