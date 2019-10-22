
def ExecSummaryCorr(data, printupdate=False):
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

def main():
    print('In the file. within the main() func.')

if __name__ =='__main__':
    main()
