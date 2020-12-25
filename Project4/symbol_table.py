class RedeclarationError(Exception): pass
class UndeclaredError(Exception): pass


class SymbolTable:
    def __init__(self):
        self.declared_variables = {}
        self.var_count = 1
        self.label_count = 1
        self.loop_stack = []
        self.scope = 0

    def declare_variable(self, name, declaration_type):
        key = (self.scope, name)
        if key in self.declared_variables:
            raise RedeclarationError(f'{name} has already been declared!')
        entry = self.get_entry()
        self.declared_variables[key] = Data(entry, declaration_type)
        return self.declared_variables[key]

    def get_entry_for_variable(self, name):
        for i in range(self.scope, -1, -1):
            key = (i, name)
            try:
                return self.declared_variables[key]
            except:
                continue
        raise UndeclaredError(f'{name} has not been declared!')
        
    def get_entry(self):
        address = self.var_count
        self.var_count += 1
        return f"s{address}"
        
    def get_logical_end_label(self):
        num = self.label_count
        self.label_count += 1
        return f"logical_end_{num}"
        
    def get_logical_lazy_jump_label(self):
        num = self.label_count
        self.label_count += 1
        return f"logical_lazy_jump_{num}"
    
    def get_oic_label(self):
        num = self.label_count
        self.label_count += 1
        return f"oic_{num}"
        
    def get_if_true_jump_label(self):
        num = self.label_count
        self.label_count += 1
        return f"after_if_true_block_{num}"
    
    def get_loop_start_label(self):
        num = self.label_count
        self.label_count += 1
        return f"loop_start_{num}"
        
    def get_loop_end_label(self):
        num = self.label_count
        self.label_count += 1
        return f"loop_end_{num}"
        
        
class Data:
    def __init__(self, address, data_type):
        self.address = address
        self.data_type = data_type
        
    def __repr__(self):
        return f"Data({self.address, self.data_type})"