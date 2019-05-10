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

        # pallet trasportati da ogni k2 che serve s
        palletTrasportati = []

        # numero massimo di pallet trasportabili dal veicolo k che serve s
        uk2diS = {}

        # lista dei clienti di s
        Gamma = GammadiS[s]

        # dizionario delle rotte per ogni veicolo : rotta [ k ] = ( gamma1, pallet1) , ( gamma2, pallet2) , ( gamma3, pallet3) ....
        rotte = {}

        # pallet totali che partono da s
        palletDaConsegnare = 0

        for v in K2diS[s]:
            # print("uk2[{}]: {}".format(v, uk2[v]))
            uk2diS [v] = uk2[v]


        # print("Pgac: {}".format(Pgac))

        for gamma in GammadiS[s]:
            # print("PsGa[({}, {})]: {}".format(s, gamma, PsGa[(s, gamma)]))
            PGa[gamma] = PsGa[(s, gamma)]
            palletDaConsegnare += PGa[gamma]

        # print("K2diS[{}]: {}".format(s, K2diS[s]))

        K2 = K2diS[s]

        # print("A2: ")
        # for arc in A2:
        #     if ((s == arc[0]) and arc[1] in GammadiS[s]) or ((arc[0] in GammadiS[s]) and (arc[1] in GammadiS[s])):
        #         print(arc)
        #
        # print("GammadiS[{}]: {}".format(s, GammadiS[s]))
        # print("CdiS: {}".format(CdiS))

        # iterazione per scorrere i veicoli e i clienti di gamma
        posV = 0
        posG = 0


        palletTrasportati = [0] * len(K2)

        while (palletDaConsegnare > 0):
            # cicla finchè non trova un veicolo con ancora spazio
            while (palletTrasportati[posV] >= uk2diS [K2[posV]]):
                posV = (posV + 1) % len(K2)

            # se il cliente deve ancora ricevere dei pallet
            if (PGa[Gamma[posG]] > 0):
                # consegna a gamma
                if (PGa[Gamma[posG]] <= (uk2diS[K2[posV]] - palletTrasportati[posV])):
                    # aggiorno le rotte
                    if K2[posV] in rotte:
                        rotte[K2[posV]] += [(Gamma[posG], PGa[Gamma[posG]])]
                    else:
                        rotte[K2[posV]] = [(Gamma[posG], PGa[Gamma[posG]])]

                    palletDaConsegnare -= PGa[Gamma[posG]]
                    palletTrasportati[posV] += PGa[Gamma[posG]]
                    PGa[Gamma[posG]] = 0
                else:
                    # aggiorno le rotte
                    if K2[posV] in rotte:
                        rotte[K2[posV]] += [(Gamma[posG], (uk2diS[K2[posV]] - palletTrasportati[posV]))]
                    else:
                        rotte[K2[posV]] = [(Gamma[posG], (uk2diS[K2[posV]] - palletTrasportati[posV]))]

                    palletDaConsegnare -= uk2diS[K2[posV]] - palletTrasportati[posV]
                    PGa[Gamma[posG]] -= uk2diS[K2[posV]] - palletTrasportati[posV]
                    palletTrasportati[posV] += PGa[Gamma[posG]] # full

                # passo al veicolo sucessivo
                posV = (posV + 1) % len(K2)

            # passo al cliente sucessivo
            posG = (posG + 1) % len(Gamma)


        # aggiornare x2 e w2 in base a rotte[k]
        arcoI = s

        for k in K2:
            for (g , p) in rotte[k]:
                x2[(k , g, arcoI, g)] = p
                w2[(k, arcoI, g)]=1

                arcoI=g


        print(rotte)
