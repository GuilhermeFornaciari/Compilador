import sys
import os
import json
from lexer import Lexer
from Parser import Parser

def ast_to_dict(node):
    if node is None:
        return None
    
    result = {
        "node_type": node.node_type,
    }
    
    if node.op:
        result["op"] = node.op
    if node.data_type:
        result["data_type"] = str(node.data_type.name) if hasattr(node.data_type, 'name') else str(node.data_type)
        
    if hasattr(node, 'children') and node.children:
        result["children"] = [ast_to_dict(c) for c in node.children]
        
    return result

def main():
    if len(sys.argv) < 2:
        print("Uso incorreto.")
        print("Execute da seguinte forma: python main.py <caminho_do_arquivo_codigo.p>")
        return 1

    input_file = sys.argv[1]
    print(f"Iniciando a compilacao do arquivo: {input_file}...\n")
    
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    output_dir = os.path.join("../saidas", base_name)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # FASE 1: ANALISE LEXICA
    try:
        lexer = Lexer.from_file(input_file)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{input_file}' nao foi encontrado.")
        return 1
        
    tokens, erros_lexicos = lexer.tokenize()

    # Saida: Tokens e Erros Lexicos
    lexica_path = os.path.join(output_dir, "saida_lexica.txt")
    with open(lexica_path, "w", encoding="utf-8") as f:
        f.write("--- TOKENS RECONHECIDOS ---\n")
        for t in tokens:
            f.write(str(t) + "\n")
        
        if erros_lexicos:
            f.write("\n--- ERROS LEXICOS ---\n")
            for erro in erros_lexicos:
                f.write(erro + "\n")

    print(f"Analise Lexica concluida (verifique {lexica_path}).")


    # FASE 2: ANALISE SINTATICA E TABELAS
    parser = Parser(tokens)
    parser.parse_program()

    # SAIDA OBRIGATORIA 1: Arquivo de Erros Sintaticos
    sintatico_path = os.path.join(output_dir, "saida_erros_sintaticos.txt")
    with open(sintatico_path, "w", encoding="utf-8") as f:
        if parser.syntactic_errors:
            f.write("--- ERROS SINTATICOS ---\n")
            for erro in parser.syntactic_errors:
                f.write(erro + "\n")
        else:
            f.write("Analise sintatica concluida sem erros.\n")
            
    print(f"Analise Sintatica concluida (verifique {sintatico_path}).")

    # SAIDA OBRIGATORIA 2: Tabelas de Simbolos por Escopo
    tabela_path = os.path.join(output_dir, "saida_tabela_simbolos.txt")
    with open(tabela_path, "w", encoding="utf-8") as f:
        for func_name, tabela in parser.global_table.items():
            f.write(f"\n================================================================================\n")
            f.write(f"Tabela de Simbolos da Funcao: {func_name}\n")
            
            tipo_retorno = tabela.ret_type.name if hasattr(tabela.ret_type, 'name') else str(tabela.ret_type)
            f.write(f"Tipo de retorno: {tipo_retorno}\n")
            f.write(f"================================================================================\n")
            f.write(f"{'NOME':<15} | {'TIPO (DataTypes)':<20} | {'EH PARAM?':<10} | {'POSICAO':<10} | {'CHAMADAS DE FUNCAO'}\n")
            f.write("-" * 80 + "\n")
            
            for sym_name, record in tabela.symbols.items():
                chamadas = [c.name for c in record.call_refs]
                tipo_str = record.datatype.name if hasattr(record.datatype, 'name') else str(record.datatype)
                
                f.write(f"{record.name:<15} | {tipo_str:<20} | {str(record.is_param):<10} | {record.pos_param:<10} | {chamadas}\n")

    print(f"Tabela de Simbolos gerada (verifique {tabela_path}).")

    # SAIDA OBRIGATORIA 3: Visualizacao da Arvore de Sintaxe Abstrata (ASA) em JSON
    asa_dict = {}
    for func_name, ast_node in parser.global_asa.items():
        asa_dict[func_name] = ast_to_dict(ast_node)

    asa_path = os.path.join(output_dir, "saida_asa.json")
    with open(asa_path, "w", encoding="utf-8") as f:
        json.dump(asa_dict, f, indent=4, ensure_ascii=False)
        
    print(f"ASA exportada em formato hierarquico (verifique {asa_path}).\n")
    print("Compilacao da Entrega 2 finalizada com sucesso!")
    return 0

if __name__ == "__main__":
    sys.exit(main())