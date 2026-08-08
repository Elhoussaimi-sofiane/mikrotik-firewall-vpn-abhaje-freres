from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon


# Chemin calcule depuis l'emplacement du script (tmp/pdfs/), afin que le
# dossier du projet puisse etre deplace sans casser la generation.
_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = str(_ROOT / "output" / "pdf" / "Dossier-livraison-Firewall-MikroTik.pdf")

pdfmetrics.registerFont(
    TTFont("Arial", "/System/Library/Fonts/Supplemental/Arial.ttf")
)
pdfmetrics.registerFont(
    TTFont("Arial-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
)

PAGE_W, PAGE_H = A4
NAVY = colors.HexColor("#12304A")
BLUE = colors.HexColor("#176B87")
TEAL = colors.HexColor("#2A9D8F")
LIGHT = colors.HexColor("#EEF5F7")
PALE = colors.HexColor("#F7FAFB")
GREEN = colors.HexColor("#2E7D32")
AMBER = colors.HexColor("#F4A261")
RED = colors.HexColor("#B3261E")
TEXT = colors.HexColor("#25313A")
MUTED = colors.HexColor("#5E6C76")
GRID = colors.HexColor("#CAD7DD")

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="TitleCustom",
        fontName="Arial-Bold",
        fontSize=25,
        leading=30,
        textColor=colors.white,
        alignment=TA_LEFT,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="SubtitleCustom",
        fontName="Arial",
        fontSize=11.5,
        leading=16,
        textColor=colors.HexColor("#D9EBF2"),
    )
)
styles.add(
    ParagraphStyle(
        name="H1Custom",
        fontName="Arial-Bold",
        fontSize=17,
        leading=21,
        textColor=NAVY,
        spaceBefore=5,
        spaceAfter=9,
    )
)
styles.add(
    ParagraphStyle(
        name="H2Custom",
        fontName="Arial-Bold",
        fontSize=12.5,
        leading=16,
        textColor=BLUE,
        spaceBefore=8,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyCustom",
        fontName="Arial",
        fontSize=9.5,
        leading=13.2,
        textColor=TEXT,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="SmallCustom",
        fontName="Arial",
        fontSize=8.2,
        leading=11,
        textColor=MUTED,
    )
)
styles.add(
    ParagraphStyle(
        name="BulletCustom",
        fontName="Arial",
        fontSize=9.3,
        leading=13,
        textColor=TEXT,
        leftIndent=13,
        firstLineIndent=-8,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="CalloutCustom",
        fontName="Arial",
        fontSize=9.2,
        leading=13,
        textColor=NAVY,
        leftIndent=8,
        rightIndent=8,
        spaceBefore=5,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHead",
        fontName="Arial-Bold",
        fontSize=8.5,
        leading=10,
        textColor=colors.white,
        alignment=TA_LEFT,
    )
)
styles.add(
    ParagraphStyle(
        name="TableCell",
        fontName="Arial",
        fontSize=8.2,
        leading=10.5,
        textColor=TEXT,
    )
)


def p(text, style="BodyCustom"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph("• " + text, styles["BulletCustom"])


def table(rows, widths, header=True):
    converted = []
    for row_i, row in enumerate(rows):
        style = "TableHead" if header and row_i == 0 else "TableCell"
        converted.append([p(str(cell), style) for cell in row])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    ts = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
    ]
    if header:
        ts.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    t.setStyle(TableStyle(ts))
    return t


