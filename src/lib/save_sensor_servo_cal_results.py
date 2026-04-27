import json
import os

# Specify the file path to store the variable
file_path = "/home/bossman/sensors/sensor_servo_cal_results.json"

def main():
    pass

# Function to write a variable to the file
def write_variable(variable_name, variable_value):
    data = {}
    # Load existing data if the file exists, but only if it contains valid JSON
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            pass  # Ignore invalid JSON

    # Update the data with the new variable
    data[variable_name] = variable_value

    # Save the updated data to the file, ensuring proper JSON formatting
    with open(file_path, "w") as file:
        json.dump(data, file) 

# Function to read a variable from the file
def read_variable(variable_name):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            return data.get(variable_name)
    else:
        return None  # Return None if the file doesn't exist

def validate_variables():
    if os.path.exists(file_path):
       with open(file_path, "r") as file:
           first_line = file.readline()
           num_chars = len(first_line)
           return num_chars
    else:
        return None  # Return None if the file doesn't exist

def clear_json_values():
    with open(file_path, "w") as file:
        # Write an empty JSON object to clear the file
        json.dump({}, file)

if __name__ == '__main__':
    main()

