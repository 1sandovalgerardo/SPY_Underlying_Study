import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_data(filepath, startdate):
    '''
    Inputs: 
    filepath: is the location of the excel file containing the ticker symbols you want to 
    download data for.
    
    startdate: start date for downloading data.
    
    Returns: Pandas DataFrame containing the close price for each ticker on the list.
    Index will be timeseries.
    columns will be the ticker symbol
    
    '''
    file = pd.read_excel(filepath)
    tickers = file['Identifier']
    startdate=startdate
    
    data = pd.DataFrame()
    status = 0
    for ticker in tickers:
        data[ticker] = web.DataReader(ticker, data_source='yahoo',\
                                     start=startdate)['Close']
        status +=1
        print(status, end=',')
    print()
    print(data.shape)
    return data


def my_summary(df):
    '''
    Takes in a DataFrame. 
    Returns a DataFrame containing statistical summaries of the data
    '''
    import pandas as pd
    assert type(df)==type(pd.DataFrame()), 'Input not type Pandas DataFrame.'
    d = {}
    columns=['std', 'max','max date', 'min', 'min date', 'mean', 'median']
    index = df.columns
    funcs = [df.std(), df.max(), df.idxmax(), df.min(), df.idxmin(),
            df.mean(), df.median()]
    for item in df:
        for num in range(len(columns)):
            d[columns[num]] = funcs[num]

        
    return pd.DataFrame(d, columns=columns)

def UpperLowerBounds(df):
    '''
    Takes in a DataFrame and returnds the 1 standard deviation bounds
    of the data. The return object is type pandas.DataFrame.
    Can also take in a list or tuple of DataFrames.
    '''
    if type(df) == list or type(df) == tuple:
        assert type(df[0]) == type(pd.DataFrame()), 'List does not contain type DataFrame'
        bounds = []
        for item in df:
            bounds.append(UpperLowerBounds(item))
        return bounds
    else:
        assert type(df)==type(pd.DataFrame()), 'Input not type Pandas DataFrame.'
        upper = df.mean() + df.std()
        lower = df.mean() - df.std()
        bounds = pd.DataFrame([upper, lower], index=['UpperBounds', 'LowerBounds'])
        return bounds

def TimesBoundsExceeded(data):
    '''
    Takes in a DataFrame and returnds the 1 standard deviation bounds
    of the data. The return object is type pandas.DataFrame.
    Can also take in a list or tuple of DataFrames.
    If a list in entered, the returned item is a list of DataFrames. 
    In this list, each index = the result of DataFrame in respective order of how they were contained 
    in the list.
    '''
    if type(data) == list or type(data) == tuple:
        assert type(data[0]) == type(pd.DataFrame()), 'List does not contain type DataFrame'
        bounds = []
        for item in data:
            bounds.append(TimesBoundsExceeded(item))
        request = pd.DataFrame(bounds)
        return request
    else:
        assert (type(data)==type(pd.DataFrame())), 'Input not type Pandas DataFrame.'
        upper = data > UpperLowerBounds(data).loc['UpperBounds']
        lower = data < UpperLowerBounds(data).loc['LowerBounds']
        count = data[upper].count() + data[lower].count()
        return count
    
    
def ShowYear(data, year):
    '''
    takes in pd.DataFrame and either an int or list or tuple.
    If list or tuple is passed in for year, data must be type int. 
    The return item will be a dictionary where the keys are the str of
    the years that where input.
    
    If an int is passed in for year, a data will be returned filtered by 
    the year.
    '''
    if (type(year) == list) or (type(year) == tuple):
        request = {}
        for n in year:
            assert type(n) == int, 'Year must contain type int.'
            cut = ShowYear(data, n)
            request[n] = cut
        return request
    else:
        choose = data.index.year == year
        return data[choose]
    
