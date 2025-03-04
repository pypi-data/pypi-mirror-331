
from feature_flags import feature_flags
import sys
import os
from typing import Any, List

from testweaver.constants import Constants

variable_names = "abcdefghijklmnopqrstuvwxyz"
input_limit = len(variable_names)
original_args = None

class CustomClass:
    pass

def generate_test_cases(coding_language: Constants.CodingLanguage, filepath: str, *args):

    if coding_language is None:
        raise Exception("Coding Language Not Chosen")

    if not feature_flags.is_enabled('generate_input_handling_test_cases_template_file'):
        return

    given_too_many_inputs = len(args) > input_limit
    if given_too_many_inputs:
        args = args[:input_limit]
        print(F"Truncating input down to input_limit {input_limit}")

    filepath = filepath.strip()
    file_exists = filepath is not None and filepath is not ""
    if not file_exists:
        filepath = os.path.abspath("generated_tests_cases.txt")
        print(F"Using '{filepath}'")

    # i know this is bad
    global original_args
    original_args = args

    output: List[List[Any]] = []

    for i, input in enumerate(args):

        if isinstance(input, int):

            inputs_list = [
            -2147483648,      # 0
            0,                # 1
            2147483647        # 2
            ]
        elif isinstance(input, str) and input == "{{object}}":
            inputs_list = [
                None
            ]
        elif isinstance(input, str):

            input = input.strip()

            inputs_list = []

            # Generating
            input_variations = [
                None, 
                "",
                input.lower(),
                input.upper(),
                input[0],                                                           # 1 char
                ''.join([input[0], input]),                                         # 1 extra char
                input[1:],                                                          # 1 less char
                input[:(len(input) // 2)] + "\t" + input[(len(input) // 2):],   # special char
                input[:(len(input) // 2)] + "😃" + input[(len(input) // 2):],   # special char
                "   ",
                F" {input}",
                F"{input} ",
            ]

            # deduping
            for i, value in enumerate(input_variations):
                if value in inputs_list:
                    continue
                inputs_list.append(value)

        else:
            raise Exception("Not Yet Implemented")

        if isinstance(input, int):

            # Inserting in numerical order
            exists_in_list = input in inputs_list
            if not exists_in_list:
                for i, element in enumerate(inputs_list):
                    found = input < element
                    if found:
                        inputs_list.insert(i, input)
                        break

        else:

            # Inserting the original input at the top of the list
            exists_in_list = input in inputs_list
            if exists_in_list:
                for i, element in enumerate(args):
                    found = element == input
                    if found:
                        inputs_list.pop(i)
                        break

            inputs_list.insert(0, input)
        
        output.append(inputs_list)

    write_test_case_code(coding_language, filepath, output)

    return True

def write_test_case_code(coding_language: Constants.CodingLanguage, file_path, input_list_list):

    code_lines = []
    datatypes_list = []
    datatypes_captured = False
    symbol = "{{data}}"
    symbol2 = "{{data2}}"
    symbol3 = "{{data3}}"

    # add more code languages here, as needed
    if Constants.CodingLanguage.DotNet == coding_language:

        if not feature_flags.is_enabled('dotnet_support'):
            raise Exception(Constants.DotNetSupportException)

        null_symbol = "null"
        header_format = F"[DataTestMethod]\n"
        data_row_line_format = F"[DataRow({symbol})]"
        footer_format = F"public void CanMethodNameIH({symbol2})"

    elif Constants.CodingLanguage.Python == coding_language:

        if not feature_flags.is_enabled('python_support'):
            raise Exception(Constants.PythonSupportException)

        null_symbol = "None"
        header_format = '''
    def test_ih_main(self):

        # arrange
        test_cases = [
'''
        data_row_line_format = F"            ({symbol}),"
        footer_format = F'''        ]
        
        for {symbol3} in test_cases:
            with self.subTest({symbol2}):

                # arrange 

                # act

                # assert
                self.assertEqual(a, a)
'''

    else:
        raise Exception("Not Yet Implemented")

    number_of_inputs = len(input_list_list)

    # Format Data Row Lines
    # [ [ " foo", " bar" ], [ -1, 0, -1 ] ]
    for i, input_list in enumerate(input_list_list):
        # [ " foo", " bar" ]
        typ = "int" if isinstance(input_list[0], int) else "string"
        for j, v in enumerate(input_list):
            # " foo"

            case_parameters_list = []
            for k in range(number_of_inputs):
                at_input_under_test = k == i
                if at_input_under_test:
                    # Grabbing the value under test
                    value = input_list_list[k][j]
                else: 
                    # Grabbing a happy path variable
                    value = original_args[k]

                # Formatting the value appropriately
                if value is None:
                    formatted_value = null_symbol
                elif isinstance(value, int):
                    formatted_value = str(value)
                    if not datatypes_captured:
                        datatypes_list.append("int")
                elif isinstance(value, str) and value == "{{object}}":
                    formatted_value = F"\"{value}\""
                    if not datatypes_captured:
                        datatypes_list.append("object")
                elif isinstance(value, str):
                    formatted_value = F"\"{value}\""
                    if not datatypes_captured:
                        datatypes_list.append("string")
                # add more datatypes here, as needed
                else:
                    raise Exception("Not Yet Implemented")

                case_parameters_list.append(formatted_value)
                
            if not datatypes_captured: datatypes_captured = True
                
            case_parameters_string = ", ".join(case_parameters_list)
            data_row_line = data_row_line_format.replace(symbol, case_parameters_string)
            code_lines.append(data_row_line)

    # Format headers
    header = header_format

    # Format Footers
    argument_signatures2 = []
    argument_signatures3 = []
    for i, value in enumerate(datatypes_list):

        argument_signature2 = None
        argument_signature3 = None

        if Constants.CodingLanguage.DotNet == coding_language:
            if "int" == value:
                argument_signature2 = F"int {variable_names[i]}"
            elif "object" == value:
                argument_signature2 = F"object {variable_names[i]}"
            elif "string" == value:
                argument_signature2 = F"string {variable_names[i]}"
            # add more datatypes here, as needed
            else:
                raise Exception("Not Yet Implemented")
            
        if Constants.CodingLanguage.Python == coding_language:
                argument_signature2 = F"{variable_names[i]}={variable_names[i]}"
                argument_signature3 = F"{variable_names[i]}"
            
        if argument_signature2:
            argument_signatures2.append(argument_signature2)

        if argument_signature3:
            argument_signatures3.append(argument_signature3)
    
    footer = footer_format.replace(symbol2, ", ".join(argument_signatures2)) 
    footer = footer.replace(symbol3, ", ".join(argument_signatures3))

    # Generating code from lines
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(header)
        for i, value in enumerate(code_lines):
            file.write(F"{value}\n")
        file.write(footer)
        print(F"Saved to '{file_path}'")

    return True

