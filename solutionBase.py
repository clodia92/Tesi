class Solution:

    # struttura che contiene tutte le mosse con relativi costi
    # dizionari di smd
    # smd = {}

    def findSolutionBase(self, s, x2, w2, uk2, Pgac, PsGa, K2diS, A2, GammadiS, CdiS):
        print("START findSolutionBase(), satellite: ", s)

        # x2[(k, gamma, i, j)]
        # w2[(k, i, j)]
        #- uk2
        # Pgac
        #- PsGa
        #- K2diS[s]
        #- A2
        #- GammadiS
        # CdiS

        # dizionatio che contiene i pallet richiesti dai clienti di s
        PGa = {}

        # lista dei veicoli assegnati ad s nel Prob2
        K2 = []

        # numero massimo di pallet trasportabili dal veicolo k che serve s
        uk2diS = {}

        # lista dei clienti di s
        Gamma = GammadiS[s]

        # pallet totali che partono da s
        palletDaConsegnare = 0

        for v in K2diS[s]:
            print("uk2[{}]: {}".format(v, uk2[v]))
            uk2diS [v] = uk2[v]


        print("Pgac: {}".format(Pgac))

        for gamma in GammadiS[s]:
            print("PsGa[({}, {})]: {}".format(s, gamma, PsGa[(s, gamma)]))
            PGa[gamma] = PsGa[(s, gamma)]
            palletDaConsegnare += PGa[gamma]

        print("K2diS[{}]: {}".format(s, K2diS[s]))

        K2 = K2diS[s]

        print("A2: ")
        for arc in A2:
            if ((s == arc[0]) and arc[1] in GammadiS[s]) or ((arc[0] in GammadiS[s]) and (arc[1] in GammadiS[s])):
                print(arc)

        print("GammadiS[{}]: {}".format(s, GammadiS[s]))
        print("CdiS: {}".format(CdiS))

        # iterazione per scorrere i veicoli e i clienti di gamma
        posV = 0
        posG = 0


        #while (palletDaConsegnare > 0):




