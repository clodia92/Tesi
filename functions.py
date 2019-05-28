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

def inizializzaSMD10(smd10, rotte, nik2ij, ak2ij, x2, w2, s, K2, Gamma):
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
