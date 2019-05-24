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
    veicoliDiCliente = {}
    for k in rotte:
        for c in rotte[k]:
            if c[1] in veicoliDiCliente:
                veicoliDiCliente[c[1]] += [k]
            else:
                veicoliDiCliente[c[1]] = [k]

    x = 0
    for k in rotte:
        listCustomer = [s]+[c2 for c1,c2 in rotte[k]]
        for n1 in listCustomer:
            for n2 in Gamma:
                #print(list(w2.keys())[list(w2.values()).index(1)])

                #any(j == n2 for (kappa, i, j) in w2)
                if n2!=n1:
                    # DA CORREGGERE
                    # smd10[k, n1, n2] = nik2ij[(k, n2, n1)] + ak2ij[(k, n2, n1)]
                    x += 1
    print("x: ", x)
    # smd10[k, n1, n2] for k in K2 for n1 in Gamma for n2 in s + Gamma