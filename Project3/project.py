from . lolcode_lexer import build_lexer
from . lolcode_parser import build_parser, parse_LOLcode
from . symbol_table import SymbolTable
import pprint

def generate_LMAOcode_from_LOLcode(lolcode_str):
    tree = parse_LOLcode(lolcode_str)
    pprint.pprint(tree)
    compiled_code = []
    symbol_table = SymbolTable()
    tree.compile(compiled_code, symbol_table)


    # print(compiled_code)
    return '\n'.join(compiled_code) + '\n'