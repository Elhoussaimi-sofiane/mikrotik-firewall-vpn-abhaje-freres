# Résumé du projet Firewall MikroTik et VPN sécurisés

## 1. Présentation générale

Ce projet consiste à construire et tester une infrastructure réseau sécurisée pour une entreprise possédant :

- un siège principal (**HQ**) ;
- une succursale (**Branch**) ;
- des employés qui doivent pouvoir travailler à distance ;
- une connexion Internet pour chaque site ;
- une communication chiffrée entre le siège et la succursale.

Le laboratoire a été réalisé dans **UTM sur un Mac Apple Silicon**, avec des machines virtuelles ARM64. Les pare-feu utilisent **MikroTik CHR sous RouterOS 7.22.1**.

L’objectif principal est d’autoriser uniquement les communications nécessaires et de bloquer tout le reste par défaut.

**État du projet : laboratoire fonctionnel, testé et validé le 26 juillet 2026.**

---

## 2. Architecture réalisée

```text
                         INTERNET / RÉSEAU WAN UTM
                                  │
              ┌───────────────────┴───────────────────┐
              │                                       │
       WAN 192.168.64.2                         WAN 192.168.64.4
          ┌─────────┐        WireGuard             ┌───────────┐
          │  R1-HQ  │◄──── VPN site-à-site ───────►│ R2-Branch │
          │Firewall │     UDP 13232                 │ Firewall  │
          └────┬────┘     10.255.255.0/30           └─────┬─────┘
               │                                        │
       LAN 10.10.10.1/24                       LAN 10.30.30.1/24
               │                                        │
       Réseau du siège                         Réseau succursale
       10.10.10.0/24                           10.30.30.0/24
               │
       Ubuntu HQ-Test-Client
          10.10.10.200

 Employé externe ── WireGuard UDP 13231 ──► R1-HQ
     10.20.20.2                            10.20.20.1
```

### Machines virtuelles principales

| Machine virtuelle | Rôle |
|---|---|
| MikroTik CHR Automated | R1-HQ, pare-feu principal du siège |
| R2-Branch | Pare-feu et routeur de la succursale |
| HQ-Test-Client | Ubuntu placé dans le LAN du siège pour les tests |
| Remote-Employee-Test | Simulation d’un employé connecté depuis l’extérieur |

Les anciennes machines MikroTik ont été conservées et ne font pas partie de l’architecture finale.

---

## 3. Plan d’adressage

| Élément | Interface ou rôle | Adresse / réseau |
|---|---|---|
| R1-HQ | WAN `ether1` | `192.168.64.2/24` |
| R1-HQ | Passerelle LAN `ether2` | `10.10.10.1/24` |
| Réseau HQ | LAN protégé | `10.10.10.0/24` |
| DHCP HQ | Adresses distribuées | `10.10.10.100-10.10.10.200` |
| Ubuntu HQ-Test-Client | Client de test | `10.10.10.200/24` |
| VPN employés | Réseau WireGuard | `10.20.20.0/24` |
| R1-HQ | Passerelle VPN employés | `10.20.20.1/24` |
| Employé de test | Client VPN | `10.20.20.2/32` |
| R2-Branch | WAN `ether1` | `192.168.64.4/24` |
| R2-Branch | Passerelle LAN `ether2` | `10.30.30.1/24` |
| Réseau Branch | LAN protégé | `10.30.30.0/24` |
| DHCP Branch | Adresses distribuées | `10.30.30.100-10.30.30.200` |
| VPN site-à-site | Réseau de transit | `10.255.255.0/30` |
| R1-HQ | Extrémité du tunnel | `10.255.255.1/30` |
| R2-Branch | Extrémité du tunnel | `10.255.255.2/30` |

Les adresses WAN `192.168.64.x` appartiennent au laboratoire UTM. Elles devront être remplacées par les vraies informations réseau lors du passage en entreprise.

---

## 4. Préparation et sécurisation de R1-HQ

Le premier MikroTik a été configuré comme routeur principal du siège et renommé **R1-HQ**.

