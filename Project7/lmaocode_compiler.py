import itertools

HEAP_START = 10000
CALL_STACK_START = 20000
COUNTER = 0

def compile_ROFLcode_from_LMAOcode(lmaocode_str):
    roflcode_lines = get_header_ROFLcode()
    for lmao_line in lmaocode_str.splitlines():
        roflcode_lines.append('# Converting ' + lmao_line)
        roflcode_lines += convert_lmao_line_to_rofl_lines(lmao_line)
    return '\n'.join(roflcode_lines) + '\n'

def get_header_ROFLcode():
    return [
        f'STORE {HEAP_START} 0 # Start heap at {HEAP_START}',
        f'VAL_COPY {CALL_STACK_START} regH # Start Call Stack at 20000'
    ]

def convert_lmao_line_to_rofl_lines(lmao_line):
    parts = break_line_into_parts(lmao_line)
    
    if not parts:
        return []

    assert len(parts) >= 2
    
    command, *args = parts
    
    if command == 'VAL_COPY':
        assert len(args) == 2
        source, dest = args
        lines = load_reg('regA', source)
        lines += ['VAL_COPY regA regB']
        lines += store_reg('regB', dest)
        return lines
    if command in {'OUT_CHAR', 'OUT_NUM'}:
        assert len(args) == 1
        lines = load_reg('regA', args[0])
        lines += [f'{command} regA']
        return lines
    if command in {'RANDOM', 'IN_CHAR'}:
        assert len(args) == 1
        lines = [f'{command} regA']
        lines += store_reg('regA', args[0])
        return lines
    math_commands = {'ADD', 'SUB', 'MULT', 'DIV', 'TEST_LESS', 
                     'TEST_GTR', 'TEST_EQU', 'TEST_NEQU', 
                     'TEST_GTE', 'TEST_LTE'}
    if command in math_commands:
        assert len(args) == 3
        lines = load_reg('regA', args[0])
        lines += load_reg('regB', args[1])
        lines += [f'{command} regA regB regC']
        lines += store_reg('regC', args[2])
        return lines
    if args[0] == ':':
        assert len(args) == 1
        return [command + ':']
    if command == 'JUMP':
        assert len(args) == 1
        lines = load_reg('regA', args[0])
        lines +=  ['JUMP regA']
        return lines
    if command in {'JUMP_IF_0', 'JUMP_IF_N0'}:
        assert len(args) == 2
        lines = load_reg('regA', args[0])
        lines += load_reg('regB', args[1])
        lines +=  [f'{command} regA regB']
        return lines

    if command == 'AR_SET_SIZE':
        assert len(args) == 2
        array_var, size_var = args

        assert array_var[0] == 'a'
        
        array_pointer = array_var[1:]

        new_size = 'regA'
        free_mem = 'regB'
        new_free_mem = 'regC'

        lines = [f'# Load the size into {new_size}']
        lines += load_reg(new_size, size_var)
        lines += [
            f'LOAD 0 {free_mem} # free_mem value',
            f'STORE {free_mem} {array_pointer} # update pointer to free mem',
            f'STORE {new_size} {free_mem} # Store size in new array',
            f'ADD {new_size} {free_mem} {new_free_mem} # Begin calulation of new free mem',
            f'ADD 1 {new_free_mem} {new_free_mem} # {new_free_mem} is the new end of allocated mem',
            f'STORE {new_free_mem} 0 # Save new free mem in position 0'
        ]
        return lines
    
    if command == 'AR_GET_SIZE':
        assert len(args) == 2
        array_var, store_var = args
        assert array_var[0] == 'a'

        address = array_var[1:]
        lines = load_reg('regA', array_var)
        lines += ['LOAD regA regB']
        lines += store_reg('regB', store_var)
        return lines
    if command == 'AR_SET_IDX':
        assert len(args) == 3
        array_var, index_var, value_var = args
        assert array_var[0] == 'a'

        lines = load_reg('regA', array_var)
        lines += load_reg('regB', index_var)
        lines += load_reg('regC', value_var)

        lines += [
            'ADD regA 1 regD',
            'ADD regD regB regD',
            'STORE regC regD'
        ]
        return lines
    if command == 'AR_GET_IDX':
        assert len(args) == 3
        array_var, index_var, value_var = args
        assert array_var[0] == 'a'

        lines = load_reg('regA', array_var)
        lines += load_reg('regB', index_var)

        lines += [
            'ADD regA 1 regD',
            'ADD regD regB regD',
            'LOAD regD regC']

        lines += store_reg('regC', value_var)
        return lines

    if command == 'AR_COPY':
        assert len(args) == 2
        source_array_var, dest_array_var = args

        assert source_array_var[0] == 'a'
        assert dest_array_var[0] == 'a'
        
        source_array_pointer = source_array_var[1:]
        dest_array_pointer = dest_array_var[1:]


        source_array = 'regA'
        new_size = 'regB'
        old_free_mem = 'regC'
        new_free_mem = 'regD'
        last_element_of_source = 'regE'
        dest_array = old_free_mem
        is_done = 'regF'

        start_label = get_unique_label('Start_of_array_copy_loop')
        end_label = get_unique_label('End_of_array_copy_loop')


        # Get size
        lines = [
            f'LOAD {source_array_pointer} {source_array} # Get start of source array',
            f'LOAD {source_array} {new_size} # Get size of source array',
        ]

        # Create destination array
        lines += [
            f'LOAD 0 {old_free_mem} # free_mem value',
            f'STORE {old_free_mem} {dest_array_pointer} # update pointer to free mem',
            f'STORE {new_size} {old_free_mem} # Store size in new array',
            f'ADD {new_size} {old_free_mem} {new_free_mem} # Begin calulation of new free mem',
            f'ADD 1 {new_free_mem} {new_free_mem} # {new_free_mem} is the new end of allocated mem',
            f'STORE {new_free_mem} 0 # Save new free mem in position 0'
        ]

        # Set up for copy loop
        lines += [
            f'ADD 1 {source_array} {source_array} # Make {source_array} point at the first element of source',
            f'ADD 1 {dest_array} {dest_array} # Make {dest_array} point at the first element of dest',
            f'ADD {source_array} {new_size} {last_element_of_source} # Make {last_element_of_source} the end of the array',
        ]

        # Do copy loop
        lines += [
            f'{start_label}:',
            f'# {is_done} is 1 if source pointer ({source_array}) is past the end of the array',
            f'TEST_GTR {source_array} {last_element_of_source} {is_done}', 
            f'JUMP_IF_N0 {is_done} {end_label}',

            f'MEM_COPY {source_array} {dest_array}',

            f'ADD 1 {source_array} {source_array} # Increment source pointer',
            f'ADD 1 {dest_array} {dest_array} # Increment dest pointer',
            f'JUMP {start_label}',
            f'{end_label}:',
        ]
        return lines
        
    if command == 'POP':
        assert len(args) == 1
        lines = [
            'SUB regH 1 regH',
            'LOAD regH regA']
        lines += store_reg('regA', args[0])
        return lines
        
    if command == 'PUSH':
        assert len(args) == 1
        lines = load_reg('regA', args[0])
        lines += [
            'STORE regA regH',
            'ADD 1 regH regH'
            ]
        return lines
        
    raise AssertionError(f'Unexpected command ({command})')
        


