#! /usr/bin/env python3
"""
Do Not Modify This File
"""
__version__ = '2018-04-28 18:00'

import itertools
from pprint import pprint
import argparse
import sys
import random
import numbers
import operator
import copy
import itertools
from . rply import LexerGenerator, ParserGenerator


MEMORY = {}
SYMBOL_TABLE = {}
REGISTER_TABLE = {}
LABEL_TABLE = {}
INSTRUCTIONS = []
STACK = []
INPUT = ""
OUTPUT = ""

DEBUG_FILENAME = 'debug.txt'
MAX_STEPS = 10000

class InterpreterError(Exception):
    pass

class LMAOError(InterpreterError):
    pass

class ROFLError(InterpreterError):
    pass

common_commands = [
    'VAL_COPY',
    'ADD',
    'SUB',
    'MULT',
    'DIV',
    'TEST_LESS',
    'TEST_GTR',
    'TEST_EQU',
    'TEST_NEQU',
    'TEST_GTE',
    'TEST_LTE',
    'JUMP_IF_0',
    'JUMP_IF_N0',
    'JUMP',
    'RANDOM',
    'OUT_NUM',
    'OUT_CHAR',
    'IN_CHAR',
    'NOP',
]

lmao_commands = [
    'AR_GET_IDX',
    'AR_SET_IDX',
    'AR_GET_SIZE',
    'AR_SET_SIZE',
    'AR_COPY',
    'PUSH',
    'POP',
]

rofl_commands = [
    'LOAD',
    'STORE',
    'MEM_COPY',
]

def build_lexer():
    lg = LexerGenerator()
    commands = sorted(itertools.chain(common_commands, lmao_commands, rofl_commands))
    for command in reversed(commands):
        lg.add(command, command)
    lg.add('NEWLINE', r'\n')

    lg.add('SCALAR_VAR', r's\d+')
    lg.add('ARRAY_VAR', r'a\d+')

    lg.add('REGISTER', r'reg[A-H]')
    lg.add('LABEL', r'[a-zA-Z_][a-zA-Z_0-9]*')
    lg.add('NUM_LITERAL', r'-?((\d+)(\.\d+)?)|(\.\d+)')
    lg.add('CHAR_LITERAL', r"'([^\\']|\\n|\\t|\\'|\\\\)'")
    lg.add('COLON', r':')

    lg.ignore(r'[ \t]')
    lg.ignore(r'\#.*')
    lg.add('ERROR', r'.')

    return lg.build()

def get_possible_tokens(lexer):
    return [rule.name for rule in lexer.rules if rule.name != 'ERROR']

def check_for_lexing_errors(tokens, language):
    for token in tokens:
        if token.name == 'ERROR':
            raise InterpreterError(f'Lexing error on token ({token.value}).')
        if token.name in lmao_commands and language == 'ROFL':
            raise ROFLError(f'Command {token.name} not allowed in ROFLcode.')
        if token.name in rofl_commands and language == 'LMAO':
            raise LMAOError(f'Command {token.name} not allowed in LMAOcode.')

class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return str(self.name)
    def nice_str(self):
        return f'{self.name}({self.get_value()})'
    def __eq__(self, other):
        return ((type(self) == type(other))
                and (self.name == other.name))
    def __hash__(self):
        return hash(self.name)
    def get_value(self):
        raise NotImplementedError()
    def set_value(self, value):
        raise NotImplementedError()

class Constant(Var):
    def get_value(self):
        return self.name

class SymbolTableVar(Var):
    def get_value(self):
        if self.name not in SYMBOL_TABLE:
            raise InterpreterError(f'{self.name} not in interpreter symbol table')
            # SYMBOL_TABLE[self.name] = 0
        return SYMBOL_TABLE[self.name]
    def set_value(self, value):
        SYMBOL_TABLE[self.name] = value

class ScalarVar(SymbolTableVar):
    pass

class ArrayVar(SymbolTableVar):
    def get_value(self):
        if self.name not in SYMBOL_TABLE:
            SYMBOL_TABLE[self.name] = []
        return SYMBOL_TABLE[self.name]

class Register(Var):
    def get_value(self):
        return REGISTER_TABLE[self.name]
    def set_value(self, value):
        REGISTER_TABLE[self.name] = value

class Label(Var):
    def get_value(self):
        if self.name not in LABEL_TABLE:
            raise InterpreterError(f'{self.name} not in interpreter label table')
            # return -1
        return LABEL_TABLE[self.name]