Des sauvegardes ont été créées avant et après les premières modifications :

- `R1-HQ-baseline.backup` : état initial avant les changements importants ;
- `R1-HQ-step1-secured.backup` : état après la première sécurisation ;
- `R1-HQ-final-validated.backup` : configuration finale testée ;
- `R1-HQ-final-validated.rsc` : export texte final permettant l’audit ou une reconstruction manuelle.

Les services inutiles et risqués ont été désactivés :

- Telnet ;
- FTP ;
- API ;
- API-SSL ;
- reverse proxy.

Les services nécessaires à l’administration ont été conservés :

- **WebFig**, pour l’administration depuis un navigateur ;
- **SSH**, pour l’administration sécurisée en ligne de commande ;
- **WinBox**, pour l’administration avec l’outil MikroTik.

Cette réduction des services diminue la surface d’attaque du routeur.

---

## 5. Configuration des réseaux LAN et DHCP

### Réseau du siège

L’interface `ether2` de R1-HQ représente le LAN de l’entreprise. Elle possède l’adresse `10.10.10.1/24` et joue le rôle de passerelle pour les machines du siège.

Le serveur DHCP de R1-HQ distribue automatiquement :

- une adresse comprise entre `10.10.10.100` et `10.10.10.200` ;
- la passerelle `10.10.10.1` ;
- le serveur DNS `10.10.10.1`.

### Réseau de la succursale

L’interface `ether2` de R2-Branch possède l’adresse `10.30.30.1/24`. Le serveur DHCP de la succursale distribue les adresses `10.30.30.100-10.30.30.200`, avec `10.30.30.1` comme passerelle et DNS.

Le DHCP évite de configurer manuellement chaque poste et garantit que les clients reçoivent les bons paramètres réseau.

---

## 6. Fonctionnement du pare-feu

Le pare-feu est basé sur une politique **default deny** : seuls les flux explicitement autorisés passent ; tout le reste est bloqué.

### Chaîne INPUT

La chaîne `input` protège le routeur lui-même. Elle concerne par exemple :

- WebFig, SSH ou WinBox ;
- le ping vers le routeur ;
- les ports WireGuard ;
- les requêtes DNS ou DHCP destinées au routeur.

L’ordre logique appliqué est le suivant :

1. autoriser l’administration depuis l’hôte UTM `192.168.64.1` ;
2. accepter les connexions `established`, `related` et `untracked` ;
3. bloquer les paquets `invalid` ;
4. autoriser la réponse DHCP du WAN ;
5. autoriser un nombre limité de paquets ICMP ;
6. autoriser l’administration depuis le LAN de confiance ;
7. ouvrir uniquement les ports UDP nécessaires à WireGuard ;
8. autoriser les réseaux VPN identifiés ;
9. terminer par une règle **drop** qui bloque tout le reste.

### Chaîne FORWARD

La chaîne `forward` contrôle le trafic qui traverse le routeur. Elle concerne :

- le LAN vers Internet ;
- l’employé VPN vers le siège ;
- l’employé VPN vers Internet ;
- le siège vers la succursale ;
- la succursale vers le siège.

Les règles principales autorisent :

- `10.10.10.0/24` vers Internet via R1-HQ ;
- `10.30.30.0/24` vers Internet via R2-Branch ;
- `10.20.20.0/24` vers le LAN HQ et Internet ;
- `10.10.10.0/24` vers `10.30.30.0/24` via WireGuard ;
- `10.30.30.0/24` vers `10.10.10.0/24` via WireGuard.

Chaque routeur termine aussi sa chaîne `forward` par un **drop final**.

### États de connexion

- **Established** : paquet appartenant à une connexion déjà autorisée, par exemple la réponse d’un site Internet à un client du LAN.
- **Related** : nouvelle communication directement liée à une connexion déjà autorisée.
- **Invalid** : paquet incohérent ou impossible à associer à une connexion valide ; il est bloqué.

---

## 7. NAT masquerade et accès Internet

