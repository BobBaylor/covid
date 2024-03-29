""" covid.py

workon covid
get latest data from
https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
https://opendata.ecdc.europa.eu/covid19/casedistribution/csv
pandas quickstart from
https://www.fullstackpython.com/blog/learn-pandas-basic-commands-explore-covid-19-data.html
"""

import os
from datetime import datetime
from math import ceil
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if __name__ == '__main__':
    try:
        import docopt
    except ModuleNotFoundError:
        print(f'docopt import failed for {__name__}. Use an environment with docopt installed, please.')


USAGE_TEXT = """
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
  -t --threshold <T>      min case count [default: 2].
  -v --version            show the version.
    """
DATA_FILE = 'req.csv'

def get_data():
    """ curl https://opendata.ecdc.europa.eu/covid19/casedistribution/csv/ > req.csv
    """
    print('getting file...', end='', flush=True)
    response = requests.get(r'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv/')
    with open(DATA_FILE, 'w') as csv_f:
        csv_f.write(response.text)
    print('done')

def show_all_country_codes(df):
    """print a list of the geoIds and country names
       in as many columns as will fit. Harder than it sounds if you want alpha order
       to go down, then across instead of across, then down.
    """
    c_and_t = df.countriesAndTerritories.unique()
    geo_ids = df.geoId.unique()
    ids_and_cntry = list(zip(list(geo_ids), list(c_and_t)))

    # how many columns fit on the screen?
    fmt_one = '%5s %-34s'             # each colum is this wide (40)
    spacer = ' '                      # between columns
    terminal_size = os.get_terminal_size()                  # returns a named tuple
    # divide screen by column width to get the count of columns
    #
    col_count = terminal_size.columns// (len(spacer)+len(fmt_one%('', '')))
    col_length = int(ceil(len(ids_and_cntry)/col_count))        # so, this many rows
    col_remainder = col_length * col_count - len(ids_and_cntry) # blank entries for last column

    # rearrange into a list of col_count lists
    cols = [ids_and_cntry[i*col_length:(i+1)*col_length] for i in range(col_count-1)]
    cols += [ids_and_cntry[(col_count-1)*col_length:],]

    # last column may get up to col_count-1 extra blank entries
    blank_pair = ('', '')
    cols[-1] += [blank_pair,]*col_remainder  # this syntax took a while to get right :-/

    # now that the columns are all the same length, zip them into rows
    rows = list(zip(*cols))   # each row looks like [[id, cntry],[id, cntry],[id, cntry],]
    for row in rows:
        print(spacer.join([fmt_one%tuple(pair) for pair in row]))


def show_country_stats(df, country_id):
    """the grim stats of the selected df """
    df3 = df[df['geoId'] == country_id]
    pop = df3.iloc[0]['popData2019']
    d_cum = df3.iloc[-1]['total deaths']
    c_cum = df3.iloc[-1]['total cases']
    print(f'sum of cases:  {c_cum:8,}  ({(100.0*c_cum/pop):.2f}% of 2019 population)')
    print(f'sum of deaths: {d_cum:8,}  ({(100.0*d_cum/pop):.2f}% of 2019 population)')


def show_country_name(df, country_id):
    """grab the name from the 1st entry of the selected df """
    df3 = df[df['geoId'] == country_id]
    country_name = df3.iloc[0]['countriesAndTerritories']
    print(f'\n{country_id} ({country_name}):')


def display_one_country(opts, df, country):
    """Plot/list/stat a single country on a single graph
    """
    show_country_name(df, country)     # display the full country name from the df

    # select a single country
    df3 = df[df['geoId'] == country]
    if opts['--lines']:
        print(df3)
    show_country_stats(df3, country)
    if opts['--plot']:
        plot_one_country(opts, df3)


def plot_multi_countries(opts, df, countries):
    """Plot/stat all selected countries on a single graph.
    """
    for country in countries.split(','):
        show_country_name(df, country)
        show_country_stats(df, country)

    df3 = df[df['geoId'].isin(countries.split(','))]
    df4 = df3[['Date',
               'geoId',
               'daily cases',
               'daily deaths',
               'total cases',
               'total deaths',
               'popData2019',]]

    y_col = {'c':'daily cases',
             'd':'daily deaths',
             'C':'total cases',
             'D':'total deaths'}[opts['--multi']]
    norm_str = ' (% of pop)' if opts['--norm'] else ''
    title = f'{y_col}{norm_str}'

    fig, ax = plt.subplots(figsize=(8, 5))          # 8 wide by 4 tall seems good

    # groupby is magic.   https://realpython.com/pandas-groupby/
    for key, grp in df4.groupby(['geoId']):
        if opts['--norm']:
            y_norm = grp.iloc[0]['popData2019'] * 1e-2
            y_str = f'{(grp.iloc[-1][y_col]/y_norm):0.3f} '
        else:
            y_str = f'{int(grp.iloc[-1][y_col]):8,} '
            y_norm = 1.0
        ax.plot(grp['Date'], grp[y_col]/y_norm, label=y_str+key, linewidth=7)

    ax.legend()                                     # show the legend
    if opts['--log']:
        ax.set_yscale('log')                            # log y axis to see slope
        plt.ylim(bottom=int(opts['--threshold'])//2)
    else:
        plt.autoscale()

    ax.set_title(title)

    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))  # every week x ticks
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # major x: the first of every month
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b 1')) # x labels month day

    plt.grid(which='major', axis='both')             # show both major axis
    plt.grid(which='minor', axis='y', ls='dotted')   # show y minor as dotted
    fig.autofmt_xdate()       # rotate, right align, and leave room for date labels
    plt.show()