def build_parser(possible_tokens, language):
    assert language in {'LMAOcode', 'ROFLcode'}, language
    pg = ParserGenerator(possible_tokens)
    
    @pg.production('program : optional_newlines statements')
    def program(p):
        return p[1]

    @pg.production('program : empty_program')
    def empty_program(p):
        return []

    @pg.production('empty_program : optional_newlines')
    @pg.production('optional_newlines : newlines')
    @pg.production('optional_newlines : ')
    @pg.production('newlines : NEWLINE')
    @pg.production('newlines : NEWLINE newlines')
    def do_nothing(p):
        pass

    @pg.production('statements : statement newlines statements')
    def multiple_statements(p):
        return [p[0]] + p[2]
    
    @pg.production('statements : statement newlines')
    def single_statement(p):
        return [p[0]]


    @pg.production('math_command : ADD')
    @pg.production('math_command : SUB')
    @pg.production('math_command : MULT')
    @pg.production('math_command : DIV')
    @pg.production('math_command : TEST_LESS')
    @pg.production('math_command : TEST_GTR')
    @pg.production('math_command : TEST_EQU')
    @pg.production('math_command : TEST_NEQU')
    @pg.production('math_command : TEST_GTE')
    @pg.production('math_command : TEST_LTE')
    def math_command(p):
        return p[0]

    @pg.production('statement : math_command value value store_value')
    @pg.production('statement : VAL_COPY value store_value')
    @pg.production('statement : JUMP value')
    @pg.production('statement : JUMP_IF_0 value value')
    @pg.production('statement : JUMP_IF_N0 value value')
    @pg.production('statement : RANDOM store_value')
    @pg.production('statement : OUT_NUM value')
    @pg.production('statement : OUT_CHAR value')
    @pg.production('statement : NOP')
    @pg.production('statement : PUSH value')
    @pg.production('statement : POP store_value')
    @pg.production('statement : PUSH array_var')
    @pg.production('statement : POP array_var')
    @pg.production('statement : AR_GET_IDX array_var value store_value')
    @pg.production('statement : AR_SET_IDX array_var value value')
    @pg.production('statement : AR_GET_SIZE array_var store_value')
    @pg.production('statement : AR_SET_SIZE array_var value')
    @pg.production('statement : AR_COPY array_var array_var')
    @pg.production('statement : LOAD value value')
    @pg.production('statement : STORE value value')
    @pg.production('statement : MEM_COPY value value')
    @pg.production('statement : IN_CHAR store_value')
    def complete_statement(p):
        p[0] = p[0].getstr()
        return p

    @pg.production('value : CHAR_LITERAL')
    def char_literal(p):
        char_str = p[0].getstr()
        assert char_str[0] == "'"
        assert char_str[-1] == "'"
        char_str_without_quotes = char_str[1:-1]
        if len(char_str_without_quotes) == 1:
            return Constant(ord(char_str_without_quotes))

        assert len(char_str_without_quotes) == 2
        assert char_str_without_quotes[0] == '\\'
        escaped_char = char_str_without_quotes[1]
        mapping = {
            'n': '\n',
            '\\': '\\',
            't': '\t',
            "'": "'"
        }
        assert escaped_char in mapping
        return Constant(ord(mapping[escaped_char]))
    
    @pg.production('value : NUM_LITERAL')
    def num_literal(p):
        float_value = float(p[0].getstr())
        if float_value.is_integer():
            value = int(float_value)
        else:
            value = float_value
        return Constant(value)

    @pg.production('label : LABEL')
    def label(p):
        return Label(p[0].getstr())

    @pg.production('scalar_var : SCALAR_VAR')
    def scalar_var(p):
        if language == 'ROFLcode':
            raise ROFLError('Can\'t use scalar variables in ROLFcode.')
        return ScalarVar(p[0].getstr())

    @pg.production('array_var : ARRAY_VAR')
    def array_var(p):
        if language == 'ROFLcode':
            raise ROFLError('Can\'t use array variables in ROFLcode.')
        return ArrayVar(p[0].getstr())

    @pg.production('register : REGISTER')
    def register(p):
        if language == 'LMAOcode':
            raise LMAOError('Can\'t use registers in LMAOcode.')
        return Register(p[0].getstr())

    @pg.production('value : store_value')
    @pg.production('store_value : scalar_var')
    @pg.production('store_value : register')
    @pg.production('value : label')
    def values(p):
        return p[0]



    @pg.production('statement : label COLON')
    def label_statement(p):
        return [p[0], ':']


    @pg.error
    def error_handler(token):
        raise InterpreterError(f"Ran into a {token} where it wasn't expected {token.source_pos}.")

    return pg.build()


