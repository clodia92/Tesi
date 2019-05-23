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

    return (vincolo29 and vincolo30 and vincolo31 and vincolo32 and vincolo34 and vincolo35 and vincolo36)