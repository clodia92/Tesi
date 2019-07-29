from constraintsModelThree import *

import heapq
from copy import deepcopy
from random import shuffle
import pathlib


# generate variables for Model Three
#
# x2: variabile di trasporto del pallet, che rappresenta il numero di pallet che vengono spediti lungo l’arco (i,j)∈A2 al cliente γ∈Γ dal veicolo k∈K2, altrimenti 0
# w2: variabile di instradamento, che vale 1 se il veicolo k∈K2 attraversa l’arco (i,j)∈A2, altrimenti 0
# K2diS: L’insieme di PCV selezionati assegnati al satellite s∈S dalla soluzione di Prob2
# GammadiS: L’insieme di clienti γ∈Γ serviti dal satellite s∈S secondo la soluzione di Prob1
# A2: insieme di archi che collegano clienti e satelliti tra di loro
# sat: satellite
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


# inizializza x2 e w2 in base alla soluzione iniziale
#
# x2: variabile di trasporto del pallet, che rappresenta il numero di pallet che vengono spediti lungo l’arco (i,j)∈A2 al cliente γ∈Γ dal veicolo k∈K2, altrimenti 0
# w2: variabile di instradamento, che vale 1 se il veicolo k∈K2 attraversa l’arco (i,j)∈A2, altrimenti 0
# trasportoPalletDiGamma: dizionario delle rotte per ogni veicolo con relativi pallet
# rotte: dizionario della lista ordinata di archi per ogni veicolo:
def assignx2w2(x2, w2, trasportoPalletDiGamma, rotte):
    for k in rotte:
        for posArc, (arcI, arcJ) in enumerate(rotte[k]):
            for (gamma, pallet) in trasportoPalletDiGamma[k][posArc:]:
                x2[k, gamma, arcI, arcJ] = pallet
                w2[k, arcI, arcJ] = 1


# verifica se la soluzione è ammissibile restituendo True o False
#
# sat: satellite
# x2: variabile di trasporto del pallet, che rappresenta il numero di pallet che vengono spediti lungo l’arco (i,j)∈A2 al cliente γ∈Γ dal veicolo k∈K2, altrimenti 0
# w2: variabile di instradamento, che vale 1 se il veicolo k∈K2 attraversa l’arco (i,j)∈A2, altrimenti 0
# uk2: numero massimo di pallet che possono essere trasportati dal veicolo k∈K2 nel secondo livello
# Pgac: l’insieme dei pallet nel container c con destinazione γ
# PsGa: l’insieme di pallet con destinazione γ∈Γs trasportati al satellite s∈Sneg secondo la soluzione di Prob1
# K2: l'insieme di PCV (veicoli del secondo livello)
# A2: insieme di archi che collegano clienti e satelliti tra di loro
# Gamma: l'insieme di clienti
# CdiS: L’insieme di container c∈C trasportati verso il satellite s∈Sneg secondo la soluzione di Prob1
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


# inizializzazione del smd10
# 1-0 Exchange
# p pallet del cliente n2 della rotta v2 vengono spostati dopo il cliente n1 della rotta v1
#
# smd10: dizionario che contiene la mossa con relativa variazione di costo
# rotte: rotta a cui vengono applicate le mosse
# nik2ij: costo di instradamento del veicolo k∈K2 che attraversa l’arco (i,j)∈A2 nel secondo livello.
# ak2ij: costo di trasporto del pallet con destinazione γ∈Γ che attraversa l’arco (i,j)∈A2 con il veicolo k∈K2
# x2: variabile di trasporto del pallet, che rappresenta il numero di pallet che vengono spediti lungo l’arco (i,j)∈A2 al cliente γ∈Γ dal veicolo k∈K2, altrimenti 0
# s: satellite
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
                    if (n2 in [c[1] for c in rotte[v1]]) and v1 != v2 and n2 != n1:
                        # viene creata la chiave
                        smd10[v1, v2, n1, n2, numeroPallet] = 0
                        # calcolo dei costi
                        # v1
                        # nik2ij
                        # non viene modificato

                        # ak2ij
                        for arc in rotte[v1]:
                            #
                            if arc[0] == n2:
                                break
                            smd10[v1, v2, n1, n2, numeroPallet] += (numeroPallet * ak2ij[v1, arc[0], arc[1]])

                        # v2
                        # nik2ij -> non essendo eliminato l'arco in v2, non vi sono ripercussioni sull'smd per nik2ij

                        # ak2ij modifica costi sui precedenti di n2
                        for arc in rotte[v2]:
                            # n2,succN2[0]
                            if arc[0] == n2:
                                break

                            # prima di precN2[0]
                            smd10[v1, v2, n1, n2, numeroPallet] -= (numeroPallet * ak2ij[v2, arc[0], arc[1]])
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
                            smd10[v1, v2, n1, n2, numeroPallet] += (numeroPallet * ak2ij[v1, n1, n2])
                        for arc in rotte[v1]:
                            # n1, n2
                            if arc[0] == n1:
                                flag = 1
                            # dopo n2 -> non vengono modificati
                            if arc[0] == succN1[0]:
                                break

                            # prima di n1
                            if flag == 0:
                                smd10[v1, v2, n1, n2, numeroPallet] += (numeroPallet * ak2ij[v1, arc[0], arc[1]])
                            # n1, n2
                            if flag == 1:
                                smd10[v1, v2, n1, n2, numeroPallet] += (numeroPallet * ak2ij[v1, n1, n2])
                                if succN1[0] != -1:
                                    for gamma in succN1:
                                        smd10[v1, v2, n1, n2, numeroPallet] += (
                                                x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, n2])
                                        smd10[v1, v2, n1, n2, numeroPallet] += (
                                                x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n2, succN1[0]])
                                        smd10[v1, v2, n1, n2, numeroPallet] -= (
                                                x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, succN1[0]])
                            # dopo n2 -> non vengono modificati

                        # v2
                        # nik2ij
                        # non viene modificato

                        # ak2ij
                        for arc in rotte[v2]:
                            # n2, succN2[0]
                            if arc[0] == n2:
                                break

                            smd10[v1, v2, n1, n2, numeroPallet] -= (numeroPallet * ak2ij[v2, arc[0], arc[1]])
                            # dopo N2 -> non vengono modificati

                ######### Senza split
                numeroPallet = x2[v2, n2, precN2[0], n2]

                # se viene trattato un cliente splittato sulle rotte v1 e v2
                # Spostamento di tutti i pallet verso un altro veicolo
                if n2 in [c[1] for c in rotte[v1]] and v1 != v2 and n2 != n1:
                    # viene creata la chiave
                    smd10[v1, v2, n1, n2, numeroPallet] = 0
                    # calcolo dei costi
                    # v1
                    # nik2ij
                    # non viene modificato

                    # ak2ij
                    for arc in rotte[v1]:
                        #
                        if arc[0] == n2:
                            break
                        smd10[v1, v2, n1, n2, numeroPallet] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc[0], arc[1]])

                    # v2
                    # rimozione del vecchio arco in n2
                    smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v2, precN2[0], n2]
                    # prima di precN2[0]
                    flag = 0
                    for arc in rotte[v2]:
                        # precN2[0], n2
                        if arc[0] == precN2[0]:
                            flag = 1
                        # n2, succN2[0]
                        if arc[0] == n2:
                            flag = 2
                        # dopo succN2[0] -> non vengono modificati
                        if arc[0] == succN2[0]:
                            break

                        # prima di precN2[0]
                        if flag == 0:
                            smd10[v1, v2, n1, n2, numeroPallet] -= (
                                    x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc[0], arc[1]])
                        # precN2[0], n2
                        if flag == 1:
                            smd10[v1, v2, n1, n2, numeroPallet] -= (
                                    x2[v2, n2, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                            if succN2[0] != -1:
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] += (
                                            x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], succN2[0]])
                                    smd10[v1, v2, n1, n2, numeroPallet] -= (
                                            x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                        # n2, succN2[0]
                        if flag == 2:
                            # rimozione del vecchio arco out n2
                            smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v2, n2, succN2[0]]
                            # aggiunta del nuovo arco in sostituzione di n2
                            smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v2, precN2[0], succN2[0]]
                            for gamma in succN2:
                                smd10[v1, v2, n1, n2, numeroPallet] -= (
                                        x2[v2, gamma, n2, succN2[0]] * ak2ij[v2, n2, succN2[0]])
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
                        for arc in rotte[v1]:
                            if arc[0] == precN2[0]:
                                flag = 1
                            if arc[0] == n2:
                                flag = 2
                            if arc[0] == n1:
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
                        flag = 0
                        for arc in rotte[v1]:
                            # (n1, succN1)
                            if arc[0] == n1:
                                flag = 1
                            # (succN1, ...)
                            if arc[0] == succN1[0]:
                                flag = 2
                            # (n2, succN2)
                            if arc[0] == n2:
                                flag = 3
                            # (succN2, ...)
                            if arc[0] == succN2[0]:
                                break

                            # (n1, succN1)
                            if flag == 1:
                                for gamma in succN1:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                        v1, n1, succN1[0]]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                        v1, n1, n2]
                                    if gamma != n2:
                                        smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                            v1, n2, succN1[0]]
                            # (succN1, ...)
                            if flag == 2:
                                smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, n2, precN2[0], n2] * ak2ij[
                                    v1, arc[0], arc[1]]
                            # (n2, succN2)
                            if flag == 3:
                                smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, precN2[0], n2]
                                smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n2, succN2[0]]
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n2, succN2[0]] * ak2ij[
                                        v1, n2, succN2[0]]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n2, succN2[0]] * ak2ij[
                                        v1, precN2[0], succN2[0]]

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
                        flag = 0
                        for arc in rotte[v1]:
                            # (precN2, n2)
                            if arc[1] == n2:
                                flag = 1
                            # (n2, succN2)
                            if arc[0] == n2:
                                flag = 2
                            # (succN2, ...)
                            if arc[0] == succN2[0]:
                                flag = 3
                            # (n1, succN1)
                            if arc[0] == n1:
                                flag = 4
                            # (succN1, ...)
                            if arc[0] == succN1[0]:
                                break

                            # (precN2, n2)
                            if flag == 1:
                                for gamma in [n2] + succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, precN2[0], n2] * ak2ij[
                                        v1, precN2[0], n2]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, precN2[0], n2] * ak2ij[
                                        v1, precN2[0], succN2[0]]
                            # (n2, succN2)
                            if flag == 2:
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n2, succN2[0]] * ak2ij[
                                        v1, n2, succN2[0]]
                            # (succN2, ...)
                            if flag == 3:
                                smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, n2, precN2[0], n2] * ak2ij[
                                    v1, arc[0], arc[1]]
                            # (n1, succN1)
                            if flag == 4:
                                smd10[v1, v2, n1, n2, numeroPallet] -= nik2ij[v1, n1, succN1[0]]
                                smd10[v1, v2, n1, n2, numeroPallet] += nik2ij[v1, n2, succN1[0]]
                                for gamma in succN1:
                                    smd10[v1, v2, n1, n2, numeroPallet] -= x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                        v1, n1, succN1[0]]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                        v1, n1, n2]
                                    smd10[v1, v2, n1, n2, numeroPallet] += x2[v1, gamma, n1, succN1[0]] * ak2ij[
                                        v1, n2, succN1[0]]

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
                    for arc in rotte[v1]:
                        # n1, n2
                        if arc[0] == n1:
                            flag = 1
                        # dopo n2 -> non vengono modificati
                        if arc[0] == succN1[0]:
                            # flag=2
                            break

                        # prima di n1
                        if flag == 0:
                            smd10[v1, v2, n1, n2, numeroPallet] += (
                                    x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc[0], arc[1]])
                        # n1, n2
                        if flag == 1:
                            smd10[v1, v2, n1, n2, numeroPallet] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, n1, n2])
                            if succN1[0] != -1:
                                for gamma in succN1:
                                    smd10[v1, v2, n1, n2, numeroPallet] += (
                                            x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, n2])
                                    smd10[v1, v2, n1, n2, numeroPallet] += (
                                            x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n2, succN1[0]])
                                    smd10[v1, v2, n1, n2, numeroPallet] -= (
                                            x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, succN1[0]])
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
                    for arc in rotte[v2]:
                        # precN2[0], n2
                        if arc[0] == precN2[0]:
                            flag = 1
                        # n2, succN2[0]
                        if arc[0] == n2:
                            flag = 2
                        # dopo succN2[0] -> non vengono modificati
                        if arc[0] == succN2[0]:
                            break

                        # prima di precN2[0]
                        if flag == 0:
                            smd10[v1, v2, n1, n2, numeroPallet] -= (
                                    x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc[0], arc[1]])
                        # precN2[0], n2
                        if flag == 1:
                            smd10[v1, v2, n1, n2, numeroPallet] -= (
                                    x2[v2, n2, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                            if succN2[0] != -1:
                                for gamma in succN2:
                                    smd10[v1, v2, n1, n2, numeroPallet] += (
                                            x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], succN2[0]])
                                    smd10[v1, v2, n1, n2, numeroPallet] -= (
                                            x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n2])
                        # n2, succN2[0]
                        if flag == 2:
                            for gamma in succN2:
                                smd10[v1, v2, n1, n2, numeroPallet] -= (
                                        x2[v2, gamma, n2, succN2[0]] * ak2ij[v2, n2, succN2[0]])
                        # dopo succN2[0] -> non vengono modificati


