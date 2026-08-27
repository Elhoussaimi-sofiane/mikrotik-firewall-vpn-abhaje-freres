# Pare-feu MikroTik et VPN sécurisés — Sté Abhaje Frères

Laboratoire réseau complet : deux pare-feu **MikroTik CHR sous RouterOS 7.22.1**
(arm64, virtualisés sous UTM sur Mac Apple Silicon), un VPN WireGuard pour les
employés en télétravail et une liaison site-à-site chiffrée entre le siège et la
succursale.

**État : laboratoire fonctionnel, testé et validé le 26 juillet 2026.**

---

## Avertissement de sécurité — à lire avant toute mise en production

Le disque de la machine virtuelle R1-HQ est fourni dans ce dépôt pour que le
routeur démarre tel quel. **Ce disque contient les clés privées WireGuard et les
hachages de mots de passe du routeur.**

Conséquences directes :

1. Ce dépôt doit rester **privé**. Ne jamais le rendre public.
2. Avant la mise en production, **régénérer les clés WireGuard** des deux
   routeurs et de chaque poste employé, et **changer les mots de passe
   administrateurs**. Toute personne ayant eu accès au dépôt a eu accès aux clés
   actuelles.
3. Les sauvegardes binaires `.backup` de RouterOS ne sont **pas** versionnées
   (voir `.gitignore`) : elles sont transmises séparément. Les exports texte
   `.rsc`, eux, ne contiennent aucun secret et sont versionnés pour l'audit.

---

## Architecture

