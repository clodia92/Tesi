class Solution:

    # struttura che contiene tutte le mosse con relativi costi
    # dizionari di smd
    # smd = {}

    def findSolutionBase(self, s, x2, w2, uk2, Pgac, PsGa, K2diS, A2, GammadiS, CdiS,):
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

        for v in K2diS[s]:
            print("uk2[{}]: {}".format(v, uk2[v]))

        for gamma in GammadiS[s]:
            print("PsGa[({}, {})]: {}".format(s, gamma, PsGa[(s, gamma)]))

        print("K2diS[{}]: {}".format(s, K2diS[s]))

        print("A2: ")
        for arc in A2:
            if ((s == arc[0]) and arc[1] in GammadiS[s]) or ((arc[0] in GammadiS[s]) and (arc[1] in GammadiS[s])):
                    print(arc)

        print("GammadiS[{}]: {}".format(s, GammadiS[s]))
        print("CdiS: {}".format(CdiS))


        numeroVeicoliDiS= len(K2diS[s])


