# INFO833_Epidemic_broadcast
## Aspect technique du projet :
Le projet est une simulation qui représente une épidémie dans un village en quarantaine. On a donc un graph composé de sous-graph de nœuds interconnecté représentant les familles. Le programme utilise Sim Py pour faire une simulation à évènement discret et Networkx pour faire les graphs. Chaque nœud représente un villageois à l’exception des nœuds : H, S et G
-	H : L’Hôpital
-	S : Le supermaché
-	G : Le Cimetière
L’hôpital est une ressource SimPy qui peut donc être utilisé simultanément par un nombre limité. Pour solliciter la ressource le nœud doit émettre une requête. Si les places sont déjà toutes prises, un système de file d’attente est alors mis en place.
Le supermarché et le cimetière sont principalement pour rendre les interactions des nœuds du graph plus intuitif visuellement. 

