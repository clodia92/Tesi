# -*- coding: utf-8 -*-

# generate Objective Function for model Three
def computeCost(x2, w2, K2diS, GammadiS, A2, nik2ij, ak2ij, sat):
    myObjFunction = 0

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:

        # for all arcs in A2
        for i, j in A2:
            # print("A2", A2)

            if i != j:

                myObjFunction += w2[(k, i, j)] * nik2ij[(k, i, j)]

                # for all customers in the "s" satellite
                for ga in GammadiS[sat]:
                    # print("GammadiS[1]", GammadiS[sat])

                    myObjFunction += x2[(k, ga, i, j)] * ak2ij[(k, i, j)]
                    pass
                pass
            pass
        pass

    return myObjFunction


# generate Objective Function for model Three with penalty
def computeCostPenalty(x2, w2, K2diS, GammadiS, A2, nik2ij, ak2ij, sat, infeasibleK2, penalty):
    cost = 0

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:
        tmpCost = 0
        # for all arcs in A2
        for i, j in A2:
            # print("A2", A2)

            if i != j:

                tmpCost += w2[(k, i, j)] * nik2ij[(k, i, j)]

                # for all customers in the "s" satellite
                for ga in GammadiS[sat]:
                    # print("GammadiS[1]", GammadiS[sat])

                    tmpCost += x2[(k, ga, i, j)] * ak2ij[(k, i, j)]

        # se la capacità di k viene superata, penalizza la rotta
        if k in infeasibleK2:
            # print("penalizzare rotta: {}, costo: {}, penalty: {}".format(k, tmpCost, penalty))
            tmpCost += tmpCost / 100 * penalty

        cost += tmpCost

    return cost


# generate Constraint 29
def BuildConstr29(GammadiS, x2, K2, PsGa, sat):
    vincolo29 = True

    # for all customers
    for ga in GammadiS:
        vincolo29 = (sum([x2[(k, ga, sat, j)] for k in K2 for j in GammadiS if sat != j]) == (
            PsGa[(sat, ga)]))
        if (not vincolo29):
            return vincolo29

    return vincolo29


# generate Constraint 30
def BuildConstr30(GammadiS, x2, K2, Pgac, CdiS, sat):
    vincolo30 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all customers
    for ga in GammadiS:
        vincolo30 = (sum([x2[(k, ga, i, ga)] for k in K2 for i in
                          parcheggio + GammadiS if ((k, ga, i, ga) in x2) if i != ga]) ==
                     sum([Pgac[(c, ga)] for c in CdiS[sat] if ((c, ga) in Pgac)]))
        if (not vincolo30):
            return vincolo30

    return vincolo30


# generate Constraint 31
def BuildConstr31(GammadiS, K2, x2, sat):
    vincolo31 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all customers in the "s" satellite
    for ga_1 in GammadiS:
        # for all customers in the "s" satellite
        for ga_2 in GammadiS:

            if ga_1 != ga_2:

                # for all vehicles in the "s" satellite
                for k in K2:
                    vincolo31 = sum([x2[(k, ga_1, i, ga_2)] for i in parcheggio + GammadiS if
                                     i != ga_2 and (k, ga_1, i, ga_2) in x2]) == sum(
                        [x2[(k, ga_1, ga_2, i)] for i in GammadiS if
                         ga_2 != i and (k, ga_1, ga_2, i) in x2])
                    if (not vincolo31):
                        return vincolo31

    return vincolo31


# generate Constraint 32
def BuildConstr32(K2, w2, GammadiS, sat):
    vincolo32 = True

    # for all vehicles in the "s" satellite
    for k in K2:
        vincolo32 = sum([w2[(k, sat, j)] for j in GammadiS]) <= 1
        if (not vincolo32):
            return vincolo32

    return vincolo32


# generate Constraint 34
def BuildConstr34(K2, GammadiS, w2, sat):
    vincolo34 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all vehicles in the "s" satellite
    for k in K2:
        # for all customers in the "s" satellite
        for j in GammadiS:
            vincolo34 = sum([w2[(k, i, j)] for i in parcheggio + GammadiS if i != j and (k, i, j) in w2]) >= sum(
                [w2[(k, j, l)] for l in GammadiS if
                 j != l and (k, j, l) in w2])
            if (not vincolo34):
                return vincolo34

    return vincolo34


# generate Constraint 35
def BuildConstr35(K2, A2, x2, GammadiS, uk2, w2, sat, uk2increased):
    vincolo35 = True

    # for all vehicles in the "s" satellite
    for k in K2:
        # for all arcs in A2
        for i, j in A2:

            if i != j:
                vincolo35 = sum([x2[(k, ga, i, j)] for ga in GammadiS]) <= (uk2[k] * w2[(k, i, j)])
                if (not vincolo35):
                    return vincolo35

    return vincolo35


# generate Constraint 36
def BuildConstr36(K2, GammadiS, w2, sat):
    vincolo36 = True

    for k in K2:
        for i in GammadiS:
            for j in GammadiS:
                if i != j:
                    vincolo36 = (w2[(k, i, j)] + w2[(k, j, i)]) <= 1
                    if (not vincolo36):
                        return vincolo36

    return vincolo36
