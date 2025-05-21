
from grammar import Grammar
from ll1_parser import LL1Parser
from slr1_parser import SLR1Parser

def main():
    """
    Función principal que lee la gramática de entrada y ejecuta el análisis sintáctico.
    """
    try:
        # Leer número de no terminales
        num_non_terminals = int(input())
        
        # Leer líneas de entrada
        input_lines = [str(num_non_terminals)]
        
        for _ in range(num_non_terminals):
            line = input()
            input_lines.append(line)
        
        # Crear gramática
        grammar = Grammar()
        grammar.read_grammar(input_lines)
        
        # Crear analizadores
        ll1_parser = LL1Parser(grammar)
        slr1_parser = SLR1Parser(grammar)
        
        # Verificar si la gramática es LL(1) o SLR(1)
        is_ll1 = ll1_parser.is_grammar_ll1()
        is_slr1 = slr1_parser.is_grammar_slr1()
        
        # Casos según el tipo de gramática
        if is_ll1 and is_slr1:
            while True:
                print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
                choice = input().strip()
                
                if choice == 'Q':
                    break
                elif choice == 'T':
                    parse_strings(ll1_parser)
                elif choice == 'B':
                    parse_strings(slr1_parser)
        elif is_ll1:
            print("Grammar is LL(1).")
            parse_strings(ll1_parser)
        elif is_slr1:
            print("Grammar is SLR(1).")
            parse_strings(slr1_parser)
        else:
            print("Grammar is neither LL(1) nor SLR(1).")
            
    except Exception as e:
        print(f"Error: {e}")

def parse_strings(parser):
    """
    Analiza cadenas usando el analizador especificado.
    
    Args:
        parser: Analizador sintáctico (LL1Parser o SLR1Parser)
    """
    while True:
        string = input().strip()
        
        if not string:
            break
            
        result = parser.parse(string)
        print("yes" if result else "no")

if __name__ == "__main__":
    main()


"""
3
S -> S+T T
T -> T*F F
F -> (S) i
"""

"""
3
S -> AB
A -> aA d
B -> bBc e
"""

"""
2
S -> A
A -> A b
"""