'''
Driver's Top Qualifying Tracks Analyzer

Find any driver's best qualifying tracks (depending on the selected range of years)

Author: Jazib Ahmed
'''
from fastf1.plotting import get_team_name_by_driver, get_driver_names_by_team, get_driver_abbreviation
import fastf1
import matplotlib.pyplot as plt
from datetime import timedelta

fastf1.Cache.enable_cache('fastf1_cache')

#-----------------------------------
# Change the variables here for different years/different drivers
yearstart = 2022
yearend = 2024

target_driver = 'Charles Leclerc'

# Number that marks how many top qualifying tracks to show (set by default to top 7 qualifying tracks)
topqualirange = 7

# Limit to exclude qualifying gaps that are outliers (in seconds)
outlierlimit = 2

# Set the title and chart/font size/bar color for the analysis
chart_title = target_driver + "'s Top "+str(topqualirange)+" Qualifying Tracks (" + str(yearstart) + " - "+ str(yearend) + ")"
chartsize = (20,6) #((width, height))
fontsize = 20
bar_color = "maroon"
#----------------------------------

years = range(yearstart,yearend+1)
driver1qualigap = {}

def format_lap(laptime):
    # Format the average difference with a '+' or '-' sign at the front
    if laptime < timedelta(0):
        # If negative, format it with a '-' sign
        formatted_diff = "-" + f"{abs(laptime)}"[13:19]
    else:
        # If positive or zero, format it with a '+' sign
        formatted_diff = "+" + f"{laptime}"[13:19]
    return formatted_diff

#Going through the range of  years
for year in years:
    # Getting all the races from that year
    calendar = fastf1.get_event_schedule(year,include_testing = False)
    races = list(calendar['EventName'])

    # Going through each race
    for race in races:
        # If driver was not in the qualifying for the race that year
        if race not in driver1qualigap.keys():
            driver1qualigap[race] = []

        # Loading a qualifying session
        session = fastf1.get_session(year, race, 'Q')
        session.load(telemetry=False,weather=False,messages=False)
        # Getting the names of all drivers
        drivers = " ".join(list(session.results['FullName'].str.lower()))

        # If driver exists in the list of drivers
        if target_driver.lower() in drivers:

            # Find teammate by checking who else is in the same team
            target_team = get_team_name_by_driver(target_driver,session)
            drivers = get_driver_names_by_team(target_team,session)

            teammate = None
            for drv in drivers:
                if target_driver.lower() not in drv.lower():
                    teammate = drv
                    break

            # Get driver abbreviations and load their laps with them
            abrev1 = get_driver_abbreviation(target_driver, session)
            abrev2 = get_driver_abbreviation(teammate, session)

            driverslap = session.laps.pick_drivers(abrev1).pick_fastest()['LapTime']
            teammateslap = session.laps.pick_drivers(abrev2).pick_fastest()['LapTime']

            # Add the qualifying gap to teammate
            driver1qualigap[race].append((driverslap-teammateslap))

# Getting rid of outliers
no_outliers = {k:[v[i] for i in range(len(v)) if -outlierlimit < float(format_lap(v[i])) < outlierlimit]
for k, v in driver1qualigap.items() if v}

# Getting the average gap to teammate for the track and formatting it
processed = {k: float(format_lap(sum(v,timedelta())))/len(v) for k, v in no_outliers.items() if v}

# Get the 7 most negative deltas (lowest values)
lowest7 = dict(sorted(processed.items(), key=lambda item: item[1])[:topqualirange])

# X-axis labels showing which race each bar corresponds to
xlabels = [key[:-10] + "GP" for key in lowest7.keys()]

plt.style.use('dark_background')

# Plotting
plt.figure(figsize=((topqualirange-1)*2, 8),facecolor="#1E1E1E")
plt.gca().set_facecolor("#1E1E1E")  # This sets the axes (plot area) background

# Extra settings for the chart
bars = plt.bar(xlabels, lowest7.values(), color=bar_color)
plt.axhline(0, color='gray', linewidth=0.8)
plt.title(chart_title,fontsize = 23)
plt.ylabel("Average Qualifying Gap to Teammate (s)",fontsize = fontsize)
plt.xticks(rotation=45,fontsize = fontsize)
plt.yticks(fontsize = fontsize)

# Set y-axis to start at 0 and extend downward
ymax = min(lowest7.values()) * 1.15
plt.ylim(0, ymax)  # Add small buffer below lowest bar

# Annotate bars with the average gap texts
for bar in bars:
    yval = bar.get_height() + (ymax/25)
    plt.text(bar.get_x() + bar.get_width()/2, yval, round(bar.get_height(),3), ha='center', va='top',fontsize = fontsize)

plt.tight_layout()
plt.show()
