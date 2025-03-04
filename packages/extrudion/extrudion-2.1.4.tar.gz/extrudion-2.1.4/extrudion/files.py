class TRAFolder:
    class FolderNotFound(Exception):
        pass

    def __init__(self, folder_path: str):
        self.folder_path = folder_path

        self.file_list = self.getTRAFiles()

        import pandas as pd
        self.results = pd.DataFrame()

        import os
        if not os.path.exists(folder_path + '/plots'):
            os.makedirs(folder_path + '/plots')

    def analyze(self, options={}):
        if not self.file_list:
            return

        import pandas as pd

        for file in self.file_list:
            print(file)
            result = TRAFile(file, self.folder_path).analyze(options)
            result['File'] = self.pad_numeric_part(file)

            self.results = pd.concat([self.results, result])

        self.printCopyrights()
        return self.results.set_index('File').sort_index()

    def getTRAFiles(self):
        import os

        try:
            dir_list = os.listdir(self.folder_path)

            try:
                file_list = [
                    filename for filename in dir_list if filename.endswith('.TRA')]

                if not file_list:
                    print('No .TRA files found in the folder.')
                    return []
                else:
                    return file_list

            except FileNotFoundError:
                print('An error occurred while filtering files.')
                raise

        except FileNotFoundError:
            raise TRAFolder.FolderNotFound('Folder not found')

    def pad_numeric_part(self, filename):
        parts = filename.split('_')
        if len(parts) != 2:
            return filename
        prefix, numeric_part = parts
        try:
            numeric_part = int(numeric_part.split('.')[0])
            padded_numeric_part = '{:04d}'.format(numeric_part)
            return '{}_{}.{}'.format(prefix, padded_numeric_part, filename.split('.')[-1])
        except ValueError:
            return filename

    def printCopyrights(self):
        print("*********************************************")
        print("                EXTRUDION")
        print("*********************************************")
        print()
        print("by Paride Azzari (C) 2024")
        print()
        print("info on: github.com/azzarip/extrudion")
        print("*********************************************")
        print("RESULTS:")
        print()
        print("Analysis.csv contains the analyzed data")
        print()
        print("The plots folder contains all the figures")
        print("*********************************************")
        print()


class TRAFile:

    def __init__(self, file: str, folder_path: str):
        import os
        import pandas as pd
        self.filename = file.replace('.TRA', '')

        if folder_path:
            self.filepath = os.path.join(folder_path, file)
        else:
            self.filepath = file

        df = pd.read_table(self.filepath, header=[
                           3], encoding='Windows-1252', sep=',')
        df['mm'] = df['mm'].apply(replace_negative_values)
        self.data = df

    def analyze(self, options):
        from .analyzers import StressStrain
        from .fit import Fit
        from .plot import Plot

        data = StressStrain(
            self.data, sample_area=options['sample_area'], initial_length=options['initial_length'])

        fit = Fit(data)

        if "plot" not in options or options["plot"] is not False:
            Plot(fit, data, self.filename)

        print(fit.results)
        return fit.results


def replace_negative_values(x):
    if x >= 0:
        return x
    if abs(x) < 0.01:
        return 0
    else:


<< << << < HEAD
raise ValueError("Negative values in column 'mm'")
== == == =
raise ValueError("Negative values in column 'mm'")
>>>>>> > 8c1643b1469747eec8636596ff5bf458efe2392c
