from enum import Enum

class DataTypes(Enum):
    DATA_ERROR = -1
    DATA_INT = 0
    DATA_FLOAT = 1
    DATA_CHAR = 2
    DATA_VOID = 3

class FunctionRegister:
    def __init__(self, name: str, args: list[str]):
        self.name = name            #lexema com o nome da func chamada
        self.args = args            #lexema dos argumentps
        self.num_args = len(args)   #numero de argumentos

class SymbolRecord:
    def __init__(self, name: str, datatype: DataTypes, is_param: bool, pos_param: int):
        self.name = name            #nome da variavel ou func
        self.datatype = datatype    #tipo da variavel
        self.is_param = is_param    #flag se e variavel ou parametro
        self.pos_param = pos_param  #-1 para locais e outros numeros para parametros
        self.call_refs = []         #referencias para o FunctionRegister
        
class SymbolTable:
    def __init__(self, name: str, ret_type: DataTypes):
        self.name = name            #nome da funcao dona desse escopo
        self.ret_type = ret_type    #atributo separado para o tipo de retorno
        self.symbols = {}          #hash onde a chave eh o lexema do identificador e o valor eh o SymbolRecord
    
    def insert_symbol(self, record: SymbolRecord):
        self.symbols[record.name] = record
    
    def insert_call(self, name_symbol: str, call: FunctionRegister):
        #associa um FunctionRegister ao vetor call_refs de um simbolo
        if name_symbol in self.symbols:
            self.symbols[name_symbol].call_refs.append(call)