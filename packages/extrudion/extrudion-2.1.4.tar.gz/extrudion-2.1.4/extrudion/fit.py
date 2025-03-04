class Fit:
    import pandas as pd
    from .analyzers import StressStrain

    def __init__(self, data: StressStrain, cut_off: bool = True, fit_window: int = 200):

        self.data = data.data
        self.max_stress_index = self.maxStressIndex()

        if cut_off:
            self.cutOffData()

        self.fit_results = self.getBestFit(fit_window)
        self.results = self.getResults()

    def maxStressIndex(self):
        max_stress_row = self.data[self.data['stress']
                                   == self.data['stress'].max()]
        return max_stress_row.index[0]

    def getResults(self) -> pd.DataFrame:
        import pandas as pd

        maxValues = self.data.iloc[self.max_stress_index]
        yieldValues = self.getYield()
        return pd.DataFrame({
            'Max Stress [kPa]': [maxValues['stress']],
            'Max Strain': [maxValues['strain']],
            'Young Modulus [kPa]': [self.fit_results.slope],
            'Intercept [kPa]': [self.fit_results.intercept],
            'Yield Stress [kPa]': [yieldValues['stress']],
            'Yield Strain': [yieldValues['strain']], })

    def cutOffData(self):
        self.data = self.data.iloc[0:self.max_stress_index + 1]
        return None

    def getBestFit(self, window=200):
        import pandas as pd
        import numpy as np

        window = 200
        step = 10

        fit_results = pd.DataFrame()

        sizeData = len(self.data[self.data['strain'] < 0.1])

        if window / sizeData > 0.2:
            window = max([int(sizeData * 0.2), min([30, sizeData])])
            step = 5

        left = 0
        right = window

        while True:

            if right > sizeData:
                break

            data = self.data[left:right]

            slope, intercept = np.polyfit(data['strain'], data['stress'], 1)

            y_exp = slope * data['strain'] + intercept

            ss_res = np.sum((data['stress'] - y_exp) ** 2)
            ss_tot = np.sum((data['stress'] - np.mean(data['stress'])) ** 2)
            r2 = 1 - (ss_res / ss_tot)

            error = (data['stress'] - y_exp)**2
            df = pd.DataFrame({
                'strain':  data[['strain']].iloc[int(
                    window / 2)].values,
                'slope': slope,
                'intercept': intercept,
                'error': error.sum(),
                'r2': r2
            })
            fit_results = pd.concat([fit_results, df], axis=0)

            left += step
            right += step
        bestFit = fit_results[fit_results['slope']
                              == fit_results['slope'].max()].iloc[0]
        print('Best Fit \n')
        print(bestFit)

        return bestFit

    def getYield(self):
        df = self.data.copy()
        df['error'] = abs(df['stress'] - (df['strain']-0.02)
                          * self.fit_results.slope - self.fit_results.intercept)
        yieldValues = df[df['error'] == df['error'].min()].iloc[0]
        return yieldValues