def execute_bad_instruction(instruction):
    command = instruction[0]
    binary_arithmetic_commands = {
        'ADD': operator.add,
        'SUB': operator.sub,
        'DIV': operator.truediv,
        'MULT': operator.mul
    }
    binary_logic_commands = {
        'TEST_LESS': operator.lt,
        'TEST_GTR': operator.gt,
        'TEST_EQU': operator.eq,
        'TEST_NEQU': operator.ne,
        'TEST_GTE': operator.ge,
        'TEST_LTE': operator.le
    }
    if command == 'VAL_COPY':
        a = instruction[1].get_value()
        instruction[2].set_value(a)
        return

    if command in binary_arithmetic_commands:
        a = instruction[1].get_value()
        b = instruction[2].get_value()
        result = binary_arithmetic_commands[command](a, b)
        instruction[3].set_value(result)
        return

    if command in binary_logic_commands:
        a = instruction[1].get_value()
        b = instruction[2].get_value()
        is_true = binary_logic_commands[command](a, b)
        if is_true:
            result = 1
        else:
            result = 0
        instruction[3].set_value(result)
        return

    if isinstance(command, Label):
        return

    if command == 'JUMP':
        a = instruction[1].get_value()
        return a

    if command == 'JUMP_IF_0':
        a = instruction[1].get_value()
        b = instruction[2].get_value()
        if a == 0:
            return b
        return None

    if command == 'JUMP_IF_N0':
        a = instruction[1].get_value()
        b = instruction[2].get_value()
        if a != 0:
            return b
        return None

    if command == 'RANDOM':
        result = random.randrange(100)
        instruction[1].set_value(result)
        return

    if command == 'IN_CHAR':
        global INPUT
        if not INPUT:
            raise InterpreterError('Not enough standard input provided')
        result = INPUT[0]
        INPUT = INPUT[1:]
        instruction[1].set_value(ord(result))
        return

    global OUTPUT
    if command == 'OUT_NUM':
        a = instruction[1].get_value()
        result = str(a)
        OUTPUT += result
        return
    
    if command == 'OUT_CHAR':
        a = instruction[1].get_value()
        result = chr(a)
        OUTPUT += result
        return

    if command == 'NOP':
        return

    if command == 'PUSH':
        a = instruction[1].get_value()
        STACK.append(a)
        return

    if command == 'POP':
        a = STACK.pop()
        instruction[1].set_value(a)
        return

    if command == 'AR_GET_IDX':
        array = instruction[1].get_value()
        idx = instruction[2].get_value()
        result = array[int(idx)]
        instruction[3].set_value(result)
        return

    if command == 'AR_SET_IDX':
        array = instruction[1].get_value()
        idx = instruction[2].get_value()
        value = instruction[3].get_value()
        array[int(idx)] = value
        return

    if command == 'AR_GET_SIZE':
        array = instruction[1].get_value()
        result = len(array)
        instruction[2].set_value(result)
        return

    if command == 'AR_SET_SIZE':
        array = instruction[1].get_value()
        new_size = instruction[2].get_value()
        while new_size < len(array):
            array.pop()
        while new_size > len(array):
            array.append(0)
        return

    if command == 'AR_COPY':
        source_array = instruction[1].get_value()
        instruction[2].set_value(copy.deepcopy(source_array))
        return

    if command == 'STORE':
        value = instruction[1].get_value()
        address = int(instruction[2].get_value())
        assert address >= 0
        MEMORY[address] = value
        return

    if command == 'LOAD':
        address = int(instruction[1].get_value())
        assert address >= 0
        value = MEMORY.get(address, 0)
        instruction[2].set_value(value)
        return

    if command == 'MEM_COPY':
        address_source = int(instruction[1].get_value())
        address_dest = int(instruction[2].get_value())
        assert address_source >= 0 and address_dest >= 0
        value = MEMORY.get(address_source, 0)
        MEMORY[address_dest] = value
        return

    raise InterpreterError("Unknown command: {}".format(command))


def add_label_locations_to_label_table(INSTRUCTIONS):
    for i, instruction in enumerate(INSTRUCTIONS):
        if instruction:
            first_instruction = instruction[0]
            if isinstance(first_instruction, Label):
                assert first_instruction not in LABEL_TABLE
                LABEL_TABLE[first_instruction.name] = i

