# Prompt — Corrections à appliquer sur les pare-feu MikroTik

> Copier-coller le bloc ci-dessous tel quel dans une nouvelle session.

---

## CONTEXTE

Je dispose d'un laboratoire réseau validé le 26 juillet 2026, à durcir avant mise en production.

**Matériel / logiciel** : 2 × MikroTik CHR, RouterOS 7.22.1, arm64, virtualisés sous UTM sur Mac Apple Silicon.

**Architecture**

```
                    WAN UTM 192.168.64.0/24  (hôte = 192.168.64.1)
                    │                                   │
            R1-HQ (192.168.64.2) ◄── WireGuard wg-s2s ──► R2-Branch (192.168.64.4)
                    │              UDP 13232                    │
                    │              10.255.255.0/30              │
            LAN HQ 10.10.10.1/24                        LAN Branch 10.30.30.1/24
            DHCP .100-.200                              DHCP .100-.200
            Ubuntu HQ-Test-Client 10.10.10.200

  Employé distant ── WireGuard wg-employees UDP 13231 ──► R1-HQ (10.20.20.1/24)
```

**État actuel**
- Politique `default deny` sur `input` et `forward`, NAT masquerade sur les 3 réseaux privés, routes statiques via `wg-s2s`.
- Tous les tests de connectivité passent (0 % de perte, `HTTP 200 OK` depuis le LAN HQ).
- Deux scripts de durcissement existent mais **n'ont jamais été appliqués** :
  `delivery/hardening/R1-HQ-hardening.rsc` et `delivery/hardening/R2-Branch-hardening.rsc`.
- Documentation de référence : `Resume_Projet_Firewall_MikroTik.md` (chapitre 14).

---

## PROBLÈMES À RÉSOUDRE

### P1 — Plan de management de niveau 2 hors firewall  *(R1 + R2, critique)*
MAC-WinBox et MAC-Telnet sont actifs sur **toutes** les interfaces. Ces services fonctionnent en couche 2 et ne traversent jamais `/ip firewall filter` : la règle `INPUT default deny` ne les voit pas. N'importe quel poste du même domaine de diffusion peut ouvrir une session d'administration.
→ Restreindre `mac-server`, `mac-winbox`, `mac-server ping` et `ip neighbor discovery` à la seule liste d'interfaces `LAN`.

### P2 — Interface `ether3` non documentée sur R1-HQ  *(R1, critique)*
La VM de R1 déclare 3 cartes : `net0` Shared → `ether1` (WAN), `net1` Host → `ether2` (LAN), `net2` **Bridged sur en0** → `ether3` = réseau physique réel du Mac. `ether3` n'apparaît dans aucune adresse, route, règle ou interface-list. Combinée à P1, elle constituait un chemin d'administration L2 vers le réseau physique.
→ Vérifier `/interface print stats` et `/interface ethernet print detail`; si aucun trafic utile, désactiver l'interface plutôt que de se reposer uniquement sur P1. R2 n'a que 2 cartes, non concernée.

### P3 — Aucun filtrage IPv6  *(R1 + R2)*
`/ipv6 firewall filter` est vide sur les deux routeurs alors que le paquet `ipv6` est actif : une pile réseau complète échappe à la politique de filtrage. Rien dans l'architecture n'utilise IPv6.
→ Désactiver IPv6 (`/ipv6 settings set disable-ipv6=yes`, **redémarrage requis**), ou écrire un jeu de règles IPv6 reprenant la logique IPv4.

### P4 — Règles de rejet sans journalisation  *(R1 + R2)*
Les règles `INPUT default deny`, `FORWARD default deny` et `INPUT drop invalid` bloquent correctement mais ne laissent aucune trace : en cas d'incident, impossible de savoir ce qui a été bloqué ni depuis quelle adresse.
→ Ajouter les préfixes `IN-DROP`, `FWD-DROP`, `IN-INVALID`. Prévoir un syslog distant en production (le tampon mémoire par défaut ne suffit pas sur `FORWARD`).

### P5 — MSS non ajusté sur les tunnels WireGuard  *(R1 + R2)*
MTU WireGuard = 1420. Sans `change-mss`, certaines sessions TCP (typiquement HTTPS) négocient un segment trop grand, détruit en chemin sans erreur exploitable — *PMTU black hole*. Le défaut n'apparaît pas dans les tests actuels, basés sur le ping et une requête HTTPS unique.
→ Règle `mangle` `change-mss` / `clamp-to-pmtu` sur `out-interface-list=VPN`.

