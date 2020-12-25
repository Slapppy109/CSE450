from . lolcode_parser import build_parser, parse_LOLcode
from  . symbol_table import SymbolTable

def convert_compiled_code_to_str(compiled_code):
    lines = ''
    for row in compiled_code:
        line = ''
        for elem in row:
            line += str(elem) + ' '
        line = line.strip()
        line += '\n'
        lines += line
    return lines

def generate_LMAOcode_from_LOLcode(lolcode_str):
    parse_tree = parse_LOLcode(lolcode_str)
    print("Parse Tree:")
    print(parse_tree)

    symbol_table = SymbolTable()
    compiled_code = []
    parse_tree.compile(symbol_table, compiled_code)
    
    lmaocode_str = convert_compiled_code_to_str(compiled_code)
    return lmaocode_str
    
def generate_ROFLcode_from_LOLcode(lolcode_str):
    label_num = 0
    lmaocode_str = generate_LMAOcode_from_LOLcode(lolcode_str)
    lmao_array = lmaocode_str.split('\n')
    rofl_array = [['STORE', '10000', '0']]
    for lmao_line in lmao_array:
        lmao_line_array = lmao_line.split()
        lines = []
        #print(lmao_line_array)
        if len(lmao_line_array) == 0:
            continue
        try:
            if lmao_line_array[1] == "'":
                lmao_line_array = [lmao_line_array[0], "' '", lmao_line_array[3]]
            if lmao_line_array[3] == "'" and lmao_line_array[4] == "'":
                lmao_line_array = [lmao_line_array[0], lmao_line_array[1], lmao_line_array[2], "' '"]
        except:
            pass
        if lmao_line_array[0] == 'VAL_COPY':
            if len(lmao_line_array[1]) > 1 and lmao_line_array[1][0] == 's':
                lines.append(['LOAD', lmao_line_array[1][1:], 'regA'])
            else:
                lines.append(['VAL_COPY', lmao_line_array[1], 'regA'])
            lines.append(['VAL_COPY', 'regA', 'regB'])
            lines.append(['STORE', 'regB', lmao_line_array[2][1:]])
        elif lmao_line_array[0] == 'OUT_NUM':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA'])
            lines.append(['OUT_NUM','regA'])
        elif lmao_line_array[0] == 'OUT_CHAR':
            if lmao_line_array[1][0] != 's':
                lines.append(['VAL_COPY', lmao_line_array[1], 'regA'])
            else:
                lines.append(['LOAD', lmao_line_array[1][1:], 'regA'])
            lines.append(['OUT_CHAR','regA'])
        elif lmao_line_array[0] == 'RANDOM':
            lines.append(['RANDOM', 'regA'])
            lines.append(['STORE','regA', lmao_line_array[1][1:]])
        elif lmao_line_array[0] == 'IN_CHAR':
            lines.append(['IN_CHAR','regA'])
            lines.append(['STORE', 'regA', lmao_line_array[1][1:]])
        elif lmao_line_array[0] == 'ADD':
            if lmao_line_array[1].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[1], 'regA'])
            else:
                lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            lines.append(['LOAD', lmao_line_array[2][1:], 'regB'])
            lines.append(['ADD', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'SUB':
            if lmao_line_array[1].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[1], 'regA'])
            else:
                lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            lines.append(['LOAD', lmao_line_array[2][1:], 'regB'])
            lines.append(['SUB', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'MULT':
            if lmao_line_array[1].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[1], 'regA'])
            else:
                lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            lines.append(['LOAD', lmao_line_array[2][1:], 'regB'])
            lines.append(['MULT', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'DIV':
            if lmao_line_array[1].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[1], 'regA'])
            else:
                lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            lines.append(['LOAD', lmao_line_array[2][1:], 'regB'])
            lines.append(['DIV', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'TEST_NEQU':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA'])
            if lmao_line_array[2].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[2], 'regB'])
            else:
                lines.append(['LOAD', lmao_line_array[2][1:], 'regB']) 
            lines.append(['TEST_NEQU', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'TEST_EQU':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            if lmao_line_array[2].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[2], 'regB'])
            else:
                lines.append(['LOAD', lmao_line_array[2][1:], 'regB']) 
            lines.append(['TEST_EQU', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'TEST_GTE':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            if lmao_line_array[2].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[2], 'regB'])
            else:
                lines.append(['LOAD', lmao_line_array[2][1:], 'regB']) 
            lines.append(['TEST_GTE', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'TEST_GTR':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            if lmao_line_array[2].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[2], 'regB'])
            else:
                lines.append(['LOAD', lmao_line_array[2][1:], 'regB']) 
            lines.append(['TEST_GTR', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'TEST_LESS':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            if lmao_line_array[2].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[2], 'regB'])
            else:
                lines.append(['LOAD', lmao_line_array[2][1:], 'regB']) 
            lines.append(['TEST_LESS', 'regA', 'regB', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'JUMP_IF_0':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            lines.append(['VAL_COPY', lmao_line_array[2], 'regB'])
            lines.append(['JUMP_IF_0', 'regA', 'regB' ])
        elif lmao_line_array[0] == 'JUMP_IF_N0':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA']) 
            lines.append(['VAL_COPY', lmao_line_array[2], 'regB'])
            lines.append(['JUMP_IF_N0', 'regA', 'regB' ])
        elif lmao_line_array[0] == 'JUMP':
            lines.append(['VAL_COPY', lmao_line_array[1], 'regA'])
            lines.append(['JUMP', 'regA'])
        elif lmao_line_array[0] == 'AR_SET_SIZE':
            lines.append(['LOAD', lmao_line_array[2][1:], 'regA'])
            lines.append(['LOAD', 0, 'regB'])
            lines.append(['STORE', 'regB', lmao_line_array[1][1:]])
            lines.append(['STORE', 'regA', 'regB'])
            lines.append(['ADD', 'regA', 'regB', 'regC'])
            lines.append(['ADD', 1, 'regC', 'regC'])
            lines.append(['STORE', 'regC', 0])
        elif lmao_line_array[0] == 'AR_GET_SIZE':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA'])
            lines.append(['LOAD', 'regA', 'regB'])
            lines.append(['STORE', 'regB', lmao_line_array[2][1:]])
        elif lmao_line_array[0] == 'AR_SET_IDX':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA'])
            if lmao_line_array[2].isdigit():
                lines.append(['VAL_COPY', lmao_line_array[2], 'regB'])
            else:
                lines.append(['LOAD', lmao_line_array[2][1:], 'regB'])
            if lmao_line_array[3][0] != 's':
                lines.append(['VAL_COPY', lmao_line_array[3], 'regC'])
            else:    
                lines.append(['LOAD', lmao_line_array[3][1:], 'regC'])
            lines.append(['ADD', 'regA', 1, 'regD'])
            lines.append(['ADD', 'regD', 'regB', 'regD'])
            lines.append(['STORE', 'regC', 'regD'])
        elif lmao_line_array[0] == 'AR_GET_IDX':
            lines.append(['LOAD', lmao_line_array[1][1:], 'regA'])
            lines.append(['LOAD', lmao_line_array[2][1:], 'regB'])
            lines.append(['ADD', 'regA', 1, 'regD'])
            lines.append(['ADD', 'regD', 'regB', 'regD'])
            lines.append(['LOAD', 'regD', 'regC'])
            lines.append(['STORE', 'regC', lmao_line_array[3][1:]])
        elif lmao_line_array[0] == 'AR_COPY':
            lines.append(['LOAD', 0, 'regA'])
            lines.append(['STORE', 'regA', lmao_line_array[2][1:]])
            lines.append(['LOAD', lmao_line_array[1][1:], 'regB'])
            lines.append(['LOAD', 'regB', 'regC'])
            lines.append(['MEM_COPY', 'regB', 'regA'])
            lines.append(['ADD', 1, 'regA', 'regA'])
            lines.append(['ADD', 1, 'regB', 'regB'])
            lines.append(['VAL_COPY', 0, 'regD'])
            loop_start_label = f"ar_copy_loop_start_{label_num}"
            loop_end_label = f"ar_copy_loop_end_{label_num}"
            label_num += 1
            lines.append([loop_start_label + ':'])
            lines.append(['MEM_COPY', 'regB', 'regA'])
            lines.append(['ADD', 1, 'regA', 'regA'])
            lines.append(['ADD', 1, 'regB', 'regB'])
            lines.append(['ADD', 1, 'regD', 'regD'])
            lines.append(['TEST_EQU', 'regD', 'regC', 'regE'])
            lines.append(['JUMP_IF_N0', 'regE', loop_end_label])
            lines.append(['JUMP', loop_start_label])
            lines.append([loop_end_label + ':'])
            lines.append(['STORE', 'regA', 0])
        else:
            lines.append([lmao_line_array[0]])
        for line in lines:
                rofl_array.append(line)
    rofl_str = convert_compiled_code_to_str(rofl_array)
    return rofl_str