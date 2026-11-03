#Link do AFD base: https://canva.link/x84sbsstohedt39
from dataclasses import dataclass
import sys

@dataclass(frozen=True)
class Token:
    lexema: str
    tipo: str
    n_linha: int
    n_col: int
class Lexer:
    
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

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tamanho = len(source_code)
        self.pos = 0
        self.linha = 1
        self.coluna = 1
        self.tokens: list[Token] = []
        self.erros: list[str] = []
    
    def e_final(self) -> bool:
        return self.pos >= self.tamanho
    
    @classmethod
    def from_file(cls, filepath: str) -> "Lexer":
        with open(filepath, "r", encoding="utf-8") as f:
            return cls(f.read())
    
    @staticmethod
    def classifica(char:str):
        if char in " \n\t\r"                  : return "espaco" 
        if char.isascii() and char.isalpha(): return "letra" 
        if char in "0123456789"             : return "digito"
        return char
        
    def _fecha_token(self,lexema, estado, linha, col) -> Token:
        if estado == "ID":
            estado = self.palavras_reservadas.get(lexema, "ID")
        # char precisa de exatamente 1 caractere, string de pelo menos 1
        if estado == "CHAR_LITERAL" and len(lexema) != 3: estado = "ERRO"
        if estado == "FMT_STRING" and len(lexema) < 3:    estado = "ERRO"
        if estado not in self.ESTADOS_FINAIS and estado not in self.palavras_reservadas.values():
            estado = "ERRO"
        return Token(lexema, estado, linha, col)

    def tokenize(self) -> tuple[list[Token], list[str]]:
        estado = "inicio"
        lexema = ""
        
        while not self.e_final():
            c = self.source_code[self.pos]
            linha_c, col_c = self.linha, self.coluna

            if c == "\n":
                self.linha += 1
                self.coluna = 1
            else:
                self.coluna += 1

            self.pos += 1
            char = self.classifica(c)
            dentro_asp = estado in ("asp1", "asp2")

            if char != "espaco" or dentro_asp:
                lexema += c

            if estado != "inicio" and char == "espaco" and not dentro_asp:
                tok = self._fecha_token(lexema, estado, linha_c, col_c - len(lexema))
                if tok.tipo == "ERRO":
                    self.erros.append(f"Erro léxico na linha {tok.n_linha}, coluna {tok.n_col}: lexema inválido {tok.lexema!r}")
                else:
                    self.tokens.append(tok)
                lexema = ""
                estado = "inicio"

            if char != "espaco" and estado in self.ESTADOS_FINAIS and (estado, char) not in self.ESTADOS:
                tok = self._fecha_token(lexema[:-1], estado, linha_c, col_c - len(lexema) + 1)
                if tok.tipo == "ERRO":
                    self.erros.append(f"Erro léxico na linha {tok.n_linha}, coluna {tok.n_col}: lexema inválido {tok.lexema!r}")
                else:
                    self.tokens.append(tok)
                estado = "inicio"
                lexema = c

            if estado == "asp1" and char != "'":
                continue
            if estado == "asp2" and char != '"':
                continue

            estado = self.ESTADOS.get((estado, char), "outro")
            if estado == "outro":
                self.erros.append(f"Erro léxico na linha {linha_c}, coluna {col_c}: símbolo inesperado {lexema!r}")
                lexema = ""
                estado = "inicio"

        if estado != "inicio" and lexema != "":
            tok = self._fecha_token(lexema, estado, self.linha, self.coluna - len(lexema))
            if tok.tipo == "ERRO":
                self.erros.append(f"Erro léxico na linha {tok.n_linha}, coluna {tok.n_col}: lexema inválido {tok.lexema!r}")
            else:
                self.tokens.append(tok)

        self.tokens.append(Token(lexema="", tipo="EOF", n_linha=self.linha, n_col=self.coluna))
        return self.tokens, self.erros

def main():
    if len(sys.argv) < 2:
        print("Uso: python lexer.py <caminho_arquivo>")
        return 1

    lexer = Lexer.from_file(sys.argv[1])
    tokens, erros = lexer.tokenize()

    for t in tokens:
        print(t)

    for erro in erros:
        print(erro, file=sys.stderr)

    return 0 if not erros else 1

if __name__ == "__main__":            
    main()       
    sys.exit()