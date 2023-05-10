# F1-22-Telemetry
Software that creates stat cards for the performance of drivers in a race.

New Project (31)

This is an application that uses the f1 22 UDP parser project created by raceweek telemetry. Data is collected throughout a race and then can be analysed such that each driver who participated in a race will have their own stat card, consisting of calculated ratings for their performance. These ratings include an overall, pace, consistency, racecraft and safety rating.

For this project to work, users will need to change their udp telemetry settings in the f1 22 game, such that "show online ids" is set to on as well as the ip address being set to the receiving machines ip address. NOTE: The same internet must be used between console/pc and receiving device running this application.

To run this project, make sure all modules from nodejs and python files have been downloaded (cd into the folder "process", run "npm i"), then cd back into the root directory and run app.py file. Furthermore, you can edit the analyse file for a particular race, and re - analyse the data if the race files have been changed. Output data can be found in the "data" folder, where users can see created images and statistics.

NodeJs modules used: canvas f1-22-udp ip propmt-sync python-shell

Python modules used: sys math PIL kivy subprocess