# inizializzazione del smd11
# 1-1 Exchange
# il cliente n1 della rotta v1 viene invertito con il cliente n2 della rotta v2
#
# smd11: dizionario che contiene la mossa con relativa variazione di costo
# rotte: dizionario dei percorsi dei veicoli assegnati ad un satellite
# nik2ij: costo di instradamento del veicolo k∈K2 che attraversa l’arco (i,j)∈A2 nel secondo livello.
# ak2ij: costo di trasporto del pallet con destinazione γ∈Γ che attraversa l’arco (i,j)∈A2 con il veicolo k∈K2
# x2: variabile di trasporto del pallet, che rappresenta il numero di pallet che vengono spediti lungo l’arco (i,j)∈A2 al cliente γ∈Γ dal veicolo k∈K2, altrimenti 0
def inizializzaSMD11(smd11, rotte, nik2ij, ak2ij, x2):
    # lista di tuple: (cliente, veicolo)
    clienteVeicolo = getClienteVeicolo(rotte)

    # indexCV viene utilizzato per scorrere la seconda volta clienteVeicolo solo dall'attuale coppia (v, n) in poi
    # in modo da evitare duplicati: smd11[7, 8, 3, 4] == smd11[8, 7, 4, 3]
    indexCV = 0

    for n1, v1 in clienteVeicolo:
        indexCV += 1

        for n2, v2 in clienteVeicolo[indexCV:]:
            # lista dei nodi precedenti e dei nodi successivi
            precN1, succN1 = trovaPrecSuccList(rotte[v1], n1)
            precN2, succN2 = trovaPrecSuccList(rotte[v2], n2)

            # viene creata la chiave
            smd11[v1, v2, n1, n2] = 0

            # se n1 e n2 fanno parte della stessa rotta
            if v1 == v2:
                # se (n1, n2) è un arco già presente nella rotta
                if (n1, n2) in rotte[v1]:
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
                # n1 e n2 nella stessa rotta ma non (n1, n2)
                else:
                    smd11[v1, v2, n1, n2] -= nik2ij[v1, precN1[0], n1]
                    smd11[v1, v2, n1, n2] -= nik2ij[v1, n1, succN1[0]]
                    smd11[v1, v2, n1, n2] += nik2ij[v1, precN1[0], n2]
                    smd11[v1, v2, n1, n2] += nik2ij[v1, n2, succN1[0]]
                    smd11[v1, v2, n1, n2] -= nik2ij[v1, precN2[0], n2]
                    smd11[v1, v2, n1, n2] += nik2ij[v1, precN2[0], n1]

                    # se n2 ha successori
                    if succN2[0] != -1:
                        smd11[v1, v2, n1, n2] -= nik2ij[v1, n2, succN2[0]]
                        smd11[v1, v2, n1, n2] += nik2ij[v1, n1, succN2[0]]

                    flag = 0
                    for arc in rotte[v1]:
                        # (precN1, n1)
                        if arc[0] == precN1[0]:
                            flag = 1
                        # (n1, succN1)
                        if arc[0] == n1:
                            flag = 2
                        # (succN1, ...)
                        if arc[0] == succN1[0]:
                            flag = 3
                        # (precN2, n2)
                        if arc[0] == precN2[0]:
                            flag = 4
                        # (n2, succN2)
                        if arc[0] == n2:
                            flag = 5
                        # (succN2, ...)
                        if arc[0] == succN2[0]:
                            break

                        # (precN1, n1)
                        if flag == 1:
                            for gamma in [n1] + succN1:
                                smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n1]
                                smd11[v1, v2, n1, n2] += x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n2]
                        # (n1, succN1)
                        if flag == 2:
                            for gamma in succN1:
                                smd11[v1, v2, n1, n2] -= x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n1, succN1[0]]
                                if gamma != n2:
                                    smd11[v1, v2, n1, n2] += x2[v1, gamma, n1, succN1[0]] * ak2ij[v1, n2, succN1[0]]
                            smd11[v1, v2, n1, n2] += x2[v1, n1, precN1[0], n1] * ak2ij[v1, n2, succN1[0]]
                        # (succN1, ...)
                        if flag == 3:
                            smd11[v1, v2, n1, n2] -= x2[v1, n2, arc[0], arc[1]] * ak2ij[v1, arc[0], arc[1]]
                            smd11[v1, v2, n1, n2] += x2[v1, n1, arc[0], arc[1]] * ak2ij[v1, arc[0], arc[1]]
                        # (precN2, n2)
                        if flag == 4:
                            smd11[v1, v2, n1, n2] -= x2[v1, n2, precN2[0], n2] * ak2ij[v1, precN2[0], n2]
                            smd11[v1, v2, n1, n2] += x2[v1, n1, precN1[0], n1] * ak2ij[v1, precN2[0], n1]
                        # (n2, succN2)
                        if flag == 5:
                            for gamma in succN2:
                                smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN2[0], n2] * ak2ij[v1, precN2[0], n2]
                                smd11[v1, v2, n1, n2] += x2[v1, gamma, precN2[0], n2] * ak2ij[v1, precN2[0], n1]

                                smd11[v1, v2, n1, n2] -= x2[v1, gamma, n2, succN2[0]] * ak2ij[v1, n2, succN2[0]]
                                smd11[v1, v2, n1, n2] += x2[v1, gamma, n2, succN2[0]] * ak2ij[v1, n1, succN2[0]]

            elif n1 != n2:
                # v1
                # v1: se n2 in v1
                if n2 in [c[1] for c in rotte[v1]]:
                    # in v1: n2 in precN1
                    if n2 in precN1:
                        smd11[v1, v2, n1, n2] -= nik2ij[v1, precN1[0], n1]

                        flag1 = 0
                        flag2 = 0
                        for arc in rotte[v1]:
                            if arc[0] == n1:
                                flag1 = 1
                            if arc[0] == n2:
                                flag2 = 1
                            if arc[0] == succN1[0]:
                                break

                            if flag1 == 0:
                                smd11[v1, v2, n1, n2] -= x2[v1, n1, precN1[0], n1] * ak2ij[v1, arc[0], arc[1]]
                            if flag1 == 1:
                                smd11[v1, v2, n1, n2] -= nik2ij[v1, n1, succN1[0]]
                                smd11[v1, v2, n1, n2] += nik2ij[v1, precN1[0], succN1[0]]
                                for gamma in succN1:
                                    smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN1[0], n1] * ak2ij[v1, precN1[0], n1]
                                    smd11[v1, v2, n1, n2] -= x2[v1, gamma, precN1[0], n1] * ak2ij[v1, n1, succN1[0]]
                                    smd11[v1, v2, n1, n2] += x2[v1, gamma, precN1[0], n1] * ak2ij[
                                        v1, precN1[0], succN1[0]]
                            if flag2 == 0:
                                smd11[v1, v2, n1, n2] += x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc[0], arc[1]]
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

                        flag1 = 0
                        flag2 = 0
                        for arc in rotte[v1]:
                            if arc[0] == n1:
                                flag1 = 1
                            if arc[0] == precN1[0]:
                                flag2 = 1
                            if arc[0] == succN1[0] and arc[0] != n2:
                                flag2 = 0
                            if arc[0] == n2:
                                break

                            if flag1 == 0:
                                smd11[v1, v2, n1, n2] -= x2[v1, n1, precN1[0], n1] * ak2ij[v1, arc[0], arc[1]]
                            if flag2 == 0:
                                smd11[v1, v2, n1, n2] += x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc[0], arc[1]]

                else:
                    # v1: se n1 ha successori
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

                    # v1: sempre
                    # nik2ij
                    # aggiungere costo arco (precN1, n2)
                    smd11[v1, v2, n1, n2] += nik2ij[v1, precN1[0], n2]
                    # eliminare costo arco (precN1, n1)
                    smd11[v1, v2, n1, n2] -= nik2ij[v1, precN1[0], n1]
                    # ak2ij
                    for arc in rotte[v1]:
                        # (n1, succN1[0])
                        if arc[1] == n1:
                            break
                        # aggiungere costo pallet n2 ai precN1
                        smd11[v1, v2, n1, n2] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, arc[0], arc[1]])
                        # eliminare costo pallet n1 dai precN1
                        smd11[v1, v2, n1, n2] -= (x2[v1, n1, precN1[0], n1] * ak2ij[v1, arc[0], arc[1]])
                    smd11[v1, v2, n1, n2] += (x2[v2, n2, precN2[0], n2] * ak2ij[v1, precN1[0], n2])
                    smd11[v1, v2, n1, n2] -= (x2[v1, n1, precN1[0], n1] * ak2ij[v1, precN1[0], n1])

                # v2
                # v2: se n1 in v2
                if n1 in [c[1] for c in rotte[v2]]:
                    pass
                    # in v2: n1 in precN2
                    if n1 in precN2:
                        smd11[v1, v2, n1, n2] -= nik2ij[v2, precN2[0], n2]

                        flag1 = 0
                        flag2 = 0
                        for arc in rotte[v2]:
                            if arc[0] == n2:
                                flag1 = 1
                            if arc[0] == n1:
                                flag2 = 1
                            if arc[0] == succN2[0]:
                                break

                            if flag1 == 0:
                                smd11[v1, v2, n1, n2] -= x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc[0], arc[1]]
                            if flag1 == 1:
                                smd11[v1, v2, n1, n2] -= nik2ij[v2, n2, succN2[0]]
                                smd11[v1, v2, n1, n2] += nik2ij[v2, precN2[0], succN2[0]]
                                for gamma in succN2:
                                    smd11[v1, v2, n1, n2] -= x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n2]
                                    smd11[v1, v2, n1, n2] -= x2[v2, gamma, precN2[0], n2] * ak2ij[v2, n2, succN2[0]]
                                    smd11[v1, v2, n1, n2] += x2[v2, gamma, precN2[0], n2] * ak2ij[
                                        v2, precN2[0], succN2[0]]
                            if flag2 == 0:
                                smd11[v1, v2, n1, n2] += x2[v1, n1, precN1[0], n1] * ak2ij[v2, arc[0], arc[1]]
                    # in v2: n1 in succN2
                    elif n1 in succN2:
                        smd11[v1, v2, n1, n2] -= nik2ij[v2, precN2[0], n2]
                        smd11[v1, v2, n1, n2] -= nik2ij[v2, n2, succN2[0]]
                        smd11[v1, v2, n1, n2] += nik2ij[v2, precN2[0], succN2[0]]

                        for gamma in succN2:
                            smd11[v1, v2, n1, n2] -= x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], n2]
                            smd11[v1, v2, n1, n2] -= x2[v2, gamma, precN2[0], n2] * ak2ij[v2, n2, succN2[0]]
                            smd11[v1, v2, n1, n2] += x2[v2, gamma, precN2[0], n2] * ak2ij[v2, precN2[0], succN2[0]]

                        smd11[v1, v2, n1, n2] += x2[v1, n1, precN1[0], n1] * ak2ij[v2, precN2[0], succN2[0]]

                        flag1 = 0
                        flag2 = 0
                        for arc in rotte[v2]:
                            if arc[0] == n2:
                                flag1 = 1
                            if arc[0] == precN2[0]:
                                flag2 = 1
                            if arc[0] == succN2[0] and arc[0] != n1:
                                flag2 = 0
                            if arc[0] == n1:
                                break

                            if flag1 == 0:
                                smd11[v1, v2, n1, n2] -= x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc[0], arc[1]]
                            if flag2 == 0:
                                smd11[v1, v2, n1, n2] += x2[v1, n1, precN1[0], n1] * ak2ij[v2, arc[0], arc[1]]

                else:

                    # v2: se n2 ha successori
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

                    # v2: sempre
                    # nik2ij
                    # aggiungere costo arco (precN2, n1)
                    smd11[v1, v2, n1, n2] += nik2ij[v2, precN2[0], n1]
                    # eliminare costo arco (precN2, n2)
                    smd11[v1, v2, n1, n2] -= nik2ij[v2, precN2[0], n2]
                    # ak2ij
                    for arc in rotte[v2]:
                        # (n2, succN2[0])
                        if arc[1] == n2:
                            break
                        # aggiungere costo pallet n1 ai precN2
                        smd11[v1, v2, n1, n2] += (x2[v1, n1, precN1[0], n1] * ak2ij[v2, arc[0], arc[1]])
                        # eliminare costo pallet n2 dai precN2
                        smd11[v1, v2, n1, n2] -= (x2[v2, n2, precN2[0], n2] * ak2ij[v2, arc[0], arc[1]])
                    smd11[v1, v2, n1, n2] += (x2[v1, n1, precN1[0], n1] * ak2ij[v2, precN2[0], n1])
                    smd11[v1, v2, n1, n2] -= (x2[v2, n2, precN2[0], n2] * ak2ij[v2, precN2[0], n2])

            elif v1 != v2 and n1 == n2:
                for arc in rotte[v1]:
                    if arc[0] == n1:
                        break
                    smd11[v1, v2, n1, n2] += (x2[v2, n2, precN2[0], n2] - x2[v1, n1, precN1[0], n1]) * ak2ij[
                        v1, arc[0], arc[1]]
                for arc in rotte[v2]:
                    if arc[0] == n2:
                        break
                    smd11[v1, v2, n1, n2] += (x2[v1, n1, precN1[0], n1] - x2[v2, n2, precN2[0], n2]) * ak2ij[
                        v2, arc[0], arc[1]]