def plot_one_country(opts, df):
    """A simple plot of 1 country
       select just the columns I want to plot
    """
    title = df.iloc[0]['countriesAndTerritories']

    df4 = df[['Date', 'daily cases', 'daily deaths', 'total cases', 'total deaths']]

    fig, ax = plt.subplots(figsize=(8, 5))          # 8 wide by 4 tall seems good
    if opts['--log']:
        ax.set_yscale('log')                            # log y axis to see slope

    ax.xaxis.set_minor_locator(mdates.DayLocator())  # every day x ticks
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))  # major x:Mondays
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) # x labels month/day

    plt.grid(which='major', axis='both')             # show both major axis
    plt.grid(which='minor', axis='y', ls='dotted')   # show y minor as dotted
    fig.autofmt_xdate()       # rotate, right align, and leave room for date labels
    df4.plot(x='Date',
             kind='line',
             grid=True,
             ax=ax,
             logy=opts['--log'],
             title=title,
             linewidth=7,)
    ax.legend()                                     # show the legend
    plt.show()


def test(opts):
    """Do the various things as requested
    """
    print('*'*60, '\n'+'*'*60)
    if opts['--debug']:
        print(opts)

    if opts['--get']:
        get_data()       # go ask the WHO server for a new csv and save it

    df = pd.read_csv(DATA_FILE, encoding='ISO-8859-1')
    f_date = datetime.fromtimestamp(os.path.getmtime(DATA_FILE))
    print(f'Data were retrieved {f_date:%B %d, %Y at %H:%M %p}')

    # clean the data a little. That cruise ship has the longest id strings in the whole df
    df.replace('Cases_on_an_international_conveyance_Japan',
               'Diamond_Princess_Japan',
               inplace=True)
    df.replace('JPG11668',
               'JPCS',
               inplace=True)

    if opts['--ids']:
        show_all_country_codes(df)  # show geo_ids in country alpha order

    df = df.iloc[::-1]        # reverse the df so that totals plot older to newer

    # make plotable date and rename the cases and deaths for plotting
    # I do it before selecting by country to avoid the SettingWithCopy warning
    # which is pandas saying 'you're modifying a copy, not the actual dataset'

    # WHO changed the data set! ggrrr
    # new columns as of 2020-12-17
    # dateRep,year_week,cases_weekly,deaths_weekly,countriesAndTerritories,geoId,countryterritoryCode,popData2019,continentExp,notification_rate_per_100000_population_14-days
    # and, again!
    # dateRep,day,month,year,cases,deaths,countriesAndTerritories,geoId,countryterritoryCode,popData2019,continentExp,Cumulative_number_for_14_days_of_COVID-19_cases_per_100000
    # 14/12/2020,14,12,2020,189723,1340,United_States_of_America,US,USA,329064917,America,873.21159186

    df['Date'] = pd.to_datetime(df.dateRep, format='%d/%m/%Y')
    df['total deaths'] = df.groupby(['countriesAndTerritories'])['deaths'].cumsum()
    df['total cases'] = df.groupby(['countriesAndTerritories'])['cases'].cumsum()
    df['daily cases'] = df['cases'].rolling(window=7).mean()
    df['daily deaths'] = df['deaths'].rolling(window=7).mean()
    # df['cases'] = df['cases_weekly'].divide(7.0)
    # df['deaths'] = df['deaths_weekly'].divide(7.0)

    max_date = df['Date'].max()
    print(f'Most recent date point is {max_date:%B %d, %Y at %H:%M %p}')
    # only keep what I care about
    df = df[['geoId',
             'countriesAndTerritories',
             'Date',
             'daily cases',       # 7 day running averages
             'daily deaths',
             'cases',           # actual dailies
             'deaths',
             'total cases',
             'total deaths',
             'popData2019',
             ]]

    # filter out small numbers of cases in a day
    df2 = df[df['daily cases'] >= int(opts['--threshold'])]

    plt.close('all')
    countries = opts['--country'].upper()
    if opts['--multi']:
        plot_multi_countries(opts, df2, countries)
    else:
        for country in countries.split(','):
            display_one_country(opts, df2, country)


if __name__ == '__main__':
    opts = docopt.docopt(USAGE_TEXT, version='0.0.4')
    test(opts)
