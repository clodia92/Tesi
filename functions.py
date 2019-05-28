from constraintsModelThree import *

# generate variables for Model Three
def generateVariablesModelThree(x2, w2, K2diS, GammadiS, A2, sat):
    # generate Variables x2
    # for all vehicles (second echelon)
    for k in K2diS[sat]:
        # for all customers in GammadiS
        for ga in GammadiS[sat]:
            # for all arcs in A2
            for i, j in A2:

                if i != j:
                    myx2Index = (k, ga, i, j)

                    x2[myx2Index] = 0
                    pass
                pass
            pass
        pass

    # generate Variables w2
    # for all vehicles (second echelon)
    for k in K2diS[sat]:
        # for all arcs in A2
        for i, j in A2:

            if i != j:
                myw2Index = (k, i, j)

                w2[myw2Index] = 0
                pass
            pass
        pass

    pass  # end of generateVariablesModelThree

def assignx2w2(x2, w2, trasportoPalletDiGamma, rotte):
    for k in rotte:
        for posArc, (arcI, arcJ) in enumerate(rotte[k]):
            for (gamma, pallet) in trasportoPalletDiGamma[k][posArc:]:
                x2[k, gamma, arcI, arcJ] = pallet
                # print("x2[{}, {}, {}, {}]: {}".format(k, gamma, arcI, arcJ, pallet))
                w2[k, arcI, arcJ] = 1

# verifica se la soluzione è ammissibile restituendo True o False
def verificaSoluzioneAmmissibile(sat, x2, w2, uk2, Pgac, PsGa, K2diS, A2, GammadiS, CdiS):
    vincolo29 = BuildConstr29(GammadiS, x2, K2diS, PsGa, sat)
    vincolo30 = BuildConstr30(GammadiS, x2, K2diS, Pgac, CdiS, sat)
    vincolo31 = BuildConstr31(GammadiS, K2diS, x2, sat)
    vincolo32 = BuildConstr32(K2diS, w2, GammadiS, sat)
    vincolo34 = BuildConstr34(K2diS, GammadiS, w2, sat)
    vincolo35 = BuildConstr35(K2diS, A2, x2, GammadiS, uk2, w2, sat)
    vincolo36 = BuildConstr36(K2diS, GammadiS, w2, sat)

    print("BuildConstr29", vincolo29)
    print("BuildConstr30", vincolo30)
    print("BuildConstr31", vincolo31)
    print("BuildConstr32", vincolo32)
    print("BuildConstr34", vincolo34)
    print("BuildConstr35", vincolo35)
    print("BuildConstr36???", vincolo36)

    return (vincolo29 and vincolo30 and vincolo31 and vincolo32 and vincolo34 and vincolo35 and vincolo36)

