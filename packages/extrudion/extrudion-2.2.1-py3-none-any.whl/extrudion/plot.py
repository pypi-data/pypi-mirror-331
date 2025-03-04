class Plot:
    from .fit import Fit
    from .analyzers import StressStrain

    def __init__(self, fit: Fit, data: StressStrain, filename: str):
        self.fit_results = fit.results
        self.data = fit.data
        self.filename = filename
        self.plot()

    def plot(self):
        import matplotlib.pyplot as plt
        plt.plot(self.data['strain'], self.data['stress'])
        plt.xlabel('Strain')
        plt.ylabel('Stress [kPa]')
        plt.title(self.filename)

        self.plotBestFit()
        self.plotMaxStress()
        self.plotYield()

        plt.legend(['Data', 'Young Modulus', 'Shift', 'Max Stress', 'Yield'])

        plt.savefig('plots/'+self.filename + '.png', dpi=300)
        plt.close()
        # plt.draw()
        # plt.pause(0.2)

    def plotBestFit(self):
        import matplotlib.pyplot as plt
        max_stress = self.data['stress'].max()
        max_strain = (
            max_stress - self.fit_results['Intercept [kPa]']) / self.fit_results['Young Modulus [kPa]']
        max_strain = max_strain[0]
        strain_range = self.data[self.data['strain'] < max_strain]['strain']
        line = self.fit_results['Young Modulus [kPa]'][0] * \
            strain_range + self.fit_results['Intercept [kPa]'][0]
        other = self.fit_results['Young Modulus [kPa]'][0] * \
            (strain_range) + self.fit_results['Intercept [kPa]'][0]

        plt.plot(strain_range, line, linestyle='--')
        plt.plot(strain_range + 0.02, other, linestyle='dotted')

    def plotMaxStress(self):
        import matplotlib.pyplot as plt
        x = self.fit_results.iloc[0, 1]
        y = self.fit_results.iloc[0, 0]
        plt.scatter(x, y, marker='o', color='blue')

    def plotYield(self):
        import matplotlib.pyplot as plt
        x = self.fit_results.iloc[0, 5]
        y = self.fit_results.iloc[0, 4]
        plt.scatter(x, y, marker='o', color='green')