# restituisce una lista di tuple clienteVeicolo: [(cliente, veicolo), ...]
#
# rotte: dizionario dei percorsi dei veicoli assegnati ad un satellite
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


# restituisce due liste precList e succList rispettivamente dei clienti precedenti e successivi al nodo
#
# rotta: lista del percorso di un determinato veicolo
# nodo: cliente di cui si volgiono trovare i clienti precedenti e successivi
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


# restituisce una soluzione iniziale ammissibile:
# True/False: True se è stata trovata una soluzione ammissibile, altrimenti False
# x2: aggiornato se è stata trovata una soluzione ammissibile, altrimenti invariato
# w2: aggiornato se è stata trovata una soluzione ammissibile, altrimenti invariato
# rotte: dizionario dei percorsi dei veicoli assegnati ad un satellite
#
# s: satellite
# x2: variabile di trasporto del pallet, che rappresenta il numero di pallet che vengono spediti lungo l’arco (i,j)∈A2 al cliente γ∈Γ dal veicolo k∈K2, altrimenti 0
# w2: variabile di instradamento, che vale 1 se il veicolo k∈K2 attraversa l’arco (i,j)∈A2, altrimenti 0
# uk2: numero massimo di pallet che possono essere trasportati dal veicolo k∈K2 nel secondo livello
# Pgac: l’insieme dei pallet nel container c con destinazione γ
# PsGa: l’insieme di pallet con destinazione γ∈Γs trasportati al satellite s∈Sneg secondo la soluzione di Prob1
# K2: l'insieme di PCV (veicoli del secondo livello)
# A2: insieme di archi che collegano clienti e satelliti tra di loro
# Gamma: l'insieme di clienti
# CdiS: L’insieme di container c∈C trasportati verso il satellite s∈Sneg secondo la soluzione di Prob1
def findSolutionBase(s, x2, w2, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
    print("\nSTART findSolutionBase()")

    # soluzione alternativa
    # Gamma.reverse()
    shuffle(Gamma)

    # K2.reverse()
    shuffle(K2)

    #  if s==1:
    #     #     Gamma = [5, 4, 3, 8, 7, 6]
    #     #     K2 = [7, 8]

    print("Gamma: ", Gamma)
    print("K2: ", K2)

    x2TMP = deepcopy(x2)
    w2TMP = deepcopy(w2)

    # dizionario che contiene i pallet richiesti dai clienti di s
    PGa = {}

    # numero massimo di pallet trasportabili dal veicolo k che serve s
    uk2diS = {}

    # dizionario delle rotte per ogni veicolo con relativi pallet:
    # trasportoPalletDiGamma [ k ] = ( gamma1, pallet1) , ( gamma2, pallet2) , ( gamma3, pallet3) ....
    trasportoPalletDiGamma = {}
    # dizionario della lista ordinata di archi per ogni veicolo:
    # rotte[k]: [(s,i), (i,j), (j,...)]
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
        while (palletTrasportatiDiK2[posV] > uk2diS[K2[posV]]):
            posV = (posV + 1) % len(K2)

        # se il cliente deve ancora ricevere dei pallet
        if (PGa[Gamma[posG]] > 0):
            # consegna a gamma
            # gamma non viene splittato
            # lo spazio della rotta è sufficiente per ospitare tutti i pallet di gamma
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
            # gamma viene splittato
            # la rotta non ha raggiunto il limite di capienza
            elif uk2diS[K2[posV]] != palletTrasportatiDiK2[posV]:
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
                palletTrasportatiDiK2PosV = palletTrasportatiDiK2[posV]  # variabile temporanea
                palletTrasportatiDiK2[posV] += PGa[Gamma[posG]]
                PGa[Gamma[posG]] -= uk2diS[K2[posV]] - palletTrasportatiDiK2PosV
                # full

            # passo al veicolo sucessivo
            posV = (posV + 1) % len(K2)

        # passo al cliente sucessivo
        posG = (posG + 1) % len(Gamma)

    print("trasportoPalletDiGamma: {}".format(trasportoPalletDiGamma))
    print("rotte : {}".format(rotte))

    assignx2w2(x2TMP, w2TMP, trasportoPalletDiGamma, rotte)

    # verifica dell'ammissibilità della soluzione
    if verificaSoluzioneAmmissibile(s, x2TMP, w2TMP, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
        # soluzione ammissibile trovata
        x2 = deepcopy(x2TMP)
        w2 = deepcopy(w2TMP)

        return True, x2, w2, rotte
    else:
        # soluzione non ammissibile
        return False, x2, w2, rotte


# Local Search: ricerca l'ottimo locale tra le soluzioni ammissibili
# x2: aggiornato se è stata trovata una soluzione ammissibile migliore, altrimenti invariato
# w2: aggiornato se è stata trovata una soluzione ammissibile migliore, altrimenti invariato
# minCostKey: chiave dell'smd che identifica la mossa che porta alla soluzione migliore, altrimenti restituisce -1 se è stato raggiunto un minimo locale
# True/False: se è stata trovata una soluzione migliore rispetto alla precedente
#
# heapSMD: lista unica dei costi che contiene la variazione della funzione obiettivo in base alle mosse applicate
# smd10: dizionario che contiene la mossa con relativa variazione di costo (1-0 Exchange)
# smd11: dizionario che contiene la mossa con relativa variazione di costo (1-1 Exchange)
# x2: variabile di trasporto del pallet, che rappresenta il numero di pallet che vengono spediti lungo l’arco (i,j)∈A2 al cliente γ∈Γ dal veicolo k∈K2, altrimenti 0
# w2: variabile di instradamento, che vale 1 se il veicolo k∈K2 attraversa l’arco (i,j)∈A2, altrimenti 0
# rotte: dizionario dei percorsi dei veicoli assegnati ad un satellite
# s: satellite
# uk2: numero massimo di pallet che possono essere trasportati dal veicolo k∈K2 nel secondo livello
# Pgac: l’insieme dei pallet nel container c con destinazione γ
# PsGa: l’insieme di pallet con destinazione γ∈Γs trasportati al satellite s∈Sneg secondo la soluzione di Prob1
# K2: l'insieme di PCV (veicoli del secondo livello)
# A2: insieme di archi che collegano clienti e satelliti tra di loro
# Gamma: l'insieme di clienti
# CdiS: L’insieme di container c∈C trasportati verso il satellite s∈Sneg secondo la soluzione di Prob1
def localSearch(heapSMD, smd10, smd11, x2, w2, rotte, s, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
    print("\nSTART localSearch()")
    itMAX = len(heapSMD)
    itNonAmmissibili = 0

    # x2TMP = deepcopy(x2)
    # w2TMP = deepcopy(w2)

    while heapSMD[0] < 0 and itNonAmmissibili < itMAX:

        itNonAmmissibili += 1

        # salva la chiave del valore minore
        valoreHeap = heapq.heappop(heapSMD)
        # la chiave avrà lunghezza 5 e lunghezza 4 rispettivamente per 1-0 Exchange e 1-1 Exchange
        minCostKey = [key for key, value in list(smd10.items()) + list(smd11.items()) if value == valoreHeap][0]

        # estraggo la chiave
        v1 = minCostKey[0]
        v2 = minCostKey[1]
        n1 = minCostKey[2]
        n2 = minCostKey[3]

        # lista dei nodi precedenti e dei nodi successivi
        precN1, succN1 = trovaPrecSuccList(rotte[v1], n1)
        precN2, succN2 = trovaPrecSuccList(rotte[v2], n2)

        x2TMP = deepcopy(x2)
        w2TMP = deepcopy(w2)

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
                if n2 in [c[1] for c in rotte[v1]] and v1 != v2 and n1 != n2:
                    # v1
                    for arc in rotte[v1]:
                        if arc[0] == n1:
                            break
                        x2TMP[v1, n2, arc[0], arc[1]] += numeroPallet

                    # v2
                    if numeroPallet == numeroTotPallet:
                        w2TMP[v2, precN2[0], n2] = 0
                    # prima di precN2[0]
                    flag = 0
                    for arc in rotte[v2]:
                        # precN2[0] - n2
                        if arc[1] == n2:
                            flag = 1
                        # n2 - succN2[0]
                        if arc[0] == n2:
                            flag = 2
                        # dopo succN2[0]
                        if arc[0] == succN2[0]:
                            break

                        # prima di precN2[0]
                        if flag == 0:
                            x2TMP[v2, n2, arc[0], arc[1]] -= numeroPallet
                        # precN2[0] - n2
                        if flag == 1:
                            x2TMP[v2, n2, arc[0], arc[1]] -= numeroPallet

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
                        for arc in rotte[v1]:
                            if arc[0] == precN2[0]:
                                flag = 1
                            if arc[0] == n2:
                                flag = 2
                            if arc[0] == n1:
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
                        for arc in rotte[v1]:
                            # (n1, succN1)
                            if arc[0] == n1:
                                flag = 1
                            # (succN1, ...)
                            if arc[0] == succN1[0]:
                                flag = 2
                            # (n2, succN2)
                            if arc[0] == n2:
                                flag = 3
                            # (succN2, ...)
                            if arc[0] == succN2[0]:
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
                                x2TMP[v1, n2, arc[0], arc[1]] = 0
                            # (n2, succN2)
                            if flag == 3:
                                w2TMP[v1, precN2[0], n2] = 1
                                w2TMP[v1, n2, succN2[0]] = 0

                                for gamma in succN2:
                                    x2TMP[v1, gamma, n2, succN2[0]] = 0
                                    x2TMP[v1, gamma, precN2[0], succN2[0]] = x2[v1, gamma, n2, succN2[0]]

                    # se n1 in succN2 ma non (n2, n1)
                    elif n1 in succN2 and ((n2, n1) not in rotte[v1]):

                        # nik2ij
                        w2TMP[v1, precN2[0], n2] = 0
                        w2TMP[v1, n2, succN2[0]] = 0

                        w2TMP[v1, precN2[0], succN2[0]] = 1
                        w2TMP[v1, n1, n2] = 1

                        x2TMP[v1, n2, n1, n2] = x2[v1, n2, precN2[0], n2]

                        # prima di n2
                        flag = 0
                        for arc in rotte[v1]:
                            # (precN2, n2)
                            if arc[1] == n2:
                                flag = 1
                            # (n2, succN2)
                            if arc[0] == n2:
                                flag = 2
                            # (succN2, ...)
                            if arc[0] == succN2[0]:
                                flag = 3
                            # (n1, succN1)
                            if arc[0] == n1:
                                flag = 4
                            # (succN1, ...)
                            if arc[0] == succN1[0]:
                                break

                            # (precN2, n2)
                            if flag == 1:
                                for gamma in [n2] + succN2:
                                    x2TMP[v1, gamma, precN2[0], n2] = 0
                                    x2TMP[v1, gamma, precN2[0], succN2[0]] = x2[v1, gamma, precN2[0], n2]
                            # (n2, succN2)
                            if flag == 2:
                                for gamma in succN2:
                                    x2TMP[v1, gamma, n2, succN2[0]] = 0
                            # (succN2, ...)
                            if flag == 3:
                                x2TMP[v1, n2, arc[0], arc[1]] = x2[v1, n2, precN2[0], n2]
                            # (n1, succN1)
                            if flag == 4:
                                w2TMP[v1, n1, succN1[0]] = 0
                                w2TMP[v1, n2, succN1[0]] = 1
                                for gamma in succN1:
                                    x2TMP[v1, gamma, n1, succN1[0]] = 0
                                    x2TMP[v1, gamma, n1, n2] = x2[v1, gamma, n1, succN1[0]]
                                    x2TMP[v1, gamma, n2, succN1[0]] = x2[v1, gamma, n1, succN1[0]]

                # l'arco non deve esistere nella soluzione attuale
                # un veicolo non puo' essere spostato dietro se stesso
                elif v1 != v2 and n2 != n1:
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
                    for arc in rotte[v1]:
                        # n1, n2
                        if arc[0] == n1:
                            flag = 1
                        # dopo n2 -> non vengono modificati
                        if arc[0] == succN1[0]:
                            break

                        # prima di n1
                        if flag == 0:
                            x2TMP[v1, n2, arc[0], arc[1]] = x2[v2, n2, precN2[0], n2]
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
                    for arc in rotte[v2]:
                        # precN2[0], n2
                        if arc[0] == precN2[0]:
                            flag = 1
                        # n2, succN2[0]
                        if arc[0] == n2:
                            flag = 2
                        # dopo succN2[0] -> non vengono modificati
                        if arc[0] == succN2[0]:
                            break

                        # prima di precN2[0]
                        if flag == 0:
                            x2TMP[v2, n2, arc[0], arc[1]] = x2[v2, n2, precN2[0], n2]
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
                    # print("rotte: {}".format(rotte))
                    print("localSearch TRUE, itNonAmmissibili: {}, mossa: {}, differenza costo: {}.".format(
                        itNonAmmissibili, minCostKey, smd10[minCostKey]))
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

            # se n1 e n2 fanno parte della stessa rotta
            if v1 == v2:
                # se (n1, n2) è un arco già presente nella rotta
                if (n1, n2) in rotte[v1]:
                    w2TMP[v1, precN1[0], n2] = 1
                    w2TMP[v1, n2, n1] = 1

                    w2TMP[v1, precN1[0], n1] = 0
                    w2TMP[v1, n1, n2] = 0

                    for gamma in [n1] + succN1:
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

                # n1 e n2 nella stessa rotta ma non (n1, n2)
                else:
                    w2TMP[v1, precN1[0], n1] = 0
                    w2TMP[v1, n1, succN1[0]] = 0
                    w2TMP[v1, precN1[0], n2] = 1
                    w2TMP[v1, n2, succN1[0]] = 1
                    w2TMP[v1, precN2[0], n2] = 0
                    w2TMP[v1, precN2[0], n1] = 1

                    # se n2 ha successori
                    if succN2[0] != -1:
                        w2TMP[v1, n2, succN2[0]] = 0
                        w2TMP[v1, n1, succN2[0]] = 1

                    flag = 0
                    for arc in rotte[v1]:
                        # (precN1, n1)
                        if arc[0] == precN1[0]:
                            flag = 1
                        # (n1, succN1)
                        if arc[0] == n1:
                            flag = 2
                        # (succN1, ...)
                        if arc[0] == succN1[0]:
                            flag = 3
                        # (precN2, n2)
                        if arc[0] == precN2[0]:
                            flag = 4
                        # (n2, succN2)
                        if arc[0] == n2:
                            flag = 5
                        # (succN2, ...)
                        if arc[0] == succN2[0]:
                            break

                        # (precN1, n1)
                        if flag == 1:
                            for gamma in [n1] + succN1:
                                x2TMP[v1, gamma, precN1[0], n1] = 0
                                x2TMP[v1, precN1[0], n2] = x2[v1, gamma, precN1[0], n1]
                        # (n1, succN1)
                        if flag == 2:
                            for gamma in succN1:
                                x2TMP[v1, gamma, n1, succN1[0]] = 0
                                if gamma != n2:
                                    x2TMP[v1, gamma, n2, succN1[0]] = x2[v1, gamma, n1, succN1[0]]
                            x2TMP[v1, n1, n2, succN1[0]] = x2[v1, n1, precN1[0], n1]
                        # (succN1, ...)
                        if flag == 3:
                            x2TMP[v1, n2, arc[0], arc[1]] = 0
                            x2TMP[v1, n1, arc[0], arc[1]] = x2[v1, n1, arc[0], arc[1]]
                        # (precN2, n2)
                        if flag == 4:
                            x2TMP[v1, n2, precN2[0], n2] = 0
                            x2TMP[v1, n1, precN2[0], n1] = x2[v1, n1, precN1[0], n1]
                        # (n2, succN2)
                        if flag == 5:
                            for gamma in succN2:
                                x2TMP[v1, gamma, precN2[0], n2] = 0
                                x2TMP[v1, gamma, precN2[0], n1] = x2[v1, gamma, precN2[0], n2]

                                x2TMP[v1, gamma, n2, succN2[0]] = 0
                                x2TMP[v1, gamma, n1, succN2[0]] = x2[v1, gamma, n2, succN2[0]]

            elif n1 != n2:
                # v1
                # v1: se n2 in v1
                if n2 in [c[1] for c in rotte[v1]]:
                    # in v1: n2 in precN1
                    if n2 in precN1:
                        w2TMP[v1, precN1[0], n1] = 0

                        flag1 = 0
                        flag2 = 0
                        for arc in rotte[v1]:
                            if arc[0] == n1:
                                flag1 = 1
                            if arc[0] == n2:
                                flag2 = 1
                            if arc[0] == succN1[0]:
                                break

                            if flag1 == 0:
                                x2TMP[v1, n1, arc[0], arc[1]] = 0
                            if flag1 == 1:
                                w2TMP[v1, n1, succN1[0]] = 0
                                w2TMP[v1, precN1[0], succN1[0]] = 1
                                for gamma in succN1:
                                    x2TMP[v1, gamma, precN1[0], n1] = 0
                                    x2TMP[v1, gamma, n1, succN1[0]] = 0
                                    x2TMP[v1, gamma, precN1[0], succN1[0]] = x2[v1, gamma, precN1[0], n1]
                            if flag2 == 0:
                                x2TMP[v1, n2, arc[0], arc[1]] += x2[v2, n2, precN2[0], n2]
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

                        flag1 = 0
                        flag2 = 0
                        for arc in rotte[v1]:
                            if arc[0] == n1:
                                flag1 = 1
                            if arc[0] == precN1[0]:
                                flag2 = 1
                            if arc[0] == succN1[0] and arc[0] != n2:
                                flag2 = 0
                            if arc[0] == n2:
                                break

                            if flag1 == 0:
                                x2TMP[v1, n1, arc[0], arc[1]] = 0
                            if flag2 == 0:
                                x2TMP[v1, n2, arc[0], arc[1]] += x2[v2, n2, precN2[0], n2]

                else:
                    # v1: se n1 ha successori
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

                    # v1: sempre
                    # aggiungere arco (precN1, n2)
                    w2TMP[v1, precN1[0], n2] = 1
                    # eliminare arco (precN1, n1)
                    w2TMP[v1, precN1[0], n1] = 0
                    # ak2ij
                    for arc in rotte[v1]:
                        # (n1, succN1[0])
                        if arc[1] == n1:
                            break
                        # aggiungere pallet n2 ai precN1
                        x2TMP[v2, n2, arc[0], arc[1]] = palletN2
                        # eliminare pallet n1 dai precN1
                        x2TMP[v1, n1, arc[0], arc[1]] = 0
                    x2TMP[v2, n2, precN1[0], n2] = palletN2
                    x2TMP[v1, n1, precN1[0], n1] = 0

                # v2
                # v2: se n1 in v2
                if n1 in [c[1] for c in rotte[v2]]:
                    pass
                    # in v2: n1 in precN2
                    if n1 in precN2:
                        w2TMP[v2, precN2[0], n2] = 0

                        flag1 = 0
                        flag2 = 0
                        for arc in rotte[v2]:
                            if arc[0] == n2:
                                flag1 = 1
                            if arc[0] == n1:
                                flag2 = 1
                            if arc[0] == succN2[0]:
                                break

                            if flag1 == 0:
                                x2TMP[v2, n2, arc[0], arc[1]] = 0
                            if flag1 == 1:
                                w2TMP[v2, n2, succN2[0]] = 0
                                w2TMP[v2, precN2[0], succN2[0]] = 1
                                for gamma in succN2:
                                    x2TMP[v2, gamma, precN2[0], n2] = 0
                                    x2TMP[v2, gamma, n2, succN2[0]] = 0
                                    x2TMP[v2, gamma, precN2[0], succN2[0]] = x2[v2, gamma, precN2[0], n2]
                            if flag2 == 0:
                                x2TMP[v2, n1, arc[0], arc[1]] += x2[v1, n1, precN1[0], n1]

                    # in v2: n1 in succN2
                    elif n1 in succN2:
                        w2TMP[v2, precN2[0], n2] = 0
                        w2TMP[v2, n2, succN2[0]] = 0
                        w2TMP[v2, precN2[0], succN2[0]] = 1

                        for gamma in succN2:
                            x2TMP[v2, gamma, precN2[0], n2] = 0
                            x2TMP[v2, gamma, n2, succN2[0]] = 0
                            x2TMP[v2, gamma, precN2[0], succN2[0]] = x2[v2, gamma, precN2[0], n2]

                        x2TMP[v2, n1, precN2[0], succN2[0]] += x2[v1, n1, precN1[0], n1]

                        flag1 = 0
                        flag2 = 0
                        for arc in rotte[v2]:
                            if arc[0] == n2:
                                flag1 = 1
                            if arc[0] == precN2[0]:
                                flag2 = 1
                            if arc[0] == succN2[0] and arc[0] != n1:
                                flag2 = 0
                            if arc[0] == n1:
                                break

                            if flag1 == 0:
                                x2TMP[v2, n2, arc[0], arc[1]] = 0
                            if flag2 == 0:
                                x2TMP[v2, n1, arc[0], arc[1]] += x2[v1, n1, precN1[0], n1]

                else:
                    # v2: se n2 ha successori
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

                    # v2: sempre
                    # aggiungere arco (precN2, n1)
                    w2TMP[v2, precN2[0], n1] = 1
                    # eliminare arco (precN2, n2)
                    w2TMP[v2, precN2[0], n2] = 0
                    for arc in rotte[v2]:
                        # (n2, succN2[0])
                        if arc[1] == n2:
                            break
                        # aggiungere pallet n1 ai precN2
                        x2TMP[v1, n1, arc[0], arc[1]] = palletN1
                        # eliminare pallet n2 dai precN2
                        x2TMP[v2, n2, arc[0], arc[1]] = 0
                    x2TMP[v1, n1, precN2[0], n1] = palletN1
                    x2TMP[v2, n2, precN2[0], n2] = 0

            elif v1 != v2 and n1 == n2:
                for arc in rotte[v1]:
                    if arc[0] == n1:
                        break
                    x2TMP[v1, n1, arc[0], arc[1]] = x2[v2, n2, precN2[0], n2]
                for arc in rotte[v2]:
                    if arc[0] == n2:
                        break
                    x2TMP[v2, n2, arc[0], arc[1]] = x2[v1, n1, precN1[0], n1]

            # verificare ammissibilità
            if verificaSoluzioneAmmissibile(s, x2TMP, w2TMP, uk2, Pgac, PsGa, K2, A2, Gamma, CdiS):
                # print("rotte: {}".format(rotte))
                print(
                    "localSearch TRUE, itNonAmmissibili: {}, mossa: {}, differenza costo: {}.".format(itNonAmmissibili,
                                                                                                      minCostKey, smd11[
                                                                                                          minCostKey]))
                # soluzione ammissibile trovata
                return x2TMP, w2TMP, minCostKey, True
    # non è stata trovata nessuna mossa migliorativa
    # print("rotte: {}".format(rotte))
    print("localSearch FALSE, mossa: -1.")
    return x2, w2, -1, False


# aggiorna le rotte secondo la mossa effettuata (Exchange 1-0)
#
# rotte: dizionario dei percorsi dei veicoli assegnati ad un satellite
# keyLocalSearch: mossa che viene effettuata dal Local Search
# flagAllPallets: in caso di Exchange 1-0, True se vengono spostati tutti i pallet del cliente, altrimenti False
def updateRotteSmd10(rotte, keyLocalSearch, flagAllPallets):
    v1 = keyLocalSearch[0]
    v2 = keyLocalSearch[1]
    n1 = keyLocalSearch[2]
    n2 = keyLocalSearch[3]

    # lista dei nodi precedenti e dei nodi successivi
    precN1, succN1 = trovaPrecSuccList(rotte[v1], n1)
    precN2, succN2 = trovaPrecSuccList(rotte[v2], n2)

    # se viene trattato un cliente splittato sulle rotte v1 e v2
    #
    if n2 in [c[1] for c in rotte[v1]] and v1 != v2 and n1 != n2:
        # v1 non viene modificato
        # v2
        if flagAllPallets:
            index = rotte[v2].index((precN2[0], n2))
            rotte[v2].remove((precN2[0], n2))
            if succN2[0] != -1:
                rotte[v2][index] = (precN2[0], succN2[0])

    # se n1 e n2 sono sullo stesso veicolo
    elif v1 == v2 and ((n1, n2) not in rotte[v1]):
        index = rotte[v1].index((precN2[0], n2))
        if succN2[0] != -1:
            rotte[v1][index + 1] = (precN2[0], succN2[0])
        rotte[v1].remove((precN2[0], n2))
        if precN1[0] == -1:
            index = -1
        else:
            index = [arc[1] for arc in rotte[v1]].index(n1)
            # index = rotte[v1].index((precN1[0], n1))
        if succN1[0] != -1:
            rotte[v1][index + 1] = (n2, succN1[0])
        rotte[v1].insert(index + 1, (n1, n2))

    # l'arco non deve esistere nella soluzione attuale
    # un veicolo non puo' essere spostato dietro se stesso
    elif v1 != v2 and n2 != n1:
        # v1
        if precN1[0] == -1:
            index = -1
        else:
            index = rotte[v1].index((precN1[0], n1))
        if succN1[0] != -1:
            rotte[v1][index + 1] = (n2, succN1[0])
        rotte[v1].insert(index + 1, (n1, n2))
        # v2
        if flagAllPallets:
            index = rotte[v2].index((precN2[0], n2))
            rotte[v2].remove((precN2[0], n2))
            if succN2[0] != -1:
                rotte[v2][index] = (precN2[0], succN2[0])


# aggiorna le rotte secondo la mossa effettuata (Exchange 1-1)
#
# rotte: dizionario dei percorsi dei veicoli assegnati ad un satellite
# keyLocalSearch: mossa che viene effettuata dal Local Search
def updateRotteSmd11(rotte, keyLocalSearch):
    v1 = keyLocalSearch[0]
    v2 = keyLocalSearch[1]
    n1 = keyLocalSearch[2]
    n2 = keyLocalSearch[3]

    # lista dei nodi precedenti e dei nodi successivi
    precN1, succN1 = trovaPrecSuccList(rotte[v1], n1)
    precN2, succN2 = trovaPrecSuccList(rotte[v2], n2)

    # se (n1, n2) è un arco già presente nella rotta
    if v1 == v2:
        if (n1, n2) in rotte[v1]:
            index = rotte[v1].index((n1, n2))
            rotte[v1][index] = (n2, n1)
            rotte[v1][index - 1] = (precN1[0], n2)
            if succN2[0] != -1:
                rotte[v1][index + 1] = (n1, succN2[0])
        else:
            index = rotte[v1].index((precN1[0], n1))
            rotte[v1][index] = (precN1[0], n2)
            rotte[v1][index + 1] = (n2, succN1[0])

            index = rotte[v1].index((precN2[0], n2))
            rotte[v1][index] = (precN2[0], n1)
            if succN2[0] != -1:
                rotte[v1][index + 1] = (n1, succN2[0])

    elif n1 != n2:
        # v1
        # v1: se n2 in v1
        if n2 in [c[1] for c in rotte[v1]]:
            index = rotte[v1].index((precN1[0], n1))
            rotte[v1].remove((precN1[0], n1))
            if succN1[0] != -1:
                rotte[v1][index] = (precN1[0], succN1[0])
        # v1: n2 non è presente in v1
        else:
            index = rotte[v1].index((precN1[0], n1))
            rotte[v1][index] = (precN1[0], n2)
            if succN1[0] != -1:
                rotte[v1][index + 1] = (n2, succN1[0])

        # v2
        # v2: se n1 in v2
        if n1 in [c[1] for c in rotte[v2]]:
            index = rotte[v2].index((precN2[0], n2))
            rotte[v2].remove((precN2[0], n2))
            if succN2[0] != -1:
                rotte[v2][index] = (precN2[0], succN2[0])
        # v2: n1 non è presente in v2
        else:
            index = rotte[v2].index((precN2[0], n2))
            rotte[v2][index] = (precN2[0], n1)
            if succN2[0] != -1:
                rotte[v2][index + 1] = (n1, succN2[0])

    elif v1 != v2 and n1 == n2:
        # non viene effettuata nessuna modifica nelle rotte
        pass


# Tabu Search: risale al nodo padre e aggiunge alla tabu list la mossa appena effettuata
# heapSMD: lista unica dei costi che contiene la variazione della funzione obiettivo in base alle mosse applicate
# smd10: dizionario che contiene la mossa con relativa variazione di costo (1-0 Exchange)
# smd11: dizionario che contiene la mossa con relativa variazione di costo (1-1 Exchange)
# x2: variabile di trasporto del pallet, che rappresenta il numero di pallet che vengono spediti lungo l’arco (i,j)∈A2 al cliente γ∈Γ dal veicolo k∈K2, altrimenti 0
# w2: variabile di instradamento, che vale 1 se il veicolo k∈K2 attraversa l’arco (i,j)∈A2, altrimenti 0
# rotte: dizionario dei percorsi dei veicoli assegnati ad un satellite
# cost: costo della soluzione
# padreDiAttuale: l'ultimo padre di soluzionePrecedente
# padriDiAttuale: tutti i padri di soluzionePrecedente
#
# dictSolutionsDiS: lista di soluzioni del satellite s
# soluzionePrecedente: indice della soluzione da cui non si possono effettuare altre mosse migliorative, quindi si risale verso il padre
# tabuListDiS: tabu list del satellite s
# oldKeyLocalSearch: chiave della mossa appena effettuata
# nik2ij: costo di instradamento del veicolo k∈K2 che attraversa l’arco (i,j)∈A2 nel secondo livello.
# ak2ij: costo di trasporto del pallet con destinazione γ∈Γ che attraversa l’arco (i,j)∈A2 con il veicolo k∈K2
# s: satellite
def tabuSearch(dictSolutionsDiS, soluzionePrecedente, tabuListDiS, oldKeyLocalSearch, nik2ij, ak2ij, s):
    print("\nSTART tabuSearch()")
    # prende i padri di soluzionePrecedente
    padriDiAttuale = deepcopy(dictSolutionsDiS[soluzionePrecedente][4])
    padreDiAttuale = padriDiAttuale[-1]

    # prende i valori del padre per poter salire ad esso
    cost = deepcopy(dictSolutionsDiS[padreDiAttuale][0])
    x2 = deepcopy(dictSolutionsDiS[padreDiAttuale][1])
    w2 = deepcopy(dictSolutionsDiS[padreDiAttuale][2])
    rotte = deepcopy(dictSolutionsDiS[padreDiAttuale][3])

    # aggiornamento della Tabu list
    # se è stata trovata una nuova soluzione dopo aver effettuato una volta il tabu search
    if oldKeyLocalSearch != -1:
        tabuListDiS.append((padreDiAttuale, deepcopy(oldKeyLocalSearch)))
    # non è stata trovata una nuova soluzione dopo aver effettuato una volta il tabu search
    else:
        tabuListDiS.append((padreDiAttuale, deepcopy(dictSolutionsDiS[soluzionePrecedente][6][-1])))

    # struttura che contiene tutte le mosse con relativi costi
    # dizionari di smd con chiave move point
    smd10 = {}
    smd11 = {}
    # vengono inizializzati gli SMD
    inizializzaSMD10(smd10, rotte, nik2ij, ak2ij, x2, s)
    inizializzaSMD11(smd11, rotte, nik2ij, ak2ij, x2)

    # print("stampa tabuList: {}".format(tabuListDiS))

    # eliminare le mosse tabu dagli SMD
    for mossaTabu in tabuListDiS:
        # print("mossaTabu deleted: ", mossaTabu)
        if mossaTabu[0] == padreDiAttuale:
            # 1-0 Exchange
            if len(mossaTabu[1]) == 5:
                del smd10[mossaTabu[1]]
            # 1-1 Exchange
            elif len(mossaTabu[1]) == 4:
                del smd11[mossaTabu[1]]

    # crea la lista unica dei costi in cui verrà salvato l'heap
    # non usare list(smd10.values()) direttamente perché tale lista non è modificabile e quindi non sarà un heap
    heapSMD = list(smd10.values()) + list(smd11.values())
    # crea l'heap di smd10 e smd11
    heapq.heapify(heapSMD)

    return heapSMD, smd10, smd11, x2, w2, rotte, cost, padreDiAttuale, padriDiAttuale

# scrive su file tutte le soluzioni trovate
def writeOutput(nomeFileInput, s, dictSolutions, bestSolutionIndice, timeElapsed, itMosseLS, itMosseTS):
    # creazione cartella
    print("\nOutput file, s: {}.".format(s))

    pathlib.Path('output').mkdir(parents=True, exist_ok=True)

    filename = pathlib.Path("output/" + nomeFileInput)
    # per creare file con numero che va ad aumentare:
    # verificare numero di file già esistenti nella cartella che iniziano con nomeFileinput

    filename.touch(exist_ok=True)  # will create file, if it exists will do nothing

    file = open(filename, 'a')
    file.write("s: {}".format(s))
    file.write("\ndictSolutions[{}]:".format(s))
    for solution in dictSolutions[s]:
        file.write(
            "\n{} -> costo: {}, rotte: {}, padri: {}, figli: {}, mosse: {}".format(dictSolutions[s].index(solution),
                                                                                   solution[0], solution[3],
                                                                                   solution[4], solution[5],
                                                                                   solution[6]))
    file.write("\nbestSolutionIndice: {}".format(bestSolutionIndice))
    file.write("\n{} -> costo: {}, rotte: {}, padri: {}, figli: {}, mosse: {}".format(bestSolutionIndice,
                                                                                      dictSolutions[s][
                                                                                          bestSolutionIndice][0],
                                                                                      dictSolutions[s][
                                                                                          bestSolutionIndice][3],
                                                                                      dictSolutions[s][
                                                                                          bestSolutionIndice][4],
                                                                                      dictSolutions[s][
                                                                                          bestSolutionIndice][5],
                                                                                      dictSolutions[s][
                                                                                          bestSolutionIndice][6]))
    # pallet
    trasportoPalletDiGamma = {}
    for k in dictSolutions[s][bestSolutionIndice][3]:
        trasportoPalletDiGamma[k] = []
        for arc in dictSolutions[s][bestSolutionIndice][3][k]:
            trasportoPalletDiGamma[k].append(
                (arc[1], dictSolutions[s][bestSolutionIndice][1][k, arc[1], arc[0], arc[1]]))
    file.write("\ntrasportoPalletDiGamma: {}".format(trasportoPalletDiGamma))
    file.write("\nitMosseLS: {}, itMosseTS: {}".format(itMosseLS, itMosseTS))
    file.write("\ntime elapsed: {:.2f}s.\n\n\n".format(timeElapsed))

    file.close()

# scrive su file la soluzione iniziale e la best solution
def writeOutputStartBest(nomeFileInput, s, dictSolutions, bestSolutionIndice, timeElapsed, itMosseLS, itMosseTS):
    # creazione cartella
    print("\nOutput file: start - best, s: {}.".format(s))

    pathlib.Path('output').mkdir(parents=True, exist_ok=True)

    filename = pathlib.Path("output/" + nomeFileInput + "_StartBest")
    # per creare file con numero che va ad aumentare:
    # verificare numero di file già esistenti nella cartella che iniziano con nomeFileinput

    filename.touch(exist_ok=True)  # will create file, if it exists will do nothing

    file = open(filename, 'a')
    file.write("s: {}".format(s))

    # scrittura file soluzione iniziale
    file.write("\nsoluzione iniziale: {}".format(0))
    file.write(
        "\n{} -> \ncosto: {}, \nrotte: {}".format(0, dictSolutions[s][0][0], dictSolutions[s][0][3]))
    # pallet
    trasportoPalletDiGamma = {}
    for k in dictSolutions[s][0][3]:
        trasportoPalletDiGamma[k] = []
        for arc in dictSolutions[s][0][3][k]:
            trasportoPalletDiGamma[k].append(
                (arc[1], dictSolutions[s][0][1][k, arc[1], arc[0], arc[1]]))
    file.write("\ntrasportoPalletDiGamma: {}".format(trasportoPalletDiGamma))

    # scrittura file soluzione finale
    file.write("\nbestSolutionIndice: {}".format(bestSolutionIndice))
    file.write("\n{} -> \ncosto: {}, \nrotte: {}".format(bestSolutionIndice, dictSolutions[s][bestSolutionIndice][0],
                                                         dictSolutions[s][bestSolutionIndice][3]))
    # pallet
    trasportoPalletDiGamma = {}
    for k in dictSolutions[s][bestSolutionIndice][3]:
        trasportoPalletDiGamma[k] = []
        for arc in dictSolutions[s][bestSolutionIndice][3][k]:
            trasportoPalletDiGamma[k].append(
                (arc[1], dictSolutions[s][bestSolutionIndice][1][k, arc[1], arc[0], arc[1]]))
    file.write("\ntrasportoPalletDiGamma: {}".format(trasportoPalletDiGamma))
    file.write("\nitMosseLS: {}, itMosseTS: {}".format(itMosseLS, itMosseTS))
    file.write("\nnumero di soluzioni totali trovati: {}.".format(len(dictSolutions[s])))
    file.write("\ntime elapsed: {:.2f}s.\n\n\n".format(timeElapsed))

    file.close()

def writeOutputStartBestwriteOutputStartBestAssoluta(nomeFileInput, Sneg, bestSolution):
    # scrittura su file della bestSolution in assoluto
    pathlib.Path('output').mkdir(parents=True, exist_ok=True)
    filename = pathlib.Path("output/" + nomeFileInput + "_StartBest")
    filename.touch(exist_ok=True)  # will create file, if it exists will do nothing

    file = open(filename, 'a')
    file.write("##########################################################################################\n")
    file.write("##########################################################################################\n")
    file.write("##########################################################################################\n")
    file.write("Soluzione migliore in assoluto trovata:\n")
    for s in Sneg:
        file.write("\ns: {}".format(s))
        file.write("\ncosto: {}, \nrotte: {}".format(bestSolution[s][0], bestSolution[s][3]))
        # pallet
        trasportoPalletDiGamma = {}
        for k in bestSolution[s][3]:
            trasportoPalletDiGamma[k] = []
            for arc in bestSolution[s][3][k]:
                trasportoPalletDiGamma[k].append(
                    (arc[1], bestSolution[s][1][k, arc[1], arc[0], arc[1]]))
        file.write("\ntrasportoPalletDiGamma: {}".format(trasportoPalletDiGamma))
    file.close()