def inizializzaSMD10(smd10, rotte, nik2ij, ak2ij, x2, s):
    # dizionario dei veicoli per ogni cliente
    veicoliDiCliente = {}
    # lista di tuple: (cliente, veicolo)
    Gmm = []

    for k in rotte:
        for c in rotte[k]:
            Gmm += [(c[1], k)]
            if c[1] in veicoliDiCliente:
                veicoliDiCliente[c[1]] += [k]
            else:
                veicoliDiCliente[c[1]] = [k]

    for v1 in rotte:
        # lista dei nodi del veicolo k (satellite + clienti)
        listNodes = [s]+[c2 for c1,c2 in rotte[v1]]
        for n1 in listNodes:
            for n2, v2 in Gmm:
                # v1 = veicolo di destinazione di n1
                # v2 = veicolo di partenza di n2
                # n1 = nodo dietro al quale viene spostato n2
                # n2 = nodo da spostare dietro n1

                precN1, succN1 = trovaPrecSucc(rotte[v1], n1)
                precN2, succN2 = trovaPrecSucc(rotte[v2], n2)


                # TMP: tengo anche l'attuale posizione tra le mosse (dovrebbero avere variazione costo=0)
                # perche' altrimenti tale chiave sarebbe da eliminare.
                # Includendo la seguente if risultano due mosse in meno
                # perche' per esempio in sat=2 la mossa 8, 4, 7 risulta essere un arco dell'attuale soluzione.
                # Conviene tenere le mosse dell'attuale soluzione e impostare costo=0???
                if not(v1==v2 and (n1, n2) in rotte[v1]):
                    #     print("v1: {}, n1: {}, n2: {}".format(v1, n1, n2))

                    # un veicolo non puo' essere spostato dietro se stesso
                    if n2!=n1:
                        # viene creata la chiave
                        smd10[v1, v2, n1, n2] = 0

                        # SONO DA MODIFICARE I COSTI DI ENTRAMBE LE ROTTE CHE VENGONO MODIFICATE

                        # modifica dei costi di v1
                        # nik2ij
                        if succN1==-1:
                            smd10[v1, v2, n1, n2] += nik2ij[v1, n1, n2]
                            for arc1 in rotte[v1]:
                                # scorrere fino all'arco interessato
                                if arc1 == (n1, succN1):
                                    break
                                smd10[v1, v2, n1, n2] += ak2ij[v1, arc1[0], arc1[1]] * x2[v1, n2, arc1[0], arc1[1]]

                        else:
                            smd10[v1, v2, n1, n2] -= nik2ij[v1, n1, succN1]
                            smd10[v1, v2, n1, n2] += nik2ij[v1, n2, succN1]
                            smd10[v1, v2, n1, n2] += nik2ij[v1, n1, n2]

                            # ak2ij
                            smd10[v1, v2, n1, n2] -= ak2ij[v1, n1, succN1]*x2[v1, succN1, n1, succN1]
                            smd10[v1, v2, n1, n2] += ak2ij[v1, n1, n2]*(x2[v1, n2, precN2, n2]+x2[v1, succN1, n1, succN1])
                            smd10[v1, v2, n1, n2] += ak2ij[v1, n2, succN1]*x2[v1, succN1, n1, succN1]
                            for arc1 in rotte[v1]:
                                # scorrere fino all'arco interessato
                                if arc1 == (n1, succN1):
                                    break

                                smd10[v1, v2, n1, n2] += ak2ij[v1, arc1[0], arc1[1]]*x2[v1, n2, arc1[0], arc1[1]]

                        # modifica dei costi di v2
                        # nik2ij
                        if succN2==-1:
                            smd10[v1, v2, n1, n2] -= nik2ij[v2, precN2, n2]
                            for arc2 in rotte[v2]:
                                # scorrere fino all'arco interessato
                                if arc2 == (precN2, n2):
                                    break

                                smd10[v1, v2, n1, n2] -= ak2ij[v2, arc2[0], arc2[1]] * x2[v2, n2, arc2[0], arc2[1]]

                        else:
                            smd10[v1, v2, n1, n2] -= nik2ij[v2, precN2, n2]
                            smd10[v1, v2, n1, n2] -= nik2ij[v2, n2, succN2]
                            smd10[v1, v2, n1, n2] += nik2ij[v2, precN2, succN2]

                            # ak2ij
                            smd10[v1, v2, n1, n2] += ak2ij[v2, precN2, succN2]*x2[v2, succN2, n2, succN2]
                            for arc2 in rotte[v2]:
                                smd10[v1, v2, n1, n2] -= ak2ij[v2, arc2[0], arc2[1]]*x2[v2, n2, arc2[0], arc2[1]]

                                # scorrere fino all'arco interessato
                                if arc2 == (n2, succN2):
                                    break

                    # else:
                    #     if len(veicoliDiCliente[n2])>1:
                    #         other=list(veicoliDiCliente[n2])
                    #         other.remove(v1)
                    #         for k2 in other:
                    #             if k2!=v1:
                    #                 print("doppio")
                    #                 smd10[v1, n1, n2] = None
                    #                 x += 1

    # print("smd10: {}\n# elementi: {}".format(smd10, len(smd10)))

def trovaPrecSucc(rotta, nodo):
    prec = [item[0] for item in rotta if item[1]==nodo]

    succ = [item[1] for item in rotta if item[0]==nodo]

    if len(prec) == 0 and len(succ) == 0:
        return -1, -1
    else:
        if len(prec) == 0:
            return -1, succ[0]
        else:
            if len(succ) == 0:
                return prec[0], -1
            else:
                return prec[0], succ[0]

