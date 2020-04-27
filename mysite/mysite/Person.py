import simpy
import random
import networkx as nx
import math
import matplotlib.pyplot as plt


class Person:

    def __init__(self, env, state, name, age, vaccine, graph):
        self.env = env
        self.name = name
        self.age = age
        self.voisinage = []
        self.vaccine = vaccine
        self.state = {
            "etat": state,
            "startTime": env.now
        }
        self.graph = graph
        self.infectedat = -5
        self.infectiosite = 0
        self.hospitalizedat = 0
        self.indiceNourriture = random.randint(1, 4)
        self.nourritureV = 0
        self.attenteN = False
        self.lifeToken=0


    def setVaccin(self, vaccine):
        self.vaccine = vaccine

    def isVaccine(self):
        return self.vaccine

    def getName(self):
        return self.name

    def getAge(self):
        return self.age

    def getVoisinage(self):
        return self.voisinage

    def setVoisinage(self, list):
        self.voisinage = list

    def getVoisinageTuple(self):
        tupleVoisinage = []
        for i in self.voisinage:
            tupleVoisinage.append(tuple([self, i]))
        return tupleVoisinage

    def getStatee(self):
        return self.state["etat"]

    def setStatee(self, state):
        self.state["etat"] = state
        self.state["startTime"] = self.env.now

    def getResistance(self):
        return self.resistance

    # def setIncubation(self, incub):
    #     self.incubation = incub

    # Méthode responsable de l'infection d'une personne à une autre
    def infects(self, pers, tokenCourses=False):
        # n'a pas encore été contaminé => -5
        #Verife que ce ne soit pas l'hopital le magasin ou le cimetiere, c'est bourrin mais je manque de temps
        if pers.infectedat == -5 and pers.getName()!="H" and pers.getName()!="S" and pers.getName()!="G":
            # print("#" + str(pers.getName()))

            # if pers.getName() == "p3" and pers.infectedat==-5:
            #     pers.infectedat = pers.env.now
            #     pers.env.process(pers.infectedEv())
            print("------------------------------------------")
            print("name du node : " + self.getName() + " nom du voisin : " + pers.getName() + " age : " + str(
                pers.getAge()) + " ans et vaccine :" + str(pers.isVaccine()))
            PALIER_INFECTION = 0.4
            if tokenCourses:
                PALIER_INFECTION = 0.7
            if pers.isVaccine():
                PALIER_INFECTION = 0.95
            tauxInfectiosite = random.random()
            print("le ratio est : " + str(tauxInfectiosite))
            print("infection : " + str(tauxInfectiosite > PALIER_INFECTION))
            print("la personne est : " + str(pers.getStatee()))
            if tauxInfectiosite > PALIER_INFECTION:
                pers.infectedat = pers.env.now
                pers.env.process(pers.infectedEv())
                if tokenCourses:
                    self.graph.tokenInfectionOustide += 1
                # pers.setStatee(2)
            print("token fin de fonction infect")


    def infectedEv(self):
        etat = 0
        maxT = 12
        token = False
        # Boucle tant que les deux jours ne se sont pas écoulé et que le patient ne se fait pas hospitalisé ou soit
        while (self.env.now - self.infectedat) < 12 and self.getStatee() != -1 and self.getStatee() != 6:
            # liste de t1 à t2
            # TODO mettre temps maladie en variable constante (voire même faire une classe maladie)
            # print('self.infectedat' + str(self.infectedat))
            # print('self.env.now' + str(self.env.now))
            t = (self.env.now - self.infectedat) + 1
            etat = self.getEtatTime(t, maxT)
            # s'il est dans un etat critique et qu'il n'est pas pris en charge son taux d'infectiosite continue d'evoluer
            self.infectiosite = self.getDeasesFAge(self.getAge(), t, maxT) / 100
            # print("==========TEST ZONE PLEASE==" + self.getName() + "=")
            rdm = random.uniform(0, 1)
            # Le patient est dans un cas critique est attend pout l'hopital
            if token and etat > 4:
                # fonction qui lui donne 1 chance sur 3 de mourir
                self.criticState()
            elif self.infectiosite > rdm and self.getStatee() == 4:
                # Le patient rentre dans un état critique
                self.setStatee(5)
                # print('ALTERTE AUX GOGOLES ! hRate : ' + str(self.infectiosite) + " - rdm " + str(rdm))
                self.callEmergency()
                token = True
            else:
                self.setStatee(etat)

            # print('TIME : ' + str(env.now))
            # print('petit t : ' + str(t))
            # print('pour age : ' + str(self.getAge()) + ' le taux de mortalité est de : ' + str(
            #     self.getDeasesFAge(self.getAge(), t, maxT)) + '%')
            # print('Etat : ' + str(self.getStatee()))
            yield self.env.timeout(1)

    # evolue de l'état sain à malade (1 à 4) palier
    def criticState(self):
        if self.getAge() / 100 > random.uniform(0, 1):
            self.setStatee(6)

    # evolue de l'état sain à malade (1 à 4) palier
    def getEtatTime(self, t, maxT):
        if t <= maxT / 2 and t < 5:
            return t
        elif 4 < t < 8:
            return 4
        else:
            return maxT - t

    def getDeasesFAge(self, age, t, maxT):
        maxT2 = maxT / 2
        if t <= maxT2:
            z = t / maxT2
        else:
            z = (maxT - t) / maxT2
        # time has to start at 1 and correspond at the timestamp where
        return (age / (1 + math.exp(-((age / 10) - 5)))) * (z)

    def cured(self):
        self.setStatee(0)

    def treated(self):
        self.setStatee(-1)

    def callEmergency(self):
        self.env.process(self.graph.hospitalized(self))

    def sortFaireSesCourses(self):
        self.env.process(self.graph.faireCourse(self))
        print('TIME : ' + str(self.env.now))
        print('parti faire des courses')
        # for object in self.graph.G.edges:
        #     print(object[0].getName() + " " + object[1].getName())

    def evolHunger(self):
        #test if G is initialized
        if hasattr(self.graph, 'G'):
            while True:
                if self not in list(self.graph.G.neighbors(self.graph.hospitalNode)) and \
                    self not in list(self.graph.G.neighbors(self.graph.shopNode)):
                    # print("=======================DEBUT===================================")
                    # print("TIME :"+str(self.env.now))

                    # for node in self.voisinage:
                    #     print("node : " + node.getName() + " nourriture voisinnage : " + str(node.nourritureV))
                    # print("node : " + self.getName() + " nourriture voisinnage : " + str(self.nourritureV))
                    # print("====================MANGE====================================")
                    if self.nourritureV > 0:
                        # print(list(S1.intersection(S2)))
                        self.eat()
                    elif not self.attenteN:
                        if self.getStatee() < 5:
                            self.sortFaireSesCourses()
                            self.setAttenteN()
                        else:
                            node = self.findNotTooSick()
                            if node != -1:
                                node.sortFaireSesCourses()
                                self.setAttenteN()
                # print("====================MANGE====================================")
                # for node in self.voisinage:
                #     print("node : " + node.getName() + " nourriture voisinnage : " + str(node.nourritureV))
                # print("node : " + self.getName() + " nourriture voisinnage : " + str(self.nourritureV))
                # print("====================FIN====================================")
                yield self.env.timeout(0.33)

    def eat(self):
        rd = random.randint(1, 2)
        # print("node " + self.getName() + " eating : " + str(rd))
        self.nourritureV -= rd
        for pers in self.voisinage:
            pers.nourritureV -= rd

    def setAttenteN(self):
        for node in self.voisinage:
            node.attenteN = True

    def finishedGroceries(self):
        for node in self.voisinage:
            node.attenteN = False

    def findNotTooSick(self):
        listN = []
        for node in self.voisinage:
            if 0 <= node.getStatee() < 5:
                listN.append(node)
        if not listN:
            return -1
        return random.choice(listN)

    def feedFamily(self):
        rd = random.randint(len(self.voisinage) * 3, len(self.voisinage) * 6)
        self.nourritureV += rd
        print("rd : " + str(rd))
        for node in self.voisinage:
            node.nourritureV += rd

