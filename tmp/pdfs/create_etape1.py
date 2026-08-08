from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = "/Users/sofiane/Documents/mikrotik/output/pdf/etape1.pdf"

TEAL = colors.HexColor("#0F766E")
TEAL_DARK = colors.HexColor("#134E4A")
TEAL_LIGHT = colors.HexColor("#CCFBF1")
INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#52606D")
LIGHT = colors.HexColor("#F4F7F8")
LINE = colors.HexColor("#D8E1E5")
AMBER = colors.HexColor("#F59E0B")


def footer(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "Projet MikroTik - Firewall et VPN")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Etape 1  |  Page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=20 * mm,
    title="Etape 1 - Preparation et securisation de R1-HQ",
    author="Projet MikroTik",
)

frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates(PageTemplate(id="standard", frames=[frame], onPage=footer))

styles = getSampleStyleSheet()
title = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=25,
    leading=30,
    textColor=TEAL_DARK,
    alignment=TA_LEFT,
    spaceAfter=4 * mm,
)
subtitle = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=11,
    leading=16,
    textColor=MUTED,
    spaceAfter=7 * mm,
)
heading = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=19,
    textColor=TEAL_DARK,
    spaceBefore=5 * mm,
    spaceAfter=3 * mm,
)
body = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10.3,
    leading=15,
    textColor=INK,
    spaceAfter=2.5 * mm,
)
small = ParagraphStyle(
    "Small",
    parent=body,
    fontSize=9.2,
    leading=13,
    spaceAfter=0,
)
card_title = ParagraphStyle(
    "CardTitle",
    parent=body,
    fontName="Helvetica-Bold",
    textColor=TEAL_DARK,
    spaceAfter=1 * mm,
)
center = ParagraphStyle(
    "Center",
    parent=small,
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
)


def p(text, style=body):
    return Paragraph(text, style)


def bullet(text):
    return p(f"<font color='#0F766E'><b>•</b></font> &nbsp;{text}", body)


