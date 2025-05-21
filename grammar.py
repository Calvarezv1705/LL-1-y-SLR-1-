class Grammar:
    """
    Clase que representa una gramática libre de contexto (GLC).
    Esta clase permite almacenar producciones, calcular los conjuntos FIRST y FOLLOW,
    y visualizar la gramática de manera estructurada.
    """

    def __init__(self):
        # Diccionario para almacenar las producciones de la gramática.
        self.productions = {}

        # Conjunto que almacena todos los símbolos terminales de la gramática.
        self.terminals = set()

        # Conjunto que almacena todos los símbolos no terminales de la gramática.
        self.non_terminals = set()

        # Símbolo inicial de la gramática. Por convención lo definimos como 'S'.
        self.start_symbol = 'S'

    def add_production(self, non_terminal, productions):
        """
        Agrega una nueva producción a la gramática.
        """
        # Si el no terminal no existe aún, lo agregamos al diccionario de producciones
        # y también al conjunto de no terminales.
        if non_terminal not in self.productions:
            self.productions[non_terminal] = []
            self.non_terminals.add(non_terminal)

        # Agregamos cada una de las producciones proporcionadas para este no terminal.
        for prod in productions:
            self.productions[non_terminal].append(prod)

            # Recorremos cada símbolo dentro de la producción para clasificarlo.
            for symbol in prod:
                if symbol.isupper():
                    # Si el símbolo está en mayúscula, lo tratamos como no terminal.
                    self.non_terminals.add(symbol)
                elif symbol != 'e':  # 'e' representa la cadena vacía (epsilon).
                    # Si no es mayúscula ni epsilon, lo tratamos como terminal.
                    self.terminals.add(symbol)

    def read_grammar(self, input_lines):
        """
        Lee la gramática desde una entrada dada en forma de lista de líneas.

        Args:
            input_lines (list): Lista de cadenas que representan líneas de entrada con producciones.
        """
        # La primera línea indica cuántos no terminales se van a leer.
        num_non_terminals = int(input_lines[0])

        # Leemos cada producción desde la línea 1 hasta la línea n.
        for i in range(1, num_non_terminals + 1):
            line = input_lines[i].strip()
            parts = line.split('->')  # Separamos el no terminal de sus producciones.

            non_terminal = parts[0].strip()
            productions_str = parts[1].strip().split()  # Las producciones están separadas por espacios.

            self.add_production(non_terminal, productions_str)

    def get_first_set(self):
        """
        Calcula el conjunto FIRST para cada símbolo de la gramática.
        Este conjunto representa los símbolos con los que puede comenzar una cadena derivada.
        """
        # Inicializamos los conjuntos FIRST vacíos para todos los no terminales.
        first = {symbol: set() for symbol in self.non_terminals}

        # Por definición, el FIRST de un terminal es él mismo.
        for terminal in self.terminals:
            first[terminal] = {terminal}

        # Definimos el conjunto FIRST de epsilon ('e') como {'e'}.
        first['e'] = {'e'}

        # Algoritmo iterativo para el cálculo de los conjuntos FIRST.
        # Se repite hasta que no haya más cambios en los conjuntos.
        while True:
            updated = False

            for non_terminal, productions in self.productions.items():
                for production in productions:
                    # Si la producción es directamente epsilon, se añade a FIRST.
                    if production == 'e':
                        if 'e' not in first[non_terminal]:
                            first[non_terminal].add('e')
                            updated = True
                    else:
                        # Procesamos producciones del tipo A -> Y1Y2...Yk
                        first_pos = 0
                        eps_in_everything = True

                        for symbol in production:
                            # Nos aseguramos de que el símbolo tenga un conjunto FIRST asociado.
                            if symbol not in first:
                                if symbol.isupper():
                                    first[symbol] = set()
                                else:
                                    first[symbol] = {symbol}

                            # Añadimos todos los símbolos de FIRST(symbol) menos epsilon.
                            for term in first[symbol]:
                                if term != 'e' and term not in first[non_terminal]:
                                    first[non_terminal].add(term)
                                    updated = True

                            # Si el símbolo actual no puede derivar a epsilon, detenemos la cadena.
                            if 'e' not in first[symbol]:
                                eps_in_everything = False
                                break

                            first_pos += 1

                        # Si todos los símbolos de la producción pueden derivar a epsilon, lo agregamos también.
                        if eps_in_everything and 'e' not in first[non_terminal]:
                            first[non_terminal].add('e')
                            updated = True

            # Terminamos cuando no hay actualizaciones nuevas.
            if not updated:
                break

        return first

    def get_follow_set(self, first_sets):
        """
        Calcula el conjunto FOLLOW para cada símbolo no terminal de la gramática.
        Este conjunto representa los símbolos que pueden aparecer inmediatamente después
        de un no terminal en alguna derivación.
        """
        # Inicializamos los conjuntos FOLLOW vacíos para todos los no terminales.
        follow = {non_terminal: set() for non_terminal in self.non_terminals}

        # Agregamos el símbolo de fin de cadena '$' al FOLLOW del símbolo inicial.
        follow[self.start_symbol].add('$')

        # Algoritmo iterativo similar al de FIRST.
        while True:
            updated = False

            for non_terminal, productions in self.productions.items():
                for production in productions:
                    if production == 'e':
                        continue  # No analizamos producciones vacías

                    for i, symbol in enumerate(production):
                        if not symbol.isupper():
                            continue  # Ignoramos terminales

                        # Caso 1: A -> aBb, calcular FIRST(resto)
                        if i < len(production) - 1:
                            rest = production[i+1:]
                            first_rest = set()
                            all_have_epsilon = True

                            for sym in rest:
                                if sym not in first_sets:
                                    if sym.isupper():
                                        continue
                                    else:
                                        first_rest.add(sym)
                                        all_have_epsilon = False
                                        break

                                for term in first_sets[sym]:
                                    if term != 'e':
                                        first_rest.add(term)

                                if 'e' not in first_sets[sym]:
                                    all_have_epsilon = False
                                    break

                            for term in first_rest:
                                if term not in follow[symbol]:
                                    follow[symbol].add(term)
                                    updated = True

                            # Caso 2: Si todo el resto puede derivar a epsilon,
                            # se añade FOLLOW del no terminal padre.
                            if all_have_epsilon:
                                for term in follow[non_terminal]:
                                    if term not in follow[symbol]:
                                        follow[symbol].add(term)
                                        updated = True
                        else:
                            # Caso 3: A -> aB, se añade FOLLOW(A) a FOLLOW(B)
                            for term in follow[non_terminal]:
                                if term not in follow[symbol]:
                                    follow[symbol].add(term)
                                    updated = True

            if not updated:
                break

        return follow

    def __str__(self):
        """
        Devuelve una representación legible de todas las producciones de la gramática.
        
        Returns:
            str: Cadena de texto que representa todas las reglas de la gramática.
        """
        result = "Gramática:\n"
        for non_terminal, productions in self.productions.items():
            # Mostramos las producciones de forma compacta con símbolo '|'.
            result += f"{non_terminal} -> {' | '.join(productions)}\n"
        return result