### P6 — Horloge non synchronisée  *(R1 + R2)*
Aucun client NTP configuré : l'horodatage des journaux de P4 est inexploitable et la validation des certificats TLS impossible.
→ Activer le client NTP en unicast.

### P7 — Asymétrie R1 / R2 sur le tunnel site-à-site  *(R2)*
Côté R1 la règle `INPUT allow Branch via site-to-site` accepte tout ce qui arrive par `wg-s2s`; côté R2 l'équivalent est limité à `src-address=10.10.10.0/24`. R1 émettant depuis `10.255.255.1`, un `ping 10.255.255.2` depuis R1 échoue alors que le tunnel fonctionne. Ce n'est pas une faille, mais cela fausse le diagnostic.
→ Ajouter sur R2 une règle acceptant `10.255.255.1/32` via `wg-s2s`, placée avant le rejet final.

### P8 — Algorithmes SSH anciens  *(R1 + R2)*
→ `/ip ssh set strong-crypto=yes`. Sans effet sur les clients OpenSSH modernes.

### P9 — Dérive entre configuration exportée et configuration active  *(R1, à investiguer)*
Depuis l'hôte, R1 répond sur TCP 22, 80 et 8291 mais **ne répond pas au ping**, alors que les règles `INPUT allow UTM host management` puis `INPUT allow limited ICMP` devraient l'autoriser. La configuration active a probablement dérivé de l'export du 26 juillet.
→ Faire `/export file=R1-etat-actuel` + `/system package print` et comparer avec `R1-HQ-final-validated.rsc` avant toute modification.

### P10 — Points de passage en production non traités  *(R1 + R2)*
Restent ouverts, volontairement hors du palier de durcissement : restriction de WebFig/SSH/WinBox à un réseau d'administration, comptes administrateurs nominatifs avec mots de passe uniques, certificat HTTPS valide pour WebFig, `rp-filter`, IP publique ou redirection UDP pour WireGuard, DNS dynamique, supervision et alertes, redondance, révocation des accès employés.

---

## CONTRAINTES

- Ne pas modifier la configuration validée du 26/07/2026 sans sauvegarde préalable : `/system backup save` **et** `/export`.
- Travailler en **Safe Mode** (`Ctrl+X`) : toute coupure de session restaure automatiquement l'état précédent.
- **Aucun changement ne doit pouvoir couper l'accès depuis l'hôte UTM `192.168.64.1`** — séparer les modifications additives (palier 1) des modifications à risque touchant `/ip service`, les règles de management ou `rp-filter` (palier 2).
- Appliquer section par section, vérifier après chacune, puis quitter le Safe Mode.
- Les `.backup` binaires contiennent les clés privées WireGuard et les hachages de mots de passe : ne jamais les versionner (déjà couvert par `.gitignore`).
- Ne jamais restaurer la sauvegarde de R1 sur R2, ni l'inverse.

---

## CE QUE J'ATTENDS

1. Un ordre d'application argumenté, en distinguant ce qui n'interrompt rien de ce qui nécessite un redémarrage ou une vérification préalable.
2. Pour chaque problème : les commandes RouterOS 7.22.1 exactes, avec la commande de vérification associée.
3. La procédure de retour arrière si une section échoue.
4. Le plan de tests à rejouer après application :
   - `ping 10.255.255.1` depuis R2 → 0 % de perte
   - `ping 10.10.10.200` depuis Branch → 0 % de perte
   - `ping 10.30.30.1` depuis Ubuntu HQ → 0 % de perte
   - `curl -I https://example.com` depuis Ubuntu HQ → `HTTP 200 OK`
   - employé externe **sans** VPN vers HQ → doit rester bloqué
   - employé externe **avec** VPN vers HQ → doit aboutir
   - redémarrage R2 puis R1 → configuration, routes et tunnels restaurés

Prérequis : démarrer la VM R2-Branch (elle était à l'arrêt lors de l'analyse) et attendre le rétablissement du tunnel WireGuard, ainsi que HQ-Test-Client et Remote-Employee-Test pour les tests.