```text
                         INTERNET / RÉSEAU WAN UTM
                                  │
              ┌───────────────────┴───────────────────┐
              │                                       │
       WAN 192.168.64.2                         WAN 192.168.64.4
          ┌─────────┐        WireGuard            ┌───────────┐
          │  R1-HQ  │◄──── VPN site-à-site ──────►│ R2-Branch │
          │Firewall │      UDP 13232              │ Firewall  │
          └────┬────┘      10.255.255.0/30        └─────┬─────┘
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

Les adresses WAN `192.168.64.x` appartiennent au laboratoire UTM. Elles devront
être remplacées par les vraies informations du fournisseur d'accès lors du
déploiement réel.

---

## Contenu du dépôt

| Chemin | Contenu |
|---|---|
| `Resume_Projet_Firewall_MikroTik.md` | Documentation principale, 15 chapitres : architecture, plan d'adressage, règles de pare-feu, VPN, tests, durcissement. **Point d'entrée pour la relecture.** |
| `PROMPT-corrections-MikroTik.md` | Les 10 points de durcissement identifiés après validation (P1 à P10), avec leur criticité et le résultat attendu. |
| `vm/MikroTik CHR Automated.utm/` | Machine virtuelle UTM du routeur principal **R1-HQ**, prête à démarrer. |
| `delivery/backups/R1-HQ/*.rsc` | Export texte de la configuration validée de R1-HQ. |
| `delivery/backups/R2-Branch/*.rsc` | Export texte de la configuration validée de R2-Branch. |
| `delivery/hardening/*.rsc` | Scripts de durcissement des deux routeurs — **écrits mais jamais appliqués** : la configuration validée du 26 juillet reste la référence. |
| `delivery/architecture-*.png` / `.svg` | Schémas d'architecture. |
| `output/pdf/` | Cahier des charges et dossier de livraison au format PDF. |
| `output/documents/` | Cahier des charges au format DOCX. |
| `cloud-init-seed/` | Configuration de la VM Ubuntu de test du LAN siège. |
| `*.applescript` | Scripts d'automatisation de la création des VM sous UTM. |
| `build_mikrotik_guide.py`, `tmp/` | Générateurs des documents PDF et rendus intermédiaires. |

---

## Démarrer le routeur R1-HQ

Prérequis : un Mac Apple Silicon et [UTM](https://mac.getutm.app).

1. Cloner le dépôt.
2. Double-cliquer sur `vm/MikroTik CHR Automated.utm` : UTM importe la machine.
3. Démarrer la VM. Au premier lancement, UTM regénère le fichier de variables
   EFI (`efi_vars.fd`, 376 Mo), volontairement exclu du dépôt.
4. Se connecter en console UTM, ou depuis le Mac hôte :

   ```sh
   ssh admin@192.168.64.2        # SSH
   # WebFig :  http://192.168.64.2
   # WinBox :  192.168.64.2:8291
   ```

Les mots de passe ne figurent pas dans ce dépôt ; ils sont transmis séparément.

La VM déclare trois cartes réseau : `ether1` → WAN (mode *Shared*), `ether2` →
LAN siège (mode *Host*), `ether3` → pontée sur `en0`. **`ether3` n'est utilisée
par aucune configuration** ; c'est le point P2 du fichier de corrections.

### Reconstruire un routeur depuis zéro

Si vous préférez repartir d'une image CHR propre plutôt que d'utiliser le disque
fourni — ce qui est la démarche recommandée en production, puisqu'aucun secret
n'est alors hérité :

```sh
# Sur le routeur, une fois l'image CHR démarrée :
/import file=R1-HQ-final-validated.rsc
```

Les clés privées WireGuard ne se trouvant pas dans l'export `.rsc`, il faut
ensuite générer une nouvelle paire de clés par interface WireGuard et mettre à
jour les clés publiques chez chaque pair.

La VM R2-Branch n'est pas incluse dans ce dépôt : elle se reconstruit de la même
façon à partir de `delivery/backups/R2-Branch/R2-Branch-final-validated.rsc`.

---

## Politique de filtrage

Les deux routeurs appliquent un **`default deny`** sur les chaînes `input` et
`forward` : tout ce qui n'est pas explicitement autorisé est rejeté.

Flux autorisés :

- LAN siège et LAN succursale vers Internet, en NAT masquerade ;
- employés VPN vers le LAN siège et vers Internet ;
- LAN siège ↔ LAN succursale, via le tunnel site-à-site ;
- administration depuis l'hôte UTM `192.168.64.1` et depuis les LAN de confiance ;
- ICMP, avec limitation de débit.

Services désactivés sur les deux routeurs : Telnet, FTP, API, API-SSL, reverse
proxy. Services d'administration conservés : WebFig, SSH, WinBox.

---

## Ce qui reste à faire

Les 10 points de `PROMPT-corrections-MikroTik.md` ne sont **pas** appliqués. Les
plus critiques :

- **P1** — MAC-WinBox et MAC-Telnet sont actifs sur toutes les interfaces. Ces
  services opèrent en couche 2 et ne traversent jamais `/ip firewall filter` :
  le `default deny` ne les voit pas. Tout poste du même domaine de diffusion
  peut ouvrir une session d'administration.
- **P2** — L'interface `ether3` de R1-HQ est pontée sur le réseau physique du
  Mac et n'est documentée nulle part. Combinée à P1, elle constituait un chemin
  d'administration de niveau 2 vers ce réseau.
- **P3** — Aucune règle IPv6 alors que la pile IPv6 est active : une pile réseau
  complète échappe au filtrage.
- **P9** — Dérive constatée entre la configuration active de R1 et l'export du
  26 juillet, à investiguer avant toute modification.

Les points de passage en production (restriction de l'administration à un réseau
dédié, comptes nominatifs, certificat HTTPS pour WebFig, syslog distant, IP
publique pour WireGuard, supervision, révocation des accès employés) sont
détaillés au chapitre 13 de la documentation.

---

## Contribuer aux corrections

Toute modification de configuration doit respecter les contraintes du chapitre
14 de la documentation :

1. Sauvegarder avant : `/system backup save` **et** `/export`.
2. Travailler en **Safe Mode** (`Ctrl+X`) : une coupure de session restaure
   automatiquement l'état précédent.
3. Aucun changement ne doit pouvoir couper l'accès depuis l'hôte UTM
   `192.168.64.1`.
4. Appliquer section par section et vérifier après chacune.
5. Ne jamais restaurer la sauvegarde de R1 sur R2, ni l'inverse.

---

Auteur : El Houssaimi Sofiane — projet de stage, Sté Abhaje Frères.
