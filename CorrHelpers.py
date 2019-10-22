# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 14:15:00 2019

@author: Gerardo Sandoval
"""
import pandas as pd
import numpy as np


def YearsContained(data):
    """
    Purpose: Return the years found in the data.
    Input: pd.DataFrame where the index values are datetime.
    Output: a list containing the years found in the index.
    """
    if (type(data.index) != pd.core.indexes.datetimes.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
        return YearsContained(data)
    else:
        return sorted(list(set(data.index.year)))
    ''' original method but simplified using set.
        for year in data.index.year:
            if year in years:
                pass
            else:
                years.append(year)
        return years
    '''


def ByYear(data, year):
    '''
    Input: data=pd.DataFrame containing multiple stock or single stock data.
           year=int(calendar year) or a list of years. You can use
                YearsContained in this keyword to simply your code.
    Output: If data=single stock data and year=single year, then a pd.Series
            is returned.
            If data=multiple stocks and year=single year, then a pd.DataFrame
            is returned.
            If data=multiple or single stock and year=multiple years,
            then a dictionary is returned. the key=calendar years and
            the value=data.
    '''
    if type(data.index) != pd.core.indexes.datetimes.DatetimeIndex:
        try:
            data.index = pd.to_datetime(data.index)
        except Exception as exception_object:
            print('Can not conver index type to Datetime', exception_object)
    if (type(year) == list) or (type(year) == tuple):
        request = {}
        for n in year:
            assert type(n) == int, 'Year must contain type int.'
            cut = ByYear(data, n)
            # replaces timedate index with int range.
            cut.index = range(1, (len(cut)+1))
            request[n] = cut
        return request
    else:
        return data[data.index.year == year]


def ByStockAndYear(data):
    '''
    Purpose: take dataframe of stock's data and return it
        broken down by stock then year.
    Input: pd.DataFrame
    Returns: Dictionary:
              keys=tickers
              values=DataFrame where columns=calendar year and
                index= the number day of the year (not month/day)
    '''
    # if data for one stock is entered
    if type(data.index) != pd.core.indexes.datetimes.DatetimeIndex:
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
            # getStockYears = pd.DataFrame(getStockYears)
            request[ticker] = pd.DataFrame(getStockYears)
        return request

def LoopYear(byStockAndYearOutput):
    request = {}
    for stock, data in byStockAndYearOutput.items():
        columns = list(data.columns)
        daysData = {}
        for i, column in enumerate(columns):
            try:
                a = round(data[columns[i]][105:], 2)
                b = round(data[columns[i+1]][:70], 2)
                c = pd.concat([a,b])
                daysData[f'{columns[i]}/{columns[i+1]}'] = c
            except:
                continue
        request[stock] = pd.DataFrame(daysData)
    return request    
    

def RollCorr(data, period):
    '''
    input: data=dictionary containing dataframes, period=window to use
             for rolling periods.
           designed for data to = ByStockAndYear output.
    output: dictionary.
            Key=ticker symbol.
            Value=pd.DataFrame with multilevel index,
                  value columns=calendar years,
                  value index=outside is the day of the year the corr was
                  calculated for, inside=calendar year
    '''
    request = {}
    for stock in data:
        request[stock] = data[stock].rolling(window=period)\
                                    .corr().dropna()
    return request


def SeasonCorrTest(dataDict, dropNum, n):
    '''
    Input: pandas correlation matrix, designed to take RollCorr output.
        dropNum: the number used to determine how many non NaN must be
        present in a column for the column not to be dropped.
        n: the desired correlation level minimum
    Output: DICTIONARY whose keys are the ticker symbols.
        Values are DataFrame Correlation Matrixs that contain
        True values if the dropNum and correlation test level
        is met (n).
    '''
    request = {}
    for stock, df in dataDict.items():
        test = (((df >= n) | (df <= -n)) & (df < 0.99))
        request[stock] = df[test].unstack(level=0)\
                                 .dropna(axis=1, thresh=dropNum)\
                                 .unstack().dropna()
        # print(f'{stock} completed', end='|')
    return request


def HighCorrDays(data):
    '''
    Purpose: Provide what days have high correlation.
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


def PctReturnForDays(data, pxData, periods):
    '''
    Purpose: to extract 2 items from days that had high correlation.
             1: avg return for the period that generated a high corr.
             2: return details by calendar year for period of high corr.
    input: data = output from func HighCorrDays,
           pxData=price data from which to pull the %returns,
                  preferably from output of func byStockAndYear.
           periods=rolling time frame used in data.
    return: 3 level dictionary with the average return for the rolling
                period and all the percent returns by year for the period.
            level 1 key = 'ticker'
            level 2 key = 'DayN' where N=int() of the day analyzed
            level 3 key = 2 keys: key1='AvgReturn', key2='ReturnDetails'
    '''
    request = {}
    for stock, data in data.items():
        requestValue = {}
        for day in data:
            dataValue = {}
            # px at the day at which the high correlation occured
            end = pxData[stock].loc[day]
            # px N days prior to end day
            if (day-periods) == 0:
                start = pxData[stock].loc[(day-periods+1)]
            elif day < periods:
                remainder = periods-day
                # find max of index for pxData
                endYearDay = max(pxData[stock].index)
                i = endYearDay - remainder
                start = pxData[stock].loc[i]
            else:
                start = pxData[stock].loc[(day-periods)]
            pctChange = (end-start) / start
            dataValue['AvgReturn'] = round(pctChange.mean()*100, 2)
            dataValue['ReturnDetails'] = round(pctChange*100, 2)
            requestValue[f'Day{day}'] = dataValue
        request[stock] = requestValue
    return request


def ExecSummaryCorr(data, printupdate=False):
    '''
    input: data = returned item from func PctReturnForDays
    output: 3 level dictionary
        level 1 keys = ticker
        level 1 value = dict
        level 2 keys = 'DayN' where the day with results
        level 2 value = dict
        level 3 keys = 'TotalTrades', 'NumPos', 'NumNeg',
                       'AvgReturnOnPos', 'AvgReturnOnNeg'
        level 3 value = results
    kwargs: printupdate = will print 'load' status
    '''
    request = {}
    status = 0
    outOf = len(data.keys())
    for stock, days in data.items():
        if printupdate:
            print(f'{status}/{outOf}', end=' | ')
            status += 1
        if len(days) >= 1:
            requestValue = {}
            for day, details in days.items():
                value = {}
                data = details['ReturnDetails']
                posTest = data > 0
                daysPos = data[posTest].count()
                daysNeg = data.count() - daysPos
                value['StartDay'] = details['StartDay']
                value['TotalTrades'] = data.count()
                value['NumPos'] = daysPos
                value['NumNeg'] = daysNeg
                value['AvgReturnOnPos'] = round(data[posTest].mean(), 2)
                value['AvgReturnOnNeg'] = round(data[data < 0].mean(), 2)
                requestValue[day] = value
            request[stock] = requestValue
    if printupdate:
        print()
    return request
