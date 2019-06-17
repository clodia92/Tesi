from constraintsModelThree import *
import heapq


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
                w2[k, arcI, arcJ] = 1


# verifica se la soluzione è ammissibile restituendo True o False
def verificaSoluzioneAmmissibile(sat, x2, w2, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
    vincolo29 = BuildConstr29(Gamma, x2, K2, PsGa, sat)
    vincolo30 = BuildConstr30(Gamma, x2, K2, Pgac, CdiS, sat)
    vincolo31 = BuildConstr31(Gamma, K2, x2, sat)
    vincolo32 = BuildConstr32(K2, w2, Gamma, sat)
    vincolo34 = BuildConstr34(K2, Gamma, w2, sat)
    vincolo35 = BuildConstr35(K2, A2, x2, Gamma, uk2, w2, sat)
    vincolo36 = BuildConstr36(K2, Gamma, w2, sat)

    if vincolo29 and vincolo30 and vincolo31 and vincolo32 and vincolo34 and vincolo35 and vincolo36:
        return True
    else:
        return False


def inizializzaSMD10(smd10, rotte, nik2ij, ak2ij, x2, s):
    # lista di tuple: [(cliente, veicolo), ...]
    clienteVeicolo = getClienteVeicolo(rotte)

    for v1 in rotte:
        # lista dei nodi del veicolo k (satellite + clienti)
        listNodes = [s] + [c2 for c1, c2 in rotte[v1]]
        for n1 in listNodes:
            for n2, v2 in clienteVeicolo:
                # v1 = veicolo di destinazione di n1
                # v2 = veicolo di partenza di n2
                # n1 = nodo dietro al quale viene spostato n2
                # n2 = nodo da spostare dietro n1

                # lista dei nodi precedenti e dei nodi successivi
                precN1, succN1 = trovaPrecSuccList(rotte[v1], n1)
                precN2, succN2 = trovaPrecSuccList(rotte[v2], n2)

                for numeroPallet in range(1, x2[v2, n2, precN2[0], n2]):
                    # se viene trattato un cliente splittato sulle rotte v1 e v2
                    #
                    if (n2 in [c for c, k in clienteVeicolo if k == v1]) and v1 != v2:
                        # viene creata la chiave
                        smd10[v1, v2, n1, n2, numeroPallet] = 0
                        # calcolo dei costi
                        # v1
                        # nik2ij
                        # non viene modificato

                        # ak2ij
                        for arc1 in rotte[v1]:
                            #
                            if arc1[0] == n2:
                                break
                            smd10[v1, v2, n1, n2, numeroPallet] += (numeroPallet * ak2ij[v1, arc1[0], arc1[1]])

                        # v2
                        # nik2ij -> non essendo eliminato l'arco in v2, non vi sono ripercussioni sull'smd per nik2ij

                        # ak2ij modifica costi sui precedenti di n2
                        for arc2 in rotte[v2]:
                            # n2,succN2[0]
                            if arc2[0] == n2:
                                break

                            # prima di precN2[0]
                            smd10[v1, v2, n1, n2, numeroPallet] -= (numeroPallet * ak2ij[v2, arc2[0], arc2[1]])
                    # l'arco non deve esistere nella soluzione attuale
                    # un veicolo non puo' essere spostato dietro se stesso
                    elif (v1 != v2) and (n2 != n1):
                        # viene creata la chiave
                        smd10[v1, v2, n1, n2, numeroPallet] = 0

                        # calcolo dei costi
                        # v1
                        # nik2ij
                        # se n1 non è l'ultimo nodo della sua rotta
                        if succN1[0] != -1:
                            # aggiunta del nuovo arco out n2
                            smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n2, succN1[0]]
                            # rimozione del vecchio arco da sostituire con n2
                            smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n1, succN1[0]]
                        # aggiunta del nuovo arco in n2
                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n1, n2]

                        # ak2ij
                        # prima di n1
                        flag = 0
                        if succN1[0] == -1:
                            smd10[v1, v2, n1, n2, numeroPallet] += (numeroPallet * ak2ij[v1, n1, n2])
                        for arc1 in rotte[v1]:
                            # n1, n2
                            if arc1[0] == n1:
                                flag = 1
                            # dopo n2 -> non vengono modificati
                            if arc1[0] == succN1[0]:
                                break

                            # prima di n1
                            if flag == 0:
                                smd10[v1, v2, n1, n2, numeroPallet] += (numeroPallet * ak2ij[v1, arc1[0], arc1[1]])
                            # n1, n2
                            if flag == 1:
                                smd10[v1, v2, n1, n2, numeroPallet] += (numeroPallet * ak2ij[v1, n1, n2])
                                if succN1[0] != -1:
                                    for gamma in succN1:
                                        smd10[v1, v2, n1, n2, numeroPallet] += (x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, n2])
                                        smd10[v1, v2, n1, n2, numeroPallet] += (
                                                    x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n2, succN1[0]])
                                        smd10[v1, v2, n1, n2, numeroPallet] -= (
                                                    x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, succN1[0]])
                            # dopo n2 -> non vengono modificati

                        # v2
                        # nik2ij
                        # non viene modificato

                        # ak2ij
                        for arc2 in rotte[v2]:
                            # n2, succN2[0]
                            if arc2[0] == n2:
                                break

                            smd10[v1, v2, n1, n2, numeroPallet] -= (numeroPallet * ak2ij[v2, arc2[0], arc2[1]])
                            # dopo N2 -> non vengono modificati

                ######### Senza split
                numeroPallet = x2[v2, n2, precN2[0], n2]

                # se viene trattato un cliente splittato sulle rotte v1 e v2
                # Spostamento di tutti i pallet verso un altro veicolo
                if n2 in [c for c, k in clienteVeicolo if k == v1] and v1 != v2:
                    # viene creata la chiave
                    smd10[v1, v2, n1, n2, numeroPallet] = 0
                    # calcolo dei costi
                    # v1
                    # nik2ij
                    # non viene modificato

                    # ak2ij
                    for arc1 in rotte[v1]:
                        #
                        if arc1[0] == n2:
                            break
                        smd10[v1, v2, n1, n2, numeroPallet] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc1[0], arc1[1]])

                    # v2
                    # rimozione del vecchio arco in n2
                    smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v2, precN2[0], n2]
                    # prima di precN2[0]
                    flag = 0
                    for arc2 in rotte[v2]:
                        # precN2[0], n2
                        if arc2[0] == precN2[0]:
                            flag = 1
                        # n2, succN2[0]
                        if arc2[0] == n2:
                            flag = 2
                        # dopo succN2[0] -> non vengono modificati
                        if arc2[0] == succN2[0]:
                            break

                        # prima di precN2[0]
                        if flag == 0:
                            smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc2[0], arc2[1]])
                        # precN2[0], n2
                        if flag == 1:
                            smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v2, n2, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                            if succN2[0] != -1:
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] += (
                                            x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], succN2[0]])
                                    smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                        # n2, succN2[0]
                        if flag == 2:
                            # rimozione del vecchio arco out n2
                            smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v2, n2, succN2[0]]
                            # aggiunta del nuovo arco in sostituzione di n2
                            smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v2, precN2[0], succN2[0]]
                            for gamma in succN2:
                                smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v2, gamma, n2, succN2[0]] * ak2ij[v2, n2, succN2[0]])
                        # dopo succN2[0] -> non vengono modificati
                    pass

                # se n1 e n2 sono sullo stesso veicolo
                elif v1 == v2 and ((n1, n2) not in rotte[v1]):
                    # se esiste l'arco (n2, n1)
                    if (n2, n1) in rotte[v1]:
                        smd10[v1, v2, n1, n2, numeroPallet] = 0

                        # nik2ij
                        smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, precN2[0], n2]
                        smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n2, n1]

                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, precN2[0], n1]
                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n1, n2]

                        if succN1[0] != -1:
                            smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n1, succN1[0]]
                            smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n2, succN1[0]]

                        # ak2ij
                        flag = 0
                        for arc1 in rotte[v1]:
                            if arc1[0] == precN2[0]:
                                flag = 1
                            if arc1[0] == n2:
                                flag = 2
                            if arc1[0] == n1:
                                flag = 3

                            if flag == 1:
                                for gamma in [n2] + succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, precN2[0], n2] * ak2ij[
                                        v1, precN2[0], n2]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, precN2[0], n2] * ak2ij[
                                        v1, precN2[0], n1]
                            if flag == 2:
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n2, n1] * ak2ij[v1, n2, n1]
                            if flag == 3:
                                for gamma in succN1:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                        v1, n1, succN1[0]]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                        v1, n1, n2]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                        v1, n2, succN1[0]]
                                break
                        smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, n2, precN2[0], n2] * ak2ij[v1, n1, n2]
                    # se n2 in succN1
                    elif n2 in succN1 and ((n1, n2) not in rotte[v1]):
                        # viene creata la chiave
                        smd10[v1, v2, n1, n2, numeroPallet] = 0

                        # nik2ij
                        smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n1, succN1[0]]
                        smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, precN2[0], n2]

                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n1, n2]
                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n2, succN1[0]]

                        # ak2ij
                        # prima di n1
                        flag=0
                        for arc1 in rotte[v1]:
                            # (n1, succN1)
                            if arc1[0]==n1:
                                flag=1
                            # (succN1, ...)
                            if arc1[0]==succN1[0]:
                                flag=2
                            # (n2, succN2)
                            if arc1[0]==n2:
                                flag=3
                            # (succN2, ...)
                            if arc1[0]==succN2[0]:
                                break

                            # (n1, succN1)
                            if flag==1:
                                for gamma in succN1:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, succN1[0]]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, n2]
                                    if gamma!=n2:
                                        smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n2, succN1[0]]
                            # (succN1, ...)
                            if flag==2:
                                smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, n2, precN2[0], n2] * ak2ij[v1, arc1[0], arc1[1]]
                            # (n2, succN2)
                            if flag==3:
                                smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, precN2[0], n2]
                                smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n2, succN2[0]]
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n2, succN2[0]] * ak2ij[v1, n2, succN2[0]]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n2, succN2[0]] * ak2ij[v1, precN2[0], succN2[0]]

                    # se n1 in succN2 ma non (n2, n1)
                    elif n1 in succN2 and ((n2, n1) not in rotte[v1]):
                        # viene creata la chiave
                        smd10[v1, v2, n1, n2, numeroPallet] = 0

                        # nik2ij
                        smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, precN2[0], n2]
                        smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n2, succN2[0]]

                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, precN2[0], succN2[0]]
                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n1, n2]

                        smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, n2, precN2[0], n2] * ak2ij[v1, n1, n2]

                        # prima di n2
                        flag=0
                        for arc1 in rotte[v1]:
                            # (precN2, n2)
                            if arc1[1] == n2:
                                flag=1
                            # (n2, succN2)
                            if arc1[0] == n2:
                                flag=2
                            # (succN2, ...)
                            if arc1[0] == succN2[0]:
                                flag=3
                            # (n1, succN1)
                            if arc1[0] == n1:
                                flag=4
                            # (succN1, ...)
                            if arc1[0] == succN1[0]:
                                break

                            # (precN2, n2)
                            if flag==1:
                                for gamma in [n2]+succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, precN2[0], n2] * ak2ij[v1, precN2[0], n2]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, precN2[0], n2] * ak2ij[v1, precN2[0], succN2[0]]
                            # (n2, succN2)
                            if flag==2:
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n2, succN2[0]] * ak2ij[v1, n2, succN2[0]]
                            # (succN2, ...)
                            if flag==3:
                                smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, n2, precN2[0], n2] * ak2ij[v1, arc1[0], arc1[1]]
                            # (n1, succN1)
                            if flag==4:
                                smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n1, succN1[0]]
                                smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n2, succN1[0]]
                                for gamma in succN1:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, succN1[0]]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, n2]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n2, succN1[0]]

                # l'arco non deve esistere nella soluzione attuale
                # un veicolo non puo' essere spostato dietro se stesso
                elif v1 != v2 and n2 != n1:
                    # viene creata la chiave
                    smd10[v1, v2, n1, n2, numeroPallet] = 0

                    # calcolo dei costi
                    # v1
                    # nik2ij
                    # se n1 non è l'ultimo nodo della sua rotta
                    if succN1[0] != -1:
                        # aggiunta del nuovo arco out n2
                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n2, succN1[0]]
                        # rimozione del vecchio arco da sostituire con n2
                        smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n1, succN1[0]]
                    # aggiunta del nuovo arco in n2
                    smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n1, n2]

                    # ak2ij
                    # prima di n1
                    flag = 0
                    if succN1[0] == -1:
                        smd10[v1, v2, n1, n2, numeroPallet] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, n1, n2])
                    for arc1 in rotte[v1]:
                        # n1, n2
                        if arc1[0] == n1:
                            flag = 1
                        # dopo n2 -> non vengono modificati
                        if arc1[0] == succN1[0]:
                            # flag=2
                            break

                        # prima di n1
                        if flag == 0:
                            smd10[v1, v2, n1, n2, numeroPallet] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc1[0], arc1[1]])
                        # n1, n2
                        if flag == 1:
                            smd10[v1, v2, n1, n2, numeroPallet] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, n1, n2])
                            if succN1[0] != -1:
                                for gamma in succN1:
                                    smd10[v1, v2, n1, n2, numeroPallet] += (x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, n2])
                                    smd10[v1, v2, n1, n2, numeroPallet] += (x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n2, succN1[0]])
                                    smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, succN1[0]])
                        # dopo n2 -> non vengono modificati

                    # v2
                    # nik2ij
                    # se n2 non è l'ultimo nodo della sua rotta
                    if succN2[0] != -1:
                        # rimozione del vecchio arco out n2
                        smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v2, n2, succN2[0]]
                        # aggiunta del nuovo arco in sostituzione di n2
                        smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v2, precN2[0], succN2[0]]
                    # rimozione del vecchio arco in n2
                    smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v2, precN2[0], n2]

                    # ak2ijsuccN2
                    # prima di precN2[0]
                    flag = 0
                    for arc2 in rotte[v2]:
                        # precN2[0], n2
                        if arc2[0] == precN2[0]:
                            flag = 1
                        # n2, succN2[0]
                        if arc2[0] == n2:
                            flag = 2
                        # dopo succN2[0] -> non vengono modificati
                        if arc2[0] == succN2[0]:
                            break

                        # prima di precN2[0]
                        if flag == 0:
                            smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc2[0], arc2[1]])
                        # precN2[0], n2
                        if flag == 1:
                            smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v2, n2, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                            if succN2[0] != -1:
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] += (x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], succN2[0]])
                                    smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                        # n2, succN2[0]
                        if flag == 2:
                            for gamma in succN2:
                                smd10[v1, v2, n1, n2, numeroPallet] -= (x2[v2, gamma, n2, succN2[0]] * ak2ij[v2, n2, succN2[0]])
                        # dopo succN2[0] -> non vengono modificati