Les réseaux `10.10.10.0/24`, `10.20.20.0/24` et `10.30.30.0/24` utilisent des adresses privées qui ne peuvent pas être routées directement sur Internet.

Le **NAT masquerade** remplace temporairement l’adresse privée du client par l’adresse WAN du MikroTik :

```text
Ubuntu 10.10.10.200 → R1-HQ → Internet
                         │
                         └─ la source visible devient l’adresse WAN de R1-HQ
```

Quand la réponse revient, R1-HQ utilise sa table de connexions pour la remettre à `10.10.10.200`.

Les règles NAT configurées sont :

- LAN HQ `10.10.10.0/24` vers Internet ;
- VPN employés `10.20.20.0/24` vers Internet ;
- LAN Branch `10.30.30.0/24` vers Internet.

Le trafic entre HQ et Branch n’est pas masqué. Les deux routeurs conservent les vraies adresses internes et utilisent des routes statiques via WireGuard.

---

## 8. VPN WireGuard pour les employés

Un VPN d’accès distant nommé `wg-employees` a été créé sur R1-HQ.

Paramètres principaux :

- protocole : WireGuard ;
- port d’écoute : UDP `13231` ;
- réseau VPN : `10.20.20.0/24` ;
- passerelle VPN : `10.20.20.1` ;
- employé de test : `10.20.20.2` ;
- keepalive : 25 secondes.

Un employé possédant la configuration et la clé WireGuard correctes peut établir un tunnel chiffré depuis un réseau externe. Après connexion, les règles du firewall l’autorisent à atteindre le réseau du siège et à utiliser Internet selon les autorisations définies.

Sans VPN, le poste externe ne peut pas atteindre directement les ressources du siège.

---

## 9. VPN site-à-site entre HQ et Branch

Un second tunnel WireGuard nommé `wg-s2s` relie R1-HQ et R2-Branch.

Paramètres principaux :

- port : UDP `13232` ;
- réseau de transit : `10.255.255.0/30` ;
- R1-HQ : `10.255.255.1` ;
- R2-Branch : `10.255.255.2` ;
- keepalive : 25 secondes.

Les routes statiques sont :

- sur R1-HQ : `10.30.30.0/24` via `wg-s2s` ;
- sur R2-Branch : `10.10.10.0/24` via `wg-s2s`.

Ce VPN permet aux machines autorisées du siège et de la succursale de communiquer dans un tunnel chiffré, sans exposer directement leurs réseaux internes.

---

## 10. Tests réalisés

| Test | Résultat |
|---|---|
| Employé externe sans VPN vers le réseau HQ | Bloqué |
| Employé externe connecté au VPN vers HQ | Réussi |
| Handshake WireGuard de l’employé | Réussi |
| Employé VPN vers Internet | Réussi |
| R2-Branch vers l’extrémité VPN de R1-HQ | Réussi, 0 % de perte |
| Branch vers Ubuntu HQ `10.10.10.200` | Réussi, 0 % de perte |
| Ubuntu HQ vers R2-Branch `10.30.30.1` | Réussi, 0 % de perte |
| Ubuntu HQ vers Internet | Réussi, réponse HTTPS `HTTP 200 OK` |
| Redémarrage de R2 puis R1 | Configuration et VPN restaurés automatiquement |

Une réponse `HTTP 200 OK` signifie que le client Ubuntu a pu atteindre un serveur web par HTTPS et que le serveur a répondu correctement. Ce test confirme le fonctionnement de la route, du firewall, du NAT, du DNS et de la connexion Internet.

---

## 11. Sauvegardes finales

Deux formats ont été conservés pour chaque routeur :

- **`.backup`** : copie binaire complète permettant de restaurer rapidement le même routeur ou la même VM ;
- **`.rsc`** : export texte lisible pour l’audit, la documentation ou une reconstruction manuelle.

Fichiers finaux :

- `R1-HQ-final-validated.backup` ;
- `R1-HQ-final-validated.rsc` ;
- `R2-Branch-final-validated.backup` ;
- `R2-Branch-final-validated.rsc`.

