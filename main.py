from parser import parser

# Read the input file and execute the program
with open('input.txt', 'r', encoding='utf-8') as file:
    code = file.read()

try:
    print("Parsing the input code...")
    parser.parse(code)
    print("Execution completed successfully")
except Exception as e:
    print(f"Error: {e}")