def inizializzaSMD11(smd11, rotte, nik2ij, ak2ij, x2):
    # lista di tuple: (cliente, veicolo)
    clienteVeicolo = getClienteVeicolo(rotte)

    # index2 viene utilizzato per scorrere la seconda volta clienteVeicolo solo dall'attuale coppia (v, n) in poi
    # in modo da evitare duplicati: smd11[7, 8, 3, 4] == smd11[8, 7, 4, 3]
    index2 = 0

    for n1, v1 in clienteVeicolo:
        index2 += 1

        for n2, v2 in clienteVeicolo[index2:]:
            # lista dei nodi precedenti e dei nodi successivi
            precN1, succN1 = trovaPrecSuccList(rotte[v1], n1)
            precN2, succN2 = trovaPrecSuccList(rotte[v2], n2)

            # viene creata la chiave
            smd11[v1, v2, n1, n2] = 0

            # se (n1, n2) è un arco già presente nella rotta
            if v1 == v2 and (n1, n2) in rotte[v1]:
                # nik2ij
                smd11[v1, v2, n1, n2] += nik2ij[v1, precN1[0], n2]
                smd11[v1, v2, n1, n2] += nik2ij[v1, n2, n1]

                smd11[v1, v2, n1, n2] -= nik2ij[v1, precN1[0], n1]
                smd11[v1, v2, n1, n2] -= nik2ij[v1, n1, n2]

                # ak2ij
                for gamma in [n1] + succN1:
                    smd11[v1, v2, n1, n2] += x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n2]
                    smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n1]

                if succN2[0] != -1:
                    # nik2ij
                    smd11[v1, v2, n1, n2] += nik2ij[v1, n1, succN2[0]]
                    smd11[v1, v2, n1, n2] += nik2ij[v1, n2, succN2[0]]

                    # ak2ij
                    for gamma in succN2:
                        smd11[v1, v2, n1, n2] += x2[v1, gamma, n1, n2] * ak2ij[v1, n2, n1]
                        smd11[v1, v2, n1, n2] -= x2[v1, gamma, n1, n2] * ak2ij[v1, n1, n2]

                        smd11[v1, v2, n1, n2] += x2[v1, gamma, n2, succN2[0]] * ak2ij[v1, n1, succN2[0]]
                        smd11[v1, v2, n1, n2] -= x2[v1, gamma, n2, succN2[0]] * ak2ij[v1, n2, succN2[0]]

                # ak2ij
                smd11[v1, v2, n1, n2] += x2[v1, n1, precN1[0], n1] * ak2ij[v1, n2, n1]
                smd11[v1, v2, n1, n2] -= x2[v1, n2, precN2[0], n2] * ak2ij[v1, n1, n2]

            ### PERMETTERE MOSSA [7, 8, 7, 7]?
            ### PER ORA NO
            elif n1!=n2:
                # v1
                # v1 se n2 in v1
                # DA VERIFICARE
                if n2 in [c[1] for c in rotte[v1]]:
                    pass
                    # in v1: n2 in precN1
                    if n2 in precN1:
                        smd11[v1, v2, n1, n2] -= nik2ij[v1, precN1[0], n1]

                        flag1=0
                        flag2=0
                        for arc1 in rotte[v1]:
                            if arc1[0] == n1:
                                flag1=1
                            if arc1[0] == n2:
                                flag2=1
                            if arc1[0] == succN1[0]:
                                break

                            if flag1==0:
                                smd11[v1, v2, n1, n2] -= x2[v1, n1, precN1[0], n1] * ak2ij[v1, arc1[0], arc1[1]]
                            if flag1==1:
                                smd11[v1, v2, n1, n2] -= nik2ij[v1, n1, succN1[0]]
                                smd11[v1, v2, n1, n2] += nik2ij[v1, precN1[0], succN1[0]]
                                for gamma in succN1:
                                    smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n1]
                                    smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN1[0], n1] * ak2ij[v1, n1, succN1[0]]
                                    smd11[v1, v2, n1, n2] += x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], succN1[0]]
                            if flag2==0:
                                smd11[v1, v2, n1, n2] += x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc1[0], arc1[1]]
                    # in v1: n2 in succN1
                    elif n2 in succN1:
                        smd11[v1, v2, n1, n2] -= nik2ij[v1, precN1[0], n1]
                        smd11[v1, v2, n1, n2] -= nik2ij[v1, n1, succN1[0]]
                        smd11[v1, v2, n1, n2] += nik2ij[v1, precN1[0], succN1[0]]

                        for gamma in succN1:
                            smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n1]
                            smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN1[0], n1] * ak2ij[v1, n1, succN1[0]]
                            smd11[v1, v2, n1, n2] += x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], succN1[0]]

                        smd11[v1, v2, n1, n2] += x2[v2, n2, precN2[0], n2] * ak2ij[v1, precN1[0], succN1[0]]

                        flag1=0
                        flag2=0
                        for arc1 in rotte[v1]:
                            if arc1[0]==n1:
                                flag1=1
                            if arc1[0]==precN1[0]:
                                flag2=1
                            if arc1[0]==succN1[0] and arc1[0]!=n2:
                                flag2=0
                            if arc1[0]==n2:
                                break

                            if flag1==0:
                                smd11[v1, v2, n1, n2] -= x2[v1, n1, precN1[0], n1] * ak2ij[v1, arc1[0], arc1[1]]
                            if flag2==0:
                                smd11[v1, v2, n1, n2] += x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc1[0], arc1[1]]

                # DA VERIFICARE
                else:
                    # v1 se n1 ha successori
                    if succN1[0] != -1:
                        # nik2ij
                        # aggiungere costo arco (n2, succN1)
                        smd11[v1, v2, n1, n2] += nik2ij[v1, n2, succN1[0]]
                        # eliminare costo arco (n1, succN1)
                        smd11[v1, v2, n1, n2] -= nik2ij[v1, n1, succN1[0]]
                        # ak2ij
                        for gamma in succN1:
                            # aggiungere costi pallet dei succN1 in (precN1, n2) e (n2, succN1)
                            smd11[v1, v2, n1, n2] += (x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n2])
                            smd11[v1, v2, n1, n2] += (x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n2, succN1[0]])
                            # eliminare costi pallet dei succN1 da (precN1, n1) e (n1, succN1)
                            smd11[v1, v2, n1, n2] -= (x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n1])
                            smd11[v1, v2, n1, n2] -= (x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, succN1[0]])

                    # v1 sempre
                    # nik2ij
                    # aggiungere costo arco (precN1, n2)
                    smd11[v1, v2, n1, n2] += nik2ij[v1, precN1[0], n2]
                    # eliminare costo arco (precN1, n1)
                    smd11[v1, v2, n1, n2] -= nik2ij[v1, precN1[0], n1]
                    # ak2ij
                    for arc1 in rotte[v1]:
                        # (n1, succN1[0])
                        if arc1[1] == n1:
                            break
                        # aggiungere costo pallet n2 ai precN1
                        smd11[v1, v2, n1, n2] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc1[0], arc1[1]])
                        # eliminare costo pallet n1 dai precN1
                        smd11[v1, v2, n1, n2] -= (x2[v1, n1, precN1[0], n1] * ak2ij[v1, arc1[0], arc1[1]])
                    smd11[v1, v2, n1, n2] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, precN1[0], n2])
                    smd11[v1, v2, n1, n2] -= (x2[v1, n1, precN1[0], n1] * ak2ij[v1, precN1[0], n1])

                # v2
                # v2 se n1 in v2
                # DA VERIFICARE
                if n1 in [c[1] for c in rotte[v2]]:
                    pass
                    # in v2: n1 in precN2
                    if n1 in precN2:
                        smd11[v1, v2, n1, n2] -= nik2ij[v2, precN2[0], n2]

                        flag1=0
                        flag2=0
                        for arc2 in rotte[v2]:
                            if arc2[0] == n2:
                                flag1=1
                            if arc2[0] == n1:
                                flag2=1
                            if arc2[0] == succN2[0]:
                                break

                            if flag1==0:
                                smd11[v1, v2, n1, n2] -= x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc2[0], arc2[1]]
                            if flag1==1:
                                smd11[v1, v2, n1, n2] -= nik2ij[v2, n2, succN2[0]]
                                smd11[v1, v2, n1, n2] += nik2ij[v2, precN2[0], succN2[0]]
                                for gamma in succN1:
                                    smd11[v1, v2, n1, n2] -= x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n2]
                                    smd11[v1, v2, n1, n2] -= x2[v2, gamma, precN2[0], n2] * ak2ij[v2, n2, succN2[0]]
                                    smd11[v1, v2, n1, n2] += x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], succN2[0]]
                            if flag2==0:
                                smd11[v1, v2, n1, n2] += x2[v1, n1, precN1[0], n1] * ak2ij[v2, arc2[0], arc2[1]]
                    # in v2: n1 in succN2

                # DA VERIFICARE
                else:

                    # v2 se n2 ha successori
                    if succN2[0] != -1:
                        # nik2ij
                        # aggiungere costo arco (n1, succN2)
                        smd11[v1, v2, n1, n2] += nik2ij[v2, n1, succN2[0]]
                        # eliminare costo arco (n2, succN2)
                        smd11[v1, v2, n1, n2] -= nik2ij[v2, n2, succN2[0]]
                        # ak2ij
                        for gamma in succN2:
                            # aggiungere costi pallet dei succN2 in (precN2, n1) e (n1, succN2)
                            smd11[v1, v2, n1, n2] += (x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n1])
                            smd11[v1, v2, n1, n2] += (x2[v2, gamma, n2, succN2[0]] * ak2ij[v2, n1, succN2[0]])
                            # eliminare costi pallet dei succN2 da (precN2, n2) e (n2, succN2)
                            smd11[v1, v2, n1, n2] -= (x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                            smd11[v1, v2, n1, n2] -= (x2[v2, gamma, n2, succN2[0]] * ak2ij[v2, n2, succN2[0]])

                    # v2 sempre
                    # nik2ij
                    # aggiungere costo arco (precN2, n1)
                    smd11[v1, v2, n1, n2] += nik2ij[v2, precN2[0], n1]
                    # eliminare costo arco (precN2, n2)
                    smd11[v1, v2, n1, n2] -= nik2ij[v2, precN2[0], n2]
                    # ak2ij
                    for arc2 in rotte[v2]:
                        # (n2, succN2[0])
                        if arc2[1] == n2:
                            break
                        # aggiungere costo pallet n1 ai precN2
                        smd11[v1, v2, n1, n2] += (x2[v1, n1, precN1[0], n1] * ak2ij[v2, arc2[0], arc2[1]])
                        # eliminare costo pallet n2 dai precN2
                        smd11[v1, v2, n1, n2] -= (x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc2[0], arc2[1]])
                    smd11[v1, v2, n1, n2] += (x2[v1, n1, precN1[0], n1] * ak2ij[v2, precN2[0], n1])
                    smd11[v1, v2, n1, n2] -= (x2[v2, n2, precN2[0], n2] * ak2ij[v2, precN2[0], n2])


