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
