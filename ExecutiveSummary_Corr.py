# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 12:14:08 2019

@author: Gerardo Sandoval
"""

# import the data and supporting libraries.
import os
import pandas as pd
import numpy as np
import CorrHelpers as ch

baseDir = os.getcwd()
dataLocation = 'data/Master_Data.csv'
dataFilePath = os.path.join(baseDir, dataLocation)

roughData = pd.read_csv(dataFilePath, index_col=0)
print(len(roughData.columns))
masterData = roughData.dropna(axis=1)
print(len(masterData.columns))
byStockAndYear = ch.ByStockAndYear(masterData)

# drop data for 2019
for _, data in byStockAndYear.items():
    del data[2019]

rollCorr_20 = ch.RollCorr(byStockAndYear, period=20)
print('Rolling Correlation analysis completed.')
seasonalCorr = ch.SeasonCorrTest(rollCorr_20, dropNum=10, n=0.75)
print('Seasonal Correlation analysis completed.')
daysWithHighCorr = ch.HighCorrDays(seasonalCorr)
print('High Correlation Days analysis completed.')
pctChangeOfResults = ch.PctReturnForDays(daysWithHighCorr, byStockAndYear,
                                         periods=20)

execSummary = ch.ExecSummaryCorr(pctChangeOfResults)

for stock, data in execSummary.items():
    print(stock)
    for k, details in data.items():
        print(f'{k}: {details}')
        print()