def info_card(title_text, content, color=TEAL_LIGHT):
    table = Table(
        [[p(title_text, card_title)], [p(content, small)]],
        colWidths=[doc.width],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


story = []
story.append(p("ETAPE 1", ParagraphStyle("Kicker", parent=small, fontName="Helvetica-Bold", textColor=TEAL, spaceAfter=2 * mm)))
story.append(p("Preparation et securisation de R1-HQ", title))
story.append(p("Premiere configuration du routeur MikroTik CHR dans UTM, avant la creation du LAN et des regles de firewall.", subtitle))

story.append(info_card(
    "Objectif de cette etape",
    "Preparer le routeur principal, reduire les services exposes et creer des points de restauration avant de construire le vrai reseau de l'entreprise.",
))

story.append(p("1. Connexion au routeur", heading))
story.append(p("Nous nous sommes connectes a l'interface WebFig du MikroTik avec l'adresse suivante : <b>http://192.168.64.2</b>.", body))
story.append(p("Cette adresse a ete donnee automatiquement a <b>ether1</b> par le reseau partage de UTM. Pour le moment, ether1 represente le cote WAN, c'est-a-dire la connexion vers l'exterieur.", body))

story.append(p("2. Identification du routeur", heading))
story.append(p("Le nom du routeur a ete change de <b>MikroTik</b> vers <b>R1-HQ</b>.", body))

name_table = Table(
    [
        [p("R1", center), p("Premier routeur, utilise comme routeur principal.", small)],
        [p("HQ", center), p("Headquarters : le reseau du siege principal de l'entreprise.", small)],
    ],
    colWidths=[28 * mm, doc.width - 28 * mm],
)
name_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), TEAL_LIGHT),
    ("GRID", (0, 0), (-1, -1), 0.6, LINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story.append(name_table)

story.append(p("3. Premier backup", heading))
story.append(p("Un backup a ete cree avant les changements importants :", body))
story.append(info_card("Fichier de restauration", "<b>R1-HQ-baseline.backup</b><br/>Il permet de revenir a l'etat de depart si une configuration suivante pose un probleme.", LIGHT))

services = [
    [p("Services desactives", card_title), p("Services conserves", card_title)],
    [p("Telnet<br/>FTP<br/>API<br/>API-SSL<br/>Reverse Proxy", small), p("WebFig - administration par navigateur<br/>SSH - administration securisee<br/>WinBox - outil d'administration MikroTik", small)],
]
service_table = Table(services, colWidths=[doc.width / 2, doc.width / 2])
service_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#FFF7ED")),
    ("BACKGROUND", (1, 0), (1, -1), TEAL_LIGHT),
    ("BOX", (0, 0), (-1, -1), 0.7, LINE),
    ("INNERGRID", (0, 0), (-1, -1), 0.7, LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story.append(p("4. Reduction des services exposes", heading))
story.append(p("Les services qui ne sont pas necessaires pour notre laboratoire ont ete desactives. Moins de services actifs signifie moins de portes possibles pour une attaque.", body))
story.append(KeepTogether([service_table]))

story.append(p("5. Deuxieme backup", heading))
story.append(p("Apres la securisation initiale, un deuxieme point de restauration a ete cree : <b>R1-HQ-step1-secured.backup</b>.", body))
story.append(p("Le premier backup garde l'etat initial. Le deuxieme garde l'etat securise de l'etape 1.", body))

story.append(Spacer(1, 2 * mm))
story.append(KeepTogether([
    p("Pourquoi le firewall n'est pas encore configure ?", heading),
    info_card(
        "Une separation WAN/LAN est obligatoire",
        "Le routeur possede actuellement une seule carte reseau, <b>ether1</b>. Pour creer un firewall correct, il faut d'abord ajouter <b>ether2</b> et definir clairement les deux cotes du routeur.",
        colors.HexColor("#FFF7ED"),
    ),
]))

story.append(Spacer(1, 4 * mm))
topology = Table(
    [[
        p("INTERNET / UTM<br/><font size='8'>Reseau externe</font>", center),
        p("ether1<br/><font size='8'>WAN</font>", center),
        p("R1-HQ<br/><font size='8'>MikroTik</font>", center),
        p("ether2<br/><font size='8'>LAN - a ajouter</font>", center),
        p("HQ-LAN<br/><font size='8'>10.10.10.0/24</font>", center),
    ]],
    colWidths=[39 * mm, 25 * mm, 35 * mm, 31 * mm, 44 * mm],
)
topology.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#E5E7EB")),
    ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FEE2E2")),
    ("BACKGROUND", (2, 0), (2, 0), TEAL),
    ("TEXTCOLOR", (2, 0), (2, 0), colors.white),
    ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#FEF3C7")),
    ("BACKGROUND", (4, 0), (4, 0), TEAL_LIGHT),
    ("BOX", (0, 0), (-1, -1), 0.7, LINE),
    ("INNERGRID", (0, 0), (-1, -1), 0.7, LINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 10),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
]))
story.append(topology)

story.append(p("<b>ether1 = WAN :</b> connexion vers UTM et l'exterieur. Cette zone n'est pas consideree comme fiable.", body))
story.append(p("<b>ether2 = LAN :</b> futur reseau interne de l'entreprise. Il recevra l'adresse <b>10.10.10.1/24</b>.", body))
story.append(p("Si nous ajoutons des regles avant cette separation, nous risquons de bloquer notre propre acces WebFig ou d'appliquer une regle au mauvais cote du routeur.", body))

story.append(p("Prochaine etape", heading))
next_steps = [
    "Arreter proprement la VM R1-HQ dans UTM.",
    "Creer un reseau interne isole nomme <b>HQ-LAN</b>.",
    "Ajouter une deuxieme carte reseau VirtIO au MikroTik.",
    "Redemarrer et verifier que l'interface <b>ether2</b> existe.",
    "Attribuer <b>10.10.10.1/24</b> a ether2.",
    "Configurer ensuite DHCP, NAT et les regles du firewall.",
]
for item in next_steps:
    story.append(bullet(item))

story.append(Spacer(1, 3 * mm))
story.append(info_card(
    "Resultat de l'etape 1",
    "R1-HQ est accessible, clairement identifie, sauvegarde et mieux securise. Il est maintenant pret a recevoir sa deuxieme interface reseau avant la construction du firewall.",
))

doc.build(story)
print(OUTPUT)
