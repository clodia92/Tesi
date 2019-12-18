# -*- coding: utf-8 -*-

__author__ = "Dennis Incollu, Claudia Porcu"
__date__ = "2019"

from lettura import readFile
from functions import *
from constraintsModelThree import computeCostPenalty

from copy import deepcopy
import heapq
import time
from math import modf


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
        self.CdiS = myRead.get_CdiS()

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

        pass


if __name__ == "__main__":

    # granularity

    startTimeTotal = time.time()

    print("Start Prob3: ")
    myProb = Prob3("006")

    # modificare itNSI per modificare il numero di soluzioni iniziali da esplorare
    itNSIMax = 10
    # modificare itMosseTSMax per modificare il numero iterazioni del Tabu Search da effettuare
    itMosseTSMax = 20
    # modificare elapsedTimeTotalMax per modificare il tempo massimo di esecuzione (in secondi)
    elapsedTimeTotalMax = 3600

    # modificare alternate10or11 per modificare se alternare 1-0 exchange e 1-1 exchange (1 o -1)
    # oppure utilizzare sempre entrambe contemporaneamente (0)
    #  1:   1-0 start
    # -1:   1-1 start
    #  0:   1-0 and 1-1
    alternate10or11 = 0

    # infeasible solutions
    # violare il vincolo35
    # penalità (in percentuale) da applicare al costo totale delle soluzioni non ammissibili
    penalty = 20
    # aumento di capacità (in percentuale) da applicare al vincolo35
    uk2Increased = 50
    
    # beta: valore che oscilla in un determinato intercallo. Se uguale a zero si annulla la soglia di granularità
    beta = 0.01

    # inizializzazione del valore soglia granularità
    granularityThreshold = 0

    # creazione file: il file vecchio viene sovrascritto
    pathlib.Path('outputTabuSearchProb3').mkdir(parents=True, exist_ok=True)
    if alternate10or11 == 0:
        filename = pathlib.Path(
            "outputTabuSearchProb3/" + myProb.nomeFile + "_" + str(itNSIMax) + "_" + str(itMosseTSMax) + "_and" + "_" + str(beta) + "_" + str(penalty) + "_" + str(uk2Increased))
    elif alternate10or11 == 1 or alternate10or11 == -1:
        filename = pathlib.Path(
            "outputTabuSearchProb3/" + myProb.nomeFile + "_" + str(itNSIMax) + "_" + str(itMosseTSMax) + "_or" + "_" + str(beta) + "_" + str(penalty) + "_" + str(uk2Increased))
    filename.touch(exist_ok=True)  # will create file, if it exists will do nothing

    file = open(filename, 'w')
    file.write("itNSIMax: {}, itMosseTSMax: {}, beta: {}, penalty: {}%, uk2Increased: {}%.\n".format(itNSIMax, itMosseTSMax, beta, penalty, uk2Increased))
    file.close()

    pathlib.Path('outputTabuSearchProb3').mkdir(parents=True, exist_ok=True)
    if alternate10or11 == 0:
        filename = pathlib.Path("outputTabuSearchProb3/" + myProb.nomeFile + "_" + str(itNSIMax) + "_" + str(
            itMosseTSMax) + "_and" + "_" + str(beta) + "_" + str(penalty) + "_" + str(uk2Increased) + "_StartBest")
    elif alternate10or11 == 1 or alternate10or11 == -1:
        filename = pathlib.Path("outputTabuSearchProb3/" + myProb.nomeFile + "_" + str(itNSIMax) + "_" + str(
            itMosseTSMax) + "_or" + "_" + str(beta) + "_" + str(penalty) + "_" + str(uk2Increased) + "_StartBest")
    filename.touch(exist_ok=True)  # will create file, if it exists will do nothing

    file = open(filename, 'w')
    file.write("itNSIMax: {}, itMosseTSMax: {}, beta: {}, penalty: {}%, uk2Increased: {}%.\n".format(itNSIMax, itMosseTSMax, beta, penalty, uk2Increased))
    file.close()
    # creazione file: il file vecchio viene sovrascritto

    # contatore numero soluzioni iniziali
    itNSI = 0

    # soluzione migliore assoluta trovata
    # [cost, x2, w2, rotte, padri, figli, mossaDiArrivo, itNSI]
    bestSolution = {}
    for s in myProb.Sneg:
        bestSolution[s] = []

    while itNSI < itNSIMax:
        # incremento contatore
        itNSI += 1

        # scrittura file stacco per ogni soluzione diversa
        pathlib.Path('outputTabuSearchProb3').mkdir(parents=True, exist_ok=True)
        if alternate10or11 == 0:
            filename = pathlib.Path("outputTabuSearchProb3/" + myProb.nomeFile + "_" + str(itNSIMax) + "_" + str(
                itMosseTSMax) + "_and" + "_" + str(beta) + "_" + str(penalty) + "_" + str(uk2Increased))
        elif alternate10or11 == 1 or alternate10or11 == -1:
            filename = pathlib.Path("outputTabuSearchProb3/" + myProb.nomeFile + "_" + str(itNSIMax) + "_" + str(
                itMosseTSMax) + "_or" + "_" + str(beta) + "_" + str(penalty) + "_" + str(uk2Increased))
        filename.touch(exist_ok=True)  # will create file, if it exists will do nothing

        file = open(filename, 'a')
        file.write("##########################################################################################\n")
        file.close()

        pathlib.Path('outputTabuSearchProb3').mkdir(parents=True, exist_ok=True)
        if alternate10or11 == 0:
            filename = pathlib.Path("outputTabuSearchProb3/" + myProb.nomeFile + "_" + str(itNSIMax) + "_" + str(
                itMosseTSMax) + "_and" + "_" + str(beta) + "_" + str(penalty) + "_" + str(uk2Increased)+ "_StartBest")
        elif alternate10or11 == 1 or alternate10or11 == -1:
            filename = pathlib.Path("outputTabuSearchProb3/" + myProb.nomeFile + "_" + str(itNSIMax) + "_" + str(
                itMosseTSMax) + "_or" + "_" + str(beta) + "_" + str(penalty) + "_" + str(uk2Increased)+ "_StartBest")
        filename.touch(exist_ok=True)  # will create file, if it exists will do nothing

        file = open(filename, 'a')
        file.write("##########################################################################################\n")
        file.close()
        # scrittura file stacco per ogni soluzione diversa
        print("itNSIMax: {}, itMosseTSMax: {}, beta: {}, penalty: {}%, uk2Increased: {}%.".format(itNSIMax, itMosseTSMax,
                                                                                             beta, penalty,
                                                                                             uk2Increased))
        print("##########################################################################################")

        # dizionario delle soluzioni per ogni satellite
        dictSolutions = {}

        # dizionario delle soluzioni tabu
        tabuList = {}

        # ogni rotta viene calcolata per ogni satellite separatamente
        for s in myProb.Sneg:
            print("\n\n\nSTART satellite: {}".format(s))
            start_timeS = time.time()

            # lista delle soluzioni trovate: (cost, x2, w2, rotte, padri, figli, mossaDiArrivo)
            # padri: lista di indici alle soluzioni di partenza in solutions
            # figli: lista di indici alle soluzioni ricavate in solutions
            # mossaDiArrivo: mossa che ha portato all'attuale soluzione
            # infeasibleK2: lista dei veicoli che superano la capacità
            dictSolutions[s] = []

            # tabu list per ogni satellite. Vengono riportati l'indice della soluzione e la mossa che l'ha determinata
            tabuList[s] = []
            # tabuList[s].append((0, (6, 6, 6, 5, 14)))

            # generate variables for Model Three
            generateVariablesModelThree(myProb.x2, myProb.w2, myProb.K2diS, myProb.GammadiS, myProb.A2, s)

            # trova una soluzione di base ammissibile
            resultSolutionBase, myProb.x2, myProb.w2, rotte = findSolutionBase(s, myProb.x2, myProb.w2, myProb.uk2,
                                                                               myProb.Pgac, myProb.PsGa,
                                                                               myProb.K2diS[s], myProb.A2,
                                                                               myProb.GammadiS[s], myProb.CdiS)
            vincolo35 = 1
            infeasibleK2 = []
            # variabile che contiene il costo della soluzione appena trovata
            cost = computeCostPenalty(myProb.x2, myProb.w2, myProb.K2diS, myProb.GammadiS, myProb.A2,
                                      myProb.nik2ij, myProb.ak2ij, s, infeasibleK2, penalty)
            # variabile che contiente il costo della nuova soluzione (inizialmente maggiore di cost)
            costNew = cost + 1

            # dizionari per ogni tipo di mossa che contengono tutte le mosse con relativi costi
            smd10 = {}  # 1-0 Exchange: chiave: [v1, v2, n1, n2, p]
            smd11 = {}  # 1-1 Exchange: chiave: [v1, v2, n1, n2]

            # inizializzazione della bestSolution (soluzione iniziale)
            bestSolutionIndice = 0

            elapsedTimeTotal = time.time() - startTimeTotal
            # se è stata trovata una soluzione iniziale
            if resultSolutionBase and elapsedTimeTotal < elapsedTimeTotalMax:

                zSoluzioneIniziale = cost

                # determinazione del valore soglia granularità in base alla soluzione iniziale trovata
                granularityThreshold = - beta * (zSoluzioneIniziale/(len(myProb.GammadiS) + len(myProb.K2diS)))


                print("Soluzione di base trovata, costo: {}.".format(cost))
                # lista dei padri della soluzione
                padri = [-1]
                # aggiungo la soluzione iniziale alle soluzioni
                dictSolutions[s].append(
                    [cost, deepcopy(myProb.x2), deepcopy(myProb.w2), deepcopy(rotte), padri, [], [-1], []])
                # aggiornamento di padri
                padri = [len(dictSolutions[s]) - 1]
                # indice della soluzione attuale che genera un figlio con il local search
                soluzionePrecedente = 0

                # SMD10
                if alternate10or11 == 1:
                    # vengono inizializzati gli SMD
                    inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s, granularityThreshold)

                # SMD11
                elif alternate10or11 == -1:
                    # vengono inizializzati gli SMD
                    inizializzaSMD11(smd11, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, granularityThreshold)

                # SMD10 and SMD11
                elif alternate10or11 == 0:
                    # vengono inizializzati gli SMD
                    inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s, granularityThreshold)
                    inizializzaSMD11(smd11, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, granularityThreshold)
                # crea la lista unica dei costi in cui verrà salvato l'heap
                # non usare list(smd10.values()) direttamente perché tale lista non è modificabile e quindi non sarà un heap
                # genera le liste contenenti le tuple: (valore differenza, chiave mossa)
                smd10ListReverse = [(v, k) for k, v in smd10.items()]
                smd11ListReverse = [(v, k) for k, v in smd11.items()]

                heapSMD = smd10ListReverse + smd11ListReverse
                # crea l'heap di smd10 e smd11
                heapq.heapify(heapSMD)

                # contatore di mosse effettuate nel localSearch e nel tabuSearch
                itMosseLS = 0
                itMosseTS = 0

                # chiave della mossa precedente
                oldKeyLocalSearch = -1

                # flag per segnalare che sono stati analizzati entrambi i tipo di mossa quando vengono alternate
                flagTried10and11 = False



                # iterazioni continuano finché non si presentano determinate condizioni
                # (esplorazione completa tramite Tabu Search, numero di iterazioni limitate, ecc)
                while True:

                    elapsedTimeTotal = time.time() - startTimeTotal
                    # print("elapsedTimeTotal: ", elapsedTimeTotal)
                    # non è stato raggiunto il tempo massimo di esecuzione
                    if elapsedTimeTotal < elapsedTimeTotalMax:
                        # parte il LocalSearch
                        # print("LS, alternate10or11: {}: ".format(alternate10or11))
                        x2TMP, w2TMP, keyLocalSearch, flagAllPallets, vincolo35 = localSearch(heapSMD, deepcopy(myProb.x2),
                                                                                              deepcopy(myProb.w2), rotte, s,
                                                                                              myProb.uk2, myProb.Pgac, myProb.PsGa,
                                                                                              myProb.K2diS[s], myProb.A2,
                                                                                              myProb.GammadiS[s], myProb.CdiS,
                                                                                              uk2Increased)
                        # se è stata trova una nuova mossa
                        if keyLocalSearch != -1:
                            # se il vincolo 35 non è stato violato
                            if vincolo35 == 1:
                                infeasibleK2 = []
                            # se il vincolo 35 è stato violato rispettando l'incremento di capacità
                            elif vincolo35 == 0:
                                rotteUpdated = deepcopy(rotte)
                                # aggiornare rotte dopo una mossa ammissibile
                                # 1-0 Exchange
                                if len(keyLocalSearch) == 5:
                                    updateRotteSmd10(rotteUpdated, keyLocalSearch, flagAllPallets)
                                # 1-1 Exchange
                                elif len(keyLocalSearch) == 4:
                                    updateRotteSmd11(rotteUpdated, keyLocalSearch)

                                # vengono trovati i veicoli che superano la propria capacità
                                # e il loro costo viene penalizzato in computeCost
                                infeasibleK2 = findInfeasibleK2(myProb.K2diS[s], myProb.uk2, x2TMP, rotteUpdated)

                            # aggiornamento del costo
                            costNew = computeCostPenalty(x2TMP, w2TMP, myProb.K2diS, myProb.GammadiS, myProb.A2,
                                                         myProb.nik2ij, myProb.ak2ij, s, infeasibleK2, penalty)
                        else:
                            infeasibleK2 = []
                            costNew = cost

                        # print("localSearch, key: {} cost: {}, costNew: {}".format(keyLocalSearch, cost, costNew))
                    # è stato raggiunto il tempo massimo di esecuzione
                    else:
                        keyLocalSearch = -1
                        costNew = cost

                    # effettua mossa migliorativa
                    if keyLocalSearch != -1:# and costNew < cost:
                        flagTried10and11 = False

                        itMosseLS += 1
                        cost = costNew

                        # aggiornare rotte dopo una mossa ammissibile
                        # 1-0 Exchange
                        if len(keyLocalSearch) == 5:
                            updateRotteSmd10(rotte, keyLocalSearch, flagAllPallets)
                        # 1-1 Exchange
                        elif len(keyLocalSearch) == 4:
                            updateRotteSmd11(rotte, keyLocalSearch)

                        # aggiornare x2 e w2 dopo una mossa ammissibile
                        myProb.x2 = deepcopy(x2TMP)
                        myProb.w2 = deepcopy(w2TMP)

                        # aggiornare SMD dopo una mossa ammissibile
                        smd10.clear()
                        smd11.clear()
                        # alternare 1-0 exchange e 1-1 exchange
                        alternate10or11 = alternate10or11 * -1
                        # SMD10
                        if alternate10or11 == 1:
                            inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s, granularityThreshold)

                        # SMD11
                        elif alternate10or11 == -1:
                            inizializzaSMD11(smd11, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, granularityThreshold)

                        # SMD10 and SMD11
                        elif alternate10or11 == 0:
                            inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s, granularityThreshold)
                            inizializzaSMD11(smd11, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, granularityThreshold)

                        print("Soluzione migliore trovata, costo: {}.".format(cost))
                        # print("rotte: {}".format(rotte))

                        listaCosti = [item[0] for item in dictSolutions[s]]

                        # se esiste già una soluzione con lo stesso costo
                        if cost in listaCosti:
                            indiceSoluzionePresente = listaCosti.index(cost)

                            # se la rotta è uguale ad una soluzione precedente e anche x2 è uguale
                            if cost == dictSolutions[s][indiceSoluzionePresente][0] and \
                                    dictSolutions[s][indiceSoluzionePresente][3] == rotte and \
                                    dictSolutions[s][indiceSoluzionePresente][1] == x2TMP:
                                # aggiornamento del padre della nuova soluzione
                                dictSolutions[s][indiceSoluzionePresente][4].append(soluzionePrecedente)
                                # aggiornamento dei figli del padre della nuova soluzione
                                dictSolutions[s][soluzionePrecedente][5].append(indiceSoluzionePresente)
                                # aggiornamento delle mosse di arrivo della nuova soluzione
                                dictSolutions[s][indiceSoluzionePresente][6].append(keyLocalSearch)

                                soluzionePrecedente = indiceSoluzionePresente
                                pass
                            # se la rotta non è uguale ad una soluzione precedente
                            elif cost == dictSolutions[s][indiceSoluzionePresente][0] and \
                                    dictSolutions[s][indiceSoluzionePresente][3] != rotte:
                                # aggiunta di una nuova soluzione
                                dictSolutions[s].append(
                                    [cost, deepcopy(myProb.x2), deepcopy(myProb.w2), deepcopy(rotte), deepcopy(padri),
                                     [], [keyLocalSearch], infeasibleK2])
                                for padreSingolo in padri:
                                    dictSolutions[s][padreSingolo][5].append(len(dictSolutions[s]) - 1)
                                padri = [len(dictSolutions[s]) - 1]

                                soluzionePrecedente = len(dictSolutions[s]) - 1
                            # rotte uguali ma con distribuzione dei pallet differenti
                            elif cost == dictSolutions[s][indiceSoluzionePresente][0] and \
                                    dictSolutions[s][indiceSoluzionePresente][3] == rotte and \
                                    dictSolutions[s][indiceSoluzionePresente][1] != x2TMP:
                                # aggiunta di una nuova soluzione
                                dictSolutions[s].append(
                                    [cost, deepcopy(myProb.x2), deepcopy(myProb.w2), deepcopy(rotte),
                                     [soluzionePrecedente], [], [keyLocalSearch], infeasibleK2])
                                padri = [len(dictSolutions[s]) - 1]

                                soluzionePrecedente = len(dictSolutions[s]) - 1
                        # non esiste una soluzione con lo stesso costo
                        else:
                            # aggiunta di una nuova soluzione
                            dictSolutions[s].append(
                                [cost, deepcopy(myProb.x2), deepcopy(myProb.w2), deepcopy(rotte), [soluzionePrecedente],
                                 [], [keyLocalSearch], infeasibleK2])
                            for padreSingolo in padri:
                                dictSolutions[s][padreSingolo][5].append(len(dictSolutions[s]) - 1)
                            padri = [len(dictSolutions[s]) - 1]

                            soluzionePrecedente = len(dictSolutions[s]) - 1

                        # eliminare le mosse tabu dagli SMD
                        for mossaTabu in tabuList[s]:
                            # print("mossaTabu deleted: ", mossaTabu)
                            if mossaTabu[0] == soluzionePrecedente:
                                # 1-0 Exchange
                                if len(mossaTabu[1]) == 5 and alternate10or11 != -1:
                                    del smd10[mossaTabu[1]]
                                # 1-1 Exchange
                                elif len(mossaTabu[1]) == 4 and alternate10or11 != 1:
                                    del smd11[mossaTabu[1]]

                        # genera le liste contenenti le tuple: (valore differenza, chiave mossa)
                        smd10ListReverse = [(v, k) for k, v in smd10.items()]
                        smd11ListReverse = [(v, k) for k, v in smd11.items()]

                        # crea la lista unica dei costi in cui verrà salvato l'heap
                        heapSMD = smd10ListReverse + smd11ListReverse

                        # crea l'heap di smd10 e di smd11
                        heapq.heapify(heapSMD)

                        oldKeyLocalSearch = keyLocalSearch

                        # aggiornamento della bestSolution finora trovata
                        # questo aggiornamento deve essere fatto ogni volta che viene effettuato il LocalSearch
                        # perché se si imposta elapsedTimeTotalMax tale da non permettere di arrivare ad un minimo
                        # locale, allora deve esere salvata la soluzione con costo minimo trovata fino ad allora.
                        # Inoltre, il vincolo 35 non deve essere violato
                        if costNew < dictSolutions[s][bestSolutionIndice][0] and vincolo35 == 1:
                            bestSolutionIndice = soluzionePrecedente
                            # print("bestSolution:\ncosto: {}, rotte: {}".format(dictSolutions[s][bestSolutionIndice][0],
                            #                                                    dictSolutions[s][bestSolutionIndice][3]))

                    # non esiste mossa migliorativa con il tipo di mossa attuale,
                    # quindi tenta l'altro tipo di mossa prima di uscire
                    elif keyLocalSearch == -1 and costNew == cost and flagTried10and11 == False:
                        flagTried10and11 = True
                        # alternare 1-0 exchange e 1-1 exchange
                        alternate10or11 = alternate10or11 * -1
                        # SMD10
                        if alternate10or11 == 1:
                            # vengono inizializzati gli SMD
                            inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s, granularityThreshold)

                        # SMD11
                        elif alternate10or11 == -1:
                            # vengono inizializzati gli SMD
                            inizializzaSMD11(smd11, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, granularityThreshold)

                        # SMD10 and SMD11
                        elif alternate10or11 == 0:
                            # vengono inizializzati gli SMD
                            inizializzaSMD10(smd10, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, s, granularityThreshold)
                            inizializzaSMD11(smd11, rotte, myProb.nik2ij, myProb.ak2ij, myProb.x2, granularityThreshold)

                        # eliminare le mosse tabu dagli SMD
                        for mossaTabu in tabuList[s]:
                            # print("mossaTabu deleted: ", mossaTabu)
                            if mossaTabu[0] == soluzionePrecedente:
                                # 1-0 Exchange
                                if len(mossaTabu[1]) == 5 and alternate10or11 != -1:
                                    del smd10[mossaTabu[1]]
                                # 1-1 Exchange
                                elif len(mossaTabu[1]) == 4 and alternate10or11 != 1:
                                    del smd11[mossaTabu[1]]

                        # crea la lista unica dei costi in cui verrà salvato l'heap
                        # non usare list(smd10.values()) direttamente perché tale lista non è modificabile e quindi non sarà un heap
                        # genera le liste contenenti le tuple: (valore differenza, chiave mossa)
                        smd10ListReverse = [(v, k) for k, v in smd10.items()]
                        smd11ListReverse = [(v, k) for k, v in smd11.items()]

                        heapSMD = smd10ListReverse + smd11ListReverse
                        # crea l'heap di smd10 e smd11
                        heapq.heapify(heapSMD)

                    # non esiste mossa migliorativa
                    # oppure è stato raggiunto il tempo massimo
                    # e sono state esplorati entrambi i tipi di mossa
                    elif keyLocalSearch == -1 and costNew == cost and flagTried10and11 == True:
                        # elapsedTimeTotal = time.time() - startTimeTotal
                        # print("elapsedTimeTotal: ", elapsedTimeTotal)
                        # se non è stata raggiunta nuovamente la soluzione iniziale (non è possibile applicare il Tabu Search)
                        # viene verificato anche se è stata raggiunta la lunghezza massima della Tabu List e il tempo massimo di esecuzione
                        if dictSolutions[s][soluzionePrecedente][4] != [-1] \
                                and itMosseTS < itMosseTSMax \
                                and elapsedTimeTotal < elapsedTimeTotalMax:
                            print("Soluzione minimo locale trovata, itMosseLS: {}, costo: {}.".format(itMosseLS, cost))
                            # print("rotte: {}".format(rotte))

                            # print("dictSolutions[{}]:".format(s))
                            # for solution in dictSolutions[s]:
                            #    print("{} -> costo: {}, rotte: {}, padri: {}, figli: {}, mosse: {}".format(dictSolutions[s].index(solution), solution[0], solution[3],
                            #                                                              solution[4], solution[5], solution[6]))

                            # applica Tabu Search
                            heapSMD, smd10, smd11, myProb.x2, myProb.w2, rotte, cost, soluzionePrecedente, padri, alternate10or11 = tabuSearch(
                                dictSolutions[s], soluzionePrecedente, tabuList[s], oldKeyLocalSearch, myProb.nik2ij,
                                myProb.ak2ij, s, alternate10or11, granularityThreshold)
                            oldKeyLocalSearch = -1
                            itMosseTS += 1
                            flagTried10and11 = False

                        # condizione di uscita
                        else:
                            print("dictSolutions[{}]:".format(s))
                            for solution in dictSolutions[s]:
                                print("{} -> costo: {}, rotte: {}, padri: {}, figli: {}, mosse: {}, infeasibleK2: {}".format(
                                    dictSolutions[s].index(solution), solution[0], solution[3], solution[4],
                                    solution[5], solution[6], solution[7]))

                            print(
                                "\n\n\nLa soluzione migliore trovata, itMosseLS: {}, itMosseTS: {}, costo: {}.".format(
                                    itMosseLS, itMosseTS, dictSolutions[s][bestSolutionIndice][0]))
                            print("{} -> costo: {}, rotte: {}".format(bestSolutionIndice,
                                                                      dictSolutions[s][bestSolutionIndice][0],
                                                                      dictSolutions[s][bestSolutionIndice][3]))

                            # se non è stata ancora assegnata un bestSolution (prima iterazione) oppure
                            # se la nuova soluzione è migliore della bestSolution trovata fino ad allora
                            if bestSolution[s] == [] or dictSolutions[s][bestSolutionIndice][0] < bestSolution[s][0]:
                                # aggiornamento della bestSolution assoluta
                                bestSolution[s] = dictSolutions[s][bestSolutionIndice]
                                # riferimento a itNSI
                                bestSolution[s].append(itNSI)

                            timeElapsedS = time.time() - start_timeS
                            print("time elapsed: {:.2f}s.".format(timeElapsedS))

                            # creazione file output
                            writeOutput(myProb.nomeFile, s, dictSolutions, bestSolutionIndice, timeElapsedS, itMosseLS,
                                        itMosseTS, itNSIMax, itMosseTSMax, alternate10or11, beta, penalty, uk2Increased)
                            writeOutputStartBest(myProb.nomeFile, s, dictSolutions, bestSolutionIndice, timeElapsedS,
                                                 itMosseLS, itMosseTS, itNSI, itNSIMax, itMosseTSMax, alternate10or11, beta, penalty, uk2Increased)

                            break
            # se non è stata trovata una soluzione iniziale
            else:
                # trovare un'altra soluzione
                print("Trova un'altra soluzione iniziale.")

    elapsedTimeTotal = time.time() - startTimeTotal
    print("Total time elapsed: {:.2f}s.".format(elapsedTimeTotal))

    # scrittura su file della bestSolution in assoluto
    writeOutputStartBestwriteOutputStartBestAssoluta(myProb.nomeFile, myProb.Sneg, bestSolution, itNSIMax, itMosseTSMax,
                                                     elapsedTimeTotal, alternate10or11, beta, penalty, uk2Increased)
