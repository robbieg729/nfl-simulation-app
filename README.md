## Table of Contents
1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [Root Files](#root-files)
4. [Sub-directories](#sub-directories)

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
* [Jupyter-Notebook](https://jupyter.org/): Version 6.4.6
***

## Root files
***
The root directory of this project contains several sub-directories, as well as Python (.py) files, and Jupyter Notebook Python (.ipynb) files. The .py files are not intended to be used (they can be viewed) in any form, they are just imported into the .ipynb files and only contain functions, with no options for user input of any kind. The .ipynb files are where all of the simulations occur. Each one performs a specific task and outputs a specific result, which is alluded to in the filename. Some of these files ask for user input when the program is run, others just need to have certain variables edited before run-time.
***

## Sub-directories
***
1. [Base](#base)
2. [Game-Simulations](#game-simulations)
3. [Instagram-Posts](#instagram-posts)
4. [Season-Simulations](#season-simulations)

### Base
The Base sub-directory contains a single .jpg file which is needed for one of the functions in Image_Making.py, and several other directories. "Excel Files" contains templates of various spreadsheets used to store some of the data for each team. "Fonts" contains over 500 font styles, used in Image_Making.py. "Gamebooks" contains .txt files sorted into directories by year and week, which contain the play result for every play from the game specified by the name of the .txt file. The .txt files are a partial match to the PDF Gamebooks from https://nfl.com, and are used to log and write data for each team to Excel files. "Team Logos" contains the franchise logos for all 32 NFL teams, used in Image_Making.py. Finally, "Teams" contains a directory for each NFL team, which in turn contains multiple Excel files which store data necessary to simulate games and obtain desired results.

### Game Simulations
This sub-directory contains Excel spreadsheets, storing results from simulations for every game during the 2021 NFL season. For each week, it also includes a file "Fantasy Projections.xlsx", which contains a list of players sorted by simulated fantasy points for each position.

### Instagram Posts
This sub-directory contains .png files for each week, which display and visualize various results from simulations.

### Season Simulations
This sub-directory contains Excel spreadsheets which store results from simulations such as playoff chances and Super Bowl chances for every NFL team, from different starting points in the season.
***