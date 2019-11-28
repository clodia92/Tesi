import heapq
from copy import deepcopy
from random import shuffle
import pathlib

from functions import *

# key: chiave della mossa appena effettuata
# smd11: Vecchio smd da aggiornare
# rotte: rotte aggiornate dopo la mossa
# x2: x2 old
# x2TMP: x2 aggiornato dopo la mossa
# n1InV2: indica se n1 è presente in v2 prima di effettuare la mossa
# n2InV1: indica se n2 è presente in v1 prima di effettuare la mossa
def updateSMD(key, smd11, rotte, x2, x2TMP, n1InV2, n2InV1):
    v1Mossa = key[0]
    v2Mossa = key[1]
    n1Mossa = key[2]
    n2Mossa = key[3]

    precN1Mossa, succN1Mossa = trovaPrecSuccList(rotte[v1Mossa], n1Mossa)
    precN2Mossa, succN2Mossa = trovaPrecSuccList(rotte[v2Mossa], n2Mossa)

    # flag1 è True finchè non si supera n1 sulla rotta v1
    flag1 = True
    # flag2 è True finchè non si supera n2 sulla rotta v2
    flag2 = True


    for k in rotte:
        # indica se n1 e n2 sono presenti nella rotta aggiornata
        n1InRotta = False
        n2InRotta = False
        for arc in rotte[k]:
            if arc[1] == n1Mossa and k != v2Mossa:
                n1InRotta = True
            if arc[1] == n2Mossa and k != v1Mossa:
                n2InRotta = True


        for arc in rotte[k]:
            # applicare le regole per n1
            if k == v1Mossa and n1Mossa == arc[1]:
                flag1 = False
            else:

                if flag1 == True:
                    # (k, v1Mossa, arc[1], n1Mossa)
                    pass
                else:
                    # (v1Mossa, k, n1Mossa, arc[1])
                    pass

            # applicare le regole per n2
            if k == v2Mossa and n2Mossa == arc[1]:
                flag2 = False
            else:

                if flag2 == True:
                    # (k, v2Mossa, arc[1], n2Mossa)
                    pass
                else:
                    # (v2Mossa, k, n2Mossa, arc[1])
                    pass


def updateSMDold(key, smd10, smd11, rotte, nik2ij, ak2ij, x2, x2TMP, w2, w2TMP, numeroTotPallet):
    # lista dei nodi precedenti e dei nodi successivi
    precN1, succN1 = trovaPrecSuccList(rotte[key[0]], key[2])
    precN2, succN2 = trovaPrecSuccList(rotte[key[1]], key[3])

    if len(key) == 5:
        updateSMD10_10(key, smd10, numeroTotPallet, nik2ij, ak2ij, x2, x2TMP, w2, w2TMP, precN1, precN2, succN1, succN2)
        updateSMD10_11(key, smd11, nik2ij, ak2ij, x2, x2TMP, w2, w2TMP, precN2, succN1, succN2)
    if len(key) == 4:
        updateSMD11_10(key, smd10, nik2ij, ak2ij, x2, x2TMP, w2, w2TMP, precN1, precN2, succN1, succN2)
        updateSMD11_11(key, smd11, nik2ij, ak2ij, x2, x2TMP, w2, w2TMP, precN1, precN2, succN1, succN2)

def updateSMD10_10(key, smd10, numeroTotPallet, nik2ij, ak2ij, x2, x2TMP, w2, w2TMP, precN1, precN2, succN1, succN2):
    # estraggo la chiave
    v1 = key[0]
    v2 = key[1]
    n1 = key[2]
    n2 = key[3]
    numeroPallet = key[4]

    # se vengono spostati tutti i pallet: arco precN2-n2 e/o n2-succN2 eliminato/i
    if numeroPallet == numeroTotPallet and v1 != v2:
        for mossa, value in smd10.items:
            # n1 = A
            # + (n1 - n2) , - (n1 - succN1)
            if mossa[2] == n1 and mossa[0] == v1 :
                # non sono sicura
                smd10[mossa[0], mossa[1], n1, mossa[3], mossa[4]] += (x2TMP[v1, n2, n1, n2] * ak2ij[v1, n1, n2]) # numeroPallet
                if succN1[0] != -1:
                    for gamma in succN1:
                        smd10[mossa[0], mossa[1], n1, mossa[3], mossa[4]] -= (x2[mossa[0], gamma, n1, succN1[0]] * ak2ij[mossa[0], n1, succN1[0]])
                        smd10[mossa[0], mossa[1], n1, mossa[3], mossa[4]] += (x2TMP[mossa[0], gamma, n1, succN1[0]] * ak2ij[mossa[0], n1, succN1[0]])

                        smd10[mossa[0], mossa[1], n2, succN1[0], mossa[4]] += (x2TMP[v1, gamma, n2, succN1[0]] * ak2ij[v1, n2, succN1[0]])
                if precN1[0] != -1:
                    for gamma in precN1:
                        smd10[mossa[0], mossa[1], n1, succN1[0], mossa[4]] += (x2TMP[v1, gamma, n2, succN1[0]] * ak2ij[v1, n2, succN1[0]])


def updateSMD10_11(key, smd11, nik2ij, ak2ij, x2, x2TMP, w2, w2TMP, precN2, succN1, succN2):
    # test
    return

def updateSMD11_10(key, smd10, nik2ij, ak2ij, x2Old, x2New, w2Old, w2New, precN1, precN2, succN1, succN2):
    # estraggo la chiave
    v1 = key[0]
    v2 = key[1]
    n1 = key[2]
    n2 = key[3]

    for keySMD10, valueSMD10 in smd10.items():
        # n1
        # n1 = pred(A)
        if keySMD10[0] == v1 and keySMD10[2] == precN1:
            pass
        # n1 = A
        if keySMD10[0] == v1 and keySMD10[2] == n1:
            pass
        # n1 = pred(B)
        if keySMD10[1] == v2 and keySMD10[2] == precN2:
            pass
        # n1 = B
        if keySMD10[1] == v2 and keySMD10[2] == n2:
            pass

        # n2
        # n2 = pred(A)
        if keySMD10[0] == v1 and keySMD10[3] == precN1:
            pass
        # n2 = A
        if keySMD10[0] == v1 and keySMD10[3] == n1:
            pass
        # n2 = succ(A)
        if keySMD10[0] == v1 and keySMD10[3] == succN1:
            pass
        # n2 = pred(B)
        if keySMD10[1] == v2 and keySMD10[3] == precN2:
            pass
        # n2 = B
        if keySMD10[1] == v2 and keySMD10[3] == n2:
            pass
        # n2 = succ(B)
        if keySMD10[1] == v2 and keySMD10[3] == succN2:
            pass

def updateSMD11_11(key, smd11, nik2ij, ak2ij, x2Old, x2New, w2Old, w2New, precN1, precN2, succN1, succN2):
    return