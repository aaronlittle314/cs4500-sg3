# sg3.py
# This program was written in Python 3
# To load and run this program in Thonny, select File >> Open and browse for this file.
#-------------------------------------------------------------------------------------------
# Authors: Denny Dyer, Chris Imgarten, Kevin Linden, Aaron Little, Matt Willerding
# Date: 04/26/2025
# Class: cs4500
# Group: 4
# Project: sg3
# References:
# https://www.w3schools.com/python
# https://www.geeksforgeeks.org/python-programmin-language-tutorial
# https://docs.python.org/3/tutorial
# cs4500-Group5-sg2.py
#-------------------------------------------------------------------------------------------
# Program Overview:
# - Prompts user for a valid .csv filename and verifies its existence.
# - Reads and validates the file's structure (header, dates, and data values).
# - Extracts and stores species names, dates, and abundance counts.
# - Generates four output files:
#   - Species.txt (list of species names)
#   - DatedData.txt (list of dates)
#   - PresentAbsent.txt (0/1 presence-absence matrix)
#   - HeatMap.txt (heat map table based on abundance values)
# - Displays max abundance and associated species for each date.
# - Identifies and groups dates with identical presence/absence patterns.
# - Constructs and displays a heat map of abundance levels (High, Medium, Low).
# - Detects and reports species sharing identical heat map patterns.
# - Provides clear error handling and user prompts at each validation step.
#----------------------------------------------------------------------------------------
import os
import re

# Validate csv file name and check that file exists
# Return true if the file name is valid and the file exists
def validate_file(file_name):
    if not (os.path.isfile(file_name) and os.path.abspath(os.path.dirname(file_name)) == os.getcwd()):
    #if not os.path.isfile(f"./{file_name}"):
        print(f"The file, {file_name}, does not exist in current directory.")
        return False
    elif not (re.findall(r"(\.[cC][sS][vV])$", file_name)):
        print(f"{file_name} is not a valid file name.\n"
              f"File name must end with the .csv extension.")
        return False
    elif os.path.getsize(file_name) == 0:
        print(f"The file {file_name} has no data.")
        return False
    elif (re.findall(r"(\.[cC][sS][vV])$", file_name)) and os.path.isfile(file_name):
        return True
    else:
        return False


