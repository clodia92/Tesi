from lettura import readFile
from functions import *
from constraintsModelThree import computeCost
import heapq

class Prob3:

    def __init__(self, nomeFileInput):
        # lettura del file
        self.nomeFile = nomeFileInput
        print("Nome file input", nomeFileInput)
        myRead = readFile(self.nomeFile)

        # print("Numero di satelliti -->", myRead.get_numberOfSatellites())
        # print("Numero di containers -->", myRead.get_numberOfContainers())
        # print("Numero di veicoli in K1 -->", myRead.get_numberOfVehicles1st())
        # print("Numero di veicoli in K2 -->", myRead.get_numberOfVehicles2nd())
        # print("Numero di clienti -->", myRead.get_numberOfCustomers())
        #
        # print("Set dei satelliti -->", myRead.get_setOfSatellites())
        # print("Set dei containers -->", myRead.get_setOfContainers())
        # print("Set dei veicoli in K1 -->", myRead.get_setOfVehicles1st())
        # print("Set dei veicoli in K2 -->", myRead.get_setOfVehicles2nd())
        # print("Set dei clienti -->", myRead.get_setOfCustomers())
        # print("Set degli archi in A1 -->", myRead.get_setOfArcA1())
        # print("Set degli archi in A2 -->", myRead.get_setOfArcA2())
        #
        # print("Dizionario di fs --> ", myRead.get_dictionaryOfFs())
        # print("Dizionario di nik2ij -->", myRead.get_dictionaryOfNik2ij())
        # print("Dizionario di ak2ij -->", myRead.get_dictionaryOfAk2ij())
        # print("Dizionario di betas -->", myRead.get_dictionaryOfBetaS())
        # print("Dizionario di aks -->", myRead.get_dictionaryOfAks())
        # print("Dizionario di ak1s -->", myRead.get_dictionaryOfAk1s())
        # print("Dizionario di uk2 -->", myRead.get_dictionaryOfUk2())
        # print("Dizionario di us -->", myRead.get_dictionaryOfUs())
        # print("Dizionario di vs -->", myRead.get_dictionaryOfVs())
        # print("Dizionario di PalletInContainer -->", myRead.get_dictionaryOfPalletInContainer())
        # print("Dizionario di pis -->", myRead.get_dictionaryOfPis())
        # print("Lunghezza A2 --> ", len(myRead.get_setOfArcA2()))
        # print("Mezzi Prob2 -->", myRead.get_K2diS())
        # print("Domande -->", myRead.get_PsGa())
        # print("Sneg -->", myRead.get_Sneg())
        # print("Pgac -->", myRead.get_Pgac())

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
        self.CdiS = myRead.get_CdiS()     #####  <-------- chiedere a Simone

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
        self.PcGaKs = {}   #     <------------------------------------- controllare se è la soluzione finale

        pass

if __name__ == "__main__":

    print("Start Prob3: ")
    myProb = Prob3("2_2_100_0_20")

    # ogni rotta viene calcolata per ogni satellite separatamente
    for s in myProb.Sneg:
        print("\nSTART satellite: {}".format(s))
        # lista delle soluzioni trovate: (x2, w2, cost)
        solutions = []

        # generate variables for Model Three
        generateVariablesModelThree(myProb.x2, myProb.w2, myProb.K2diS, myProb.GammadiS, myProb.A2, s)

        # trova una soluzione di base ammissibile
        result, myProb.x2, myProb.w2, rotte = findSolutionBase(s, myProb.x2, myProb.w2, myProb.uk2, myProb.Pgac, myProb.PsGa, myProb.K2diS, myProb.A2, myProb.GammadiS, myProb.CdiS)
        cost = computeCost(myProb.x2, myProb.w2, myProb.K2diS, myProb.GammadiS, myProb.A2, myProb.nik2ij, myProb.ak2ij, s)


        # struttura che contiene tutte le mosse con relativi costi
        # dizionari di smd con chiave move point
        smd10 = {}  # dimensione: n*(n+k-1) (n: nodi, k: veicoli)
        # smd11 = {}
        # smd2opt = {}

        if result:
            print("Soluzione di base trovata, costo: {}.".format(cost))
            # aggiungo la soluzione alle soluzioni
            solutions.append((myProb.x2, myProb.w2, cost))

            # viene inizializzato l'SMD
            inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s)
            # crea la lista in cui verrà salvato l'heap
            # non usare list(smd10.values()) direttamente perché tale lista non è modificabile e quindi non sarà un heap
            heapSMD10 = list(smd10.values())
            # crea l'heap di smd10
            heapq.heapify(heapSMD10)

            localSearch(heapSMD10, smd10, myProb.x2, myProb.w2, rotte)

        else:
            # trovare un'altra soluzione
            print("Trova un'altra soluzione.")

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
