import simpy
import random
import networkx as nx
import math
import matplotlib.pyplot as plt
#Test
# from mysite.mysite.Network import Network
from .Network import Network

def main():

    #TODO Saisi des données ICI
    NB_PEOPLE=100
    NB_INFECTED=1
    NB_VACCINES=0
    NB_VOISINS=5
    NB_DAYS = 2
    CAPACITE_HOPITAL = 2
    #TODO Saisi des données ICI

    env = simpy.Environment()
    hospital = simpy.Resource(env, capacity=CAPACITE_HOPITAL)
    g1 = Network(env, NB_PEOPLE, NB_INFECTED, NB_VACCINES, NB_VOISINS, hospital)
    g1.initialisation()
    env.process(g1.startGraph())

    print(g1.hospital)
    env.run(until=NB_DAYS)
    g1.plotGraph()
    #test
    qs_count = 1
    labels = ["Users", "Blue", "Yellow", "Green", "Purple", "Orange"]
    default_items = [qs_count, 230, 2, 3, 12, 2]
    data = {
        "labels": labels,
        "default": default_items,
        "NB_PEOPLE":NB_PEOPLE,
        "evolState":g1.days,
        "tranchesAge":g1.tranchesAge()
    }
    return data



def getData():
    qs_count = 1
    labels = ["Users", "Blue", "Yellow", "Green", "Purple", "Orange"]
    default_items = [qs_count, 23, 2, 3, 12, 2]
    data = {
        "labels": labels,
        "default": default_items,
    }
    return data


if __name__ == '__main__':
    main()

