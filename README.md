# Mini Projet INFO834
> Simulation à événement discret d'une épidémie dans un village en quarantaine

### Description du projet

Aspect technique du projet :
Le projet est une simulation qui représente une épidémie dans un village en quarantaine. On a donc un graph composé de sous-graph de nœuds interconnecté représentant les familles. Le programme utilise Sim Py pour faire une simulation à évènement discret et Networkx pour faire les graphs. Chaque nœud représente un villageois à l’exception des nœuds : H, S et G
-	H : L’Hôpital
-	S : Le supermaché
-	G : Le Cimetière
L’hôpital est une ressource SimPy qui peut donc être utilisé simultanément par un nombre limité. Pour solliciter la ressource le nœud doit émettre une requête. Si les places sont déjà toutes prises, un système de file d’attente est alors mis en place.
Le supermarché et le cimetière sont principalement pour rendre les interactions des nœuds du graph plus intuitif visuellement. 


## Installation

### Les packages
Copier ou télécharger le git puis installer les packages suivant dans le rep /mysite
```sh
pip install django
pip install simpy
pip install networkx
pip install mat
pip install matplotlib
pip install djangorestframework
pip install markdown
pip install django-filter
pip install spicy
```

Une fois installer toujours dans le rep « mysite » lancer la commande 
```sh
python manage.py runserver 
```
Normalement un serveur local à l'url http://127.0.0.1:8000/ devrait se lancer. Patienter un peu le temps que la simulation se fasse en backend. Il s'affichera normalement après un dashboards avec des graphs résumant le déroulement de la simulation.

### Personalisation de la simutation 
Dans le fichier mysite/mysite/main
changer le nombre de jours, le nombre de personnes, le nombre de voisins moyens par personnes, la capacité de l'hôpital, le nombre d'infectés initiaux, le nombre de vaccinés

## Problèmes
Si vous rencontrez des soucis lors de l'installation merci de me conatacter.
Bonne expérience à tous !
