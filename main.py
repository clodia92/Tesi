from lettura import readFile

class Prob3:

    def __init__(self, nomeFileInput):
        # lettura del file
        self.nomeFile = nomeFileInput
        print("Nome file input", nomeFileInput)
        myRead = readFile(self.nomeFile)

        print ("Numero di satelliti -->", myRead.get_numberOfSatellites())
        print ("Numero di containers -->", myRead.get_numberOfContainers())
        print ("Numero di veicoli in K1 -->", myRead.get_numberOfVehicles1st())
        print ("Numero di veicoli in K2 -->", myRead.get_numberOfVehicles2nd())
        print ("Numero di clienti -->", myRead.get_numberOfCustomers())

        print ("Set dei satelliti -->", myRead.get_setOfSatellites())
        print ("Set dei containers -->", myRead.get_setOfContainers())
        print ("Set dei veicoli in K1 -->", myRead.get_setOfVehicles1st())
        print ("Set dei veicoli in K2 -->", myRead.get_setOfVehicles2nd())
        print ("Set dei clienti -->", myRead.get_setOfCustomers())
        print ("Set degli archi in A1 -->", myRead.get_setOfArcA1())
        print ("Set degli archi in A2 -->", myRead.get_setOfArcA2())

        print ("Dizionario di fs --> ", myRead.get_dictionaryOfFs())
        print ("Dizionario di nik2ij -->", myRead.get_dictionaryOfNik2ij())
        print ("Dizionario di ak2ij -->", myRead.get_dictionaryOfAk2ij())
        print ("Dizionario di betas -->", myRead.get_dictionaryOfBetaS())
        print ("Dizionario di aks -->", myRead.get_dictionaryOfAks())
        print ("Dizionario di ak1s -->", myRead.get_dictionaryOfAk1s())
        print ("Dizionario di uk2 -->", myRead.get_dictionaryOfUk2())
        print ("Dizionario di us -->", myRead.get_dictionaryOfUs())
        print ("Dizionario di vs -->", myRead.get_dictionaryOfVs())
        print ("Dizionario di PalletInContainer -->", myRead.get_dictionaryOfPalletInContainer())
        print ("Dizionario di pis -->", myRead.get_dictionaryOfPis())
        print ("Lunghezza A2 --> ", len(myRead.get_setOfArcA2()))
        print("Mezzi Prob2 -->", myRead.get_K2diS())
        print("Domande -->", myRead.get_PsGa())



        pass

