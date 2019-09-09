from csv_parser import read_data, isF2row, isF3row
from os import walk
from os.path import join
import argparse

log = dict()
def validate_data(data):
    expected = 'F2'
    encountered = 0
    for index, row in data.iterrows():
        isF2 = isF2row(row)
        isF3 = isF3row(row)
        if expected == 'F2' and isF3:
            return f"F3 row found when F2 was expected around line {index + 2}"
        elif expected == 'F3' and isF2:
            return f"F2 row found when F3 was expected around line {index + 2}"
        elif expected == 'F2' and isF2:
            expected = 'F3'
            encountered += 1
        elif expected == 'F3' and isF3:
            expected = 'F2'
            encountered += 1
        else:
            pass
    if encountered < 28:
        return "Less than 14 pairs found"
    return "Valid"

def validate(path):
    global log
    for root, dirs, files in walk(path):
        for name in files:
            if name.endswith('.csv'):
                data = read_data(join(root, name))
                log[join(root, name)] = validate_data(data)
        for directory in dirs:
            validate(join(root, directory))
    return log

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    args = parser.parse_args()
    validate(args.path)
    for file, val in log.items():
        print(f'{file}: {val}')
