import json
import simpy
import random
import networkx as nx
import math
import matplotlib.pyplot as plt
from .Person import Person
import copy
#Test
# from mysite.mysite.Person import Person


class Network:

    def __init__(self, env, nbPers, nbInfects, nbVaccines, nbVoisins, hospital):
        self.env = env
        self.nbVoisinsMoy = nbVoisins
        self.nbPers = nbPers
        self.nbInfects = nbInfects
        self.nbVaccines = nbVaccines
        self.personList = self.initList(self.env, self.nbPers, self.nbInfects, self.nbVaccines)
        self.G = nx.Graph()
        self.hospital = hospital
        self.listPatientsAtt = []
        self.listStore = []
        # self.G.add_nodes_from(self.personList)
        self.cpt = 0
        self.shopNode = Person(self.env, 100, "S", 0, False, self.G)
        self.hospitalNode = Person(self.env, 101, "H", 0, False, self.G)
        self.graveyardNode = Person(self.env, 102, "G", 0, False, self.G)
        self.compteur = 0
        self.days=[]
        self.tokenInfectionOustide = 0

#Data processing methods
    def tranchesAge(self):
        enfants = 0  #0 à 10
        ados = 0  #10 à 20
        jeunes = 0  #20 à 30
        adultes = 0  #30 à 45
        adultesS = 0  #45 à 60
        seniors = 0  #60 à 80
        survivors = 0  #80 à 100
        for pers in self.personList:
            if 0 <= pers.getAge() <= 10:
                enfants += 1
            if 10 <= pers.getAge() <= 20:
                ados += 1
            if 20 <= pers.getAge() <= 30:
                jeunes += 1
            if 30 <= pers.getAge() <= 45:
                adultes += 1
            if 45 <= pers.getAge() <= 60:
                adultesS += 1
            if 60 <= pers.getAge() <= 80:
                seniors += 1
            if 80 <= pers.getAge() <= 110:
                survivors += 1
        return{
            "0 to 10": enfants,
            "10 to 20": ados,
            "20 to 30": jeunes,
            "30 to 45": adultes,
            "45 to 60": adultesS,
            "60 to 80": seniors,
            "80 to 100": survivors,
        }

