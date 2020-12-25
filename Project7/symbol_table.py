import collections
from . ast_nodes import PrimitiveType


class RedeclarationError(Exception): pass
class UndeclaredError(Exception): pass
class GTFO_Outside_of_Loop_Error(Exception): pass
class Outside_of_Function_Error(Exception): pass

class SymbolTable:
    def __init__(self):
        self.declared_variables = collections.ChainMap()
        self.declared_function_variables = {}
        self.var_count = 1
        self.label_count = 1
        self.gtfo_stack = []
        self.function_stack = []
        self.if_stack = []
        
        self.f_recur_variables = []

    def declare_variable(self, name, declaration_type):
        if name in self.declared_variables.maps[0]:
            raise RedeclarationError(f'{name} has already been declared!')
        entry = self.get_entry(declaration_type)
        self.declared_variables[name] = entry
        return entry

    def get_entry_for_variable(self, name):
        if name not in self.declared_variables:
            raise UndeclaredError(f'{name} has not been declared!')
        return self.declared_variables[name]
    
    def get_entry(self, expr_type):
        address = self.var_count
        self.var_count += 1
        if isinstance(expr_type, PrimitiveType):
            result = MemoryEntry(expr_type=expr_type, address=address)
        else:
            result = MemoryEntry(expr_type=expr_type, address=address, address_type='a')
            
        if self.function_stack:
            self.f_recur_variables.append(result)
            
        return result

    def get_unique_label(self, root=''):
        unique_value = self.label_count
        self.label_count += 1
        return f'{root}_{unique_value}'
    
    def push_GTFO_stack(self, label):
        self.gtfo_stack.append(label)
    
    def read_GTFO_stack(self):
        if not self.gtfo_stack:
            raise GTFO_Outside_of_Loop_Error('Attempting to read empty GTFO stack')
        return self.gtfo_stack[-1]
    
    def pop_GTFO_stack(self):
        return self.gtfo_stack.pop() 

    def increment_scope(self):
        self.declared_variables.maps.insert(0, {})
    
    def decrement_scope(self):
        self.declared_variables.maps.pop(0)
    
    def get_array_index_entry(self, expr_type, array_entry, index_entry):
        result = self.get_entry(expr_type)
        result.array_entry = array_entry
        result.index_entry = index_entry
        return result
        
    def get_arg_entries(self, func_name, func_label, args, returnType):
        self.increment_scope()
        arg_entries = []
        for arg_name, arg_type in args:
            arg_entry = self.declare_variable(arg_name, arg_type)
            arg_entries.append(arg_entry)
        self.declared_function_variables[func_name] = FunctionEntry(arg_entries, func_label, returnType)
        return arg_entries
        
    def push_func_stack(self, label):
        self.function_stack.append(label)
    
    def read_func_stack(self):
        if not self.function_stack:
            raise Outside_of_Function_Error('Attempting to return without a function')
        return self.function_stack[-1]
    
    def pop_func_stack(self):
        return self.function_stack.pop() 
        
    def push_if_stack(self, label):
        self.if_stack.append(label)
    
    def pop_if_stack(self):
        return self.if_stack.pop() 
            

class MemoryEntry:
    """
    This class represents objects that have memory positions,
    they may have names.
    """
    def __init__(self, expr_type=None, address=None,
                 address_type="s", array_entry=None, index_entry=None):
        self.address = address
        self.address_type = address_type
        self.expr_type = expr_type
        self.array_entry = array_entry
        self.index_entry = index_entry

    def __repr__(self):
        return f'{self.address_type}{self.address}'
        
class FunctionEntry:
    """
    This class represents functions and all the arg memory positions
    """
    def __init__(self, args = [], func_label = None, returnType = None):
        self.args = args
        self.returnType = returnType
        self.funcLabel = func_label
    
    
    