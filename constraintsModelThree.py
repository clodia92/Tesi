# # generate Objective Function for model Three
# def buildOFThree(K2diS, GammadiS, w2, aks, A2, nik2ij, x2, ak2ij, sat):
#           
#     print "BuildOF Three"
#   
#     myObjFunction = pulp.LpAffineExpression()
#         
#     mySumVariable = {}
#     
#     # for all vehicles in the "s" satellite
#     for k in K2diS[sat]:
#         #print("K2diS[1] = ", K2diS[sat])
#         # for all customers in the "s" satellite
#         for j in GammadiS[sat]:
#             #print("GammadiS[1]", GammadiS[sat])
#                 
#             mySumVariable[w2[(k,sat,j)]] = aks[(k,sat)]                
#             pass
#             
#         # for all arcs in A2
#         for i,j in A2:
#             #print("A2", A2)
#                 
#             if i != j:
#                 
#                 mySumVariable[w2[(k,i,j)]] = nik2ij[(k,i,j)]
#                 
#                 # for all customers in the "s" satellite
#                 for ga in GammadiS[sat]:
#                     #print("GammadiS[1]", GammadiS[sat])
#                                     
#                     mySumVariable[x2[(k,ga,i,j)]] = ak2ij[(k,i,j)]  
#                     pass                  
#                 pass                
#             pass            
#         pass
#    
#     myObjFunction += pulp.LpAffineExpression(mySumVariable)
#     
#     return myObjFunction

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


# generate Constraint 29
def BuildConstr29(Gamma, x2, K2, PsGa, sat):
    vincolo29 = True

    # for all customers
    for ga in Gamma:
        vincolo29 = (sum([x2[(k, ga, sat, j)] for k in K2 for j in Gamma if sat != j]) == (
        PsGa[(sat, ga)]))
        if (not vincolo29):
            return vincolo29

    return vincolo29


# generate Constraint 30
def BuildConstr30(Gamma, x2, K2, Pgac, CdiS, sat):
    vincolo30 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all customers
    for ga in Gamma:
        vincolo30 = (sum([x2[(k, ga, i, ga)] for k in K2 for i in
                          parcheggio + Gamma if ((k, ga, i, ga) in x2) if i != ga]) ==
                     sum([Pgac[(c, ga)] for c in CdiS[sat] if ((c, ga) in Pgac)]))
        if (not vincolo30):
            return vincolo30

    return vincolo30


# generate Constraint 31
def BuildConstr31(Gamma, K2, x2, sat):
    vincolo31 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all customers in the "s" satellite
    for ga_1 in Gamma:
        # for all customers in the "s" satellite
        for ga_2 in Gamma:

            if ga_1 != ga_2:

                # for all vehicles in the "s" satellite
                for k in K2:
                    vincolo31 = sum([x2[(k, ga_1, i, ga_2)] for i in parcheggio + Gamma if
                                     i != ga_2 and (k, ga_1, i, ga_2) in x2]) == sum(
                        [x2[(k, ga_1, ga_2, i)] for i in Gamma if
                         ga_2 != i and (k, ga_1, ga_2, i) in x2])
                    if (not vincolo31):
                        return vincolo31

    return vincolo31


# generate Constraint 32
def BuildConstr32(K2, w2, Gamma, sat):
    vincolo32 = True

    # for all vehicles in the "s" satellite
    for k in K2:
        vincolo32 = sum([w2[(k, sat, j)] for j in Gamma]) <= 1
        if (not vincolo32):
            return vincolo32

    return vincolo32


# generate Constraint 34
def BuildConstr34(K2, Gamma, w2, sat):
    vincolo34 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all vehicles in the "s" satellite
    for k in K2:
        # for all customers in the "s" satellite
        for j in Gamma:
            vincolo34 = sum([w2[(k, i, j)] for i in parcheggio + Gamma if i != j and (k, i, j) in w2]) >= sum(
                [w2[(k, j, l)] for l in Gamma if
                 j != l and (k, j, l) in w2])
            if (not vincolo34):
                return vincolo34

    return vincolo34


# generate Constraint 35
def BuildConstr35(K2, A2, x2, Gamma, uk2, w2, sat):
    vincolo35 = True

    # for all vehicles in the "s" satellite
    for k in K2:
        # for all arcs in A2
        for i, j in A2:

            if i != j:
                vincolo35 = sum([x2[(k, ga, i, j)] for ga in Gamma]) <= (
                        uk2[k] * w2[(k, i, j)])
                if (not vincolo35):
                    return vincolo35

    return vincolo35


# generate Constraint 36
def BuildConstr36(K2, Gamma, w2, sat):
    vincolo36 = True

    for k in K2:
        for i in Gamma:
            for j in Gamma:
                if i != j:
                    vincolo36 = (w2[(k, i, j)] + w2[(k, j, i)]) <= 1
                    if (not vincolo36):
                        return vincolo36

    return vincolo36
