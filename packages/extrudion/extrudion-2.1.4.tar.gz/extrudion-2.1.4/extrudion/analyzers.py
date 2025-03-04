class StressStrain:
    def __init__(self, raw, sample_area, initial_length):
        self.raw = raw

        strain = self.getStrain(initial_length)
        stress = self.getStress(sample_area)
        
        import pandas as pd
        self.data = pd.DataFrame({'strain': strain, 'stress': stress})
    
    def getStress(self, sample_area):
        return self.raw['N'] / float(sample_area) * 1_000_000 / 1000
    
    def getStrain(self, initial_length):
        from numpy import log
        length = self.raw['mm'] + float(initial_length)
        return log(length / initial_length)
    


