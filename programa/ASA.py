from tabela_simbolos import DataTypes

class AstNode:
    def __init__(self, node_type: str, op: str = None):
        self.node_type = node_type  # tipo do no ex:ifnode, aritop
        self.op = op                #Armazena o operador, nome da var ou valor literal
        self.data_type = None       #sera preenchido na analise semantica
        self.children = []          #lista dos nos filhos
    
    @property
    def num_children(self):
        return len(self.children)
    
    
    
# NOS DE ESTRUTURA E CONTROLE    
class FunctionNode(AstNode):
    #possui um unico filho o no bloco. Sera add durante o parser
        def __init__(self, name: str):
             super().__init__("FunctionNode", op=name)

class Block(AstNode):
    #possui um ou mais filhos (sequencia de comandos)
    def __init__(self):
         super().__init__("Bloco")

class IfNode(AstNode):
    #possui 2 filhos (sem else) ou 3 filhos (com else). Conficao, verdade e falso
    def __init__(self, condition: AstNode, true_block: AstNode, false_block: AstNode = None):
         super().__init__("IfNode")
         self.children.extend([condition, true_block])
         if false_block is not None:
             self.children.append(false_block)

class WhileNode(AstNode):
    #possui 2 filhos: condicao e comandos da parte verdadeira
    def __init__(self, condition: AstNode, block: AstNode):
         super().__init__("WhileNode")
         self.children.extend([condition, block])

class ReturnNode(AstNode):
    #possui somente um filho a expressao de retorno
    def __init__(self, expr: AstNode):
         super().__init__("ReturnNode")
         self.children.append(expr)
         
         
         
#NOS DE OPERACAO E COMANDOS
class AssignNode(AstNode):
    #possui 2 filhos o IdNOde (lado esquerdo) e a expressao(lado direito)
    def __init__(self, id_node: AstNode, expr_node: AstNode):
         super().__init__("AssignNode", op="=")
         self.children.extend([id_node, expr_node])

class AritOp(AstNode):
    #possui 2 filhos o operandos da esquerda e da direita
    def __init__(self, op: str, left: AstNode, right: AstNode):
         super().__init__("AritOp", op=op)
         self.children.extend([left, right])

class RelOp(AstNode):
    #possui 2 filhos o operando da esquerda e da direita
    def __init__(self, op: str, left: AstNode, right: AstNode):
         super().__init__("RelOp", op=op)
         self.children.extend([left, right])

class PrintNode(AstNode):
    #usado para a preservacao da string de formatacao
    #possui um vetor de filhos que representam os args de println
    def __init__(self, fmt_string: str):
        super().__init__("PrintNode", op=fmt_string)

class CallNode(AstNode):
    #atributo op guarda o nome da funcao
    #os filhos sao os argumentos passados na chamada da funcao
    def __init__(self, func_name: str):
         super().__init__("CallNode", op=func_name)
         


#NOS FOLHA (operandos e valores)
class IdNode(AstNode):
    def __init__(self, name: str):
         super().__init__("IdNode", op=name)

class IntconstNode(AstNode):
    def __init__(self, value: str):
         super().__init__("IntconstNode", op=value)
         self.data_type = DataTypes.DATA_INT

class FloatconstNode(AstNode):
    def __init__(self, value: str):
         super().__init__("FloatconstNode", op=value)
         self.data_type = DataTypes.DATA_FLOAT

class CharconstNode(AstNode):
    def __init__(self, value: str):
         super().__init__("CharconstNode", op=value)
         self.data_type = DataTypes.DATA_CHAR