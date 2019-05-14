import pulp


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
def buildOFThree(K2diS, GammadiS, w2, aks, A2, nik2ij, x2, ak2ij, sat):
    print("BuildOF Three")

    myObjFunction = pulp.LpAffineExpression()

    # mySumVariable = {}

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:

        # TERMINE DA TOGLIERE COL <= 1
        # for all customers in the "s" satellite
        #         for j in GammadiS[sat]:
        #             #print("GammadiS[1]", GammadiS[sat])
        #
        #             myObjFunction += w2[(k,sat,j)] * aks[(k,sat)]
        #             pass

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

    # myObjFunction += pulp.LpAffineExpression(mySumVariable)

    return myObjFunction


# generate Constraint 29
def BuildConstr29(myModelThree, GammadiS, x2, K2diS, PsGa, sat):
    print("BuildConstr29")

    # for all customers
    for ga in GammadiS[sat]:
        myModelThree += pulp.lpSum([[x2[(k, ga, sat, j)] for k in K2diS[sat]] for j in GammadiS[sat] if sat != j]) == (
            PsGa[(sat, ga)]), "C29_ga_%s" % (ga)
        pass
    pass


# generate Constraint 30
def BuildConstr30(myModelThree, GammadiS, x2, K2diS, Pgac, CdiS, sat):
    print("BuildConstr30")

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all customers
    for ga in GammadiS[sat]:
        myModelThree += pulp.lpSum(
            [[x2[(k, ga, i, ga)] for k in K2diS[sat] if x2.has_key((k, ga, i, ga))] for i in parcheggio + GammadiS[sat]
             if i != ga]) == ([Pgac[(c, ga)] for c in CdiS[sat] if Pgac.has_key((c, ga))]), "C30_ga_%s" % (ga)
        pass
    pass


# generate Constraint 31
def BuildConstr31(myModelThree, GammadiS, K2diS, x2, sat):
    print("BuildConstr31")

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all customers in the "s" satellite
    for ga_1 in GammadiS[sat]:
        # for all customers in the "s" satellite
        for ga_2 in GammadiS[sat]:

            if ga_1 != ga_2:

                # for all vehicles in the "s" satellite
                for k in K2diS[sat]:
                    myModelThree += pulp.lpSum([x2[(k, ga_1, i, ga_2)] for i in parcheggio + GammadiS[sat] if
                                                i != ga_2 and x2.has_key((k, ga_1, i, ga_2))]) == (
                                        [x2[(k, ga_1, ga_2, i)] for i in GammadiS[sat] if
                                         ga_2 != i and x2.has_key((k, ga_1, ga_2, i))]), "C31_ga1_%s_ga2_%s_k_%s" % (
                                        ga_1, ga_2, k)
                    pass
                pass
            pass
        pass
    pass


# generate Constraint 32
def BuildConstr32(myModelThree, K2diS, w2, GammadiS, sat):
    print("BuildConstr32")

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:
        myModelThree += pulp.lpSum([w2[(k, sat, j)] for j in GammadiS[sat]]) <= 1, "C32_k2_%s" % (k)
        pass
    pass


# generate Constraint 33
# def BuildConstr33EXVINCOLO33(myModelThree, w2, K2diS, GammadiS, vs, sat):
#         
#     print "BuildConstr33EXVINCOLO33"
# 
#     myModelThree += pulp.lpSum([[w2[(k,sat,j)] for k in K2diS[sat]] for j in GammadiS[sat]]) <= ([vs[sat]]), "C33_s_%s"%(sat)
#     pass

# generate Constraint 34
def BuildConstr34(myModelThree, K2diS, GammadiS, w2, sat):
    print("BuildConstr34")

    parcheggio = [sat]  # mi serve per poter sommare 2 liste

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:
        # for all customers in the "s" satellite
        for j in GammadiS[sat]:
            myModelThree += pulp.lpSum(
                [w2[(k, i, j)] for i in parcheggio + GammadiS[sat] if i != j and w2.has_key((k, i, j))]) >= (
                                [w2[(k, j, l)] for l in GammadiS[sat] if
                                 j != l and w2.has_key((k, j, l))]), "C34_k2_%s_j_%s" % (k, j)
            pass
        pass
    pass


# generate Constraint 35
def BuildConstr35(myModelThree, K2diS, A2, x2, GammadiS, uk2, w2, sat):
    print("BuildConstr35")

    # for all vehicles in the "s" satellite
    for k in K2diS[sat]:
        # for all arcs in A2
        for i, j in A2:

            if i != j:
                myModelThree += pulp.lpSum([x2[(k, ga, i, j)] for ga in GammadiS[sat]]) <= (
                    [uk2[k] * w2[(k, i, j)]]), "C35_k2_%s_i_%s_j_%s" % (k, i, j)
                pass
            pass
        pass
    pass


# generate Constraint 36
def BuildConstr36(myModelThree, K2diS, GammadiS, w2, sat):
    print("BuildConstr36")

    for k in K2diS[sat]:
        for i in GammadiS[sat]:
            for j in GammadiS[sat]:
                if i != j:
                    myModelThree += pulp.lpSum([w2[(k, i, j)] + w2[(k, j, i)]]) <= 1, "C36_k2_%s_i_%s_j_%s" % (k, i, j)
                    pass
                pass
            pass
        pass
