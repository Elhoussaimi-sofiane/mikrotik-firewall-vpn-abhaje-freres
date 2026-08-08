# ===========================================================================
#  R2-Branch  --  Durcissement complementaire (palier 1)
#  Projet Firewall MikroTik / VPN -- Ste Abhaje Freres
#  Base : R2-Branch-final-validated.rsc (RouterOS 7.22.1, CHR arm64)
# ===========================================================================
#
#  CE SCRIPT N'A PAS ETE APPLIQUE.
#
#  Meme perimetre que le palier 1 de R1-HQ : aucun changement ne peut
#  couper l'acces au routeur depuis l'hote UTM (192.168.64.1).
#
#  La VM R2-Branch etait a l'arret au moment de l'analyse. La demarrer et
#  attendre le retablissement du tunnel WireGuard avant d'appliquer quoi
#  que ce soit.
#
#  --- PROCEDURE ---------------------------------------------------------
#  1. /system backup save name=R2-pre-hardening
#     /export file=R2-pre-hardening
#  2. Terminal RouterOS, Safe Mode : Ctrl+X
#  3. Coller les sections une par une.
#  4. Quitter le Safe Mode (Ctrl+X).
#  -----------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1. Plan de management de niveau 2
# ---------------------------------------------------------------------------
# Meme raisonnement que sur R1 : MAC-WinBox et MAC-Telnet ne traversent pas
# /ip firewall filter et echappent donc a la politique "default deny".
#
# R2 n'a que deux cartes reseau (Shared + Host), elle n'est pas pontee sur
# le reseau physique. Mais son interface WAN partage le meme segment de
# niveau 2 que R1 (192.168.64.0/24) : sans cette restriction, R1 et R2
# restent mutuellement joignables en couche 2, hors de tout filtrage IP.

/tool mac-server set allowed-interface-list=LAN
/tool mac-server mac-winbox set allowed-interface-list=LAN
/tool mac-server ping set enabled=no
/ip neighbor discovery-settings set discover-interface-list=LAN


# ---------------------------------------------------------------------------
# 2. Journalisation des paquets bloques
# ---------------------------------------------------------------------------

/ip firewall filter set [find comment="INPUT default deny"] \
    log=yes log-prefix="IN-DROP"
/ip firewall filter set [find comment="FORWARD default deny"] \
    log=yes log-prefix="FWD-DROP"
/ip firewall filter set [find comment="INPUT drop invalid"] \
    log=yes log-prefix="IN-INVALID"


# ---------------------------------------------------------------------------
# 3. Ajustement du MSS sur le tunnel WireGuard
# ---------------------------------------------------------------------------

/ip firewall mangle add chain=forward action=change-mss \
    new-mss=clamp-to-pmtu passthrough=yes protocol=tcp tcp-flags=syn \
    out-interface-list=VPN \
    comment="Ajuste le MSS sur le tunnel WireGuard (PMTU)"


# ---------------------------------------------------------------------------
# 4. Correction de l'asymetrie entre R1 et R2
# ---------------------------------------------------------------------------
# Cote R1, la regle "INPUT allow Branch via site-to-site" accepte tout ce
# qui arrive par wg-s2s. Cote R2, la regle equivalente est restreinte a
# src-address=10.10.10.0/24.
#
# Consequence : R1, qui emet depuis son extremite de tunnel 10.255.255.1,
# ne peut pas joindre R2. Un simple "ping 10.255.255.2" depuis R1 echoue,
# alors que le tunnel fonctionne. Cela fausse le diagnostic quand on
# cherche a savoir si la liaison site-a-site est active.
#
# Regle additive, placee avant le rejet final.

/ip firewall filter add chain=input action=accept \
    in-interface=wg-s2s src-address=10.255.255.1/32 \
    comment="INPUT allow R1 tunnel endpoint (diagnostic S2S)" \
    place-before=[find comment="INPUT default deny"]


# ---------------------------------------------------------------------------
# 5. Synchronisation de l'horloge
# ---------------------------------------------------------------------------

/system ntp client set enabled=yes mode=unicast \
    servers=0.pool.ntp.org,1.pool.ntp.org


# ---------------------------------------------------------------------------
# 6. Algorithmes SSH
# ---------------------------------------------------------------------------

/ip ssh set strong-crypto=yes


# ===========================================================================
#  APRES APPLICATION -- rejouer les tests du chapitre 10 du dossier
# ===========================================================================
#
#  Necessite de demarrer HQ-Test-Client et, pour le test VPN employe,
#  Remote-Employee-Test.
#
#    R2-Branch  -> extremite VPN de R1     ping 10.255.255.1
#    Branch     -> Ubuntu HQ               ping 10.10.10.200
#    Ubuntu HQ  -> R2-Branch               ping 10.30.30.1
#    Ubuntu HQ  -> Internet                curl -I https://example.com
#    Employe externe sans VPN -> HQ        doit rester bloque
#    Employe externe avec VPN -> HQ        doit aboutir
#
#  Les quatre premiers doivent afficher 0 % de perte, comme au 26/07/2026.
#
# ===========================================================================
