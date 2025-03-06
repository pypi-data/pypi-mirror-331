#############################################################
# This script will take the output from VariantFoldRNA and 
# converts it to input for CSV mode 
# Final output columns: ID,REF,ALT,SEQ,FLANK
#############################################################


# Imports 
import argparse
from tqdm import tqdm 

# Parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input", help="The input file", required=True)
parser.add_argument("--output", help="The output file", required=True)
args = parser.parse_args()

# Open the output file
output = open(args.output, 'w')

# Add the column names to the output file
output.write("ID,REF,ALT,SEQ,FLANK\n")

# Parse the intput file
x = 0
with open(args.input, 'r') as f:
    lines = f.readlines()
    for line in tqdm(lines):
        line = line.strip().split("\t")
        if x == 0:
            x += 1
            continue
        id = f"{line[0]}_{line[1]}"
        ref = line[3]
        alt = line[4]

        if ref != "-" and alt != "-":
            seq = f"{line[5]}{ref}{line[6]}"
            flank = 51

            output.write(f"{id},{ref},{alt},{seq},{flank}\n")
    # Close the output file
output.close()

