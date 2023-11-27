import time

class thomposon_NFA(object):

    SPLIT = 256
    MATCH = 257
    # Define constants for operators
    CONCAT = '.'
    OR = '|'
    OPEN_PAREN = '('
    CLOSE_PAREN = ')'
    OPERATORS = {'*', '+', '?'}
    ZERO_OR_ONE = '?'
    ZERO_OR_MORE = '*'
    ONE_OR_MORE = '+'

    def __init__(self) -> None:
        '''
        state_id : attribuer un ID unique à chaque état dans le NFA 
        list_id : identifie la liste actuelle du fragment NFA. Lors de la correspondance, à chaque caractère correspondant, une nouvelle liste est créée et le list_id augmente de 1.

        '''
        self.state_id = 0
        self.list_id = 0


    def get_state_id(self):
        '''
        Cette fonction sert à attribuer un ID unique à chaque état dans l'automate fini non déterministe (NFA).
        '''
        self.state_id += 1
        return self.state_id
    

    def re2post(self, regex):
        """
        Convert the input infix regular expression to a postfix expression.
        """

        def append_operator(operator, count):
            nonlocal res
            for _ in range(count):
                res += operator

        nalt, natom = 0, 0
        paren = []
        res = ""

        for c in regex:
            if c == self.OPEN_PAREN:
                if natom > 1:
                    natom -= 1
                    append_operator(self.CONCAT, 1)
                paren.append((nalt, natom))
                nalt, natom = 0, 0

            elif c == self.OR:
                if not natom:
                    return False
                append_operator(self.CONCAT, natom - 1)
                natom = 0
                nalt += 1

            elif c == self.CLOSE_PAREN:
                if not paren or not natom:
                    return False
                append_operator(self.CONCAT, natom - 1)
                append_operator(self.OR, nalt)
                nalt, natom = paren.pop()
                natom += 1

            elif c in self.OPERATORS:
                if not natom:
                    return False
                res += c

            else:
                if natom > 1:
                    natom -= 1
                    append_operator(self.CONCAT, 1)
                res += c
                natom += 1

        if paren:
            return False

        append_operator(self.CONCAT, natom - 1)
        append_operator(self.OR, nalt)

        return res

    def list1(self, item):
        '''
        item : (state, outtype)
        Où outtype peut prendre les valeurs 'out' et 'out1'
        Représentant respectivement le pointeur 'out' et le pointeur 'out1' de l'état 'state'.
        '''
        return [item]

    def patch(self, out, state):
        '''
        out : Tous les pointeurs non connectés du fragment NFA
        state : Un état donné s
        Cette fonction sert à connecter toutes les sorties du fragment à l'état 'state'.

        '''
        for item, out_type in out:
            if out_type == 'out':
                item.out = state
            else:
                item.out1 = state

    def append(self, out1, out2):
        '''
        out1 : Tous les pointeurs non connectés du fragment NFA 1
        out2 : Tous les pointeurs non connectés du fragment NFA 2
        Cette fonction est utilisée pour fusionner les pointeurs non connectés du fragment 1 avec ceux du fragment 2.

        '''
        return out1+out2
    
    def post2nfa(self, postfix):
        '''
        postfix : Expression régulière en notation postfixée
        Cette fonction est utilisée pour convertir l'expression régulière en notation postfixée en NFA.
        '''
        # operand
        frags = []

        for item in postfix:
            if item == self.CONCAT:
                e2 = frags.pop()
                e1 = frags.pop()
                self.patch(e1.out, e2.start)
                frags.append(thomposon_NFA.Frag(e1.start, e2.out))
            elif item == self.OR: 
                e2 = frags.pop()
                e1 = frags.pop()
                s = thomposon_NFA.State(self.get_state_id(), thomposon_NFA.SPLIT)
                s.out = e1.start
                s.out1 = e2.start
                frags.append(thomposon_NFA.Frag(s, self.append(e1.out, e2.out)))
            elif item == self.ZERO_OR_ONE:  
                e = frags.pop()
                s = thomposon_NFA.State(self.get_state_id(), thomposon_NFA.SPLIT)
                s.out = e.start
                frags.append(thomposon_NFA.Frag(
                    s, self.append(e.out, self.list1((s, 'out1')))))
            elif item == self.ZERO_OR_MORE:  
                e = frags.pop()
                s = thomposon_NFA.State(self.get_state_id(), thomposon_NFA.SPLIT)
                s.out = e.start
                self.patch(e.out, s)
                frags.append(thomposon_NFA.Frag(s, self.list1((s, 'out1'))))
            elif item == self.ONE_OR_MORE:  # ! one or more
                e = frags.pop()
                s = thomposon_NFA.State(self.get_state_id(), thomposon_NFA.SPLIT)
                s.out = e.start
                self.patch(e.out, s)
                frags.append(thomposon_NFA.Frag(
                    e.start, self.list1((s, 'out1'))))
            else:
                s = thomposon_NFA.State(self.get_state_id(), item)
                frags.append(thomposon_NFA.Frag(s, self.list1((s, 'out'))))

        e = frags.pop()

        #   À ce moment, frags devrait être vide, sinon l'expression régulière est invalide.
        if frags:
            return False

        #   e.out représente toutes les sorties du NFA. Si la chaîne d'entrée peut atteindre une sortie, on considère que le NFA peut correspondre à cette chaîne.
        self.patch(e.out, thomposon_NFA.State(self.get_state_id(), thomposon_NFA.MATCH))
        return e.start
    
    def match(self, start, input_str):
        '''
        start : NFA
        input_str : Chaîne à matcher
        Cette fonction utilise le NFA construit pour matcher la chaîne d'entrée. Si elle réussit à la matcher, elle renvoie True.

        '''
        cstates = []  # current states
        nstates = []  # next states

        # Construire l'ensemble des états initiaux à partir du NFA.
        cstates = self.start_states(cstates, start)

        for c in input_str:
            self.step(cstates, c, nstates)
            cstates = nstates
            if nstates == []:
                return False
            elif self.is_match(cstates):
                return True
            nstates = []

    
    def is_match(self, states):
        '''
        states : Fragments du NFA qui correspondent avec succès après avoir parcouru la chaîne d'entrée.
        Cette fonction vérifie si, après avoir terminé le parcours, l'un des fragments NFA restants est 
        dans l'état MATCH. Si un fragment du NFA est dans l'état MATCH, alors il y a une correspondance réussie.
        '''
        for state in states:
            if state.c == thomposon_NFA.MATCH:
                return True
        return False
    
    def step(self, cstates, c, nstates):
        '''
        cstates : Fragments du NFA actuellement correspondants avec succès.
        c : Caractère à matcher.
        nstates : Liste des états suivants, utilisée pour stocker tous les fragments du NFA qui correspondent avec succès au caractère c.
        Cette fonction vise à matcher le caractère c dans tous les fragments actuels du NFA qui correspondent avec succès. Si le match est 
        réussi, l'état suivant de ce fragment du NFA est ajouté à la liste nstates pour matcher le caractère suivant.

        '''
        self.list_id += 1
        for state in cstates:
            if state.c == c:
                self.add_state(nstates, state.out)

    def add_state(self, states, state):
        '''
        states : Liste des fragments NFA.
        state : État/fragment du NFA à ajouter.
        Cette fonction est utilisée pour ajouter "state" à "states", en prenant note que :
        1. Un état vide ou un état déjà existant ne doit pas être ajouté à nouveau.
        2. En cas d'état SPLIT, ses deux états de branche doivent être ajoutés.

        '''
        # Si "state" est vide ou si "state" est déjà dans "states", ne pas l'ajouter à nouveau.
        if state is None or state.lastlist == self.list_id:
            return

        state.lastlist = self.list_id
        if state.c == thomposon_NFA.SPLIT:
            self.add_state(states, state.out)
            self.add_state(states, state.out1)
        else:
            states.append(state)
        return
    
    def start_states(self, states, start):
        '''
        states : Liste de fragments NFA
        start : NFA
        Cette fonction est utilisée pour initialiser la liste de fragments NFA.
        '''
        self.list_id += 1
        self.add_state(states, start)
        return states

    class State(object):
        def __init__(self, id, c) -> None:
            '''
            id : identifiant unique de l'état "state"
            c : caractère représenté par l'état. Lorsque c<256, cela représente le caractère à apparier. Si c=256, cela représente l'état SPLIT. Si c=257, cela représente l'état MATCH.
            out : prochain état auquel "state" est connecté.
            out1 : utilisé uniquement lorsque c est en état SPLIT. Dans ce cas, "out" et "out1" sont utilisés pour connecter deux choix (états) différents.
            lastlist : utilisé pour identifier la liste d'états dans laquelle se trouve "state". Cela sert à éviter les ajouts répétitifs pendant l'exécution.
            '''
            self.id = id
            self.c = c
            self.out = None
            self.out1 = None
            self.lastlist = 0

    class Frag(object):
        def __init__(self, start, out=None) -> None:
            '''
            start : représente l'état de départ dans un fragment de NFA.
            out : représente tous les états dans le fragment de NFA qui ne sont pas encore connectés. Étant donné que Python passe par valeur, nous transmettons un tuple (out, outtype) et utilisons out.outtype pour la connexion.
            (s, 'out') représente s.out.
            (s, 'out1') représente s.out1.
            À la fin de la génération du NFA, ces connexions non connectées devraient être reliées à l'état MATCH.
            La classe Frag est utilisée pour simplifier la création du NFA. En mettant en cache tous les out d'un fragment de NFA, au lieu de parcourir la liste des états à chaque fois pour obtenir les états non connectés, cela peut considérablement accélérer la vitesse d'exécution.
            '''
            self.start = start
            self.out = out

def main(input_post,file):
    try:
        start_time = time.time()
        regex = thomposon_NFA()
        post = regex.re2post(input_post)
        if not post:
            print("Erreur de syntaxe dans l'expression régulière :{}".format(regex))
            return False
        start = regex.post2nfa(post)
        with open(file, 'r', encoding='utf-8') as f:
            lines = [line.replace('\n', '') for line in f.readlines()]
        for i, line in enumerate(lines, start=1):
            for index in range(len(line)):
                if(regex.match(start,line[index:])):
                    print(f'{i}: {line}', end='\n')
                    break
        end_time = time.time()
        print('\nProgram run time:', end_time - start_time, 'seconds')
    except Exception as e:
        print(f"Error: {e}")