def execute_bad_instructions(instructions, language):
    cycles = 0
    step = 0
    add_label_locations_to_label_table(instructions)
    instruction_pointer = 0
    while instruction_pointer < len(instructions):
        if step > MAX_STEPS:
            raise InterpreterError(
                f'More than {MAX_STEPS} steps, likely infinite loop.')
        step += 1
        instruction = instructions[instruction_pointer]
        new_ip = None
        if instruction:
            if language == 'LMAO':
                cycles += 1000
            elif instruction[0] in {'load', 'store', 'mem_copy'}:
                cycles += 100
            else:
                cycles += 1

            if language == 'LMAOcode':
                if instruction[0] in rofl_commands:
                    raise LMAOError(f'Can not use ROFLcode command ({instruction[0]}) in LMAOcode.')
            else: # language == 'LMAOcode':
                if instruction[0] in lmao_commands:
                    raise LMAOError(f'Can not use LMAOcode command ({instruction[0]}) in ROFLcode.')

            new_ip = execute_bad_instruction(instruction)
            if DEBUG_MODE:
                debug_output(instruction, instruction_pointer, step)
        if new_ip is not None:
            instruction_pointer = new_ip
        else:
            instruction_pointer += 1
    return cycles


def debug_output(instruction, line, step):
    output = []
    def print_line_from_table(name, table):
        if table:
            line = name + " { "
            for key in sorted(table):
                line += "{}:{} ".format(key, table[key])
            line += "}"
            output.append(line)

    def print_line_from_stack(name, stack):
        if stack:
            line = name + " (top) { "
            for value in reversed(stack):
                line += "{} ".format(value)
            line += "} (bottom)"
            output.append(line)

    def print_line_of_instruction(instruction):
        result = ''
        for part in instruction:
            if isinstance(part, Var):
                value = part.nice_str()
            else:
                value = str(part)
            result += value + ' '
        return result


    output.append("Step # {}".format(step))
    instruction_str = print_line_of_instruction(instruction)
    output.append("Executed line # {} : {}".format(line + 1, instruction_str))
    print_line_from_table("ST", SYMBOL_TABLE)
    print_line_from_table("Regs", REGISTER_TABLE)
    print_line_from_table("Mem", MEMORY)
    print_line_from_stack("Stack", STACK)
    output.append("")
    with open(DEBUG_FILENAME, "a") as debug_handle:
        debug_handle.write("\n".join(output) + "\n")

def interpret(input_, language, debug_mode=False, profile_mode=False, standard_input="", seed=0):
    assert language in {'LMAOcode', 'ROFLcode'}
    
    global DEBUG_MODE
    DEBUG_MODE = debug_mode
    
    reset(debug_mode=debug_mode)
    random.seed(seed)

    global INPUT
    INPUT = standard_input

    lexer = build_lexer()
    possible_tokens = get_possible_tokens(lexer)
    # pprint(possible_tokens)
    tokens = list(lexer.lex(input_))
    check_for_lexing_errors(tokens, language)
    # pprint(tokens)

    parser = build_parser(possible_tokens, language)
    instructions = parser.parse(iter(tokens))

    cycles = execute_bad_instructions(instructions, language)
    if profile_mode:
        return cycles
    global OUTPUT
    return OUTPUT

def main():
    parser = argparse.ArgumentParser(description="""Takes LMAOcode (or ROFLcode)
                                     from stdin, runs it, and
                                     prints output to stdout.""")
    parser.add_argument('-l', '--language', choices=['LMAOcode', 'ROFLcode'], default='LMAOcode', help="""
                        select the language to interpret.""")
    parser.add_argument('-d', '--debug', action='store_true', help="""
                        add this flag to enable debug mode, printing debug
                        output to stdout""")
    parser.add_argument('-p', '--profile', action='store_true', help="""
                        add this flag to enable profile mode, printing number
                        of cycles executed to stdout""")
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help="""
                        input (should be LMAOcode or ROFLcode) file
                        (defaults to stdin)""")
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout, help="""
                        output file (defaults to stdout)""")
    args = parser.parse_args()

    source = args.infile.read() + '\n'

    output = interpret(source, args.language, args.debug, args.profile)
    args.outfile.write(output)

def reset(debug_mode):
    global MEMORY
    MEMORY.clear()
    global SYMBOL_TABLE
    SYMBOL_TABLE.clear()
    global REGISTER_TABLE
    REGISTER_TABLE.clear()
    global LABEL_TABLE
    LABEL_TABLE.clear()
    global INSTRUCTIONS
    INSTRUCTIONS = []
    global STACK
    STACK = []
    global OUTPUT
    OUTPUT = ""
    global INPUT
    INPUT = ""
    global DEBUG_MODE
    DEBUG_MODE = debug_mode
    if DEBUG_MODE:
        handle = open(DEBUG_FILENAME, "w")
        handle.write("")
        handle.close()


if __name__ == "__main__":
    main()