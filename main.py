
from fileReader import readFile

class TabuSearch:

    def __init__(self, nameInputFile):

        self.nameInputFile = nameInputFile
        print("Name input file", nameInputFile)
        myRead = readFile(self.nameInputFile)

        # set A2
        self.A2 = myRead.get_setOfArcA2()

        # unit cost of vehicle k in K=(K1+k2) operating at satellite S
        self.aks = myRead.get_dictionaryOfAks()     # da controllare

        # transportation cost per pallet traversing arc (i,j) in A2 by vehicle k in K2
        self.ak2ij = myRead.get_dictionaryOfAk2ij()

        # routing cost of truck k in K2 traversing arc (i,j) in A2
        self.nik2ij = myRead.get_dictionaryOfNik2ij()

        # dictionary of Pgac[c,ga]
        # number of pallets in container c in C which have destination ga in gam
        self.Pgac = {}

        self.PalletInContainer = myRead.get_dictionaryOfPalletInContainer()

        # max number of pallets can be carried by vehicle k in K2 (second echelon)
        self.uk2 = myRead.get_dictionaryOfUk2()
        print ("self.uk2: ", self.uk2)

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

        self.asc = {}  # aggiunto 10 novembre 2017

        # dictionary of ys[s] variables (first Model)
        self.ys = {}

        # dictionary of x1[k][s][c] variables (first Model)
        self.x1 = {}

        # dictionary of x2[k][gamma](i,j) variables (second echelon)
        self.x2 = {}

        # dictionary of w2[k](i,j) variables (second echelon)
        self.w2 = {}

        # dictionary of C[s]
        # set of containers assigned to satellite s
        self.CdiS = {}

        # dictionary of Sneg
        # set of selected satellites
        self.Sneg = []

        # dictionary of Gamma[s]
        # set of customers served by satellite s
        self.GammadiS = {}

        # dictionary of zks[k][s] variables (second Model)
        self.zks = {}

        # dictionary of Ps[s]
        # number of pallets in satellite s in S according to the solution of P1
        self.Ps = {}

        # dictionary of K2diS[s]
        # set of vehicules K2 assigned to satellite s (when zks is 1)
        self.K2diS = {}

        # dictionary of PsGa[(s,ga)]
        # number of pallets in satellite s in S with destination gamma according to the solution of P1
        self.PsGa = {}

        # dictionary of PcGaKs[(c,ga,k,s)]
        # number of pallets unpacked from container c in C
        # moved from satellite s in Sneg to customer ga in GammadiS
        # by vehicle k in K2diS according to the solution of P1
        self.PcGaKs = {}

        # dictionary of x2Global[k][gamma](i,j) variables (second echelon)
        self.x2Global = {}

        # dictionary of w2Global[k](i,j) variables (second echelon)
        self.w2Global = {}

        # dictionary of best variables
        self.ysBest = {}

        self.x1Best = {}

        self.zksBest = {}

        self.x2GlobalBest = {}

        self.w2GlobalBest = {}

        # dictionary
        self.domandeClienti = {}

        # list
        # list of customers demands
        self.listaDomande = []

        # dictionary of x2GlobalSimulated[k][gamma](i,j) (second echelon)
        self.x2GlobalSimulated = {}

        # dictionary of w2GlobalSimulated[k](i,j) (second echelon)
        self.w2GlobalSimulated = {}

        # dictionary of K2SimulateddiS[s]
        # set of vehicules K2 assigned to satellite s (when zks is 1)
        self.K2SimulateddiS = {}

        pass