# Extract data from csv file
# Return raw data
def extract_csv_data(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as csv_file:
            csv_data = csv_file.readlines()
        return csv_data
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# Get names from csv data
# Return a list of names
def get_names(file_name):
    try:
        csv_data = extract_csv_data(file_name)
        name_list = csv_data[0].strip().split(',')
        for i in range(len(name_list) - 1):
            if name_list[i] == "":
                del name_list[i]
        return name_list
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# Count the number of names from the first line of a file
# Return the name count
def get_name_count(file_name):
    try:
        names = get_names(file_name)
        name_count = len(names)
        return name_count
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# Parse csv file into species and dated data
def parse_csv(file_name):
    csv_data = extract_csv_data(file_name)
    species = get_names(file_name)
    n = len(species)
    dated_data = []
    try:

        for idx, line in enumerate(csv_data[1:], start=2):
            parts = line.strip().split(',')
            if len(parts) != n + 1:
                print(f"Error on line {idx}: Incorrect number of entries.")
                input("Press ENTER to terminate.")
                exit()

            date = parts[0]
            if not re.match(r'^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/\d{4}$', date):
            #if not re.match(r'^(0?[1-9]|1[0-2])/([0-2]?\d|3[01])/\d{4}$', date):
                print(f"Error on line {idx}: Invalid date format '{date}'.")
                input("Press ENTER to terminate.")
                exit()

            numbers = []
            for num in parts[1:]:
                try:
                    val = float(num)
                    if val < 0:
                        raise ValueError()
                    numbers.append(val)
                except ValueError:
                    print(f"Error on line {idx}: Illegal number '{num}'.")
                    input("Press ENTER to terminate.")
                    exit()

            dated_data.append((date, numbers))

        if len(dated_data) + 1 < 2:  # adding one to account for species name line
            print(f"Error in file, {file_name}: file does not have at least 2 lines of data")
            input("Press ENTER to terminate.")
            exit()

        elif len(dated_data) + 1 > 999:  # adding one to account for species name line
            print(f"Error in file, {file_name}: file exceeds maximum number of lines of data allowed")
            input("Press ENTER to terminate.")
            exit()

        return species, dated_data

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# Write species, dates, and presence-absence data to files
def write_files(species, dated_data):
    with open("Species.txt", 'w') as sp_file:
        for name in species:
            sp_file.write(name + '\n')

    with open("DatedData.txt", 'w') as dt_file:
        for date, _ in dated_data:
            dt_file.write(date + '\n')

    pre_abs = []
    with open("PresentAbsent.txt", 'w') as pa_file:
        pa_file.write("," + ",".join(species) + "\n")
        for date, counts in dated_data:
            pa_counts = ["1" if count > 0 else "0" for count in counts]
            pre_abs.append((date, pa_counts))
            pa_file.write(date + "," + ",".join(pa_counts) + "\n")
    return pre_abs


# Print max abundance for each date
def max_abundance_report(species, dated_data):
    print("\nMax Abundance Report:")
    for date, counts in dated_data:
        max_count = max(counts)
        max_species = [species[i] for i, count in enumerate(counts) if count == max_count]
        print(f"{date}: Max abundance = {max_count}, Species: {', '.join(max_species)}")


# Report dates with identical presence/absence vectors
def same_pa_vector_report(pa):
    vectors = {}  # Regular dictionary
    for date, pa_vector in pa:
        key = tuple(pa_vector)
        if key not in vectors:
            vectors[key] = []
        vectors[key].append(date)

    print("\nDates with identical presence/absence vectors:")
    for vector, dates in vectors.items():
        if len(dates) > 1:
            print(f"Vector {','.join(vector)} occurs {len(dates)} times on dates: {', '.join(dates)}")


# Returns the transpose of a 2D matrix.
def transpose_matrix(matrix):
    return [[matrix[row][col] for row in range(len(matrix))] for col in range(len(matrix[0]))]


# Convert abundance values to heat map symbols.
# 'X': High, 'o': Medium, '-': Low
def get_heat_matrix(matrix):
    transposed = transpose_matrix(matrix)
    heat_map = []

    for row in transposed:
        low = min(row)
        high = max(row)
        range_size = (high - low) / 3
        second = low + range_size
        third = high - range_size

        heat_row = [
            'X' if num > third else '-' if num < second else 'o'
            for num in row
        ]
        heat_map.append(heat_row)

    return transpose_matrix(heat_map)


# Create table for heat map
def get_heat_table(names, dates, abundances):
    heat_matrix = get_heat_matrix(abundances)
    heat_table = [[''] + names]

    # add date and heat rows to table
    for i, row in enumerate(heat_matrix):
        heat_table.append([dates[i]] + row)

    return heat_table

# Write heatmap to HeatMap.txt
def write_heatmap(heat_table):
    heat_symbol_map = {'-': 'L', 'o': 'M', 'X': 'H'}

    with open("HeatMap.txt", 'w') as heat_file:
        for row in heat_table[1:]:
            date = row[0]
            heat_vals = [heat_symbol_map.get(val.strip("'"), val) for val in row[1:]]
            heat_file.write(f"{date} {' '.join(heat_vals)}\n")


# Display heat table to user
def print_heatmap(heat_table):
    # find max string width for columns in table
    col_widths = [max(len(str(row[i])) for row in heat_table) for i in range(len(heat_table[0]))]

    # format row in table as string
    def format_row(row):
        return " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))

    formatted = [format_row(row) for row in heat_table]     # get list of rows as strings
    separator = "-" * len(formatted[0])

    for i, line in enumerate(formatted):
        print(line)
        if i == 0:
            print(separator)


# Find identical heat map values shared by multiple species
def find_heat_dupes(heat_table):
    t_heat_table = transpose_matrix(heat_table)

    species_rows = t_heat_table[1:]

    pattern_to_species = {} # dictionary {heatmap pattern, species list}
    for row in species_rows:
        species_name = row[0]
        heat_pattern = tuple(row[1:])

        if heat_pattern in pattern_to_species:
            pattern_to_species[heat_pattern].append(species_name)
        else:
            pattern_to_species[heat_pattern] = [species_name]

    matches_found = False
    for pattern, species_list in pattern_to_species.items():
        if len(species_list) > 1:
            matches_found = True
            print(f"Species: {', '.join(species_list)}\n"
                  f"Have identical heat value pattern: {pattern}\n")

    if not matches_found:
        print("No identical heat value patterns were found among the species.")

def main():
    print("Welcome to sg3!\n"
          "This program reads a csv file containing species abundance data across different dates.\n"
          "It will validate the file's format and contents, then generate:\n"
          "- A list of species names.\n"
          "- A list of dates.\n"
          "- A presence/absence matrix.\n"
          "- A heat map representing abundance levels.\n\n"
          "sg3 will also:\n"
          "- Report maximum abundances per date.\n"
          "- Find matching patterns in data.\n"
          "- Highlight any species sharing identical patterns.\n\n"
          "Please follow the prompts to provide a valid csv file to begin.\n")

    while True:
        user_file = input("Please enter a valid csv file name:\n")
        if validate_file(user_file):
            break

    species, dated_data = parse_csv(user_file)
    name_count = len(species)
    date_count = len(dated_data)

    print(f"\nThere are {name_count} species and {date_count} dates in the csv file {user_file}.")
    input("Press ENTER to continue.")

    pa = write_files(species, dated_data)
    max_abundance_report(species, dated_data)
    same_pa_vector_report(pa)

    abundances = [counts for _, counts in dated_data]
    dates = [date for date, _ in dated_data]
    heat_table = get_heat_table(species, dates, abundances)
    write_heatmap(heat_table)
    print_heatmap(heat_table)
    find_heat_dupes(heat_table)

    print("\nThank you for using sg3!")
    input("Press ENTER to exit.")


if __name__ == "__main__":
    main()