Les exports texte de livraison ne contiennent pas les clés privées VPN ni les mots de passe. Les secrets doivent être transmis séparément et stockés dans un gestionnaire de mots de passe.

Il ne faut jamais restaurer la sauvegarde de R1-HQ sur R2-Branch, ni celle de R2-Branch sur R1-HQ.

---

## 12. Problèmes résolus par le projet

Cette infrastructure apporte les solutions suivantes :

- blocage des connexions entrantes non autorisées ;
- protection de l’administration des routeurs ;
- accès Internet contrôlé pour le siège et la succursale ;
- accès distant sécurisé pour les employés ;
- chiffrement des communications entre les deux sites ;
- séparation claire entre WAN, LAN et VPN ;
- attribution automatique des paramètres réseau avec DHCP ;
- possibilité de restaurer rapidement les routeurs grâce aux sauvegardes ;
- conservation des vraies adresses entre HQ et Branch pour faciliter le contrôle et le diagnostic.

---

## 13. Limites du laboratoire et passage en production

Le laboratoire prouve le fonctionnement technique, mais il ne doit pas être déployé tel quel dans l’entreprise. Avant la mise en production, il faudra :

- remplacer les adresses WAN UTM par les vraies connexions Internet ;
- adapter les interfaces au câblage, aux switches et aux VLAN de l’entreprise ;
- disposer d’une IP publique ou de redirections UDP pour WireGuard ;
- utiliser un DNS dynamique si l’adresse publique change ;
- limiter WebFig, SSH et WinBox à un réseau ou des adresses d’administration ;
- installer un certificat HTTPS valide pour WebFig si ce service est conservé ;
- créer des comptes administrateurs nominatifs avec des mots de passe uniques ;
- révoquer immédiatement les accès des employés qui quittent l’entreprise ;
- prévoir la supervision, la journalisation et les alertes ;
- tester le VPN employés depuis une vraie connexion externe, par exemple 4G/5G ;
- prévoir la redondance afin qu’une seule panne ne coupe pas toute l’entreprise ;
- préparer un plan de retour arrière avant chaque changement important.

---

## 14. Durcissement complémentaire

Une fois le laboratoire validé, une relecture complète des deux configurations exportées a été menée. Elle ne remet pas en cause les résultats du chapitre 10 : les flux autorisés passent, les flux non autorisés sont bloqués. Elle identifie en revanche des points qui échappent à la politique **default deny**, ou qui ne sont pas visibles dans un test de connectivité.

Les corrections sont regroupées dans deux scripts livrés séparément et **non appliqués** à la configuration validée :

- `delivery/hardening/R1-HQ-hardening.rsc` ;
- `delivery/hardening/R2-Branch-hardening.rsc`.

La configuration du 26 juillet 2026 reste donc intacte et reste la référence.

### 14.1 Le plan de management de niveau 2

C’est le point le plus important de cette relecture.

Le pare-feu configuré aux chapitres 6 et 7 filtre le trafic **IP**, c’est-à-dire la couche 3. Or RouterOS expose aussi deux services d’administration qui fonctionnent en **couche 2**, directement sur les adresses MAC : **MAC-WinBox** et **MAC-Telnet**. Ils permettent d’administrer un routeur qui n’a même pas d’adresse IP.

Ces services ne traversent pas `/ip firewall filter`. La règle `INPUT default deny` ne les voit jamais. Par défaut, ils sont activés sur **toutes** les interfaces, y compris celles du côté non fiable.

Autrement dit : un poste situé sur le même domaine de diffusion qu’une interface du routeur peut ouvrir une session d’administration sans qu’aucune règle de pare-feu n’intervienne.

La correction consiste à restreindre ces services, ainsi que le protocole de découverte de voisinage, à la seule liste d’interfaces `LAN` :

```text
/tool mac-server set allowed-interface-list=LAN
/tool mac-server mac-winbox set allowed-interface-list=LAN
/tool mac-server ping set enabled=no
/ip neighbor discovery-settings set discover-interface-list=LAN
```