def check_reg_str(reg_str):
    assert reg_str[:3] == 'reg'
    assert reg_str[3] in 'ABCDEFGH'
    assert len(reg_str) == 4

def load_reg(reg, value_str):
    check_reg_str(reg)
    first_letter = value_str[0]
    rest = value_str[1:]
    if (first_letter in {'s', 'a'}) and rest.isdigit():
        return [f'LOAD {rest} {reg}']
    else:
        return [f'VAL_COPY {value_str} {reg}']

def store_reg(reg, value_str):
    check_reg_str(reg)
    assert value_str[0] in {'s', 'a'}
    return [f'STORE {reg} {value_str[1:]}']

def break_line_into_parts(line):
    parts = line.split()
    parts = remove_comments(parts)
    parts = reassemble_space_literals(parts)
    parts = seperate_colon(parts)

    return parts

def remove_comments(parts):
    return list(itertools.takewhile(lambda x: x[0] != '#', parts))

def reassemble_space_literals(parts):
    if "'" in parts:
        index = parts.index("'")
        assert parts[index + 1] == "'", 'Expected a second apostraphe.'
        parts[index] = "' '"
        del parts[index + 1]
    return parts

def seperate_colon(parts):
    if parts and parts[0][-1] == ':':
        assert len(parts) == 1, 'Expected dropped labels to have only one part.'
        return [parts[0][:-1], ':']
    return parts



def get_unique_label(name):
    global COUNTER
    COUNTER += 1
    return f'{name}_{COUNTER}'