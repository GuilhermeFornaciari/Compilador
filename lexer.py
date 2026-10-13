from dataclasses import dataclass
import sys


palavras_reservadas = {
    "fn": "FUNCTION", 
    "main": "MAIN", 
    "let": "LET",
    "int": "INT", 
    "float": "FLOAT", 
    "char": "CHAR",
    "if": "IF", 
    "else": "ELSE", 
    "while": "WHILE",
    "println": "PRINTLN", 
    "return": "RETURN",
}

ESTADOS = {
    ("inicio","espaco"): "inicio",
    ("inicio","("): "LBRACKET",
    ("inicio",")"): "RBRACKET",
    ("inicio","{"): "LBRACE",
    ("inicio","}"): "RBRACE",
    ("inicio",":"): "COLON",
    ("inicio",";"): "SEMICOLON",
    ("inicio",","): "COMMA",
    ("inicio","+"): "PLUS",
    ("inicio","*"): "MULT",
    ("inicio","/"): "DIV",
    ("inicio","="): "ASSIGN",
    ("ASSIGN","="): "EQ",
    ("inicio","-"): "MINUS",
    ("MINUS",">"): "ARROW",
    ("inicio","!"): "exclamation",
    ("exclamation","="): "NE",
    ("inicio",">"): "GT",
    ("GT","="): "GE",
    ("inicio","<"): "LT",
    ("GT","="): "LE",

    ("inicio","digito"): "INT_CONST",
    ("INT_CONST","digito"): "INT_CONST",
    ("INT_CONST","."): "dot",
    ("dot","digito"): "FLOAT_CONST",
    ("FLOAT_CONST","digito"): "FLOAT_CONST",

    ("inicio","letra"): "ID",
    ("ID","letra"): "ID",
    ("ID","digito"): "ID",
    ("ID","_"): "ID",

    ("inicio","'"): "asp1",
    ("asp1","'"): "CHAR_LITERAL", #Caractere intermediário feito no código sem hash, porque seria necessário tratar todos os casos
    
    ("inicio",'"'): "asp2",
    ("asp2",'"'): "FMT_STRING", #Caracteres intermediários feitos no código sem hash, porque seria necessário tratar todos os casos possíveis
}
ESTADOS_FINAIS = {
    "LBRACKET","RBRACKET",
    "LBRACE","RBRACE",
    "COLON","SEMICOLON",
    "PLUS","MINUS",
    "COMMA", "ARROW",
    "MULT", "DIV",
    "EQ","NE",
    "GT","GE",
    "LT","LE",
    "ASSIGN",
    "INT_CONST",
    "FLOAT_CONST",
    "ID",
    "CHAR_LITERAL",
    "FMT_STRING",
}

@dataclass(frozen=True)
class Token:
    lexema: str
    tipo: str
    n_linha: int
    n_col: int

def classifica(char:str):
    if char in " \n\t"                  : return "espaco" 
    if char.isascii() and char.isalpha(): return "letra" 
    if char in "0123456789"             : return "digito"
    return char
    

def main():
    nome_arquivo = sys.argv[1]
    if not nome_arquivo: 
        print("Nome de arquivo inválido")
        return 0
    linha = 1
    col = 1
    estado = "inicio"
    tokens: list[Token] = []
    lexema = ""

    with open(nome_arquivo) as arquivo:
        while True:
            char = arquivo.read(1)
            if char == "": break #Chegou no EOF, encerra o loop
            if char == "\n": 
                linha += 1
                col = 1
            else: 
                col += 1

            char = classifica(char)
            if char != " ": lexema += char #Adiciona o char no final do lexema

            if estado != "inicio" and char == "espaco" :
                if not (estado in ESTADOS_FINAIS):
                    estado = "ERRO"
                tokens.append(Token(lexema,estado,linha,col))
                lexema = ""
                estado = "inicio"

            if estado == "asp1" and char != "'": continue
            if estado == "asp2" and char != '"': continue
            estado = ESTADOS.get((estado,char),"outro")


            
             