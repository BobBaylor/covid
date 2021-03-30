# covid.py
# The Data Set is no longer maintained 
# This Script is obsolete
## What is this?
A python script to display WHO daily data on covid19 using pandas.
## Why?
Really, to learn a bit of pandas. But also to visualize the world-wide time series of this pandemic.
## How do I use this?
I've only tested this on python 3.7.3
After cloning <br>and creating a new virtual environment, <br>then<br><br>... run
```
pip install -r requirements.txt
```
Pip will take a minute to collect and install all the python packages. Then run
```
python covid.py -h
```
And you will see the command line arguments which should look something like this
```
 Usage:
  covid  [--country=<C>] [--debug=<D>] [--threshold=<T>] [--get] [--lines] [--ids] [--log] [--norm] [--plot] [--multi=<M>]
  covid -h | --help
  covid -v | --version

 Options:
  -c --country <C>        choose geoIds, comma sep, no spaces [default: US,IT,FR,UK]
  -d --debug <D>          print opts,
  -g --get                Get current WHO data.
  -h --help               Show this screen.
  -i --ids                Show a list of the country geoIds.
  -l --lines              Show the data in tabular form.
  -n --norm               Plot normalized to population
  -m --multi <M>          Multi all on one plot. c=cases, d=deaths. lower case for new, upper for totals.
  -o --log                Use log Y scale
  -p --plot               Plot the data.
  -t --threshold <T>      min case count [default: 10].
  -v --version            show the version.
 ```
 You can use the short form of each option (e.g. -i) or the long form (--ids). Options that take an argument should not have
 angle brackets e.g. ```-m d``` instead of ```-m <d>```.
 ### ```--get or -g```
 You only need to do this to get new data from WHO, so, once per day, at most.
 ### ```--ids or -i```
 Displays a list of the country "geoIds" in the WHO dataset. These (mostly) 2 letter codes are how you specify which countries you want
 the script to display.
 ### ```--country or -c <C>```
 Choose which countries ```<C>``` to display. The default shown in the help, above, is USA, Italy, France, and the UK. Your list of country
 codes can only be separated by commas, no spaces. So ```US,IT,FR,UK``` works but not ```US, IT, FR, UK```.
 ### ```--lines or -l```
 Display the data table as text. It uses the pandas defaults, so countries with more than a couple of dozen entries
 will display just the head and tail (first 10 lines and last 10 lines).
 ### ```--log or -o```
 Use log y axis.
 ### ```--multi or -m <M>```
 Display the data for multiple countries on a single plot. ```<M>``` selects between new cases (c), new deaths (d), total cases (C), or total deaths (D).
 ### ```--norm or -n```
 Normalize to the population.
 ### ```--plot``` or ```-p```
 Plot the selected countries each on a separate graph. The graphs appear one after the other. You have to close each graph before the next one
 appears. Yeah, I know. Kinda lame. You probably just want to use ```-m```. The only reason to use ```-p``` is to see cases and deaths on the same plot.
 ## Examples
  * ```python covid.py -g```

    retrieves the current dataset from the World Heath Organization (WHO). Do this, at most, once a day.
  * ```python covid.py -m c -n -c US,FR,ES```

     Plots the daily new cases in the USA, France, and Spain on a single linear scale graph as a percent of the country populations. Remember: the -c county option does not accept anything but commas separating the country codes.
      * todo: more examples?
