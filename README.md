# LinkedinAnalyzer
SI 507 Final Project, Fall 2021, University of Michigan.

## Set up
- Download the required packages in requirements.txt using `pip install -r requirements.txt` <br>
    - dash==2.0.0 <br>
    - lotly==5.4.0 <br>
    - inkedin-api~=2.0.0 <br>
    
- Or run the below pip command separately <br>
    - pip install linkedin-api <br>
    - pip install dash <br>
    - pip install plotly<br>
    
## API key
- This API (https://github.com/tomquirk/linkedin-api) requires the user to log in with their own username and password to access the information. I will log in using my personal LinkedIn account. My personal login information is saved in the `secrets.py` file within the folder. When running the main file: `totalPlot.py`, it would not require additional steps connecting to the API.

## Interaction
- Step 1: cd to the directory, install the required packages, run `python totalPlot.py` in the terminal
- Step 2: Type in either `Adobe`, `Spotify`, `Pfizer` in the pop out command line input: `Type in one of the three companies you want to know about: `
- Step 3: Open `http://127.0.0.1:8050/` in browser, it will show the plots plotted using Dash
