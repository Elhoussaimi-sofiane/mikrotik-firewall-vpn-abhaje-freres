# ===========================================================================
#  R1-HQ  --  Durcissement complementaire (palier 1)
#  Projet Firewall MikroTik / VPN -- Ste Abhaje Freres
#  Base : R1-HQ-final-validated.rsc (RouterOS 7.22.1, CHR arm64)
# ===========================================================================
#
#  CE SCRIPT N'A PAS ETE APPLIQUE. Il complete la configuration validee du
#  26 juillet 2026 sans la remplacer.
#
#  Ce palier ne contient QUE des changements qui ne peuvent pas couper
#  l'acces au routeur depuis l'hote UTM (192.168.64.1) :
#    - aucune modification des regles filter existantes ;
#    - aucune modification de /ip service ;
#    - aucune modification des adresses, routes ou pairs WireGuard.
#
#  Les changements a risque (restriction de la regle de management UTM,
#  rp-filter, restriction de WebFig/SSH/WinBox) sont dans le palier 2,
#  fichier separe, a appliquer en Safe Mode uniquement.
#
#  --- PROCEDURE ---------------------------------------------------------
#  1. /system backup save name=R1-pre-hardening
#     /export file=R1-pre-hardening
#  2. Ouvrir le terminal RouterOS et activer le Safe Mode : Ctrl+X
#  3. Coller les sections une par une, verifier apres chacune.
#  4. Quitter le Safe Mode (Ctrl+X) pour rendre les changements permanents.
#  -----------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1. Plan de management de niveau 2 (MAC-Telnet / MAC-WinBox / decouverte)
# ---------------------------------------------------------------------------
# Par defaut, RouterOS accepte MAC-WinBox et MAC-Telnet sur TOUTES les
# interfaces. Ce plan de management fonctionne en couche 2 : il ne traverse
# pas les regles /ip firewall filter et n'est donc pas couvert par la
# politique "default deny" de la chaine input.
#
# Sur cette machine, R1 possede une troisieme carte reseau pontee sur en0,
# c'est-a-dire sur le reseau physique reel de l'hote (192.168.110.0/24).
# MAC-WinBox y est donc joignable depuis le vrai reseau local.
#
# Apres ces lignes, le management de niveau 2 n'est plus possible que depuis
# la liste LAN (ether2). L'acces WinBox par IP depuis 192.168.64.1 (port
# 8291) n'est pas affecte : c'est du niveau 3, gere par la chaine input.

/tool mac-server set allowed-interface-list=LAN
/tool mac-server mac-winbox set allowed-interface-list=LAN
/tool mac-server ping set enabled=no
/ip neighbor discovery-settings set discover-interface-list=LAN


# ---------------------------------------------------------------------------
# 2. Journalisation des paquets bloques
# ---------------------------------------------------------------------------
# Les regles de rejet ne laissaient aucune trace : en cas d'incident, rien
# ne permettait de savoir ce qui avait ete bloque, ni depuis ou.
# Les prefixes permettent de filtrer directement dans /log print.

/ip firewall filter set [find comment="INPUT default deny"] \
    log=yes log-prefix="IN-DROP"
/ip firewall filter set [find comment="FORWARD default deny"] \
    log=yes log-prefix="FWD-DROP"
/ip firewall filter set [find comment="INPUT drop invalid"] \
    log=yes log-prefix="IN-INVALID"

# Note : sur un lien tres sollicite, la regle FORWARD default deny peut
# generer beaucoup de lignes. En production, prevoir /system logging avec
# une action distante (syslog) plutot que le tampon memoire par defaut.


# ---------------------------------------------------------------------------
# 3. Ajustement du MSS sur les tunnels WireGuard
# ---------------------------------------------------------------------------
# Le MTU des interfaces WireGuard est fixe a 1420. Sans ajustement du MSS,
# certaines sessions TCP (typiquement HTTPS) negocient un segment trop grand
# et se bloquent sans message d'erreur lisible : la page reste en chargement.
# C'est le probleme classique du "PMTU black hole".
#
# Regle purement additive : elle ne modifie aucune regle existante.

/ip firewall mangle add chain=forward action=change-mss \
    new-mss=clamp-to-pmtu passthrough=yes protocol=tcp tcp-flags=syn \
    out-interface-list=VPN \
    comment="Ajuste le MSS sur les tunnels WireGuard (PMTU)"


# ---------------------------------------------------------------------------
# 4. Synchronisation de l'horloge
# ---------------------------------------------------------------------------
# Sans NTP, l'horodatage des journaux est faux et la validation des
# certificats TLS devient impossible. C'est un prerequis a toute
# exploitation serieuse des journaux ajoutes en section 2.
#
# Le trafic NTP sortant du routeur passe par la chaine output (non filtree)
# et les reponses reviennent en established : aucune regle a ajouter.

/system ntp client set enabled=yes mode=unicast \
    servers=0.pool.ntp.org,1.pool.ntp.org


# ---------------------------------------------------------------------------
# 5. Algorithmes SSH
# ---------------------------------------------------------------------------
# Desactive les algorithmes d'echange et de chiffrement les plus anciens.
# Les clients OpenSSH modernes (dont celui de macOS) ne sont pas concernes.

/ip ssh set strong-crypto=yes


# ===========================================================================
#  A VERIFIER AVANT APPLICATION -- ne pas coller tel quel
# ===========================================================================
#
# --- 5a. Interface ether3 (pont vers le reseau physique) ---
#
# La VM "MikroTik CHR Automated" declare trois cartes reseau :
#     net0  Shared   -> 192.168.64.0/24        = ether1 (WAN)
#     net1  Host     -> segment LAN HQ         = ether2 (LAN)
#     net2  Bridged  -> en0, reseau reel       = ether3  <-- non documente
#
# ether3 n'apparait dans aucune regle, aucune adresse et aucune liste
# d'interfaces de la configuration validee. Si elle est bien inutilisee,
# la desactiver supprime l'exposition a la racine, ce qui est plus solide
# que la seule restriction MAC-server de la section 1 :
#
#     /interface ethernet set [find default-name=ether3] disabled=yes \
#         comment="Inutilisee - pont UTM vers en0, desactivee par securite"
#
# VERIFIER D'ABORD, sur le routeur :
#     /interface ethernet print detail
#     /interface print stats
# Si ether3 ne compte aucun paquet utile, la desactivation est sans effet
# sur le fonctionnement du lab.
#
#
# --- 5b. Ecart entre la configuration validee et la configuration active ---
#
# Depuis l'hote, R1 repond sur TCP 22, 80 et 8291, mais ne repond pas au
# ping. Avec la configuration du 26 juillet, un ping depuis 192.168.64.1
# devrait aboutir (regle "INPUT allow UTM host management", puis regle
# "INPUT allow limited ICMP"). La configuration active a donc probablement
# derive de l'export.
#
# A executer avant toute modification, pour comparer :
#     /export file=R1-etat-actuel
#     /system package print
#
# ===========================================================================
