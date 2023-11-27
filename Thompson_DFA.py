
from Thompson_NFA import thomposon_NFA
import time
import sys
class thomposon_DFA(object):

    SPLIT = 256
    MATCH = 257


    def __init__(self, input_post) -> None:
        '''
        list_id : Identifie la liste de fragments NFA actuellement en cours. Durant le processus de correspondance, chaque fois qu'un caractère est associé, une nouvelle liste est créée et list_id est incrémenté de 1.
        dstate : Tous les états dans le DFA, construits sous forme d'arbre de recherche binaire.
        '''
        self.list_id = 0
        self.dstate = None
        self.regex_NFA = thomposon_NFA()
        post_NFA = self.regex_NFA.re2post(input_post)
        if not post_NFA:
            raise ValueError("Invalid regex pattern.")
        self.start = self.regex_NFA.post2nfa(post_NFA)
        self.start_dstate = self.start_dstate(self.start)

    class DState(object):
        def __init__(self, states) -> None:
            '''
            states : Un état dans le DFA correspond à un ensemble d'états (ou fragments) dans le NFA.
            next : Un dictionnaire dont la clé est la valeur ASCII d'un caractère et la valeur est le DSTATE suivant. 
            Si l'état actuel est "d" et que le caractère entrant est "c", alors d.next[c] serait l'état suivant. Si la valeur de "c" n'est pas présente parmi les clés du dictionnaire, cela signifie qu'elle n'est pas encore connectée.left : Branche gauche de l'arbre.
            right : Branche droite de l'arbre.
            left : Branche left de l'arbre.
            '''
            self.states = states
            self.next = {}
            self.right = None
            self.left = None

    def match(self, input_str):
        '''
        start : DFA
        input_str : Chaîne de caractères en entrée
        Cette fonction est utilisée pour faire correspondre la chaîne d'entrée avec le DFA.
        '''
        start = self.start_dstate
        for c in input_str:
            index = ord(c)

            if index in start.next:
                next_state = start.next[index]
            else:
                next_state = self.next_dstate(start, c)
            if self.is_match(next_state.states):
                return True
            elif next_state.states==[]:
                return False
            start = next_state
        return self.is_match(start.states)

    def is_match(self, states):
        for state in states:
            if state.c == thomposon_DFA.MATCH:
                return True

        return False

    def states_cmp(self, states1, states2):
        '''
        states1 : Ensemble des états du fragment DFA
        states2 : Ensemble des états du fragment DFA
        Cette fonction est utilisée pour comparer deux états de DFA, selon les règles suivantes :
        1. Si len(states1) < len(states2), renvoie -1
        2. Si len(states1) > len(states2), renvoie 1
        3. Si les deux ont la même longueur, compare les adresses mémoire de chaque état dans states1 et states2
        '''

        if len(states1) < len(states2):
            return -1
        if len(states1) > len(states2):
            return 1

        for i in range(len(states1)):
            if id(states1[i]) < id(states2[i]):
                return -1
            elif id(states1[i]) > id(states2[i]):
                return 1
        return 0

    def get_dstate(self, states):
        '''
        states : Ensemble des états
        Cette fonction utilise l'ensemble des états comme clé pour obtenir le DState correspondant à cet ensemble.
        '''
        # Tri
        states.sort(key=lambda state: id(state))

        # Parcour dstate
        dstate = self.dstate
        while dstate:
            cmp = self.states_cmp(states, dstate.states)
            if cmp < 0:
                dstate = dstate.left
            elif cmp > 0:
                dstate = dstate.right
            else:
                return dstate

        # creer nouvelle dstate
        dstate = thomposon_DFA.DState(states)
        return dstate
    
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
        self.list_id += 1
        self.add_state(states, start)
        return states
    

    def start_dstate(self, start):
        '''
        start: état (c'est-à-dire NFA)
        Cette fonction obtient le DFA initial à partir du NFA.
        '''
        states = []
        return self.get_dstate(self.start_states(states, start))
    
    def next_dstate(self, dstate, c):
        '''
        dstate: fragment de DFA
        c: caractère entrant
        Cette fonction obtient l'état suivant du DFA (c'est-à-dire l'ensemble des états du NFA) en fonction du DFA actuel et du caractère entrant.
        '''
        nstates = []
        self.step(dstate.states, c, nstates)
        dstate.next[ord(c)] = self.get_dstate(nstates)
        return dstate.next[ord(c)]


def main(input_post, file):
    try:
        regex_DFA = thomposon_DFA(input_post)
        
        start_time = time.time()

        with open(file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
            
            for i, line in enumerate(lines, start=1):
                for index in range(len(line)):
                    if regex_DFA.match(line[index:]):
                        print(f'{i}: {line}')
                        break

        end_time = time.time()
        print('\nProgram run time:', end_time - start_time, 'seconds')
    except Exception as e:
        print(f"Error: {e}")
