class Solution:

    # struttura che contiene tutte le mosse con relativi costi
    # dizionari di smd
    # smd = {}

    def findSolutionBase(self, s, x2, w2, uk2, Pgac, PsGa, K2diS, A2, GammadiS, CdiS,):
        print("START findSolutionBase(), satellite: ", s)

        # x2[(k, gamma, i, j)]
        # w2[(k, i, j)]
        # uk2
        # Pgac
        # PsGa
        # K2diS[s]
        # A2
        # GammadiS
        # CdiS

        for v in K2diS[s]:
            print("uk2[{}]: {}".format(v, uk2[v]))
        print("Pgac: {}".format(Pgac))
        print("PsGa: {}".format(PsGa))
        print("K2diS[{}]: {}".format(s, K2diS[s]))
        print("A2: {}".format(A2))
        print("GammadiS: {}".format(GammadiS))
        print("CdiS: {}".format(CdiS))