# Data processing methods

    def initialisation(self):
        self.G.add_nodes_from(self.personList)
        self.initEdgesCloisonnement()
        self.initListVoisinageN()
        supply = [self.shopNode, self.hospitalNode, self.graveyardNode]
        self.G.add_nodes_from(supply)

    def startGraph(self):
        compteur = 0
        self.updateState()
        # for node in self.G.nodes:
        #     print("node : " + node.getName() + " a indice : " + str(
        #         node.indiceNourriture) + " et en voisinnage : " + str(node.nourritureV))
        self.plotGraph()
        while True:
            self.plotGraph()
            compteur += 1
            print("compteur : " + str(compteur))
            self.infection(compteur)
            self.days.append(self.getBilanDaily())
            yield self.env.timeout(1)



    def updateState(self):
        print("token updateState")
        for node in self.G.nodes:
            self.env.process(node.evolHunger())

    def infection(self, compteur):
        # print("===============Voisins p3========================")
        # for object in self.G.edges:
        #     if object[0].getName() == "p3" or object[1].getName()== "p3" :
        #         print(object[0].getName() + " -?- " + object[1].getName())
        # print("===============Voisins p3========================")
        for node in self.G.nodes:
            # on s'assure que le la contamination n'a pas lui sur les noeuds qui font les courses

            if node not in list(self.G.neighbors(self.hospitalNode)) and \
                    node not in list(self.G.neighbors(self.shopNode)) and \
                    node not in list(self.G.neighbors(self.graveyardNode)):
                if 2 < node.getStatee() < 6:
                    for neighbor in self.G.neighbors(node):
                        node.infects(neighbor)

    def faireCourse(self, node):
        print("faire ses courses")
        print(node.getName())

        self.newClient(node)
        if node.getStatee() > 2:
            print("==============================SICK node with people====================")
            for pers in list(self.G.neighbors(self.shopNode)):
                node.infects(pers, True)
            print("==============================END OF SICK node with people====================")
        else:
            print("==============================HEALTHY node with sick people====================")
            for pers in list(self.G.neighbors(self.shopNode)):
                if pers.getStatee() > 2:
                    pers.infects(node, True)
            print("==============================END OF HEALTHY node with sick people====================")
        print("new clients")
        # self.plotGraph()
        print("==============================FOOD GAIN====================")
        node.feedFamily()
        print("==============================FOOD GAIN====================")
        yield self.env.timeout(0.3)

        self.getBackHome(node)
        print("back home")

    def breakEdgesN(self, node):
        for voisin in list(self.G.neighbors(node)):
            self.G.remove_edge(node, voisin)

    # Pour le magasin peut-être mettre des poids aux liens pour simuler les interactions
    def newClient(self, node):
        self.breakEdgesN(node)
        # self.listStore.append(node)
        self.G.add_edges_from([tuple([node, self.shopNode])])
        if list(self.G.neighbors(self.shopNode)):
            for client in list(self.G.neighbors(self.shopNode)):
                if client != node:
                    self.G.add_edges_from([tuple([node, client])])

    def getBackHome(self, node):
        # fonction utilisé pour l'hopital aussi donc on verifie que c'est pas un patient
        # if node.getStatee() != -1:
        #     self.listStore.remove(node)
        self.breakEdgesN(node)
        for voisin in node.getVoisinage():
            # Recréer des liens avec ses voisins qui sont encore à la maison
            if voisin not in list(self.G.neighbors(self.hospitalNode)) and \
                    voisin not in list(self.G.neighbors(self.shopNode)) and \
                    voisin not in list(self.G.neighbors(self.graveyardNode)):
                self.G.add_edges_from([tuple([node, voisin])])
            # print("[tuple([node, voisin])]: "+[tuple([node, voisin])])
        # Previens ses voisins qui a fini de faire les courses
        if node.getStatee() != -1:
            node.finishedGroceries()

    # ---------------------------------------------atl function----------------------------------------------
    # Liste pour infecter tour par tour
    # def infection(self,compteur):
    #     listInfectedPeople = []
    #     for node in self.G.nodes:
    #         if node.getStatee() == 1:
    #             listInfectedPeople.append(node)
    #     for node in listInfectedPeople:
    #         for neighbor in self.G.neighbors(node):
    #             node.infects(neighbor)
    # ---------------------------------------------atl function----------------------------------------------

    def printBilan(self, compteur):
        print("=================FIN DU TOUR " + str(compteur) + "================")
        print("BILAN IMMUNISE :")
        for node in self.G.nodes:
            if node.getStatee() == 0:
                print(node.getName() + " est immunisé")
        print("BILAN SAIN :")
        for node in self.G.nodes:
            if node.getStatee() == 1:
                print(node.getName() + " est sain")
        print("BILAN INFECTES :")
        for node in self.G.nodes:
            if node.getStatee() == 2:
                print(node.getName() + " est infecte")
        print("BILAN 1er SYMPTOMES :")
        for node in self.G.nodes:
            if node.getStatee() == 3:
                print(node.getName() + " a les 1er symptomes")
        print("BILAN MALADES :")
        for node in self.G.nodes:
            if node.getStatee() == 4:
                print(node.getName() + " est malade")
        print("BILAN CRITIQUE :")
        for node in self.G.nodes:
            if node.getStatee() == 5:
                print(node.getName() + " est dans un etat critique")
        print("BILAN MORT :")
        for node in self.G.nodes:
            if node.getStatee() == 6:
                print(node.getName() + " est mort")
        print("BILAN HOSPITALIZED :")
        for node in self.G.nodes:
            if node.getStatee() == -1:
                print(node.getName() + " est hospitalise")
        print("PATIENTS EN ATTENTE POUR L'HOPITAL :")
        for pers in self.listPatientsAtt:
            print(pers.getName() + " est en attente de soin")


    def getBilanDaily(self):
        listEtat = self.getListColors()
        return {
            "hospitalized": self.nodeToJson(listEtat["hospitalized"]),
            "cured": self.nodeToJson(listEtat["cured"]),
            "healthy": self.nodeToJson(listEtat["healthy"]),
            "infected": self.nodeToJson(listEtat["infected"]),
            "1stsymptomes": self.nodeToJson(listEtat["1stsymptomes"]),
            "ill": self.nodeToJson(listEtat["ill"]),
            "critical": self.nodeToJson(listEtat["critical"]),
            "dead": self.nodeToJson(listEtat["dead"]),
            "nbinfectionoutside":self.tokenInfectionOustide,
        }

    def nodeToJson(self,list1):
        newList=[]
        for pers in list(list1):
            pers1 = {
                "name":pers.name,
                "age":pers.age,
                "vaccine":pers.vaccine,
                "state":pers.getStatee(),
            }
            newList.append(pers1)
        return newList

    # self.name = name
    # self.age = age
    # self.voisinage = []
    # self.vaccine = vaccine
    # self.state = {
    #     "etat": state,
    #     "startTime": env.now
    # }
    # self.infectedat = -5
    # self.infectiosite = 0
    # self.hospitalizedat = 0
    # self.nourritureV = 0

    def newPatient(self, node):
        self.breakEdgesN(node)
        self.G.add_edges_from([tuple([node, self.hospitalNode])])

    def hospitalized(self, pers):
        self.listPatientsAtt.append(pers)
        request = self.hospital.request()
        yield request
        # if person not dead waiting to get cured
        self.listPatientsAtt.remove(pers)
        # on le sépare de son voisinage le temps qu'il soit traité
        # self.removeFromN(pers)
        if pers.state["etat"] != 6:
            self.newPatient(pers)
            pers.state["etat"] = -1
            # self.env.process(self.analysePatient(pers))
            pers.hospitalizedat = self.env.now
            print("===========HOPITAL TIME BEFORE YIELD 1 : " + str(
                self.env.now) + " POUR NOEUD : " + pers.getName() + " =============")
            yield self.env.timeout(1)
            print("===========HOPITAL TIME AFTER YIELD 1 : " + str(
                self.env.now) + " POUR NOEUD : " + pers.getName() + "=============")
            print("lifeToken1 : " + str(pers.lifeToken))
            print("analyse de : " + pers.getName())
            pers.lifeToken = self.soins(pers)
            print("node name : " + pers.getName())
            print('TIME : ' + str(self.env.now))
            print("self.env.now - pers.hospitalizedat : " + str(self.env.now - pers.hospitalizedat))
            # Les traitements sont efficaces ils va se faire traiter deux jours à l'hopital
            if pers.lifeToken == 1:
                print("===========HOPITAL TIME BEFORE YIELD 2 : " + str(
                    self.env.now) + " POUR NOEUD : " + pers.getName() + " state : " + str(
                    pers.getStatee()) + " =============")
                yield self.env.timeout(2)
                print("===========HOPITAL TIME AFTER YIELD 2 : " + str(
                    self.env.now) + " POUR NOEUD : " + pers.getName() + " =============")
                print('pers treated : ' + pers.getName())
                # self.reboundN(pers)
                self.getBackHome(pers)
                pers.cured()
                print("========== POUR NOEUD " + pers.getName() + " ==============state : " + str(
                    pers.getStatee()) + "===============HOSPITAL")
            # Le traitement n'est pas efficace la maladie aura raison du patient
            else:
                print("HOSPI DEAD")
                pers.setStatee(6)
                self.cimetiere(pers)
            self.hospital.release(request)
        else:
            self.hospital.release(request)
            self.cimetiere(pers)

    # Prend un tour pour préparer analyse patient
    # def analysePatient(self,pers):
    #     yield self.env.timeout(1)
    #     self.newPatient(pers)
    #     pers.hospitalizedat = self.env.now
    #     pers.state["etat"] = -1
    #     print("lifeToken1 : " + str(pers.lifeToken))
    #     print("analyse de : " + pers.getName())
    #     pers.lifeToken = self.soins(pers)

    def removeFromN(self, node):
        for pers in list(node.voisinage):
            print("node hospitalisé : " + node.getName())
            for i in list(pers.voisinage):
                print('voisinage de ' + pers.getName() + ' : ' + i.getName())
            pers.voisinage.remove(node)

    def reboundN(self, node):
        for pers in list(node.voisinage):
            pers.voisinage.append(node)

    def cimetiere(self, node):
        self.breakEdgesN(node)
        self.G.add_edges_from([tuple([node, self.graveyardNode])])

    def soins(self, pers):
        print("infectiosité : " + str(pers.infectiosite))
        rd = random.uniform(0, 1)
        print("efficacité soin : " + str(rd))
        if pers.infectiosite > rd:
            return -1
        return 1

    def initEdges(self):
        for node in self.G.nodes:
            tempNodes = list(self.G)
            # tempNodes : tous les noeuds sauf celui concerné
            tempNodes.remove(node)
            ri = random.randint(self.nbVoisinsMoy - 1, self.nbVoisinsMoy + 1)
            for i in range(ri - len(list(self.G.neighbors(node)))):
                tempNode = random.choice(tempNodes)
                self.G.add_edges_from([tuple([node, tempNode])])
                # j'enlève le node pour éviter d'avoir deux fois le même voisin
                tempNodes.remove(tempNode)
        # for object in self.G.edges:
        #     print("?")
        #     print(object[0].getName() + " " + object[1].getName())

    # Permet à chaque noeud de connaître son voisinage
    def initListVoisinageN(self):
        for node in self.G.nodes:
            node.setVoisinage(list(self.G.neighbors(node)))
            self.initFood(node)

    # Fonction qui créer la quantité de nouriture pour un voisinage
    # Update possible : créer une variable partagé au voisinage grace à une classe voisinage
    def initFood(self, node):
        for node1 in node.getVoisinage():
            node.nourritureV += node1.indiceNourriture
        node.nourritureV += node.indiceNourriture

    def initEdgesCloisonnement(self):
        nbVoisinages = len(self.personList) // self.nbVoisinsMoy
        stock = len(self.personList) % self.nbVoisinsMoy
        tempNodes = list(self.G)
        # print(tempNodes)
        # Quand le nombre de voisins moyens est plus grand que la pop totale
        if nbVoisinages == 0:
            nbVoisinages = 1
            self.nbvoisinsMoy = len(self.personList) - 1
        # Pour faire un voisinage avec le nombre d'habitants restant
        elif nbVoisinages == 1 and stock != 0:
            nbVoisinages = 2
        self.creaVoisinages(nbVoisinages, stock, tempNodes)

    # Créer les sous-graphs de voisinages
    def creaVoisinages(self, nbVoisinages, stock, tempNodes):
        nbVoisinagesTemp = nbVoisinages
        for i in range(nbVoisinages):
            voisinage = []
            nbVoisins = self.nbVoisinsMoy
            tempNode = random.choice(tempNodes)
            tempNodes.remove(tempNode)
            # tempNodes : tous les noeuds sauf celui concerné
            if stock != 0:
                if (stock + 1) >= nbVoisinagesTemp:
                    stock -= 1
                    nbVoisins += 1
                else:
                    ri1 = random.randint(-1, 1)
                    nbVoisins += ri1
                    stock -= ri1
            else:
                nbVoisins += stock
            # on soustrait le noeud en question dans le voisinage
            voisinage.append(tempNode)
            for i in range(nbVoisins - 1):
                if not tempNodes:
                    break
                else:
                    tempNodeV = random.choice(tempNodes)
                    voisinage.append(tempNodeV)
                    tempNodes.remove(tempNodeV)
            tempEdgeList = voisinage.copy()
            for node in voisinage:
                tempEdgeList.remove(node)
                for i in range(len(tempEdgeList)):
                    self.G.add_edges_from([tuple([node, tempEdgeList[i]])])
            nbVoisinagesTemp -= 1

    def initList(self, env, nbPers, nbInfectes, nbVaccines):
        persList = []
        for i in range(nbPers):
            nom = "p" + str(i + 1)
            age = random.randint(0, 100)
            persList.append(Person(env, 1, nom, age, False, self))
        # Initialise les infectés
        tempList = persList.copy()
        for i in range(nbInfectes):
            choice = random.choice(tempList)
            choice.infectedat = choice.env.now - 1
            choice.env.process(choice.infectedEv())
            tempList.remove(choice)
        # tempList2 = persList
        for i in range(nbVaccines):
            choice = random.choice(tempList)
            choice.setVaccin(True)
            tempList.remove(choice)
        # print("LISTE DANS L'INIT")
        # print([k.getName() for k in persList])
        return persList

    def getListColors(self):
        lists = {
            "hospitalized": [],
            "cured": [],
            "healthy": [],
            "infected": [],
            "1stsymptomes": [],
            "ill": [],
            "critical": [],
            "dead": [],
            "SHOP": [],
            "HOSPITAL": [],
            "GRAVEYARD": []
        }
        for node in self.G.nodes:
            if node.getStatee() == -1:
                lists["hospitalized"].append(node)
            if node.getStatee() == 0:
                lists["cured"].append(node)
            if node.getStatee() == 1:
                lists["healthy"].append(node)
            if node.getStatee() == 2:
                lists["infected"].append(node)
            if node.getStatee() == 3:
                lists["1stsymptomes"].append(node)
            if node.getStatee() == 4:
                lists["ill"].append(node)
            if node.getStatee() == 5:
                lists["critical"].append(node)
            if node.getStatee() == 6:
                lists["dead"].append(node)
            if node.getStatee() == 100:
                lists["SHOP"].append(node)
            if node.getStatee() == 101:
                lists["HOSPITAL"].append(node)
            if node.getStatee() == 102:
                lists["GRAVEYARD"].append(node)
        return lists

    def plotGraph(self):
        self.compteur+=1
        elarge = [(u, v) for (u, v, d) in self.G.edges(data=True)]

        pos = nx.spring_layout(self.G)  # positions for all nodes

        # nodes
        lists = self.getListColors()

        # Hospitalized
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["hospitalized"], node_color='#ffb8b8', node_size=700)
        # cured
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["cured"], node_color='#17c0eb', node_size=700)
        # Healthy
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["healthy"], node_color='#3ae374', node_size=700)
        # infected
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["infected"], node_color='#fff200', node_size=700)
        # 1st symptomes
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["1stsymptomes"], node_color='#ff9f1a', node_size=700)
        # ill
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["ill"], node_color='#ff4d4d', node_size=700)
        # critical
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["critical"], node_color='r', node_size=700)
        # dead
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["dead"], node_color='#3d3d3d', node_size=700)
        # shop
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["SHOP"], node_color='#c56cf0', node_size=800)
        # shop
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["HOSPITAL"], node_color='#227093', node_size=800)
        # shop
        nx.draw_networkx_nodes(self.G, pos, nodelist=lists["GRAVEYARD"], node_color='#3d3d3d', node_size=800)

        # edges
        nx.draw_networkx_edges(self.G, pos, edgelist=elarge,
                               width=6)

        # labels
        labels = {k: k.getName() for k in self.G.nodes}
        nx.draw_networkx_labels(self.G, pos, labels=labels, font_size=10, font_family='sans-serif')
        # print(labels)
        plt.axis('off')
        plt.savefig("static/outputs/Graph" + str(self.compteur) + ".png", format="PNG")
        # plt.show()
        plt.clf()
