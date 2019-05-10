import pulp

# generate variables for Model One
def generateVariablesModelOne(ys, x1, S, K1, C):
        
    #generate Variables ys
    # for all satellites
    for s in S:
            
        myysIndex = (s)

        ys[myysIndex]=pulp.LpVariable("ys_%s"%(s), 0 , 1, pulp.LpInteger) 
        #print("Valore variabile %s"%ys[myysIndex], " = %s "% ys[myysIndex].varValue)
        pass          
         
    #generate Variables x1
    # for all vehicles (first echelon)
    for k in K1:
        # for all satellites
        for s in S:
            # for all containers
            for c in C:

                myx1Index = (k,s,c)
                x1[myx1Index]=pulp.LpVariable("x1_%s_%s_%s"%(k,s,c), 0 , 1, pulp.LpInteger) 
                #print("Valore variabile %s"%x1[myx1Index], " = %s "% x1[myx1Index].varValue)
                pass
            pass
        pass
    
    pass #end of generateVariablesModelOne      
        

# generate variables for Model Two
def generateVariablesModelTwo(zks, K2, Sneg):
    
    #generate Variables zks
    # for all vehicles k in K2
    for k in K2:
        # for all satellites
        for s in Sneg:
                
            myzksIndex = (k,s)
            zks[myzksIndex]=pulp.LpVariable("zks_%s_%s"%(k,s), 0 , 1, pulp.LpInteger)
            #print("Valore variabile %s"%zks[myzksIndex], " = %s "% zks[myzksIndex].varValue)
            pass
        pass
        
    pass #end of generateVariablesModelTwo

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
                    
                    x2[myx2Index]=pulp.LpVariable("x2_%s_%s_%s_%s"%(k,ga,i,j), 0 , None, pulp.LpInteger) 
                    #print("Valore variabile %s"%x2[myx2Index], " = %s "% x2[myx2Index].varValue)
                    x2[myx2Index].varValue = 0
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
                    
                w2[myw2Index]=pulp.LpVariable("w2_%s_%s_%s"%(k,i,j), 0 , 1, pulp.LpInteger) 
                #print("Valore variabile %s"%w2[myw2Index], " = %s "% w2[myw2Index].varValue)
                w2[myw2Index].varValue = 0
                pass
            pass
        pass
    
    pass #end of generateVariablesModelThree

# generate global variables for Model Three
def generateGlobalVariablesModelThree(x2Global, w2Global, K2, gam, A2, x2GlobalSimulated, w2GlobalSimulated):
     
    #generate Variables x2Global
    # for all vehicles (second echelon)
    for k in K2:
        # for all customers in GammadiS
        for ga in gam:
            # for all arcs in A2
            for i,j in A2:                    
                     
                if i!=j:           
                    myx2GlobalIndex = (k,ga,i,j)
                    
                    x2Global[myx2GlobalIndex]=pulp.LpVariable("x2_%s_%s_%s_%s"%(k,ga,i,j), 0 , None, pulp.LpInteger) 
                    #print("Valore variabile %s"%x2Global[myx2GlobalIndex], " = %s "% x2Global[myx2GlobalIndex].varValue)
                    x2Global[myx2GlobalIndex].varValue = 0
                    pass
                pass
            pass
        pass
    
    #generate Variables w2Global
    # for all vehicles (second echelon)
    for k in K2:
        # for all arcs in A2
        for i,j in A2:  
                
            if i!=j:                  
                myw2GlobalIndex = (k,i,j)
                    
                w2Global[myw2GlobalIndex]=pulp.LpVariable("w2_%s_%s_%s"%(k,i,j), 0 , 1, pulp.LpInteger) 
                #print("Valore variabile %s"%w2Global[myw2GlobalIndex], " = %s "% w2Global[myw2GlobalIndex].varValue)
                w2Global[myw2GlobalIndex].varValue = 0
                pass
            pass
        pass
    
    #generate Dictionary of x2GlobalSimulated
    # for all vehicles (second echelon)
    for k in K2:
        # for all customers in GammadiS
        for ga in gam:
            # for all arcs in A2
            for i,j in A2:                    
                     
                if i!=j:           
                    myx2GlobalSimulatedIndex = (k,ga,i,j)
                    
                    x2GlobalSimulated[myx2GlobalSimulatedIndex] = 0 
                    #print("Valore x2GlobalSimulated[", myx2GlobalSimulatedIndex, "] = ", x2GlobalSimulated[myx2GlobalSimulatedIndex])
                    pass
                pass
            pass
        pass
    
    #generate Variables w2GlobalSimulated
    # for all vehicles (second echelon)
    for k in K2:
        # for all arcs in A2
        for i,j in A2:  
                
            if i!=j:                  
                myw2GlobalSimulatedIndex = (k,i,j)
                    
                w2GlobalSimulated[myw2GlobalSimulatedIndex] = 0 
                #print("Valore w2GlobalSimulated[", myw2GlobalSimulatedIndex, "] = ", w2GlobalSimulated[myw2GlobalSimulatedIndex])
                pass
            pass
        pass
    
    pass #end of generateVariablesModelThree