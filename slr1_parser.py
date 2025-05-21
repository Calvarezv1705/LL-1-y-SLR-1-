from grammar import Grammar

class SLR1Parser:
    """
    Implementación de un analizador sintáctico SLR(1) (Bottom-Up).
    """
    
    def __init__(self, grammar):
        """
        Inicializa el analizador SLR(1).
        
        Args:
            grammar (Grammar): La gramática para el analizador
        """
        self.grammar = grammar
        # Agregamos una producción inicial para el símbolo de inicio aumentado
        self.augmented_grammar = self._augment_grammar()
        self.first_sets = self.augmented_grammar.get_first_set()
        self.follow_sets = self.augmented_grammar.get_follow_set(self.first_sets)
        self.canonical_collection = self._build_canonical_collection()
        self.action_table, self.goto_table = self._build_parsing_tables()
        self.is_slr1 = self._check_if_slr1()
        
    def _augment_grammar(self):
        """
        Aumenta la gramática agregando una nueva producción para el símbolo inicial.
        
        Returns:
            Grammar: Gramática aumentada
        """
        aug_grammar = Grammar()
        
        # Copiar producciones originales
        for non_terminal, productions in self.grammar.productions.items():
            for production in productions:
                aug_grammar.add_production(non_terminal, [production])
        
        # Agregar producción para el símbolo inicial aumentado S' -> S
        aug_grammar.add_production("S'", [self.grammar.start_symbol])
        aug_grammar.start_symbol = "S'"
        
        return aug_grammar
    
    def _closure(self, items):
        """
        Calcula la clausura de un conjunto de items.
        
        Args:
            items (set): Conjunto de items (tuplas de la forma (non_terminal, production, dot_position))
            
        Returns:
            set: Clausura del conjunto de items
        """
        closure = set(items)
        
        while True:
            new_items = set()
            
            for item in closure:
                non_terminal, production, dot_pos = item
                
                # Si el punto está al final de la producción, no agregar nuevos items
                if dot_pos >= len(production) or production == 'e':
                    continue
                
                # Símbolo después del punto
                symbol_after_dot = production[dot_pos]
                
                # Si el símbolo después del punto es un no terminal
                if symbol_after_dot in self.augmented_grammar.non_terminals:
                    # Para cada producción de ese no terminal
                    for prod in self.augmented_grammar.productions[symbol_after_dot]:
                        # Agregar un nuevo item con el punto al inicio de la producción
                        new_item = (symbol_after_dot, prod, 0)
                        if new_item not in closure:
                            new_items.add(new_item)
            
            # Si no se agregaron nuevos items, terminar
            if not new_items:
                break
                
            closure.update(new_items)
            
        return closure
    
    def _goto(self, items, symbol):
        """
        Calcula el conjunto de items que resulta de mover el punto después de un símbolo.
        
        Args:
            items (set): Conjunto de items
            symbol (str): Símbolo para mover el punto
            
        Returns:
            set: Conjunto de items resultante
        """
        goto_items = set()
        
        for item in items:
            non_terminal, production, dot_pos = item
            
            # Si el punto está al final de la producción o la producción es epsilon, no hacer nada
            if dot_pos >= len(production) or production == 'e':
                continue
                
            # Si el símbolo después del punto coincide con el símbolo dado
            if production[dot_pos] == symbol:
                # Crear un nuevo item con el punto avanzado
                new_item = (non_terminal, production, dot_pos + 1)
                goto_items.add(new_item)
        
        # Calcular la clausura del conjunto resultante
        return self._closure(goto_items)
    
    def _build_canonical_collection(self):
        """
        Construye la colección canónica de conjuntos de items LR(0).
        
        Returns:
            tuple: (estados, transiciones)
                donde estados es una lista de conjuntos de items
                y transiciones es un diccionario que mapea (estado, símbolo) a estado
        """
        # Conjunto inicial de items con la producción aumentada
        initial_item = ("S'", self.grammar.start_symbol, 0)
        initial_items = self._closure({initial_item})
        
        states = [initial_items]
        transitions = {}
        
        # Conjunto de símbolos (terminales y no terminales)
        symbols = self.augmented_grammar.terminals.union(self.augmented_grammar.non_terminals)
        
        i = 0
        while i < len(states):
            current_state = states[i]
            
            for symbol in symbols:
                goto_result = self._goto(current_state, symbol)
                
                if goto_result and goto_result not in states:
                    states.append(goto_result)
                    transitions[(i, symbol)] = len(states) - 1
                elif goto_result:
                    transitions[(i, symbol)] = states.index(goto_result)
            
            i += 1
            
        return states, transitions
    
    def _build_parsing_tables(self):
        """
        Construye las tablas de análisis SLR(1).
        
        Returns:
            tuple: (action_table, goto_table)
                donde action_table es un diccionario que mapea (estado, terminal) a acción
                y goto_table es un diccionario que mapea (estado, no_terminal) a estado
        """
        states, transitions = self.canonical_collection
        action_table = {}
        goto_table = {}
        
        # Inicializar tablas
        for i in range(len(states)):
            action_table[i] = {}
            goto_table[i] = {}
        
        # Construir tabla GOTO
        for (state, symbol), next_state in transitions.items():
            if symbol in self.augmented_grammar.non_terminals:
                goto_table[state][symbol] = next_state
        
        # Construir tabla ACTION
        for state_idx, state in enumerate(states):
            for item in state:
                non_terminal, production, dot_pos = item
                
                # Caso 1: [A -> α.aβ] => ACTION[i, a] = shift j, donde goto(i, a) = j
                if dot_pos < len(production) and production != 'e':
                    symbol = production[dot_pos]
                    if not symbol.isupper() and (state_idx, symbol) in transitions:
                        next_state = transitions[(state_idx, symbol)]
                        action = f"s{next_state}"  # shift
                        
                        # Verificar si ya hay una acción (conflicto)
                        if symbol in action_table[state_idx] and action_table[state_idx][symbol] != action:
                            action_table[state_idx][symbol] = None  # Marcar como conflicto
                        else:
                            action_table[state_idx][symbol] = action
                
                # Caso 2: [A -> α.] => ACTION[i, a] = reduce A -> α, para todo a en FOLLOW(A)
                elif (dot_pos >= len(production) and production != 'e') or (production == 'e' and dot_pos == 0):
                    for terminal in self.follow_sets[non_terminal]:
                        # Caso especial: [S' -> S.]
                        if non_terminal == "S'" and production == self.grammar.start_symbol:
                            action = "acc"  # accept
                        else:
                            # Encontrar índice de la producción en la gramática original
                            prod_idx = 0
                            for nt, prods in self.grammar.productions.items():
                                if nt == non_terminal:
                                    for p_idx, p in enumerate(prods):
                                        if p == production:
                                            prod_idx = p_idx
                                            break
                            
                            action = f"r{non_terminal}->{production}"  # reduce
                        
                        # Verificar si ya hay una acción (conflicto)
                        if terminal in action_table[state_idx] and action_table[state_idx][terminal] != action:
                            action_table[state_idx][terminal] = None  # Marcar como conflicto
                        else:
                            action_table[state_idx][terminal] = action
        
        return action_table, goto_table
    
    def _check_if_slr1(self):
        """
        Verifica si la gramática es SLR(1).
        
        Returns:
            bool: True si la gramática es SLR(1), False en caso contrario
        """
        for state, actions in self.action_table.items():
            for terminal, action in actions.items():
                if action is None:  # Hay un conflicto
                    return False
        return True
    
    def parse(self, input_string):
        """
        Analiza una cadena usando el analizador SLR(1).
        
        Args:
            input_string (str): Cadena a analizar
            
        Returns:
            bool: True si la cadena es aceptada, False en caso contrario
        """
        if not self.is_slr1:
            return False
            
        # Asegurarse de que la cadena termina con $
        if not input_string.endswith('$'):
            input_string += '$'
            
        # Inicializar pila y apuntador de entrada
        stack = [0]  # Pila de estados
        input_ptr = 0
        
        while True:
            current_state = stack[-1]
            current_input = input_string[input_ptr] if input_ptr < len(input_string) else '$'
            
            # Obtener acción
            if current_input not in self.action_table[current_state]:
                return False
                
            action = self.action_table[current_state][current_input]
            
            if action is None:  # Conflicto
                return False
            elif action.startswith('s'):  # Shift
                next_state = int(action[1:])
                stack.append(current_input)
                stack.append(next_state)
                input_ptr += 1
            elif action.startswith('r'):  # Reduce
                # Extraer producción de la acción
                production_parts = action[1:].split('->')
                non_terminal = production_parts[0]
                production = production_parts[1]
                
                # Si la producción es epsilon, no desapilamos nada
                if production != 'e':
                    # Desapilar 2 * len(producción) elementos (símbolo + estado)
                    for _ in range(2 * len(production)):
                        stack.pop()
                
                # Obtener estado en la cima de la pila
                top_state = stack[-1]
                
                # Usar tabla GOTO para obtener siguiente estado
                if non_terminal in self.goto_table[top_state]:
                    next_state = self.goto_table[top_state][non_terminal]
                    stack.append(non_terminal)
                    stack.append(next_state)
                else:
                    return False
            elif action == 'acc':  # Accept
                return True
            else:
                return False
    
    def is_grammar_slr1(self):
        """
        Verifica si la gramática es SLR(1).
        
        Returns:
            bool: True si la gramática es SLR(1), False en caso contrario
        """
        return self.is_slr1