L’accès WinBox par adresse IP n’est pas affecté : il relève de la couche 3 et reste soumis aux règles de la chaîne `input`.

### 14.2 Interface supplémentaire sur R1-HQ

La machine virtuelle de R1-HQ déclare **trois** cartes réseau, alors que le plan d’adressage du chapitre 3 n’en documente que deux :

| Carte | Mode UTM | Correspondance | Documentée |
|---|---|---|---|
| net0 | Shared | `ether1` — WAN `192.168.64.0/24` | oui |
| net1 | Host | `ether2` — LAN HQ `10.10.10.0/24` | oui |
| net2 | Bridged sur `en0` | `ether3` — réseau physique de l’hôte | **non** |

La troisième carte est pontée sur la carte réseau réelle du Mac. Elle n’apparaît dans aucune adresse, aucune route, aucune règle et aucune liste d’interfaces de la configuration validée.

Au niveau IP, cela reste sans conséquence : le trafic arrivant par `ether3` ne correspond à aucune règle d’acceptation et se termine sur `INPUT default deny`. Combinée au point 14.1, en revanche, cette carte constituait bien un chemin d’administration en couche 2 vers le réseau physique.

Si la carte est confirmée inutilisée, la désactiver supprime le problème à la racine, ce qui est préférable à la seule restriction du MAC-server :

```text
/interface ethernet set [find default-name=ether3] disabled=yes
```

R2-Branch n’est pas concernée : elle ne possède que deux cartes.

### 14.3 Absence de filtrage IPv6

Le projet a été construit entièrement en IPv4. Aucune règle n’a été écrite dans `/ipv6 firewall filter`, qui est donc vide sur les deux routeurs.

Tant que le paquet `ipv6` est actif, il existe une pile réseau complète qui n’est soumise à aucune politique de filtrage, alors que l’intention du projet est de tout bloquer par défaut. Puisque aucun élément de l’architecture n’utilise IPv6, le plus simple est de le désactiver :

```text
/ipv6 settings set disable-ipv6=yes
```

Ce changement nécessite un redémarrage. La solution alternative, si IPv6 devait être conservé, est d’écrire un jeu de règles IPv6 reprenant la même logique que le chapitre 6.

### 14.4 Journalisation des rejets

Les règles de rejet des chapitres 6 et 7 bloquent correctement, mais ne laissent aucune trace. En cas d’incident, rien ne permet de savoir ce qui a été bloqué, ni depuis quelle adresse.

Trois règles reçoivent donc un préfixe de journalisation : `IN-DROP`, `FWD-DROP` et `IN-INVALID`. Cela répond directement au besoin de « supervision, journalisation et alertes » identifié au chapitre 13.

### 14.5 Ajustement du MSS sur les tunnels WireGuard

Les interfaces WireGuard utilisent un MTU de 1420, inférieur aux 1500 habituels, car le chiffrement ajoute son propre en-tête.

Sans ajustement, certaines sessions TCP négocient un segment trop grand pour le tunnel. Le paquet est alors détruit en chemin, souvent sans message d’erreur exploitable : la connexion semble établie, mais la page reste en chargement. C’est le phénomène connu sous le nom de *PMTU black hole*.

Une règle `change-mss` sur la liste d’interfaces `VPN` ajuste automatiquement la taille annoncée à chaque ouverture de session TCP. Ce défaut n’apparaît pas dans les tests du chapitre 10, qui reposent sur le ping et sur une requête HTTPS unique.

### 14.6 Synchronisation de l’horloge

Aucun client NTP n’était configuré. Sans horloge juste, l’horodatage des journaux ajoutés en 14.4 est inexploitable, et la validation des certificats TLS devient impossible. Un client NTP est donc activé sur les deux routeurs.

### 14.7 Asymétrie entre R1-HQ et R2-Branch

Les deux routeurs ne traitent pas le tunnel site-à-site de la même façon dans la chaîne `input` :

