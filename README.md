# JoyType
This program requires at least Python ver. 3.9.6 for best results. Lower versions may work but are untested. The instructions are written in the context of windows. Adjust as necessary for UNIX.

How to Run:
1. Run `pip install -r requirements.txt` to install the required dependencies.
2. Make sure your Xbox controller is turned on and connected. The program will raise an error and require a restart if there is no controller detected.
3. Run `python.exe .\main.py` to start the program.
4. The menu requires use of the keyboard arrow buttons. The mode can be set with the left and right arrows. Start can be selected with the Enter key or the A button.
5. Runs will be saved only when "Save and Quit" is selected. Make sure to select this rather than closing with other methods.

Output Details:
The output produced from each complete set of runs is a .json file located in /output. See the sample provided for an example of the output. The output can be further processed by running `python.exe .\efficiencyCalc.py` after all trials have been run. This will produce a .json file containing the efficiency and other relvant data for each of the user trials.