def callout(text, color=LIGHT):
    t = Table([[p(text, "CalloutCustom")]], colWidths=[16.8 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def architecture_diagram():
    d = Drawing(500, 235)
    d.add(Rect(6, 158, 125, 43, 8, 8, fillColor=colors.HexColor("#E8F3F7"), strokeColor=BLUE))
    d.add(String(68, 184, "EMPLOYE DISTANT", textAnchor="middle", fontName="Arial-Bold", fontSize=9, fillColor=NAVY))
    d.add(String(68, 168, "VPN 10.20.20.0/24", textAnchor="middle", fontName="Arial", fontSize=8, fillColor=TEXT))

    d.add(Rect(184, 151, 132, 57, 8, 8, fillColor=NAVY, strokeColor=NAVY))
    d.add(String(250, 186, "R1-HQ", textAnchor="middle", fontName="Arial-Bold", fontSize=12, fillColor=colors.white))
    d.add(String(250, 170, "WAN 192.168.64.2", textAnchor="middle", fontName="Arial", fontSize=8, fillColor=colors.white))
    d.add(String(250, 158, "LAN 10.10.10.1", textAnchor="middle", fontName="Arial", fontSize=8, fillColor=colors.white))

    d.add(Rect(365, 151, 129, 57, 8, 8, fillColor=TEAL, strokeColor=TEAL))
    d.add(String(429, 186, "R2-BRANCH", textAnchor="middle", fontName="Arial-Bold", fontSize=12, fillColor=colors.white))
    d.add(String(429, 170, "WAN 192.168.64.4", textAnchor="middle", fontName="Arial", fontSize=8, fillColor=colors.white))
    d.add(String(429, 158, "LAN 10.30.30.1", textAnchor="middle", fontName="Arial", fontSize=8, fillColor=colors.white))

    d.add(Rect(178, 35, 144, 47, 8, 8, fillColor=colors.HexColor("#EAF5ED"), strokeColor=GREEN))
    d.add(String(250, 62, "RESEAU HQ", textAnchor="middle", fontName="Arial-Bold", fontSize=10, fillColor=GREEN))
    d.add(String(250, 48, "Ubuntu 10.10.10.200", textAnchor="middle", fontName="Arial", fontSize=8, fillColor=TEXT))

    d.add(Rect(359, 35, 141, 47, 8, 8, fillColor=colors.HexColor("#EAF5ED"), strokeColor=GREEN))
    d.add(String(429, 62, "RESEAU BRANCH", textAnchor="middle", fontName="Arial-Bold", fontSize=10, fillColor=GREEN))
    d.add(String(429, 48, "10.30.30.0/24", textAnchor="middle", fontName="Arial", fontSize=8, fillColor=TEXT))

    d.add(Line(131, 180, 184, 180, strokeColor=BLUE, strokeWidth=2))
    d.add(Polygon([179, 184, 184, 180, 179, 176], fillColor=BLUE, strokeColor=BLUE))
    d.add(String(157, 189, "WireGuard", textAnchor="middle", fontName="Arial-Bold", fontSize=7.5, fillColor=BLUE))
    d.add(String(157, 165, "UDP 13231", textAnchor="middle", fontName="Arial", fontSize=7.5, fillColor=MUTED))

    d.add(Line(316, 180, 365, 180, strokeColor=AMBER, strokeWidth=3))
    d.add(Polygon([360, 184, 365, 180, 360, 176], fillColor=AMBER, strokeColor=AMBER))
    d.add(Polygon([321, 184, 316, 180, 321, 176], fillColor=AMBER, strokeColor=AMBER))
    d.add(String(340, 224, "VPN SITE-TO-SITE", textAnchor="middle", fontName="Arial-Bold", fontSize=8, fillColor=NAVY))
    d.add(String(340, 212, "10.255.255.0/30 - UDP 13232", textAnchor="middle", fontName="Arial", fontSize=7.2, fillColor=MUTED))

    d.add(Line(250, 151, 250, 82, strokeColor=GREEN, strokeWidth=2))
    d.add(Polygon([246, 87, 250, 82, 254, 87], fillColor=GREEN, strokeColor=GREEN))
    d.add(Line(429, 151, 429, 82, strokeColor=GREEN, strokeWidth=2))
    d.add(Polygon([425, 87, 429, 82, 433, 87], fillColor=GREEN, strokeColor=GREEN))
    return d


def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(GRID)
        canvas.line(2 * cm, PAGE_H - 1.45 * cm, PAGE_W - 2 * cm, PAGE_H - 1.45 * cm)
        canvas.setFont("Arial-Bold", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(2 * cm, PAGE_H - 1.1 * cm, "Projet Firewall MikroTik - Dossier de livraison")
    canvas.setStrokeColor(GRID)
    canvas.line(2 * cm, 1.45 * cm, PAGE_W - 2 * cm, 1.45 * cm)
    canvas.setFont("Arial", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.05 * cm, "Validation du lab UTM - 26/07/2026")
    canvas.drawRightString(PAGE_W - 2 * cm, 1.05 * cm, f"Page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2 * cm,
    rightMargin=2 * cm,
    topMargin=1.8 * cm,
    bottomMargin=1.8 * cm,
    title="Dossier de livraison Firewall MikroTik",
    author="Projet de stage",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
doc.addPageTemplates([PageTemplate(id="all", frames=frame, onPage=header_footer)])

story = []

# Cover
cover = Table(
    [[
        p("FIREWALL MIKROTIK<br/>ET VPN SECURISES", "TitleCustom"),
        p("<b>Dossier de livraison technique</b><br/><br/>Lab valide sous UTM sur Apple Silicon<br/>RouterOS CHR 7.22.1", "SubtitleCustom"),
    ]],
    colWidths=[10.7 * cm, 6.1 * cm],
    rowHeights=[7.2 * cm],
)
cover.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ("RIGHTPADDING", (0, 0), (-1, -1), 18),
            ("BOX", (0, 0), (-1, -1), 1, NAVY),
        ]
    )
)
story += [Spacer(1, 3.0 * cm), cover, Spacer(1, 1.1 * cm)]
story.append(p("<b>Objectif</b>", "H2Custom"))
story.append(p("Construire et valider un pare-feu central pour le siege, un routeur de succursale et deux usages VPN: acces distant securise des employes et liaison securisee entre les deux sites."))
story.append(Spacer(1, 0.3 * cm))
story.append(
    table(
        [
            ["Etat", "Perimetre", "Date de validation"],
            ["VALIDE", "Lab UTM complet et teste", "26 juillet 2026"],
        ],
        [3.5 * cm, 8.2 * cm, 5.1 * cm],
    )
)
story.append(Spacer(1, 1.4 * cm))
story.append(callout("<b>Important:</b> ce document ne contient aucun mot de passe ni aucune cle privee VPN. Les secrets doivent etre remis separement et stockes dans un gestionnaire de mots de passe.", colors.HexColor("#FFF6E8")))
story.append(PageBreak())

# Executive summary and architecture
story.append(p("1. Resume du resultat", "H1Custom"))
story.append(p("Le lab simule une entreprise avec un siege (HQ), une succursale (Branch) et un employe externe. Les routeurs filtrent le trafic, donnent l'acces Internet aux reseaux internes et chiffrent les communications VPN."))
for item in [
    "<b>R1-HQ</b> protege le reseau principal 10.10.10.0/24.",
    "<b>R2-Branch</b> protege le reseau de la succursale 10.30.30.0/24.",
    "<b>VPN employes</b> permet a un poste externe autorise d'entrer dans le reseau via WireGuard.",
    "<b>VPN site-to-site</b> relie HQ et Branch par un tunnel chiffre permanent.",
    "<b>Politique firewall</b>: ce qui est explicitement autorise passe; le reste est bloque par defaut.",
]:
    story.append(bullet(item))
story.append(Spacer(1, 0.2 * cm))
story.append(p("2. Architecture validee", "H1Custom"))
story.append(architecture_diagram())
story.append(callout("<b>Lecture simple:</b> R1-HQ est la porte principale du siege. R2-Branch est la porte de la succursale. WireGuard cree des tunnels chiffres entre les personnes/sites autorises."))
story.append(PageBreak())

# Address plan
story.append(p("3. Plan d'adressage", "H1Custom"))
story.append(
    table(
        [
            ["Element", "Interface / role", "Adresse ou reseau"],
            ["R1-HQ", "WAN UTM Shared", "192.168.64.2/24"],
            ["R1-HQ", "Passerelle LAN HQ", "10.10.10.1/24"],
            ["Ubuntu HQ", "Client / serveur de test", "10.10.10.200/24"],
            ["R2-Branch", "WAN UTM Shared", "192.168.64.4/24"],
            ["R2-Branch", "Passerelle LAN Branch", "10.30.30.1/24"],
            ["DHCP Branch", "Plage clients", "10.30.30.100 - 10.30.30.200"],
            ["VPN employes", "Reseau WireGuard", "10.20.20.0/24"],
            ["R1 VPN employes", "Passerelle VPN", "10.20.20.1"],
            ["Employe test", "Client VPN", "10.20.20.2"],
            ["VPN site-to-site", "Transit WireGuard", "10.255.255.0/30"],
            ["R1 / R2 site-to-site", "Extremites du tunnel", "10.255.255.1 / 10.255.255.2"],
        ],
        [4.2 * cm, 6.0 * cm, 6.6 * cm],
    )
)
story.append(p("4. Machines virtuelles utiles", "H1Custom"))
story.append(
    table(
        [
            ["VM", "Role", "Etat recommande"],
            ["MikroTik CHR Automated", "R1-HQ - pare-feu principal", "Demarrer"],
            ["R2-Branch", "Pare-feu de la succursale", "Demarrer"],
            ["HQ-Test-Client", "Ubuntu du reseau HQ pour les tests", "Demarrer pour les tests"],
            ["Remote-Employee-Test", "Simulation d'un employe externe", "Arrete hors test VPN"],
        ],
        [5.0 * cm, 7.4 * cm, 4.4 * cm],
    )
)
story.append(callout("<b>Ne pas supprimer les anciennes VM existantes.</b> Elles ne font pas partie du lab final, mais elles ont ete conservees conformement a la consigne.", colors.HexColor("#FFF6E8")))
story.append(PageBreak())

# Firewall details
story.append(p("5. Fonctionnement du firewall", "H1Custom"))
story.append(p("Le firewall traite deux familles principales de trafic:"))
story.append(p("<b>INPUT</b>", "H2Custom"))
story.append(p("Trafic qui vise le routeur lui-meme: WebFig, SSH, WinBox, ping vers la passerelle et ports WireGuard. Il protege l'administration et les services du routeur."))
story.append(p("<b>FORWARD</b>", "H2Custom"))
story.append(p("Trafic qui traverse le routeur: LAN vers Internet, VPN vers LAN, HQ vers Branch et Branch vers HQ. Il protege les machines placees derriere le routeur."))
story.append(
    table(
        [
            ["Ordre logique", "Decision", "Pourquoi"],
            ["1", "Accepter established / related", "Laisser continuer les connexions deja autorisees et leurs flux associes."],
            ["2", "Bloquer invalid", "Rejeter les paquets incoherents ou impossibles a rattacher a une connexion valide."],
            ["3", "Autoriser les besoins connus", "LAN, administration controlee, WireGuard, HQ vers Branch et retour."],
            ["4", "Drop final", "Tout ce qui n'a pas ete explicitement autorise est refuse."],
        ],
        [2.2 * cm, 5.3 * cm, 9.3 * cm],
    )
)
story.append(p("6. NAT masquerade", "H1Custom"))
story.append(p("Les adresses 10.x.x.x sont privees et ne circulent pas directement sur Internet. La regle masquerade remplace temporairement l'adresse source privee par l'adresse WAN du MikroTik. Quand la reponse revient, le routeur sait a quel client interne la remettre."))
story.append(callout("<b>Important:</b> le trafic HQ - Branch ne doit pas etre masque. Les deux routeurs connaissent leurs reseaux par des routes WireGuard; ils conservent donc les vraies adresses internes pour faciliter le controle et les journaux."))
story.append(p("7. Services d'administration", "H1Custom"))
story.append(
    table(
        [
            ["Service", "Etat", "Justification"],
            ["SSH", "Actif", "Administration securisee en ligne de commande."],
            ["WebFig", "Actif", "Administration depuis le navigateur dans le lab."],
            ["WinBox", "Actif", "Administration MikroTik si necessaire."],
            ["Telnet, FTP, API, API-SSL, reverse proxy", "Desactives", "Reduction de la surface d'attaque."],
        ],
        [5.0 * cm, 2.7 * cm, 9.1 * cm],
    )
)
story.append(PageBreak())

# VPN and tests
story.append(p("8. VPN WireGuard", "H1Custom"))
story.append(p("<b>VPN employes - UDP 13231</b>", "H2Custom"))
story.append(p("Un employe externe possedant sa cle WireGuard peut obtenir l'adresse 10.20.20.2 et acceder uniquement aux ressources autorisees. Le test a ete effectue depuis une VM placee sur le reseau externe UTM, pas depuis le LAN HQ."))
story.append(p("<b>VPN site-to-site - UDP 13232</b>", "H2Custom"))
story.append(p("R1-HQ et R2-Branch possedent chacun une paire de cles independante. Le tunnel transporte 10.10.10.0/24 vers 10.30.30.0/24 sans NAT. Les routes et les regles firewall sont chargees automatiquement au demarrage."))
story.append(p("9. Matrice de tests", "H1Custom"))
story.append(
    table(
        [
            ["Test", "Resultat", "Preuve observee"],
            ["Employe externe sans VPN vers HQ", "BLOQUE", "Ping et SSH HQ inaccessibles."],
            ["Employe externe avec VPN vers HQ", "OK", "Handshake, ping et SSH reussis."],
            ["Employe VPN vers Internet", "OK", "Connectivite conservee pendant le test."],
            ["R2 transit vers R1", "OK", "10.255.255.2 vers 10.255.255.1: 0% perte."],
            ["Branch vers HQ Ubuntu", "OK", "10.30.30.1 vers 10.10.10.200: 0% perte."],
            ["HQ Ubuntu vers Branch", "OK", "10.10.10.200 vers 10.30.30.1: 0% perte."],
            ["Ubuntu HQ vers Internet", "OK", "Reponse HTTPS HTTP/2 200."],
            ["Redemarrage R2 puis R1", "OK", "Adresses, routes, firewall et tunnels revenus automatiquement."],
        ],
        [7.1 * cm, 2.1 * cm, 7.6 * cm],
    )
)
story.append(callout("<b>Conclusion des tests:</b> le comportement attendu est valide dans le lab: le trafic non autorise est bloque, les flux necessaires sont autorises et les VPN reviennent apres redemarrage.", colors.HexColor("#EAF5ED")))
story.append(PageBreak())

# Backup / operations
story.append(p("10. Sauvegarde et restauration", "H1Custom"))
story.append(p("Deux formats sont fournis pour chaque routeur:"))
story.append(bullet("<b>.backup</b>: image binaire complete pour restaurer rapidement le meme routeur / la meme VM."))
story.append(bullet("<b>.rsc</b>: export texte lisible, utile pour l'audit, la documentation ou une reconstruction manuelle. Les informations sensibles ont ete masquees dans l'export final."))
story.append(
    table(
        [
            ["Routeur", "Sauvegarde binaire", "Export texte"],
            ["R1-HQ", "R1-HQ-final-validated.backup", "R1-HQ-final-validated.rsc"],
            ["R2-Branch", "R2-Branch-final-validated.backup", "R2-Branch-final-validated.rsc"],
        ],
        [3.0 * cm, 7.0 * cm, 6.8 * cm],
    )
)
story.append(p("Procedure de restauration", "H2Custom"))
for item in [
    "Arreter les changements et identifier le bon routeur.",
    "Importer le fichier .backup dans Files sur le routeur concerne.",
    "Lancer la restauration depuis System > Backup, puis laisser le routeur redemarrer.",
    "Verifier ensuite l'identite, les adresses IP, les interfaces, les routes, le firewall et les handshakes VPN.",
    "Ne jamais restaurer le backup R1 sur R2 ou inversement.",
]:
    story.append(bullet(item))
story.append(p("11. Exploitation quotidienne", "H1Custom"))
story.append(
    table(
        [
            ["Controle", "Action attendue"],
            ["Etat des VPN", "Verifier le dernier handshake et les compteurs RX/TX WireGuard."],
            ["Alertes firewall", "Verifier les compteurs des regles drop et les logs utiles."],
            ["Sauvegardes", "Creer un backup avant chaque changement important et conserver une copie hors du routeur."],
            ["Mises a jour", "Tester d'abord dans une copie du lab, sauvegarder, puis planifier la maintenance."],
            ["Comptes", "Utiliser des comptes nominatifs et des mots de passe uniques; supprimer les acces des employes sortants."],
        ],
        [5.0 * cm, 11.8 * cm],
    )
)
story.append(PageBreak())

# Production readiness
story.append(p("12. Passage du lab a la production", "H1Custom"))
story.append(p("Le lab prouve le fonctionnement technique, mais il ne faut pas copier aveuglement les adresses UTM en entreprise. La production doit etre adaptee au vrai plan reseau, aux fournisseurs Internet et aux exigences de securite de l'entreprise."))
story.append(
    table(
        [
            ["A valider avant production", "Pourquoi"],
            ["Materiel / hyperviseur supporte et redondance", "Eviter qu'une seule panne coupe toute l'entreprise."],
            ["Vraies interfaces WAN et LAN", "Remplacer le reseau Shared UTM par le cablage et les VLAN reels."],
            ["IP publique ou redirection UDP 13231/13232", "Rendre les serveurs WireGuard joignables depuis l'exterieur."],
            ["DNS dynamique si IP WAN variable", "Permettre aux clients VPN de retrouver le site apres un changement d'IP."],
            ["Restriction de WebFig / SSH / WinBox", "Autoriser l'administration seulement depuis un VLAN ou des IP de gestion."],
            ["Certificat HTTPS valide", "Proteger WebFig si son usage est maintenu."],
            ["MFA et gestion des identites", "Renforcer l'acces des administrateurs et le cycle de vie des employes."],
            ["Journalisation et supervision", "Detecter les pannes, tentatives d'intrusion et anomalies."],
            ["Test externe reel", "Valider depuis une vraie connexion 4G/5G ou un autre FAI."],
            ["Plan de retour arriere", "Pouvoir restaurer rapidement le service en cas d'echec."],
        ],
        [7.1 * cm, 9.7 * cm],
    )
)
story.append(Spacer(1, 0.3 * cm))
story.append(callout("<b>Statut final:</b> LAB FONCTIONNEL ET VALIDE. Le passage en production reste une operation separee qui doit etre planifiee avec l'entreprise et adaptee a son infrastructure reelle.", colors.HexColor("#EAF5ED")))
story.append(PageBreak())

# Hardening review (correspond au chapitre 14 du resume du projet)
story.append(p("13. Durcissement complementaire", "H1Custom"))
story.append(p("Une relecture complete des deux configurations exportees a ete menee apres la validation. Elle ne remet pas en cause la matrice de tests de la section 9: les flux autorises passent, les flux non autorises sont bloques. Elle identifie en revanche des points qui echappent a la politique default deny, ou qui restent invisibles dans un test de connectivite."))
story.append(
    callout(
        "<b>Les corrections ne sont pas appliquees.</b> Elles sont livrees sous forme de deux scripts distincts, R1-HQ-hardening.rsc et R2-Branch-hardening.rsc. La configuration validee du 26 juillet 2026 reste intacte et demeure la reference."
    )
)
story.append(p("Point principal: le plan de management de niveau 2", "H2Custom"))
story.append(p("Le firewall decrit en section 5 filtre le trafic IP, c'est-a-dire la couche 3. Or RouterOS expose aussi deux services d'administration qui fonctionnent en couche 2, directement sur les adresses MAC: <b>MAC-WinBox</b> et <b>MAC-Telnet</b>. Ils permettent d'administrer un routeur qui n'a meme pas d'adresse IP."))
story.append(p("Ces services ne traversent pas /ip firewall filter. La regle INPUT default deny ne les voit jamais, et ils sont actifs par defaut sur <b>toutes</b> les interfaces. Un poste situe sur le meme domaine de diffusion qu'une interface du routeur peut donc ouvrir une session d'administration sans qu'aucune regle de firewall n'intervienne."))
story.append(p("La correction restreint ces services, ainsi que le protocole de decouverte de voisinage, a la seule liste d'interfaces LAN. L'acces WinBox par adresse IP n'est pas affecte: il releve de la couche 3 et reste soumis aux regles de la chaine input."))
story.append(p("Points releves", "H2Custom"))
story.append(
    table(
        [
            ["Point", "Nature", "Effet sur le service"],
            [
                "Management de niveau 2 (MAC-WinBox / MAC-Telnet) actif sur toutes les interfaces",
                "Ajout",
                "Aucune interruption.",
            ],
            [
                "Regles de rejet sans journalisation: aucune trace en cas d'incident",
                "Modification de regles existantes",
                "Aucune interruption.",
            ],
            [
                "MSS non ajuste sur les tunnels WireGuard (MTU 1420): risque de sessions TCP bloquees sans erreur lisible",
                "Ajout",
                "Aucune interruption.",
            ],
            [
                "Aucun client NTP: horodatage des journaux et validation TLS non fiables",
                "Ajout",
                "Aucune interruption.",
            ],
            [
                "Chaine input asymetrique entre R1 et R2 sur le tunnel site-a-site: fausse le diagnostic",
                "Ajout",
                "Aucune interruption.",
            ],
            [
                "Aucune regle dans /ipv6 firewall filter alors que le projet est entierement en IPv4",
                "Parametre systeme",
                "Redemarrage requis.",
            ],
            [
                "R1-HQ declare une troisieme carte reseau, pontee sur le reseau physique de l'hote, absente du plan d'adressage",
                "Parametre d'interface",
                "A verifier au prealable.",
            ],
        ],
        [8.0 * cm, 4.0 * cm, 4.8 * cm],
    )
)
story.append(p("Gestion des secrets", "H2Custom"))
story.append(p("La section 10 prevoit la remise des sauvegardes binaires. Contrairement aux exports texte .rsc, un fichier .backup contient l'integralite de la configuration, <b>y compris les cles privees WireGuard et les hachages des mots de passe administrateurs</b>. Il doit donc etre transmis par un canal separe et conserve dans un gestionnaire de mots de passe, au meme titre qu'un mot de passe."))
# Bloc garde d'un seul tenant: le titre ne doit pas se retrouver seul en
# bas de page, separe de ses puces.
_methode = [p("Methode d'application", "H2Custom")]
for item in [
    "Sauvegarder l'etat courant: /system backup save puis /export.",
    "Activer le Safe Mode du terminal RouterOS (Ctrl+X): si la session d'administration est interrompue, le routeur restaure automatiquement la configuration precedente.",
    "Appliquer les sections une par une, en verifiant apres chacune.",
    "Quitter le Safe Mode pour rendre les changements permanents.",
    "Rejouer la matrice de tests de la section 9 avant de considerer la nouvelle configuration comme validee.",
]:
    _methode.append(bullet(item))
_methode.append(
    callout(
        "Les points relevant du passage en production - restriction de WebFig, SSH et WinBox, comptes nominatifs, certificat HTTPS - restent traites en section 12 et ne sont pas repris ici. Le detail complet de cette relecture figure au chapitre 14 du resume du projet.",
        colors.HexColor("#EAF5ED"),
    )
)
story.append(KeepTogether(_methode))
story.append(Spacer(1, 0.4 * cm))

story.append(p("14. Contenu du dossier de livraison", "H1Custom"))
for item in [
    "Le present dossier PDF.",
    "Les backups binaires finals de R1-HQ et R2-Branch, a transmettre par un canal separe (voir section 13).",
    "Les exports texte finals de R1-HQ et R2-Branch.",
    "Les deux scripts de durcissement complementaire, non appliques (voir section 13).",
    "Les VM UTM conservees sur le Mac pour demonstration et tests.",
]:
    story.append(bullet(item))
story.append(Spacer(1, 0.5 * cm))
story.append(p("Fin du document", "SmallCustom"))

doc.build(story)
print(OUTPUT)
