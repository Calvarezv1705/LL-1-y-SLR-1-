from grammar import Grammar

class LL1Parser:
    """
    Clase que implementa un analizador sintáctico LL(1). Este tipo de analizador utiliza una tabla de análisis para determinar qué producción aplicar en función del símbolo no terminal actual y el símbolo terminal de entrada.
    """
    
    def __init__(self, grammar):
        """
        Constructor que inicializa el analizador LL(1).
        
        Recibe una instancia de una gramática libre de contexto (Grammar) y realiza lo siguiente:
        - Calcula los conjuntos FIRST de todos los símbolos.
        - Calcula los conjuntos FOLLOW de todos los no terminales.
        - Construye la tabla de análisis LL(1) basada en los conjuntos FIRST y FOLLOW.
        - Verifica si la gramática es compatible con el método LL(1).
        """
        self.grammar = grammar
        self.first_sets = grammar.get_first_set()
        self.follow_sets = grammar.get_follow_set(self.first_sets)
        self.parse_table = self._build_parse_table()
        self.is_ll1 = self._check_if_ll1()
        
    def _get_first_of_string(self, string):
        """
        Calcula el conjunto FIRST para una cadena de símbolos.
        Es útil cuando las producciones tienen múltiples símbolos a la derecha del símbolo de producción.
        """
        if not string or string == 'e':
            # Si la cadena está vacía o es epsilon, el conjunto FIRST es simplemente {e}
            return {'e'}
            
        first_set = set()
        all_derive_epsilon = True  # Indica si todos los símbolos hasta el momento pueden derivar epsilon
        
        for symbol in string:
            if symbol not in self.first_sets:
                # Si el símbolo no está en los conjuntos FIRST, se asume que es terminal y se agrega tal cual
                first_set.add(symbol)
                all_derive_epsilon = False
                break
                
            # Agregar FIRST(symbol) sin epsilon al conjunto actual
            symbol_first = self.first_sets[symbol].copy()
            if 'e' in symbol_first:
                symbol_first.remove('e')
            first_set.update(symbol_first)
            
            # Si el símbolo no puede derivar a epsilon, se detiene el análisis
            if 'e' not in self.first_sets[symbol]:
                all_derive_epsilon = False
                break
        
        # Si todos los símbolos pudieron derivar a epsilon, se agrega epsilon al resultado
        if all_derive_epsilon:
            first_set.add('e')
            
        return first_set
    
    def _build_parse_table(self):
        """
        Construye la tabla de análisis LL(1). Esta tabla se usa para decidir qué producción aplicar
        en base al símbolo de entrada y el símbolo en la cima de la pila del parser.
        
        Returns:
            dict: Diccionario que representa la tabla de análisis LL(1), indexada por no_terminal -> terminal.
        """
        parse_table = {}

        # Inicializar las filas de la tabla para cada no terminal
        for non_terminal in self.grammar.non_terminals:
            parse_table[non_terminal] = {}
            
        # Llenar la tabla aplicando las reglas de FIRST y FOLLOW
        for non_terminal, productions in self.grammar.productions.items():
            for production in productions:
                # Calcular FIRST(producción)
                first_of_production = self._get_first_of_string(production)
                
                for terminal in first_of_production:
                    if terminal != 'e':
                        # Si hay conflicto (más de una producción para un mismo par no_terminal/terminal)
                        if terminal in parse_table[non_terminal]:
                            parse_table[non_terminal][terminal] = None  # Marca de conflicto
                        else:
                            parse_table[non_terminal][terminal] = production
                
                # Si epsilon está en el FIRST de la producción, usar los FOLLOW del no terminal
                if 'e' in first_of_production:
                    for terminal in self.follow_sets[non_terminal]:
                        if terminal in parse_table[non_terminal]:
                            parse_table[non_terminal][terminal] = None  # Conflicto detectado
                        else:
                            parse_table[non_terminal][terminal] = production
        
        return parse_table
    
    def _check_if_ll1(self):
        """
        Verifica si la gramática es LL(1), es decir, que no haya conflictos en la tabla de análisis.
        Un conflicto ocurre si dos o más producciones compiten por la misma celda de la tabla.
        
        Returns:
            bool: True si la gramática es LL(1), False si hay al menos un conflicto.
        """
        for non_terminal, table_row in self.parse_table.items():
            for terminal, production in table_row.items():
                if production is None:  # Celda con conflicto
                    return False
        return True
    
    def parse(self, input_string):
        """
        Método principal de análisis: verifica si una cadena de entrada es válida según la gramática LL(1).
        
        El análisis se realiza usando una pila y la tabla de análisis. La entrada se consume símbolo por símbolo,
        mientras que en la pila se simulan las derivaciones.

        Args:
            input_string (str): Cadena de entrada a analizar. Se espera que termine con '$'.

        Returns:
            bool: True si la cadena es aceptada, False si no es válida.
        """
        if not self.is_ll1:
            # Si la gramática no es LL(1), no se puede hacer el análisis correctamente
            return False
            
        # Asegurarse de que la cadena finalice con '$' (símbolo de fin de entrada)
        if not input_string.endswith('$'):
            input_string += '$'
            
        # Inicialización: pila con el símbolo de fin y el símbolo inicial de la gramática
        stack = ['$', self.grammar.start_symbol]
        input_ptr = 0  # Apuntador al carácter actual de la entrada
        
        while stack:
            top = stack.pop()  # Símbolo actual en la cima de la pila
            current_input = input_string[input_ptr] if input_ptr < len(input_string) else '$'
            
            if top == 'e':
                # Si el símbolo es epsilon, simplemente lo ignoramos (no afecta la entrada)
                continue
            elif not top.isupper():
                # Si es un terminal, debe coincidir exactamente con la entrada
                if top == current_input:
                    input_ptr += 1  # Avanzar en la entrada
                else:
                    return False  # Error de coincidencia
            else:
                # Si es un no terminal, usar la tabla de análisis
                if current_input in self.parse_table[top]:
                    production = self.parse_table[top][current_input]
                    if production is None:
                        # Conflicto detectado en la tabla: no se puede continuar
                        return False
                    elif production != 'e':
                        # Si la producción no es epsilon, se apilan los símbolos de la derecha (en orden inverso)
                        for symbol in reversed(production):
                            stack.append(symbol)
                else:
                    return False  # No hay entrada válida en la tabla, error de análisis
        
        # Si se consumió toda la entrada correctamente, la cadena es válida
        return input_ptr >= len(input_string) or (input_ptr == len(input_string) - 1 and input_string[-1] == '$')
    
    def is_grammar_ll1(self):
        """
        Devuelve el resultado del chequeo de la gramática. Permite consultar externamente
        si la gramática dada es válida para el análisis LL(1).

        Returns:
            bool: True si la gramática es LL(1), False si no lo es.
        """
        return self.is_ll1