def YearsContained(data):
    '''
    Purpose: return the years the data contains.
    Input: pd.DataFrame where the index values are datetime 
    Output: a list containing the years found in the index.
    '''
    years = []
    if (type(data.index) != pd.core.indexes.datetimes.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
        return YearsContained(data)
    else:    
        for year in data.index.year:
            if year in years:
                pass
            else:
                years.append(year)
        return years

def ByYear(data, year):
    '''
    Input:
      pd.DataFrame or list/tuple. If list/tuple, values must be
      type pd.DataFrame as well
    
    If list or tuple is passed in for year, data must be type int. 
    The return item will be a dictionary where the keys are the str of
    the years that where input.
    
    If an int is passed in for year, a data will be returned filtered by 
    the year.
    '''
    if (type(year) == list) or (type(year) == tuple):
        request = {}
        for n in year:
            assert type(n) == int, 'Year must contain type int.'
            cut = ByYear(data, n)
            # replaces timedate index with int range.
            cut.index = range(1,(len(cut)+1))
            request[n] = cut
        return request
    else:
        choose = data.index.year == year
        return data[choose]


def ByStockAndYear(data):
    '''
    Purpose: take dataframe of stock's data and return it 
        broken down by stock and year.
    Input: pd.DataFrame 
    Returns: Dictionary where keys=tickers and values=DataFrame.
        Within the Values, the columns are calendar years and 
        the index are the number day in the year.
    '''
    # if data for one stock is entered
    data.index = pd.to_datetime(data.index)
    if type(data) == pd.Series:
        request = ByYear(data, YearsContained(data))
        request = pd.DataFrame(request)
        return ByYear(data, YearsContained(data))
    
    # if data for multiple stocks is entered
    else:
        tickers = data.columns
        request = {}
        for ticker in tickers:
            getStockYears = ByYear(data[ticker], YearsContained(data))
            getStockYears = pd.DataFrame(getStockYears)
            request[ticker] = getStockYears
        return request
    
    
def CorrOverN(data, n): 
    '''
    Purpose: take a dataset and return the values where correlation is >=
        or <= to n.
    input: data frame
    output: correlation table 
    '''
    if type(n) == list:
        Ns = []
        for item in n:
            Ns.appen(item)
        test = (data>Ns[0]) | (data<Ns[1])
        return data[test]
    else:
        test = (data > n) | (data < -n)
        return data[test]
    
def CorrelationTest(data, r):
    '''
    Input Type: pd.DataFrame
    Input: DataFrame that was the output of the an output of the byStockAndYear function.
        DataFrame must be for a single stock. 
    Output: The instances in which the correlation was >= or <= to r.
        All corr values of 1 are excluded.
    Purpose: a test to see if there is any correlation in the data by year.
    '''
    data = data.corr() 
    test = ((data >= r) | (data <= -r)) & (data != 1)
    request = data[test].unstack().sort_values().dropna()
    if len(request) == 0:
        return print('There were no instances that met your criteria')
    return request.drop_duplicates()

def CorrSlideShow(data):
    '''
    Input a dictionary whose values are dataframes.
    Output: yields correlation matrix by years.
    Note: yield is being used. Should you wish to advance,
    you will have to use next()
    '''
    assert type(data) == dict, 'Input must be type dictionary.'
    for year in data:
        yield print(str(year),'\n',data[year].corr())
        
def SeasonCorrTest(dataDict, dropNum, n):
    '''
    Input: pandas correlation matrix
        dropNum: the number used to determine how many NaN must be
        present in a column for the column to be dropped.
        n: the desired correlation level minimum
    Output: DICTIONARY whose keys are the ticker symbols.
        Values are DataFrame Correlation Matrixs that contain 
        True values if the dropNum and correlation test level
        is met (n).
    '''
    request = {}
    for stock, df in dataDict.items():
        test = (((df >= n) | (df <= -n)) & (df < 0.99))
        request[stock] = df[test].unstack(level=0).dropna(axis=1, thresh=dropNum)\
                            .unstack().dropna()
        print(f'{stock} completed')
    return request
        
def JustDaysCorrelated(data):
    '''
    Input: returned item from func: SeasonCorrTest()
    Output: dictionary. Key=stock, value= pd.series of the days
        that had high correlation. High correlation was established in 
        SeasonCorrTest()
    '''
    request = {}
    for stock in data:
        days = []
        for n in range(len(data[stock].index)):
            a, b, c = data[stock].index[n]
            days.append(b)
        days = list(set(days))
        days.sort()
        request[stock] = days
    return request
        
def CycleRollingCharts(data):
    '''
    Input: byStockAndYear[ticker]
    Output: 3 pane chart where the charts cycle in the pattern abc, bcd, cde...
    Area for Improvement: a better method for showing the next chart. Clear() works ok.
        Labeling and add key.
        Change the color of the lines.
        Must change chart dimensions to better fit the window.
    '''
    for stock, value in data.items():
        for i, year in enumerate(value.columns):
            # axes = pane; 0=top, 1=middle, 2=bottom
            fig, axes = plt.subplots(3,1)
            axes[0].set(ylabel=year+2)
            axes[1].set(ylabel=year+1)
            axes[2].set(ylabel=year)
            axes[0].plot(value[year+2])
            axes[1].plot(value[year+1])
            axes[2].plot(value[year])
            print(i)
            yield plt.show()   