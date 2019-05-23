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
def computeCost(K2diS, GammadiS, w2, aks, A2, nik2ij, x2, ak2ij, sat):
    print("computeCost")

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
def BuildConstr29(GammadiS, x2, K2diS, PsGa, sat):
    print("BuildConstr29")

    vincolo29 = True

    # for all customers
    for ga in GammadiS[sat]:
        vincolo29 = (sum([x2[(k, ga, sat, j)] for k in K2diS[sat] for j in GammadiS[sat] if sat != j]) == (PsGa[(sat, ga)]))
        if (not vincolo29):
            return vincolo29

    return vincolo29


# generate Constraint 30
def BuildConstr30(GammadiS, x2, K2diS, Pgac, CdiS, sat):
    print("BuildConstr30")

    vincolo30 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all customers
    for ga in GammadiS[sat]:
        vincolo30 = (sum([x2[(k, ga, i, ga)] for k in K2diS[sat] for i in
                       parcheggio + GammadiS[sat] if ((k, ga, i, ga) in x2) if i != ga]) ==
                     sum([Pgac[(c, ga)] for c in CdiS[sat] if ((c, ga) in Pgac)]))
        if (not vincolo30):
            return vincolo30

    return vincolo30


# generate Constraint 31
def BuildConstr31(GammadiS, K2diS, x2, sat):
    print("BuildConstr31")

    vincolo31 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all customers in the "s" satellite
    for ga_1 in GammadiS[sat]:
        # for all customers in the "s" satellite
        for ga_2 in GammadiS[sat]:

            if ga_1 != ga_2:

                # for all vehicles in the "s" satellite
                for k in K2diS[sat]:
                    vincolo31 = sum([x2[(k, ga_1, i, ga_2)] for i in parcheggio + GammadiS[sat] if
                                  i != ga_2 and (k, ga_1, i, ga_2) in x2]) == sum(
                                    [x2[(k, ga_1, ga_2, i)] for i in GammadiS[sat] if
                                     ga_2 != i and (k, ga_1, ga_2, i) in x2])
                    if (not vincolo31):
                        return vincolo31

    return vincolo31


# generate Constraint 32
def BuildConstr32(K2diS, w2, GammadiS, sat):
    print("BuildConstr32")

    vincolo32 = True

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:
        vincolo32 = sum([w2[(k, sat, j)] for j in GammadiS[sat]]) <= 1
        if (not vincolo32):
            return vincolo32

    return vincolo32


# generate Constraint 34
def BuildConstr34(K2diS, GammadiS, w2, sat):
    print("BuildConstr34")

    vincolo34 = True

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:
        # for all customers in the "s" satellite
        for j in GammadiS[sat]:
            vincolo34 = sum([w2[(k, i, j)] for i in parcheggio + GammadiS[sat] if i != j and (k, i, j) in w2]) >= sum(
                [w2[(k, j, l)] for l in GammadiS[sat] if
                 j != l and (k, j, l) in w2])
            if (not vincolo34):
                return vincolo34

    return vincolo34


# generate Constraint 35
def BuildConstr35(K2diS, A2, x2, GammadiS, uk2, w2, sat):
    print("BuildConstr35")

    vincolo35 = True

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:
        # for all arcs in A2
        for i, j in A2:

            if i != j:
                vincolo35 = sum([x2[(k, ga, i, j)] for ga in GammadiS[sat]]) <= (
                    uk2[k] * w2[(k, i, j)])
                if (not vincolo35):
                    return vincolo35

    return vincolo35


# generate Constraint 36
def BuildConstr36(K2diS, GammadiS, w2, sat):
    print("BuildConstr36")

    vincolo36 = True

    for k in K2diS[sat]:
        for i in GammadiS[sat]:
            for j in GammadiS[sat]:
                if i != j:
                    vincolo36 = (w2[(k, i, j)] + w2[(k, j, i)]) <= 1
                    if (not vincolo36):
                        return vincolo36

    return vincolo36
