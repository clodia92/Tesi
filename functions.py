# generate variables for Model Three
def generateVariablesModelThree(x2, w2, K2diS, GammadiS, A2, sat):
    
    #generate Variables x2
    # for all vehicles (second echelon)
    for k in K2diS[sat]:
        # for all customers in GammadiS
        for ga in GammadiS[sat]:
            # for all arcs in A2
            for i,j in A2:                    
                     
                if i!=j:           
                    myx2Index = (k,ga,i,j)

                    x2[myx2Index] = 0
                    pass
                pass
            pass
        pass
    
    #generate Variables w2
    # for all vehicles (second echelon)
    for k in K2diS[sat]:
        # for all arcs in A2
        for i,j in A2:  
                
            if i!=j:                  
                myw2Index = (k,i,j)

                w2[myw2Index] = 0
                pass
            pass
        pass
    
    pass #end of generateVariablesModelThree

def assignx2w2(x2, w2, trasportoPalletDiGamma, rotte):
    for k in rotte:
        for posArc, (arcI, arcJ) in enumerate(rotte[k]):
            for (gamma, pallet) in trasportoPalletDiGamma[k][len(trasportoPalletDiGamma[k]) - posArc -1:]:
                #if (posGP >= 0 and posGP <= len(trasportoPalletDiGamma[k] - posArc)):
                x2[k, gamma, arcI, arcJ] =  pallet
                print("x2[{}, {}, {}, {}]: {}".format(k, gamma, arcI, arcJ, pallet))
                w2[k, arcI, arcJ] = 1