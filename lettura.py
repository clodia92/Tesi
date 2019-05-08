import csv


class readFile:

    def __init__(self, nomeFile):

        # number of satellites S
        self.NumberOfSatellitesPark = 0
        # number of containers C
        self.NumberOfContainersPark = 0
        # number of vehicles in the first echelon K1
        self.NumberOfVehiclesEchelon1Park = 0
        # number of vehicles in the second echelon K2
        self.NumberOfVehiclesEchelon2Park = 0
        # number of customers GAMMA
        self.NumberOfCustomersPark = 0
        # set of satellites S
        self.satelliteSetPark = []
        # set of containers C
        self.containersSetPark = []
        # set of vehicles 1st echelon
        self.vehiclesK1SetPark = []
        # set of vehicles 2nd echelon
        self.vehiclesK2SetPark = []
        # set of customers
        self.customersSetPark = []
        # set of arc A1
        self.arcSetA1Park = []
        # set of arc A2
        self.arcSetA2Park = []
        # flag
        self.flagA2from = 0
        self.flagA2to = 0

        # fixed cost of selection of satellite s in S
        self.fsPark = {}
        # routing cost of truck k in K2 traversing arc (i,j) in A2
        self.nik2ijpark = {}
        # transportation cost per pallet traversing arc (i,j) in A2 by vehicle k in K2
        self.ak2ijpark = {}
        # unit cost of vehicle k in K=(K1+k2) operating at satellite S
        self.akspark = {}
        # transportation cost per container moved to satellite s in S
        # by vehicle k in K1
        self.ak1spark = {}
        # unit cost per pallet served by satellite s in S
        self.betasPark = {}
        # max number of pallets can be carried by vehicle k in K2 (second echelon)
        self.uk2Park = {}
        # max number of containers entering satellite s in S
        self.usPark = {}
        # max number of vehicles served by satellite s in S
        self.vsPark = {}
        self.pcPark = {}
        # max number of pallets cross-docking in satellite s in S
        self.pisPark = {}

        # dictionary of Pgac[c,ga]
        # number of pallets in container c in C which have destination ga in gam
        self.Pgac = {}

        # set of Sneg
        self. Sneg = []

        # dictionary of K2diS[s]
        # mezzi k2 assegnati ad ogni satellite
        self.K2diS = {}
        # conta il numero di occorrenza di K2diS
        self.conta_K2diS = 0


        # dictionary of PsGa[(s,ga)]
        # number of pallets in satellite s in S with destination gamma according to the solution of P1
        self.PsGa = {}
        # conta il numero di occorrenza di PsGa
        self.conta_PsGa = 0

        # counter for occurrences of PalletInContainer
        self.conta_Pc = 1
        # counter for occurrences of nik2ij
        self.conta_ni = 0
        # counter for occurrences of ak2ij
        self.conta_a2 = 0
        # counter for occurrences of aks
        self_conta_aks = 1
        # counter for occurrences of ak1s
        self.conta_ak1s = 1

        self.A2fromPark = []
        self.A2toPark = []

        with open(nomeFile + ".csv") as csvfile:
            # with open(nomeFile) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=",")
            for row in spamreader:

                if (row[0] == "info"):

                    # number of satellites S
                    self.NumberOfSatellitesPark = int(row[1])
                    for i in range(self.NumberOfSatellitesPark):
                        self.satelliteSetPark.append(i + 1)
                        pass

                    # number of containers C
                    self.NumberOfContainersPark = int(row[2])
                    for i in range(self.NumberOfContainersPark):
                        self.containersSetPark.append(i + 1)
                        pass

                    # number of vehicles in the first echelon K1
                    self.NumberOfVehiclesEchelon1Park = int(row[3])
                    for i in range(self.NumberOfVehiclesEchelon1Park):
                        self.vehiclesK1SetPark.append(i + 1)
                        pass

                    # counter for occurrences of ni
                    self.conta_ni = self.NumberOfVehiclesEchelon1Park + 1
                    # print("conta_ni = ", self.conta_ni)
                    # counter for occurrences of a2
                    self.conta_a2 = self.NumberOfVehiclesEchelon1Park + 1
                    # print("conta_a2 = ", self.conta_a2)

                    # number of vehicles in the second echelon K2
                    self.NumberOfVehiclesEchelon2Park = int(row[4]);
                    
                    for i in range(self.NumberOfVehiclesEchelon2Park):
                        self.vehiclesK2SetPark.append(i + self.NumberOfVehiclesEchelon1Park + 1)
                        pass

                        # number of customers GAMMA
                    self.NumberOfCustomersPark = int(row[5])
                    for i in range(self.NumberOfCustomersPark):
                        self.customersSetPark.append(i + 1 + self.NumberOfSatellitesPark)
                        pass
                    pass

                # fixed cost of selection of satellite s in S
                if (row[0] == "fs"):
                    row.pop(0)
                    for j in range(self.NumberOfSatellitesPark):
                        myKey = j + 1
                        self.fsPark[myKey] = int(row[j])
                    pass

                if (row[0] == "A2from"):
                    row.pop(0)
                    self.A2fromPark = [int(i) for i in row]
                    # print ("A2from = ", self.A2fromPark)
                    self.flagA2from = 1
                    pass

                if (row[0] == "A2to"):
                    row.pop(0)
                    self.A2toPark = [int(i) for i in row]
                    # print ("A2to = ", self.A2toPark)
                    self.flagA2to = 1
                    pass

                if (self.flagA2from == 1 and self.flagA2to == 1):
                    for i in range(self.NumberOfSatellitesPark):
                        self.arcSetA1Park.append((0, i + 1))
                        # for i in range(len(self.A2toPark)):
                    for i in range(len(self.A2toPark)):
                        self.arcSetA2Park.append((self.A2fromPark[i], self.A2toPark[i]))
                    self.flagA2from = 0
                    self.flagA2to = 0
                    pass

                    # routing cost of truck k in K2 traversing arc (i,j) in A2
                if ("ni" in row[0]):
                    row.pop(0)
                    # for j in xrange(self.NumberOfSatellitesPark):
                    for i in range(len(self.A2toPark)):
                        myKey = (self.conta_ni, self.A2fromPark[i], self.A2toPark[i])
                        self.nik2ijpark[myKey] = float(row[i])
                        # print ("myKey = ", myKey)
                        # print ("value = ", self.nik2ijpark[myKey])
                        pass
                    self.conta_ni += 1
                    pass

                # transportation cost per pallet traversing arc (i,j) in A2 by vehicle k in K2
                if (row[0].startswith("a2") and row[0].endswith("ij")):
                    row.pop(0)
                    for i in range(len(self.A2toPark)):
                        myKey = (self.conta_a2, self.A2fromPark[i], self.A2toPark[i])
                        self.ak2ijpark[myKey] = float(row[i])
                        # print ("myKey = ", myKey)
                        # print ("value = ", self.ak2ijpark[myKey])
                        pass
                    self.conta_a2 += 1
                    pass

                # unit cost per pallet served by satellite s in S
                if (row[0] == "betas"):
                    row.pop(0)
                    for j in range(self.NumberOfSatellitesPark):
                        myKey = j + 1
                        self.betasPark[myKey] = float(row[j])
                    # print ("betasPark = ", self.betasPark)
                    pass

                # unit cost of vehicle k in K=(K1+k2) operating at satellite S
                if (row[0].startswith("aa") and row[0].endswith("s")):
                    row.pop(0)
                    for i in range(self.NumberOfSatellitesPark):
                        myKey = (self_conta_aks, i + 1)
                        self.akspark[myKey] = int(row[i])
                        # print ("myKey = ", myKey)
                        # print ("value = ", self.akspark[myKey])
                        pass
                    self_conta_aks += 1
                    pass

                # transportation cost per container moved to satellite s in S
                # by vehicle k in K1
                if (row[0].startswith("a1") and row[0].endswith("s")):
                    row.pop(0)
                    for i in range(self.NumberOfSatellitesPark):
                        myKey = (self.conta_ak1s, i + 1)
                        self.ak1spark[myKey] = float(row[i])  # int(row[i]) corretto 2 agosto
                        # print ("myKey = ", myKey)
                        # print ("value = ", self.ak1spark[myKey])
                        pass
                    self.conta_ak1s += 1
                    pass

                # max number of pallets can be carried by vehicle k in K2 (second echelon)
                if (row[0] == "uk2"):
                    row.pop(0)
                    i = 0
                    for j in self.vehiclesK2SetPark:
                        self.uk2Park[j] = int(row[i])
                        i += 1
                        pass
                    # print ("uk2Park = ", self.uk2Park)
                    pass

                # max number of containers entering satellite s in S
                if (row[0] == "us"):
                    row.pop(0)
                    for i in range(self.NumberOfSatellitesPark):
                        self.usPark[i + 1] = int(row[i])
                    # print ("usPark = ", self.usPark)
                    pass

                # max number of vehicles served by satellite s in S
                if (row[0] == "vs"):
                    row.pop(0)
                    for i in range(self.NumberOfSatellitesPark):
                        self.vsPark[i + 1] = int(row[i])
                    # print ("vsPark = ", self.vsPark)
                    pass

                if (row[0].startswith("pc")):
                    # print("number container = ", self.contaPc)
                    row.pop(0)
                    self.listCustomers = []
                    for i in range(len(row)):
                        self.cliente=int(row[i])
                        myKey = (self.conta_Pc, self.cliente)
                        self.listCustomers.append(self.cliente)
                        if myKey in self.Pgac:
                            self.Pgac[myKey] += 1
                        else:
                            self.Pgac[myKey] = 1
                        pass
                    self.pcPark[self.conta_Pc] = self.listCustomers;
                    # print ("pcPark = ", self.pcPark)

                    self.conta_Pc += 1
                    pass

                    # max number of pallets cross-docking in satellite s in S
                if (row[0] == "pis"):
                    row.pop(0)
                    for i in range(self.NumberOfSatellitesPark):
                        self.pisPark[i + 1] = int(row[i])
                    # print ("pisPark = ", self.pisPark)
                    pass

                    # if(row[0] == "cust"):
                    #                     row.pop(0)
                    #                     for i in xrange(self.NumberOfSatellitesPark):
                    #                         self.pisPark[i+1] = int(row[i])
                    #                     #print ("pisPark = ", self.pisPark)
                    # print()
                    pass

                # soluzione Subproblem Prob2
                if (row[0].startswith("M")):
                    # aggiunto il satellite alla lista Sneg poichè soluzione del Probl 1
                    self.Sneg.append(int(''.join(filter(str.isdigit, row[0]))))
                    row.pop(0)
                    self.listaMezzi = []
                    for i in range(len(row)):
                        self.listaMezzi.append(int(row[i]))
                        pass

                    self.conta_K2diS += 1
                    self.K2diS [self.conta_K2diS] = self.listaMezzi
                    pass

                # lettura dei clienti assegnati al relativo satellite
                if (row[0].startswith("C")):
                    row.pop(0)
                    self.conta_PsGa += 1
                    self.listaClienti = []
                    self.listaClienti = [int(i) for i in row]
                    pass

                # lettura domande dei rispettivi clienti al punto sopra
                if (row[0].startswith("D")):
                    row.pop(0)
                    for i in range(len(row)):
                        myKey = (self.conta_PsGa, self.listaClienti[i])
                        self.PsGa[myKey] = int(row[i])
                        pass
                    pass

    # number of satellites S
    def get_numberOfSatellites(self):
        return self.NumberOfSatellitesPark

    # set of satellites S
    def get_setOfSatellites(self):
        return self.satelliteSetPark

    # number of containers C
    def get_numberOfContainers(self):
        return self.NumberOfContainersPark

    # set of containers C
    def get_setOfContainers(self):
        return self.containersSetPark

    # number of vehicles in the first echelon K1
    def get_numberOfVehicles1st(self):
        return self.NumberOfVehiclesEchelon1Park

    # set of vehicles 1st echelon
    def get_setOfVehicles1st(self):
        return self.vehiclesK1SetPark

    # number of vehicles in the second echelon K2
    def get_numberOfVehicles2nd(self):
        return self.NumberOfVehiclesEchelon2Park

    # set of vehicles 2nd echelon
    def get_setOfVehicles2nd(self):
        return self.vehiclesK2SetPark

    # number of customers GAMMA
    def get_numberOfCustomers(self):
        return self.NumberOfCustomersPark

    # set of customers
    def get_setOfCustomers(self):
        return self.customersSetPark

    # set of arc A1
    def get_setOfArcA1(self):
        return self.arcSetA1Park

    # set of arc A2
    def get_setOfArcA2(self):
        return self.arcSetA2Park

    # dictionary of parameter fs
    def get_dictionaryOfFs(self):
        return self.fsPark

    # dictionary of parameter nik2ij
    def get_dictionaryOfNik2ij(self):
        return self.nik2ijpark

    # dictionary of parameter ak2ij
    def get_dictionaryOfAk2ij(self):
        return self.ak2ijpark

    # dictionary of parameter betas
    def get_dictionaryOfBetaS(self):
        return self.betasPark

    # dictionary of parameter aks
    def get_dictionaryOfAks(self):
        return self.akspark

    # dictionary of parameter ak1s
    def get_dictionaryOfAk1s(self):
        return self.ak1spark

    # dictionary of parameter uk2
    def get_dictionaryOfUk2(self):
        return self.uk2Park

    # dictionary of parameter us
    def get_dictionaryOfUs(self):
        return self.usPark

    # dictionary of parameter vs
    def get_dictionaryOfVs(self):
        return self.vsPark

    # dictionary of parameter PalletInContainer
    def get_dictionaryOfPalletInContainer(self):
        return self.pcPark

    # dictionary of parameter pis
    def get_dictionaryOfPis(self):
        return self.pisPark

    # dictionary of parameter K2diS
    def get_K2diS(self):
        return self.K2diS

    # dictionary of parameter PsGa
    def get_PsGa (self):
        return self.PsGa

    # set of Sneg
    def get_Sneg (self):
        return self.Sneg

    # dictionary of Pgac[c,ga]
    def get_Pgac (self):
        return self.Pgac