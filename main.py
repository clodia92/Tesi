from lettura import readFile
from functions import *
from constraintsModelThree import computeCost
import heapq
import time


class Prob3:

    def __init__(self, nomeFileInput):
        # lettura del file
        self.nomeFile = nomeFileInput
        print("Nome file input", nomeFileInput)
        myRead = readFile(self.nomeFile)

        # fixed cost of selection of satellite s in S
        self.fs = myRead.get_dictionaryOfFs()

        # set A1
        self.A1 = myRead.get_setOfArcA1()

        # set A2
        self.A2 = myRead.get_setOfArcA2()

        # unit cost of vehicle k in K=(K1+k2) operating at satellite S
        self.aks = myRead.get_dictionaryOfAks()

        # unit cost per pallet served by satellite s in S
        self.betas = myRead.get_dictionaryOfBetaS()

        # transportation cost per container moved to satellite s in S
        # by vehicle k in K1
        self.ak1s = myRead.get_dictionaryOfAk1s()

        # transportation cost per pallet traversing arc (i,j) in A2 by vehicle k in K2
        self.ak2ij = myRead.get_dictionaryOfAk2ij()

        # routing cost of truck k in K2 traversing arc (i,j) in A2
        self.nik2ij = myRead.get_dictionaryOfNik2ij()

        # dictionary of Pgac[c,ga]
        # number of pallets in container c in C which have destination ga in gam
        self.Pgac = myRead.get_Pgac()

        self.PalletInContainer = myRead.get_dictionaryOfPalletInContainer()

        # max number of pallets can be carried by vehicle k in K2 (second echelon)
        self.uk2 = myRead.get_dictionaryOfUk2()

        # max number of containers entering satellite s in S
        self.us = myRead.get_dictionaryOfUs()

        # max number of vehicles served by satellite s in S
        self.vs = myRead.get_dictionaryOfVs()

        # max number of pallets cross-docking in satellite s in S
        self.pis = myRead.get_dictionaryOfPis()

        # number of satellites
        self.NumberOfSatellites = myRead.get_numberOfSatellites()

        # set of satellites S
        self.S = myRead.get_setOfSatellites()

        # number of customers
        self.NumberOfCustomers = myRead.get_numberOfCustomers()

        # set of customers gamma
        self.gam = myRead.get_setOfCustomers()

        # number of containers
        self.NumberOfContainers = myRead.get_numberOfContainers()

        # set of containers
        self.C = myRead.get_setOfContainers()

        # number of vehicles (first echelon)
        self.NumberOfVehiclesEchelon1 = myRead.get_numberOfVehicles1st()

        # set of vehicles K1 (first echelon)
        self.K1 = myRead.get_setOfVehicles1st()

        # number of vehicles (second echelon)
        self.NumberOfVehiclesEchelon2 = myRead.get_numberOfVehicles2nd()

        # set of vehicles K2 (second echelon)
        self.K2 = myRead.get_setOfVehicles2nd()

        # dictionary of x2[(k, gamma, i, j)] variables (second echelon)
        self.x2 = {}

        # dictionary of w2[(k, i, j)] variables (second echelon)
        self.w2 = {}

        # dictionary of C[s]
        # set of containers assigned to satellite s
        self.CdiS = myRead.get_CdiS()  #####  <-------- chiedere a Simone

        # dictionary of Sneg
        # set of selected satellites
        self.Sneg = myRead.get_Sneg()

        # dictionary of Gamma[s]
        # set of customers served by satellite s
        self.GammadiS = myRead.get_GammadiS()

        # dictionary of K2diS[s]
        # set of vehicules K2 assigned to satellite s (when zks is 1)
        self.K2diS = myRead.get_K2diS()

        # dictionary of PsGa[(s,ga)]
        # number of pallets in satellite s in S with destination gamma according to the solution of P2
        self.PsGa = myRead.get_PsGa()

        # dictionary of PcGaKs[(c,ga,k,s)]
        # number of pallets unpacked from container c in C
        # moved from satellite s in Sneg to customer ga in GammadiS
        # by vehicle k in K2diS according to the solution of P2
        self.PcGaKs = {}  # <------------------------------------- controllare se è la soluzione finale

        pass


