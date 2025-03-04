# Copyright 2023 Paride Azzari
#
# Licensed under the MIT License. See LICENSE

def start(folder_path: str = '.'):
    '''
    Give a folder path as a relative or absolute path, the script will analyze all the .TAR files found in the directory and return a DataFrame containing the results.
    Leaving returns the Current Working Directory.
    '''
    while True:
        sample_area = input("Enter the Surface of the Sample [mm2]: ")
    
        if sample_area.replace('.', '', 1).isdigit():
            break
        else:
            print("Invalid input. Please enter a valid number.")
 
    while True:
        initial_length = input("Enter the Initial Length of the Sample [mm]: ")
    
        if initial_length.replace('.', '', 1).isdigit():
            break
        else:
            print("Invalid input. Please enter a valid number.")
 
    from .files import TRAFolder
    
    results = TRAFolder(folder_path).analyze({'sample_area': float(sample_area), 'initial_length': float(initial_length)})
    results.to_csv('Analysis.csv')


# Legacy code
def analyzeDirectory(sample_area):
    '''
    Give a folder path as a relative or absolute path, the script will analyze all the .TAR files found in the directory and return a DataFrame containing the results.
    Leaving returns the Current Working Directory.
    '''
    from colorama import init, Fore
    init()

    print(Fore.RED + "---------------------------")
    print(Fore.RED + "--------- WARNING ---------")
    print(Fore.RED + "---------------------------")
    print(Fore.GREEN + "!!   OUTDATED VERSION   !!")
    print(Fore.WHITE + 'Please download the latest version at: ')
    print("https://github.com/azzarip/extrudion")
    print(Fore.RED + "---------------------------")
    print(Fore.RED + "--------- WARNING ---------")
    print(Fore.RED + "---------------------------")
    print(Fore.GREEN + "!!   OUTDATED VERSION   !!")
    print(Fore.WHITE + 'Please download the latest version at: ')
    print("https://github.com/azzarip/extrudion")
    print(Fore.RED + "---------------------------")
    print(Fore.RED + "--------- WARNING ---------")
    print(Fore.RED + "---------------------------")
    print(Fore.GREEN + "!!   OUTDATED VERSION   !!")
    print(Fore.WHITE + 'Please download the latest version at: ')
    print("https://github.com/azzarip/extrudion")
    print(Fore.RED + "---------------------------")
    print(Fore.WHITE)
    return 