def findSolutionBase(s, x2, w2, uk2, Pgac, PsGa, K2diS, A2, GammadiS, CdiS):
    print("START findSolutionBase()")

    x2TMP = x2.copy()
    w2TMP = w2.copy()

    # x2[(k, gamma, i, j)]
    # w2[(k, i, j)]
    # - uk2
    # Pgac
    # - PsGa
    # - K2diS[s]
    # - A2
    # - GammadiS
    # CdiS

    # dizionatio che contiene i pallet richiesti dai clienti di s
    PGa = {}

    # lista dei veicoli assegnati ad s nel Prob2
    K2 = []

    # pallet trasportati da ogni k2 che serve s
    palletTrasportatiDiK2 = []

    # numero massimo di pallet trasportabili dal veicolo k che serve s
    uk2diS = {}

    # lista dei clienti di s
    Gamma = GammadiS[s]

    # dizionario delle rotte per ogni veicolo con relativi pallet: trasportoPalletDiGamma [ k ] = ( gamma1, pallet1) , ( gamma2, pallet2) , ( gamma3, pallet3) ....
    trasportoPalletDiGamma = {}
    # dizionario della lista ordinata di archi per ogni veicolo: rotte[k]: [(s,i), (i,j), (j,...)]
    rotte = {}

    # pallet totali che partono da s
    palletDaConsegnare = 0

    for v in K2diS[s]:
        # print("uk2[{}]: {}".format(v, uk2[v]))
        uk2diS[v] = uk2[v]

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

    palletTrasportatiDiK2 = [0] * len(K2)

    while (palletDaConsegnare > 0):
        # cicla finchè non trova un veicolo con ancora spazio
        while (palletTrasportatiDiK2[posV] >= uk2diS[K2[posV]]):
            posV = (posV + 1) % len(K2)

        # se il cliente deve ancora ricevere dei pallet
        if (PGa[Gamma[posG]] > 0):
            # consegna a gamma
            if (PGa[Gamma[posG]] <= (uk2diS[K2[posV]] - palletTrasportatiDiK2[posV])):
                # aggiorno le rotte
                if K2[posV] in trasportoPalletDiGamma:
                    trasportoPalletDiGamma[K2[posV]] += [(Gamma[posG], PGa[Gamma[posG]])]

                    # aggiorno rotte[k]
                    rotte[K2[posV]] += [(rotte[K2[posV]][-1][1], Gamma[posG])]

                else:
                    trasportoPalletDiGamma[K2[posV]] = [(Gamma[posG], PGa[Gamma[posG]])]

                    # aggiorno rotte[k]
                    rotte[K2[posV]] = [(s, Gamma[posG])]

                palletDaConsegnare -= PGa[Gamma[posG]]
                palletTrasportatiDiK2[posV] += PGa[Gamma[posG]]
                PGa[Gamma[posG]] = 0
            else:
                # aggiorno le rotte
                if K2[posV] in trasportoPalletDiGamma:
                    trasportoPalletDiGamma[K2[posV]] += [
                        (Gamma[posG], (uk2diS[K2[posV]] - palletTrasportatiDiK2[posV]))]

                    # aggiorno rotte[k]
                    rotte[K2[posV]] += [(rotte[K2[posV]][-1][1], Gamma[posG])]
                else:
                    trasportoPalletDiGamma[K2[posV]] = [
                        (Gamma[posG], (uk2diS[K2[posV]] - palletTrasportatiDiK2[posV]))]

                    # aggiorno rotte[k]
                    rotte[K2[posV]] = [(s, Gamma[posG])]

                palletDaConsegnare -= uk2diS[K2[posV]] - palletTrasportatiDiK2[posV]
                PGa[Gamma[posG]] -= uk2diS[K2[posV]] - palletTrasportatiDiK2[posV]
                palletTrasportatiDiK2[posV] += PGa[Gamma[posG]]  # full

            # passo al veicolo sucessivo
            posV = (posV + 1) % len(K2)

        # passo al cliente sucessivo
        posG = (posG + 1) % len(Gamma)

    # aggiornare x2 e w2 in base a rotte[k]
    arcoI = s

    # for k in K2:
    #     for (g, p) in trasportoPalletDiGamma[k]:
    #         x2TMP[(k, g, arcoI, g)] = p
    #         w2TMP[(k, arcoI, g)] = 1
    #
    #         arcoI = g

    print("trasportoPalletDiGamma: {}".format(trasportoPalletDiGamma))
    print("rotte : {}".format(rotte))

    assignx2w2(x2TMP, w2TMP, trasportoPalletDiGamma, rotte)

    # verifica dell'ammissibilità della soluzione
    if (verificaSoluzioneAmmissibile(s, x2TMP, w2TMP, uk2, Pgac, PsGa, K2diS, A2, GammadiS, CdiS)):
        # soluzione ammissibile trovata
        x2 = x2TMP.copy()
        w2 = w2TMP.copy()

        return True, x2, w2, rotte
    else:
        # soluzione non ammissibile
        return False, x2, w2, rotte

def localSearch(heapSMD10, smd10, x2, w2):
    print("START localSearch()")
    itMAX=10
    it=0

    while heapSMD10[0] < 0 and it<itMAX:
        it += 1

        # salva la chiave del valore minore
        minCostKey = list(smd10.keys())[list(smd10.values()).index(heapSMD10[0])]
        print("SMD10 con differenza di costo migliore: {}, chiave: {}".format(smd10[minCostKey], minCostKey))

        v1 = minCostKey[0]
        v2 = minCostKey[1]
        n1 = minCostKey[2]
        n2 = minCostKey[3]

        x2TMP = x2.copy()
        w2TMP = w2.copy()

        # assegnare x2TMP e w2TMP
        # verificare ammissibilità
        # if True:
            # assegnare x2 e w2
            # pop
            # solutions.append(x2, w2, cost)
        # else:
            # pop