# restituisce una lista di tuple [(cliente, veicolo), ...]
def getClienteVeicolo(rotte):
    veicoliDiCliente = {}
    clienteVeicolo = []
    for k in rotte:
        for c in rotte[k]:
            clienteVeicolo += [(c[1], k)]
            if c[1] in veicoliDiCliente:
                veicoliDiCliente[c[1]] += [k]
            else:
                veicoliDiCliente[c[1]] = [k]

    return clienteVeicolo


# restituisce due liste dei clienti precedenti e successivi al nodo
def trovaPrecSuccList(rotta, nodo):
    precList = []
    succList = []

    for item in rotta:
        if item[0] == nodo:
            break
        precList = [item[0]] + precList

    flag = False
    for item in rotta:
        if item[0] == nodo:
            flag = True
        if flag:
            succList.append(item[1])

    if len(precList) == 0 and len(succList) == 0:
        return [-1], [-1]
    else:
        if len(precList) == 0:
            return [-1], succList
        else:
            if len(succList) == 0:
                return precList, [-1]
            else:
                return precList, succList


def findSolutionBase(s, x2, w2, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
    print("START findSolutionBase()")

    x2TMP = x2.copy()
    w2TMP = w2.copy()

    # dizionario che contiene i pallet richiesti dai clienti di s
    PGa = {}

    # numero massimo di pallet trasportabili dal veicolo k che serve s
    uk2diS = {}

    # lista dei clienti di s
    #Gamma = Gamma[s]
    #Gamma.reverse()

    # lista dei veicoli di s
    #K2 = K2[s]
    # soluzione alternativa
    #K2.reverse()

    # dizionario delle rotte per ogni veicolo con relativi pallet:
    # trasportoPalletDiGamma [ k ] = ( gamma1, pallet1) , ( gamma2, pallet2) , ( gamma3, pallet3) ....
    trasportoPalletDiGamma = {}
    # dizionario della lista ordinata di archi per ogni veicolo: rotte[k]: [(s,i), (i,j), (j,...)]
    rotte = {}

    # pallet totali che partono da s
    palletDaConsegnare = 0

    for v in K2:
        uk2diS[v] = uk2[v]

    for gamma in Gamma:
        PGa[gamma] = PsGa[(s, gamma)]
        palletDaConsegnare += PGa[gamma]

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

    print("trasportoPalletDiGamma: {}".format(trasportoPalletDiGamma))
    print("rotte : {}".format(rotte))

    assignx2w2(x2TMP, w2TMP, trasportoPalletDiGamma, rotte)

    # verifica dell'ammissibilità della soluzione
    if (verificaSoluzioneAmmissibile(s, x2TMP, w2TMP, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS)):
        # soluzione ammissibile trovata
        x2 = x2TMP.copy()
        w2 = w2TMP.copy()

        return True, x2, w2, rotte
    else:
        # soluzione non ammissibile
        return False, x2, w2, rotte


def localSearch(heapSMD, smd10, smd11, x2, w2, rotte, s, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
    print("\nSTART localSearch()")
    itMAX = len(heapSMD)
    itNonAmmissibili = 0

    # lista di tuple: [(cliente, veicolo), ...]
    clienteVeicolo = getClienteVeicolo(rotte)

    while heapSMD[0] < 0 and itNonAmmissibili < itMAX:

        itNonAmmissibili += 1

        # salva la chiave del valore minore
        valoreHeap = heapq.heappop(heapSMD)
        # la chiave avrà lunghezza 5 e lunghezza 4 rispettivamente per 1-0 Exchange e 1-1 Exchange
        minCostKey = [key for key, value in list(smd10.items())+list(smd11.items()) if value == valoreHeap][0]

        # estraggo la chiave
        v1 = minCostKey[0]
        v2 = minCostKey[1]
        n1 = minCostKey[2]
        n2 = minCostKey[3]

        # lista dei nodi precedenti e dei nodi successivi
        precN1, succN1 = trovaPrecSuccList(rotte[v1], n1)
        precN2, succN2 = trovaPrecSuccList(rotte[v2], n2)

        x2TMP = x2.copy()
        w2TMP = w2.copy()

        # 1-0 Exchange
        if len(minCostKey) == 5:
            # estraggo il resto della chiave
            numeroPallet = minCostKey[4]

            # numero totale di pallet che riceve n2 prima di effettuare la mossa
            numeroTotPallet = x2TMP[v2, n2, precN2[0], n2]

            # evita che i veicoli non servano nessun cliente
            if len(rotte[v2]) > 1:

                # modificare x2TMP e w2TMP

                # se viene trattato un cliente splittato sulle rotte v1 e v2
                #
                if n2 in [c for c, k in clienteVeicolo if k == v1] and v1 != v2:
                    # v1
                    for arc1 in rotte[v1]:
                        if arc1[0] == n1:
                            break
                        x2TMP[v1, n2, arc1[0], arc1[1]] += numeroPallet

                    # v2
                    if numeroPallet == numeroTotPallet:
                        w2TMP[v2, precN2[0], n2] = 0
                    # prima di precN2[0]
                    flag = 0
                    for arc2 in rotte[v2]:
                        # precN2[0] - n2
                        if arc2[1] == n2:
                            flag = 1
                        # n2 - succN2[0]
                        if arc2[0] == n2:
                            flag = 2
                        # dopo succN2[0]
                        if arc2[0] == succN2[0]:
                            break

                        # prima di precN2[0]
                        if flag == 0:
                            x2TMP[v2, n2, arc2[0], arc2[1]] -= numeroPallet
                        # precN2[0] - n2
                        if flag == 1:
                            x2TMP[v2, n2, arc2[0], arc2[1]] -= numeroPallet

                        # n2 - succN2[0]
                        if flag == 2:
                            if numeroPallet == numeroTotPallet:
                                w2TMP[v2, n2, succN2[0]] = 0
                                w2TMP[v2, precN2[0], succN2[0]] = 1
                            for gamma in succN2:
                                x2TMP[v2, gamma, precN2[0], succN2[0]] += x2TMP[v2, gamma, precN2[0], n2]
                                x2TMP[v2, gamma, precN2[0], n2] -= x2TMP[v2, gamma, precN2[0], n2]
                                x2TMP[v2, gamma, n2, succN2[0]] -= x2TMP[v2, gamma, n2, succN2[0]]

                # se n1 e n2 sono sullo stesso veicolo
                elif v1 == v2 and ((n1, n2) not in rotte[v1]):
                    # esiste l'arco (n2, n1)
                    if (n2, n1) in rotte[v1]:
                        # nik2ij
                        w2TMP[v1, precN2[0], n2] = 0
                        w2TMP[v1, n2, n1] = 0

                        w2TMP[v1, precN2[0], n1] = 1
                        w2TMP[v1, n1, n2] = 1

                        if succN1[0] != -1:
                            w2TMP[v1, n1, succN1[0]] = 0
                            w2TMP[v1, n2, succN1[0]] = 1

                        # ak2ij
                        flag = 0
                        for arc1 in rotte[v1]:
                            if arc1[0] == precN2[0]:
                                flag = 1
                            if arc1[0] == n2:
                                flag = 2
                            if arc1[0] == n1:
                                flag = 3

                            if flag == 1:
                                for gamma in [n2] + succN2:
                                    x2TMP[v1, gamma, precN2[0], n2] = 0
                                    x2TMP[v1, gamma, precN2[0], n1] = x2[v1, gamma, precN2[0], n2]
                            if flag == 2:
                                for gamma in succN2:
                                    x2TMP[v1, gamma, n2, n1] = 0
                            if flag == 3:
                                for gamma in succN1:
                                    x2TMP[v1, gamma, n1, succN1[0]] = 0
                                    x2TMP[v1, gamma, n1, n2] = x2[v1, gamma, n1, succN1[0]]
                                    x2TMP[v1, gamma, n2, succN1[0]] = x2[v1, gamma, n1, succN1[0]]
                                break
                        x2TMP[v1, n2, n1, n2] = x2[v1, n2, precN2[0], n2]

                    # se n2 in succN1
                    elif n2 in succN1 and ((n1, n2) not in rotte[v1]):
                        # nik2ij
                        w2TMP[v1, n1, succN1[0]] = 0
                        w2TMP[v1, precN2[0], n2] = 0

                        w2TMP[v1, n1, n2] = 1
                        w2TMP[v1, n2, succN1[0]] = 1

                        # ak2ij
                        # prima di n1
                        flag = 0
                        for arc1 in rotte[v1]:
                            # (n1, succN1)
                            if arc1[0] == n1:
                                flag = 1
                            # (succN1, ...)
                            if arc1[0] == succN1[0]:
                                flag = 2
                            # (n2, succN2)
                            if arc1[0] == n2:
                                flag = 3
                            # (succN2, ...)
                            if arc1[0] == succN2[0]:
                                break

                            # (n1, succN1)
                            if flag == 1:
                                for gamma in succN1:
                                    x2TMP[v1, gamma, n1, succN1[0]] = 0
                                    x2TMP[v1, gamma, n1, n2] = x2[v1, gamma, n1, succN1[0]]

                                    if gamma != n2:
                                        x2TMP[v1, gamma, n2, succN1[0]] = x2[v1, gamma, n1, succN1[0]]
                            # (succN1, ...)
                            if flag == 2:
                                x2TMP[v1, n2, arc1[0], arc1[1]] = 0
                            # (n2, succN2)
                            if flag == 3:
                                w2TMP[v1, precN2[0], n2] = 1
                                w2TMP[v1, n2, succN2[0]] = 0

                                for gamma in succN2:
                                    x2TMP[v1, gamma, n2, succN2[0]] = 0
                                    x2TMP[v1, gamma, precN2[0], succN2[0]] = x2[v1, gamma, n2, succN2[0]]

                    # se n1 in succN2 ma non (n2, n1)
                    elif n1 in succN2 and ((n2, n1) not in rotte[v1]):
                        # viene creata la chiave
                        smd10[v1, v2, n1, n2, numeroPallet] = 0

                        # nik2ij
                        w2TMP[v1, precN2[0], n2] = 0
                        w2TMP[v1, n2, succN2[0]] = 0

                        w2TMP[v1, precN2[0], succN2[0]] = 1
                        w2TMP[v1, n1, n2] = 1

                        x2TMP[v1, n2, n1, n2] = x2[v1, n2, precN2[0], n2]

                        # prima di n2
                        flag=0
                        for arc1 in rotte[v1]:
                            # (precN2, n2)
                            if arc1[1] == n2:
                                flag=1
                            # (n2, succN2)
                            if arc1[0] == n2:
                                flag=2
                            # (succN2, ...)
                            if arc1[0] == succN2[0]:
                                flag=3
                            # (n1, succN1)
                            if arc1[0] == n1:
                                flag=4
                            # (succN1, ...)
                            if arc1[0] == succN1[0]:
                                break

                            # (precN2, n2)
                            if flag==1:
                                for gamma in [n2]+succN2:
                                    x2TMP[v1, gamma, precN2[0], n2] = 0
                                    x2TMP[v1, gamma, precN2[0], succN2[0]] = x2[v1, gamma, precN2[0], n2]
                            # (n2, succN2)
                            if flag==2:
                                for gamma in succN2:
                                    x2TMP[v1, gamma, n2, succN2[0]] = 0
                            # (succN2, ...)
                            if flag==3:
                                x2TMP[v1, n2, arc1[0], arc1[1]] = x2[v1, n2, precN2[0], n2]
                            # (n1, succN1)
                            if flag==4:
                                w2TMP[v1, n1, succN1[0]] = 0
                                w2TMP[v1, n2, succN1[0]] = 1
                                for gamma in succN1:
                                    x2TMP[v1, gamma, n1, succN1[0]] = 0
                                    x2TMP[v1, gamma, n1, n2] = x2[v1, gamma, n1, succN1[0]]
                                    x2TMP[v1, gamma, n2, succN1[0]] = x2[v1, gamma, n1, succN1[0]]

                # l'arco non deve esistere nella soluzione attuale
                # un veicolo non puo' essere spostato dietro se stesso
                elif (((v1 == v2) and ((n1, n2) not in rotte[v1])) or (v1 != v2)) and n2 != n1:
                    # calcolo dei costi
                    # v1
                    # nik2ij
                    # se n1 non è l'ultimo nodo della sua rotta
                    if succN1[0] != -1:
                        # aggiunta del nuovo arco out n2
                        w2TMP[v1, n2, succN1[0]] = 1
                        # rimozione del vecchio arco da sostituire con n2
                        w2TMP[v1, n1, succN1[0]] = 0
                    # aggiunta del nuovo arco in n2
                    w2TMP[v1, n1, n2] = 1

                    # ak2ij
                    # prima di n1
                    if succN1[0] == -1:
                        x2TMP[v1, n2, n1, n2] = x2[v2, n2, precN2[0], n2]
                    flag = 0
                    for arc1 in rotte[v1]:
                        # n1, n2
                        if arc1[0] == n1:
                            flag = 1
                        # dopo n2 -> non vengono modificati
                        if arc1[0] == succN1[0]:
                            break

                        # prima di n1
                        if flag == 0:
                            x2TMP[v1, n2, arc1[0], arc1[1]] = x2[v2, n2, precN2[0], n2]
                        # n1, n2
                        if flag == 1:
                            x2TMP[v1, n2, n1, n2] = x2[v2, n2, precN2[0], n2]
                            if succN1[0] != -1:
                                for gamma in succN1:
                                    x2TMP[v1, gamma, n1, n2] = x2[v1, gamma, n1, succN1[0]]
                                    x2TMP[v1, gamma, n2, succN1[0]] = x2[v1, gamma, n1, succN1[0]]
                                    x2TMP[v1, gamma, n1, succN1[0]] = 0
                        # dopo n2 -> non vengono modificati

                    # v2
                    # nik2ij
                    # se n2 non è l'ultimo nodo della sua rotta
                    if succN2[0] != -1:
                        # rimozione del vecchio arco out n2
                        w2TMP[v2, n2, succN2[0]] = 0
                        # aggiunta del nuovo arco in sostituzione di n2
                        w2TMP[v2, precN2[0], succN2[0]] = 1
                    # rimozione del vecchio arco in n2
                    w2TMP[v2, precN2[0], n2] = 0

                    # ak2ijsuccN2
                    # prima di precN2[0]
                    flag = 0
                    for arc2 in rotte[v2]:
                        # precN2[0], n2
                        if arc2[0] == precN2[0]:
                            flag = 1
                        # n2, succN2[0]
                        if arc2[0] == n2:
                            flag = 2
                        # dopo succN2[0] -> non vengono modificati
                        if arc2[0] == succN2[0]:
                            break

                        # prima di precN2[0]
                        if flag == 0:
                            x2TMP[v2, n2, arc2[0], arc2[1]] = x2[v2, n2, precN2[0], n2]
                        # precN2[0], n2
                        if flag == 1:
                            x2TMP[v2, n2, precN2[0], n2] = 0
                            if succN2[0] != -1:
                                for gamma in succN2:
                                    x2TMP[v2, gamma, precN2[0], succN2[0]] = x2[v2, gamma, precN2[0], n2]
                                    x2TMP[v2, gamma, precN2[0], n2] = 0
                        # n2, succN2[0]
                        if flag == 2:
                            for gamma in succN2:
                                x2TMP[v2, gamma, n2, succN2[0]] = 0
                        # dopo succN2[0] -> non vengono modificati

                # verificare ammissibilità
                if verificaSoluzioneAmmissibile(s, x2TMP, w2TMP, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
                    print("localSearch TRUE, itNonAmmissibili: {}, mossa: {}, differenza costo: {}.".format(itNonAmmissibili, minCostKey, smd10[minCostKey]))
                    # soluzione ammissibile trovata
                    if numeroTotPallet == numeroPallet:
                        return x2TMP, w2TMP, minCostKey, True
                    return x2TMP, w2TMP, minCostKey, False

        # 1-1 Exchange
        elif len(minCostKey) == 4:
            # se n1 è già presente in v2
            # se n2 è già presente in v1

            # numero di pallet che ricevono n1 e n2
            palletN1 = x2TMP[v1, n1, precN1[0], n1]
            palletN2 = x2TMP[v2, n2, precN2[0], n2]

            # se (n1, n2) è un arco già presente nella rotta
            if v1 == v2 and (n1, n2) in rotte[v1]:
                w2TMP[v1, precN1[0], n2] = 1
                w2TMP[v1, n2, n1] = 1

                w2TMP[v1, precN1[0], n1] = 0
                w2TMP[v1, n1, n2] = 0

                for gamma in [n1]+succN1:
                    x2TMP[v1, gamma, precN1[0], n2] = x2[v1, gamma, precN1[0], n1]
                    x2TMP[v1, gamma, precN1[0], n1] = 0

                if succN2[0] != -1:
                    w2TMP[v1, n1, succN2[0]] = 1
                    w2TMP[v1, n2, succN2[0]] = 0

                    for gamma in succN2:
                        x2TMP[v1, gamma, n2, n1] = x2[v1, gamma, n1, n2]
                        x2TMP[v1, gamma, n1, n2] = 0

                        x2TMP[v1, gamma, n1, succN2[0]] = x2[v1, gamma, n2, succN2[0]]
                        x2TMP[v1, gamma, n2, succN2[0]] = 0
                x2TMP[v1, n1, n2, n1] = palletN1
                x2TMP[v1, n2, n1, n2] = 0

                pass

            elif n1!=n2:
                # v1
                # v1 se n2 in v1
                # DA VERIFICARE
                if n2 in [c[1] for c in rotte[v1]]:
                    pass
                    # in v1: n2 in precN1
                    if n2 in precN1:
                        w2TMP[v1, precN1[0], n1] = 0

                        flag1=0
                        flag2=0
                        for arc1 in rotte[v1]:
                            if arc1[0] == n1:
                                flag1=1
                            if arc1[0] == n2:
                                flag2=1
                            if arc1[0] == succN1[0]:
                                break

                            if flag1==0:
                                x2TMP[v1, n1, arc1[0], arc1[1]] = 0
                            if flag1==1:
                                w2TMP[v1, n1, succN1[0]] = 0
                                w2TMP[v1, precN1[0], succN1[0]] = 1
                                for gamma in succN1:
                                    x2TMP[v1, gamma, precN1[0], n1] = 0
                                    x2TMP[v1, gamma, n1, succN1[0]] = 0
                                    x2TMP[v1, gamma, precN1[0], succN1[0]] = x2[v1, gamma, precN1[0], n1]
                            if flag2==0:
                                x2TMP[v1, n2, arc1[0], arc1[1]] += x2[v2, n2, precN2[0], n2]
                    # in v1: n2 in succN1
                    elif n2 in succN1:
                        w2TMP[v1, precN1[0], n1] = 0
                        w2TMP[v1, n1, succN1[0]] = 0
                        w2TMP[v1, precN1[0], succN1[0]] = 1

                        for gamma in succN1:
                            x2TMP[v1, gamma, precN1[0], n1] = 0
                            x2TMP[v1, gamma, n1, succN1[0]] = 0
                            x2TMP[v1, gamma, precN1[0], succN1[0]] = x2[v1, gamma, precN1[0], n1]

                        x2TMP[v1, n2, precN1[0], succN1[0]] += x2[v2, n2, precN2[0], n2]

                        flag1=0
                        flag2=0
                        for arc1 in rotte[v1]:
                            if arc1[0]==n1:
                                flag1=1
                            if arc1[0]==precN1[0]:
                                flag2=1
                            if arc1[0]==succN1[0] and arc1[0]!=n2:
                                flag2=0
                            if arc1[0]==n2:
                                break

                            if flag1==0:
                                x2TMP[v1, n1, arc1[0], arc1[1]] = 0
                            if flag2==0:
                                x2TMP[v1, n2, arc1[0], arc1[1]] += x2[v2, n2, precN2[0], n2]

                # DA VERIFICARE
                else:
                    # v1 se n1 ha successori
                    if succN1[0] != -1:
                        # aggiungere arco (n2, succN1)
                        w2TMP[v1, n2, succN1[0]] = 1
                        # eliminare arco (n1, succN1)
                        w2TMP[v1, n1, succN1[0]] = 0
                        for gamma in succN1:
                            # aggiungere pallet dei succN1 in (precN1, n2) e (n2, succN1)
                            x2TMP[v1, gamma, precN1[0], n2] = x2[v1, gamma, precN1[0], n1]
                            x2TMP[v1, gamma, n2, succN1[0]] = x2[v1, gamma, n1, succN1[0]]
                            # eliminare pallet dei succN1 da (precN1, n1) e (n1, succN1)
                            x2TMP[v1, gamma, precN1[0], n1] = 0
                            x2TMP[v1, gamma, n1, succN1[0]] = 0

                    # v1 sempre
                    # aggiungere arco (precN1, n2)
                    w2TMP[v1, precN1[0], n2] = 1
                    # eliminare arco (precN1, n1)
                    w2TMP[v1, precN1[0], n1] = 0
                    # ak2ij
                    for arc1 in rotte[v1]:
                        # (n1, succN1[0])
                        if arc1[1] == n1:
                            break
                        # aggiungere pallet n2 ai precN1
                        x2TMP[v2, n2, arc1[0], arc1[1]] = palletN2
                        # eliminare pallet n1 dai precN1
                        x2TMP[v1, n1, arc1[0], arc1[1]] = 0
                    x2TMP[v2, n2, precN1[0], n2] = palletN2
                    x2TMP[v1, n1, precN1[0], n1] = 0

                # v2
                # v2 se n1 in v2
                # DA VERIFICARE
                if n1 in [c[1] for c in rotte[v2]]:
                    pass
                    # in v2: n1 in precN2
                    if n1 in precN2:
                        w2TMP[v2, precN2[0], n2] = 0

                        flag1=0
                        flag2=0
                        for arc2 in rotte[v2]:
                            if arc2[0] == n2:
                                flag1=1
                            if arc2[0] == n1:
                                flag2=1
                            if arc2[0] == succN2[0]:
                                break

                            if flag1==0:
                                x2TMP[v2, n2, arc2[0], arc2[1]] = 0
                            if flag1==1:
                                w2TMP[v2, n2, succN2[0]] = 0
                                w2TMP[v2, precN2[0], succN2[0]] = 1
                                for gamma in succN1:
                                    x2TMP[v2, gamma, precN2[0], n2] = 0
                                    x2TMP[v2, gamma, n2, succN2[0]] = 0
                                    x2TMP[v2, gamma, precN2[0], succN2[0]] = x2[v2, gamma, precN2[0], n2]
                            if flag2==0:
                                x2TMP[v2, n1, arc2[0], arc2[1]] += x2[v1, n1, precN1[0], n1]

                    # in v2: n1 in succN2

                # DA VERIFICARE
                else:
                    # v2 se n2 ha successori
                    if succN2[0] != -1:
                        # aggiungere arco (n1, succN2)
                        w2TMP[v2, n1, succN2[0]] = 1
                        # eliminare arco (n2, succN2)
                        w2TMP[v2, n2, succN2[0]] = 0
                        for gamma in succN2:
                            # aggiungere pallet dei succN2 in (precN2, n1) e (n1, succN2)
                            x2TMP[v2, gamma, precN2[0], n1] = x2[v2, gamma, precN2[0], n2]
                            x2TMP[v2, gamma, n1, succN2[0]] = x2[v2, gamma, n2, succN2[0]]
                            # eliminare pallet dei succN2 da (precN2, n2) e (n2, succN2)
                            x2TMP[v2, gamma, precN2[0], n2] = 0
                            x2TMP[v2, gamma, n2, succN2[0]] = 0

                    # v2 sempre
                    # aggiungere arco (precN2, n1)
                    w2TMP[v2, precN2[0], n1] = 1
                    # eliminare arco (precN2, n2)
                    w2TMP[v2, precN2[0], n2] = 0
                    for arc2 in rotte[v2]:
                        # (n2, succN2[0])
                        if arc2[1] == n2:
                            break
                        # aggiungere pallet n1 ai precN2
                        x2TMP[v1, n1, arc2[0], arc2[1]] = palletN1
                        # eliminare pallet n2 dai precN2
                        x2TMP[v2, n2, arc2[0], arc2[1]] = 0
                    x2TMP[v1, n1, precN2[0], n1] = palletN1
                    x2TMP[v2, n2, precN2[0], n2] = 0

            # verificare ammissibilità
            if verificaSoluzioneAmmissibile(s, x2TMP, w2TMP, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
                print("localSearch TRUE, itNonAmmissibili: {}, mossa: {}, differenza costo: {}.".format(itNonAmmissibili, minCostKey, smd11[minCostKey]))
                # soluzione ammissibile trovata
                return x2TMP, w2TMP, minCostKey, True

    return x2TMP, w2TMP, -1, False


# aggiorna le rotte
def updateRotteSmd10(rotte, keyLocalSearch, flagAllPallets):
    v1 = keyLocalSearch[0]
    v2 = keyLocalSearch[1]
    n1 = keyLocalSearch[2]
    n2 = keyLocalSearch[3]

    # lista dei nodi precedenti e dei nodi successivi
    precN1, succN1 = trovaPrecSuccList(rotte[v1], n1)
    precN2, succN2 = trovaPrecSuccList(rotte[v2], n2)

    # modifica della rotta del veicolo v1
    if succN1[0] != -1:
        index = rotte[v1].index((n1, succN1[0]))
        rotte[v1][index] = (n1, n2)
        rotte[v1].insert(index + 1, (n2, succN1[0]))

    else:
        rotte[v1].append((n1, n2))

    if flagAllPallets:
        # modifica della rotta del veicolo v2
        if succN2[0] != -1:
            index = rotte[v2].index((precN2[0], n2))
            rotte[v2][index] = (precN2[0], succN2[0])
            rotte[v2].remove((n2, succN2[0]))
        else:
            rotte[v2].remove((precN2[0], n2))


def updateRotteSmd11(rotte, keyLocalSearch):
    v1 = keyLocalSearch[0]
    v2 = keyLocalSearch[1]
    n1 = keyLocalSearch[2]
    n2 = keyLocalSearch[3]

    # se (n1, n2) è un arco già presente
    if v1 == v2 and (n1, n2) in rotte[v1]:
        # modifica della rotta del veicolo v1/v2
        for index, arc in enumerate(rotte[v1]):
            if arc[1] == n1:
                rotte[v1][index] = (arc[0], n2)
            if arc[0] == n1:
                rotte[v1][index] = (n2, n1)
            if arc[0] == n2:
                rotte[v1][index] = (n1, arc[1])

    elif v1==v2:
        for index, arc in enumerate(rotte[v1]):
            if arc[1] == n1:
                rotte[v1][index] = (arc[0], n2)
            if arc[0] == n1:
                rotte[v1][index] = (n2, arc[1])
            if arc[1] == n2:
                rotte[v1][index] = (arc[0], n1)
            if arc[0] == n2:
                rotte[v1][index] = (n1, arc[1])

    else:
        # modifica della rotta del veicolo v1
        for index, arc in enumerate(rotte[v1]):
            if arc[0] == n1:
                rotte[v1][index] = (n2, arc[1])
            if arc[1] == n1:
                rotte[v1][index] = (arc[0], n2)
        # modifica della rotta del veicolo v2
        for index, arc in enumerate(rotte[v2]):
            if arc[0] == n2:
                rotte[v2][index] = (n1, arc[1])
            if arc[1] == n1:
                rotte[v2][index] = (arc[0], n1)
