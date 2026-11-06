from lexer import Token
from tabela_simbolos import *
from ASA import *

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.syntactic_errors = []
        
        self.global_asa = {}
        self.global_table = {}
        self.current_table = None
    
    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]
    
    def consume(self, expected_type: str) -> Token:
        token = self.current_token()
        if token.tipo == expected_type:
            self.pos += 1
            return token
        else:
            self.syntactic_errors.append(
                f"Erro sintatico na linha {token.n_linha}: esperado {expected_type}"
            )
            return token
        
    def parse_type(self) -> DataTypes:

        token = self.current_token()
        if token.tipo in ["INT", "FLOAT", "CHAR"]:
            self.consume(token.tipo)
            return self.map_type(token.tipo)
        else:
            self.syntactic_errors.append(
                f"Erro sintatico na linha {token.n_linha}: esperado tipo, encontrado '{token.lexema}'"
            )
            self.pos += 1
            return DataTypes.DATA_ERROR
    
    def map_type(self, lexeme_type: str) -> DataTypes:
        if lexeme_type == "INT" : return DataTypes.DATA_INT
        if lexeme_type == "FLOAT" : return DataTypes.DATA_FLOAT
        if lexeme_type == "CHAR" : return DataTypes.DATA_CHAR
        return DataTypes.DATA_VOID
    
    
    
    # regras da gramatica
    def parse_program(self):
        while self.current_token().tipo != "EOF":
            if self.current_token().tipo == "FUNCTION":
                self.parse_function()
            else:
                tok = self.current_token()
                self.syntactic_errors.append(
                    f"Erro sintatico na linha {tok.n_linha}: declaracao ou comando fora de funcao ('{tok.lexema}')"
                )
                while self.current_token().tipo not in ["FUNCTION", "EOF"]:
                    if self.current_token().tipo == "SEMICOLON":
                        self.pos += 1
                        break
                    self.pos += 1
    
    def parse_function(self):
        self.consume("FUNCTION")
        
        token_name = self.current_token()
        function_name = token_name.lexema
        if token_name.tipo in ["ID", "MAIN"]:
            self.consume(token_name.tipo)
        else:
            self.syntactic_errors.append(
                f"Erro na linha {token_name.n_linha}: Nome de funcao invalido"
            )
            self.pos += 1
            
        # incia o no da asa para a funcao
        node_function  = FunctionNode(function_name)
        
        # cria a tabela de simbolo para esse escopo
        self.current_table = SymbolTable(name=function_name, ret_type=DataTypes.DATA_VOID)
        self.global_table[function_name] = self.current_table
        
        self.consume("LBRACKET")
        self.parse_params_list()
        self.consume("RBRACKET")
        
        if self.current_token().tipo == "ARROW":
            self.consume("ARROW")
            token_type_ret = self.current_token()
            if token_type_ret.tipo in ["INT", "FLOAT", "CHAR"]:
                self.current_table.ret_type = self.parse_type()
                
        token_type_ret = self.current_token()
        if token_type_ret.tipo in ["INT", "FLOAT", "CHAR"]:
           self.current_table.ret_type = self.parse_type()
        
        #processa o bloco e coloca como filho da funcao
        node_block = self.parse_block()
        node_function.children.append(node_block)
        
        #guarda a arvore na estrutura global
        self.global_asa[function_name] = node_function
        
    def parse_params_list(self):
        pos_param = 0
        if self.current_token().tipo == "ID":
            token_id = self.consume("ID")
            self.consume("COLON")
            param_type = self.parse_type()
            
            #inserir o parametro na tabela de simbolos
            register = SymbolRecord(name=token_id.lexema,datatype=param_type, 
                                    is_param=True, pos_param=pos_param)
            self.current_table.insert_symbol(register)
            pos_param += 1
            
            while self.current_token().tipo == "COMMA":
                self.consume("COMMA")
                token_id = self.consume("ID")
                self.consume("COLON")
                
                param_type = self.parse_type()
                
                register = SymbolRecord(name=token_id.lexema,datatype=param_type, 
                                    is_param=True, pos_param=pos_param)
                self.current_table.insert_symbol(register)
                pos_param += 1
    
    def parse_block(self) -> Block:
        node_block = Block()
        self.consume("LBRACE")
        
        while self.current_token().tipo not in ["RBRACE", "EOF"]:
            if self.current_token().tipo == "LET":
                self.parse_declaration()
            else:
                node_comand = self.parse_comand()
                if node_comand:
                    node_block.children.append(node_comand)
        
        self.consume("RBRACE")
        return node_block
                     
    def parse_declaration(self):
        self.consume("LET")
        ids = [self.consume("ID").lexema]
        
        while self.current_token().tipo == "COMMA":
            self.consume("COMMA")
            ids.append(self.consume("ID").lexema)
            
        self.consume("COLON")
        intern_type = self.parse_type()
        
        if self.current_token().tipo == "ASSIGN":
            self.consume("ASSIGN")
            self.parse_expr()
            
        self.consume("SEMICOLON")
        
        #declaracoes vao para a tabela de simbolos
        for var_name in ids:
            register = SymbolRecord(name=var_name, datatype=intern_type,
                                    is_param=False, pos_param=-1)
            self.current_table.insert_symbol(register)
            
    def parse_comand(self) -> AstNode:
        token = self.current_token()
        
        if token.tipo == "ID":
            token_id = self.consume("ID")
            id_node = IdNode(token_id.lexema)
            
            if self.current_token().tipo == "ASSIGN":
                self.consume("ASSIGN")
                expr_node = self.parse_expr()
                self.consume("SEMICOLON")
                return AssignNode(id_node=id_node, expr_node=expr_node)
            
            elif self.current_token().tipo == "LBRACKET":
                self.consume("LBRACKET")
                args = []
                if self.current_token().tipo != "RBRACKET":
                    args.append(self.parse_expr())
                    while self.current_token().tipo == "COMMA":
                        self.consume("COMMA")
                        args.append(self.parse_expr())
                        
                self.consume("RBRACKET")
                self.consume("SEMICOLON")
                
                lexemas_args = [a.op for a in args if hasattr(a, 'op') and a.op is not None]
                call = FunctionRegister(name=token_id.lexema, args=lexemas_args)
                self.current_table.insert_call(token_id.lexema, call)
                
                call_node = CallNode(token_id.lexema)
                call_node.children.extend(args)
                return call_node
        
        elif token.tipo == "WHILE":
            self.consume("WHILE")
            expr_node = self.parse_expr()
            block_node = self.parse_block()
            return WhileNode(expr_node, block_node)
        
        elif token.tipo == "IF":
            self.consume("IF")
            expr_node = self.parse_expr()
            true_block = self.parse_block()
            false_block = None
            
            if self.current_token().tipo == "ELSE":
                self.consume("ELSE")
                if self.current_token().tipo == "IF":
                    false_block = self.parse_comand()
                elif self.current_token().tipo == "LBRACE":
                    false_block = self.parse_block()
                else:
                    self.syntactic_errors.append(f"Erro na linha {self.current_token().n_linha}: esperado 'if' ou '{{' apos 'else'")
            return IfNode(condition=expr_node, true_block=true_block, false_block=false_block)
        
        elif token.tipo == "PRINTLN":
            self.consume("PRINTLN")
            self.consume("LBRACKET")
            token_fmt = self.consume("FMT_STRING")
            
            print_node = PrintNode(fmt_string=token_fmt.lexema)
            
            if self.current_token().tipo == "COMMA":
                self.consume("COMMA")
                
                arg_node = self.parse_expr()
                print_node.children.append(arg_node)
                
                while self.current_token().tipo == "COMMA":
                    self.consume("COMMA")
                    arg_node = self.parse_expr()
                    print_node.children.append(arg_node)     
                
            self.consume("RBRACKET")    
            self.consume("SEMICOLON")    
            return print_node
        
        elif token.tipo == "RETURN":
            self.consume("RETURN")
            expr_node = self.parse_expr()
            self.consume("SEMICOLON")
            return ReturnNode(expr_node)
        
        else:
            self.syntactic_errors.append(f"Comando invalido na linha {token.n_linha}: {token.lexema}")
            self.pos += 1
            return None
                
    def parse_expr(self) -> AstNode:
        node = self.parse_rel()
        while self.current_token().tipo in ["EQ", "NE"]:
            op_token = self.consume(self.current_token().tipo)
            right_node = self.parse_rel()
            node = RelOp(op=op_token.lexema, left=node, right=right_node)
        return node

    def parse_rel(self) -> AstNode:
        node = self.parse_add()
        while self.current_token().tipo in ["LT", "LE", "GT", "GE"]:
            op_token = self.consume(self.current_token().tipo)
            right_node = self.parse_add()
            node = RelOp(op=op_token.lexema, left=node, right=right_node)
        return node
    
    def parse_add(self) -> AstNode:
        node = self.parse_term()
        while self.current_token().tipo in ["PLUS", "MINUS"]:
            op_token = self.consume(self.current_token().tipo)
            right_node = self.parse_term()
            node = AritOp(op=op_token.lexema, left=node, right=right_node)
        return node
    
    def parse_term(self) -> AstNode:
        node = self.parse_factor()
        while self.current_token().tipo in ["MULT", "DIV"]:
            op_token = self.consume(self.current_token().tipo)
            right_node = self.parse_factor()
            node = AritOp(op=op_token.lexema, left=node, right=right_node)
        return node
    
    def parse_factor(self) -> AstNode:
        token = self.current_token()
        
        if token.tipo == "ID":
            token_id = self.consume("ID")
            
            if self.current_token().tipo == "LBRACKET":
                self.consume("LBRACKET")
                args = []
                if self.current_token().tipo != "RBRACKET":
                    args.append(self.parse_expr())
                    while self.current_token().tipo == "COMMA":
                        self.consume("COMMA")
                        args.append(self.parse_expr())
                        
                self.consume("RBRACKET")
                
                lexeme_args = [a.op for a in args if hasattr(a, 'op') and a.op is not None]
                call_reg = FunctionRegister(name=token_id.lexema, args=lexeme_args)
                self.current_table.insert_call(token_id.lexema, call_reg)
                
                call_node = CallNode(func_name=token_id.lexema)
                call_node.children.extend(args)
                return call_node
            else:
                return IdNode(name=token_id.lexema)

        elif token.tipo == "INT_CONST":
            return IntconstNode(value=self.consume("INT_CONST").lexema)
        elif token.tipo == "FLOAT_CONST":
            return FloatconstNode(value=self.consume("FLOAT_CONST").lexema)
        elif token.tipo == "CHAR_LITERAL":
            return CharconstNode(value=self.consume("CHAR_LITERAL").lexema)
        elif token.tipo == "LBRACKET":
            self.consume("LBRACKET")
            node = self.parse_expr()
            self.consume("RBRACKET")
            return node
        else:
            self.syntactic_errors.append(f"Erro sintatico na linha {token.n_linha}: fator invalido '{token.lexema}'")
            self.pos += 1
            return IdNode("erro")