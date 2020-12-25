class RedeclarationError(Exception): pass
class UndeclaredError(Exception): pass


class SymbolTable:
    def __init__(self):
        self.declared_variables = {}
        self.s_count = 0
    
    def get_new_s_location(self):
        self.s_count += 1
        return f"s{self.s_count}"

    def declare_variable(self, name, declaration_type):
        if name in self.declared_variables:
            raise RedeclarationError(f'{name} has already been declared!')
        self.declared_variables[name] = declaration_type

    def use_variable(self, name):
        if name not in self.declared_variables:
            raise UndeclaredError(f'{name} has not been declared!')
            
    def add_sym(self, name, destination):
        self.declared_variables[name] = destination
        
    def find_destination(self, name):
        return self.declared_variables[name]