if __name__ == "__main__":

    print("Start Prob3: ")
    myProb = Prob3("2_2_100_0_20")

    # ogni rotta viene calcolata per ogni satellite separatamente
    for s in myProb.Sneg:
        print("\n\n\nSTART satellite: {}".format(s))
        start_time = time.time()

        # lista delle soluzioni trovate: (x2, w2, cost)
        solutions = []

        # generate variables for Model Three
        generateVariablesModelThree(myProb.x2, myProb.w2, myProb.K2diS, myProb.GammadiS, myProb.A2, s)

        # trova una soluzione di base ammissibile
        resultSolutionBase, myProb.x2, myProb.w2, rotte = findSolutionBase(s, myProb.x2, myProb.w2, myProb.uk2,
                                                                           myProb.Pgac, myProb.PsGa, myProb.K2diS[s],
                                                                           myProb.A2, myProb.GammadiS[s], myProb.CdiS)
        cost = computeCost(myProb.x2, myProb.w2, myProb.K2diS, myProb.GammadiS, myProb.A2, myProb.nik2ij, myProb.ak2ij, s)
        costTMP = cost + 1

        # struttura che contiene tutte le mosse con relativi costi
        # dizionari di smd con chiave move point
        smd10 = {}  # dimensione: n*(n+k-1) (n: nodi, k: veicoli)    <---  da rivedere
        smd11 = {}  # dimensione: n!/2!(n-2)! (n: nodi)              <---  da rivedere
        # smd2opt = {}

        if resultSolutionBase:
            print("Soluzione di base trovata, costo: {}.".format(cost))
            # aggiungo la soluzione alle soluzioni
            solutions.append((cost, myProb.x2, myProb.w2))

            # vengono inizializzati gli SMD
            inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s)
            inizializzaSMD11(smd11, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2)
            # crea la lista unica dei costi in cui verrà salvato l'heap
            # non usare list(smd10.values()) direttamente perché tale lista non è modificabile e quindi non sarà un heap
            heapSMD = list(smd10.values()) + list(smd11.values())
            # crea l'heap di smd10 e smd11
            heapq.heapify(heapSMD)

            itMosse = 0

            while True:
                x2TMP, w2TMP, keyLocalSearch, flagAllPallets = localSearch(heapSMD, smd10, smd11, myProb.x2, myProb.w2, rotte, s, myProb.uk2,
                                                                           myProb.Pgac, myProb.PsGa, myProb.K2diS[s], myProb.A2,
                                                                           myProb.GammadiS[s], myProb.CdiS)
                costTMP = computeCost(x2TMP, w2TMP, myProb.K2diS, myProb.GammadiS, myProb.A2, myProb.nik2ij, myProb.ak2ij, s)

                if keyLocalSearch == -1 or costTMP > cost:

                    print("Soluzione finale trovata, itMosse: {}, costo: {}.".format(itMosse, cost))
                    print("rotte: {}".format(rotte))
                    print("time elapsed: {:.2f}s.".format(time.time() - start_time))
                    break
                else:
                    itMosse += 1
                    cost = costTMP

                    # aggiornare rotte dopo una mossa ammissibile
                    # 1-0 Exchange
                    if len(keyLocalSearch) == 5:
                        updateRotteSmd10(rotte, keyLocalSearch, flagAllPallets)
                    # 1-1 Exchange
                    elif len(keyLocalSearch) == 4:
                        updateRotteSmd11(rotte, keyLocalSearch)

                    # aggiornare x2 e w2 dopo una mossa ammissibile
                    myProb.x2 = x2TMP.copy()
                    myProb.w2 = w2TMP.copy()

                    # aggiornare SMD dopo una mossa ammissibile
                    smd10.clear()
                    inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s)
                    smd11.clear()
                    inizializzaSMD11(smd11, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2)

                    print("Soluzione migliore trovata, costo: {}.".format(cost))
                    print("rotte: {}".format(rotte))
                    solutions.append([cost, myProb.x2, myProb.w2])

                    # crea la lista unica dei costi in cui verrà salvato l'heap
                    heapSMD = list(smd10.values()) + list(smd11.values())
                    # crea l'heap di smd10 e di smd11
                    heapq.heapify(heapSMD)
                    pass
        else:
            # trovare un'altra soluzione
            print("Trova un'altra soluzione iniziale.")

########################### FUNZIONI UTILI DELL'HEAP ###########################
# restituisce la chiave del valore minore (primo elemento)
# list(smd10.keys())[list(smd10.values()).index(heapSMD10[0])]
# restituisce il valore minore dell'heap senza eliminarlo
# heapSMD10[0]
# restituisce ed elimina il valore minore dall'heap (primo elemento)
# heapq.heappop(heapSMD10)
# aggiunge elemento all'heap
# heapq.heappush(heapSMD10, -100)
########################### FUNZIONI UTILI DELL'HEAP ###########################
