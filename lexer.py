#Link do AFD base: https://canva.link/x84sbsstohedt39
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
    ("LT","="): "LE",

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
    if char in " \n\t\r"                  : return "espaco" 
    if char.isascii() and char.isalpha(): return "letra" 
    if char in "0123456789"             : return "digito"
    return char
    
def fecha(lexema, estado, linha, col):
    if estado == "ID":
        estado = palavras_reservadas.get(lexema, "ID")
    # char precisa de exatamente 1 caractere, string de pelo menos 1
    if estado == "CHAR_LITERAL" and len(lexema) != 3: estado = "ERRO"
    if estado == "FMT_STRING" and len(lexema) < 3:    estado = "ERRO"
    if estado not in ESTADOS_FINAIS and estado not in palavras_reservadas.values():
        estado = "ERRO"
    return Token(lexema, estado, linha, col)

def main():
    if len(sys.argv) < 2:                      
        print("Nome de arquivo inválido")
        return 1
    nome_arquivo = sys.argv[1]
    linha = 1
    col = 1
    estado = "inicio"
    tokens: list[Token] = []
    lexema = ""

    with open(nome_arquivo, encoding="utf-8") as arquivo:
        while True:
            c = arquivo.read(1)                 
            if c == "": break
            linha_c, col_c = linha, col        
            if c == "\n":
                linha += 1
                col = 1
            else:
                col += 1

            char = classifica(c)
            dentro_asp = estado in ("asp1", "asp2")
            if char != "espaco" or dentro_asp:  
                lexema += c                    

            if estado != "inicio" and char == "espaco" and not dentro_asp:
                tokens.append(fecha(lexema, estado, linha_c, col_c - len(lexema)))
                lexema = ""
                estado = "inicio"

            if (char != "espaco" and estado in ESTADOS_FINAIS and (estado, char) not in ESTADOS):
                tokens.append(fecha(lexema[:-1], estado, linha_c, col_c - len(lexema) + 1))
                estado = "inicio"
                lexema = c

            if estado == "asp1" and char != "'": continue
            if estado == "asp2" and char != '"': continue

            estado = ESTADOS.get((estado, char), "outro")
            if estado == "outro":
                for t in tokens:
                    print(t)
                print(f"Erro léxico na linha {linha_c}, coluna {col_c}: {lexema!r}")
                return 1

    if estado != "inicio":                   
        tokens.append(fecha(lexema, estado, linha, col - len(lexema)))


    for t in tokens:
        print(t)
    return tokens

if __name__ == "__main__":            
    main()       
    sys.exit()