| Routeur | Règle | Portée |
|---|---|---|
| R1-HQ | `INPUT allow Branch via site-to-site` | tout ce qui arrive par `wg-s2s` |
| R2-Branch | `INPUT allow HQ via site-to-site` | uniquement `10.10.10.0/24` |

R1-HQ émet depuis son extrémité de tunnel `10.255.255.1`, qui n’appartient pas à `10.10.10.0/24`. Un `ping 10.255.255.2` lancé depuis R1 échoue donc, alors même que le tunnel fonctionne. Ce n’est pas une faille, mais cela fausse le diagnostic : l’administrateur peut conclure à une panne du VPN là où il n’y en a pas.

Une règle est ajoutée sur R2-Branch pour accepter l’extrémité de tunnel de R1.

### 14.8 Gestion des secrets et versionnement

Le chapitre 11 précise que les exports `.rsc` ne contiennent ni clés privées ni mots de passe. Ce n’est pas le cas des sauvegardes binaires `.backup`, qui contiennent l’intégralité de la configuration, **y compris les clés privées WireGuard et les hachages des mots de passe administrateurs**.

Un fichier `.gitignore` a été ajouté au dépôt du projet afin d’appliquer cette distinction de manière systématique :

- les exports `.rsc`, la documentation et les schémas sont versionnés ;
- les sauvegardes `.backup`, les images disque et le fichier `cloud-init` contenant un hachage de mot de passe en sont exclus.

Le dépôt passe ainsi de 4,4 Go à 14,3 Mo et ne contient plus aucun élément sensible.

### 14.9 Récapitulatif et méthode d’application

| Point | Nature | Risque d’interruption |
|---|---|---|
| 14.1 Management de niveau 2 | Ajout | Aucun |
| 14.4 Journalisation des rejets | Modification de règles existantes | Aucun |
| 14.5 Ajustement du MSS | Ajout | Aucun |
| 14.6 Client NTP | Ajout | Aucun |
| 14.7 Asymétrie R1 / R2 | Ajout | Aucun |
| 14.3 Désactivation d’IPv6 | Paramètre système | Redémarrage requis |
| 14.2 Désactivation d’`ether3` | Paramètre d’interface | À vérifier au préalable |

Les points relevant du passage en production — restriction de WebFig, SSH et WinBox à un réseau d’administration, comptes nominatifs, certificat HTTPS — restent traités au chapitre 13 et ne sont pas repris ici.

Toute modification doit être appliquée selon la procédure suivante :

1. sauvegarder l’état courant (`/system backup save` et `/export`) ;
2. activer le **Safe Mode** du terminal RouterOS (`Ctrl+X`) : si la session d’administration est interrompue, le routeur restaure automatiquement la configuration précédente ;
3. appliquer les sections une par une, en vérifiant après chacune ;
4. quitter le Safe Mode pour rendre les changements permanents ;
5. rejouer les tests du chapitre 10 avant de considérer la nouvelle configuration comme validée.

Cette procédure répond au « plan de retour arrière avant chaque changement important » prévu au chapitre 13.

---

## 15. Conclusion

Le projet a permis de réaliser un laboratoire complet composé de deux pare-feu MikroTik, de deux réseaux LAN protégés, d’un accès Internet avec NAT, d’un VPN pour les employés et d’un VPN site-à-site.

Les tests ont confirmé que :

- les communications nécessaires sont autorisées ;
- les communications non autorisées sont bloquées ;
- les employés peuvent accéder au siège uniquement après authentification VPN ;
- le siège et la succursale communiquent dans un tunnel chiffré ;
- les configurations, routes et tunnels reviennent après redémarrage.

Le laboratoire est donc **fonctionnel et validé**. La relecture menée au chapitre 14 complète ce résultat : elle montre qu’une configuration peut réussir tous ses tests de connectivité tout en laissant subsister des chemins qui échappent au filtrage, comme le plan de management de niveau 2. Les corrections correspondantes sont livrées sous forme de scripts, distincts de la configuration validée.

Le passage en production reste une étape séparée qui doit être adaptée à l’infrastructure réelle de l’entreprise.

