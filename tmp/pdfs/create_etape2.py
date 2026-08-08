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


OUTPUT = "/Users/sofiane/Documents/mikrotik/output/pdf/etape2.pdf"

TEAL = colors.HexColor("#0F766E")
TEAL_DARK = colors.HexColor("#134E4A")
TEAL_LIGHT = colors.HexColor("#CCFBF1")
INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#52606D")
LIGHT = colors.HexColor("#F4F7F8")
LINE = colors.HexColor("#D8E1E5")
AMBER_LIGHT = colors.HexColor("#FFF7ED")
RED_LIGHT = colors.HexColor("#FEF2F2")


def footer(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "Projet MikroTik - Firewall et VPN")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Etape 2  |  Page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=20 * mm,
    title="Etape 2 - Creation du reseau LAN du siege",
    author="Projet MikroTik",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates(PageTemplate(id="standard", frames=[frame], onPage=footer))

styles = getSampleStyleSheet()
title = ParagraphStyle(
    "TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=24, leading=29, textColor=TEAL_DARK, alignment=TA_LEFT,
    spaceAfter=4 * mm,
)
subtitle = ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontName="Helvetica",
    fontSize=11, leading=16, textColor=MUTED, spaceAfter=7 * mm,
)
heading = ParagraphStyle(
    "Heading", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=15, leading=19, textColor=TEAL_DARK,
    spaceBefore=5 * mm, spaceAfter=3 * mm,
)
body = ParagraphStyle(
    "Body", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=10.2, leading=14.5, textColor=INK, spaceAfter=2.3 * mm,
)
small = ParagraphStyle(
    "Small", parent=body, fontSize=9.2, leading=13, spaceAfter=0,
)
card_title = ParagraphStyle(
    "CardTitle", parent=body, fontName="Helvetica-Bold",
    textColor=TEAL_DARK, spaceAfter=1 * mm,
)
table_header = ParagraphStyle(
    "TableHeader", parent=body, fontName="Helvetica-Bold",
    textColor=colors.white, spaceAfter=0,
)
center = ParagraphStyle(
    "Center", parent=small, alignment=TA_CENTER, fontName="Helvetica-Bold",
)


def p(text, style=body):
    return Paragraph(text, style)


def bullet(text):
    return p(f"<font color='#0F766E'><b>•</b></font> &nbsp;{text}", body)


def card(title_text, content, background=TEAL_LIGHT, border=TEAL):
    table = Table(
        [[p(title_text, card_title)], [p(content, small)]],
        colWidths=[doc.width], hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.8, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def two_col(rows, widths=(45 * mm, None)):
    second = doc.width - widths[0] if widths[1] is None else widths[1]
    table = Table(rows, colWidths=[widths[0], second], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), TEAL_LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


story = []
story.append(p("ETAPE 2", ParagraphStyle(
    "Kicker", parent=small, fontName="Helvetica-Bold",
    textColor=TEAL, spaceAfter=2 * mm,
)))
story.append(p("Creation du reseau LAN du siege", title))
story.append(p(
    "Ajout d'une deuxieme interface au routeur R1-HQ, creation du reseau interne HQ-LAN et mise en place du service DHCP.",
    subtitle,
))
story.append(card(
    "Objectif de cette etape",
    "Separer clairement le cote Internet du cote entreprise. Le routeur dispose maintenant d'une interface WAN et d'une interface LAN, ce qui prepare la future configuration du NAT et du firewall.",
))

story.append(p("1. Arret propre du routeur", heading))
story.append(p(
    "La machine virtuelle R1-HQ a ete arretee depuis <b>System &gt; Shutdown</b> dans RouterOS avant de modifier son materiel virtuel.",
    body,
))
story.append(p(
    "Un arret propre protege le disque et la configuration. Le bouton d'arret force de UTM doit etre evite, sauf si la machine ne repond plus.",
    body,
))

story.append(p("2. Creation du reseau HQ-LAN dans UTM", heading))
story.append(p(
    "Dans <b>UTM &gt; Settings &gt; Network &gt; Host Networks</b>, un nouveau reseau nomme <b>HQ-LAN</b> a ete ajoute. UTM enregistre automatiquement ce reseau et lui attribue un UUID.",
    body,
))
story.append(card(
    "Pourquoi utiliser un Host Network ?",
    "HQ-LAN doit etre un reseau interne isole. Les machines virtuelles attachees a ce meme Host Network pourront communiquer entre elles, mais UTM ne leur fournira pas directement une connexion Internet ni un serveur DHCP. Ces fonctions seront assurees par le MikroTik.",
    LIGHT,
))

story.append(p("3. Ajout de la deuxieme carte reseau", heading))
story.append(p(
    "Dans les parametres de la VM MikroTik CHR Automated, une nouvelle carte reseau a ete ajoutee sans modifier la carte WAN existante.",
    body,
))
network_rows = [
    [p("Parametre", table_header), p("Valeur", table_header)],
    [p("Network Mode", small), p("macOS Host Only", small)],
    [p("Host Network", small), p("HQ-LAN", small)],
    [p("Carte emulee", small), p("virtio-net-pci", small)],
    [p("Adresse MAC", small), p("Generee automatiquement par UTM", small)],
]
network_table = two_col(network_rows)
network_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), TEAL),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
]))
story.append(network_table)
story.append(Spacer(1, 2 * mm))
story.append(p(
    "La premiere carte reste en <b>Shared Network</b>. Elle correspond a ether1 et fournit l'acces WAN. La nouvelle carte correspond a ether2 et forme le LAN du siege.",
    body,
))

story.append(p("4. Nouvelle topologie du routeur", heading))
topology = Table([[
    p("INTERNET / UTM<br/><font size='8'>Reseau externe</font>", center),
    p("ether1<br/><font size='8'>WAN</font>", center),
    p("R1-HQ<br/><font size='8'>Firewall</font>", center),
    p("ether2<br/><font size='8'>LAN</font>", center),
    p("HQ-LAN<br/><font size='8'>10.10.10.0/24</font>", center),
]], colWidths=[39 * mm, 25 * mm, 35 * mm, 31 * mm, 44 * mm])
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
story.append(Spacer(1, 2 * mm))
story.append(bullet("<b>ether1 :</b> WAN vers le reseau partage de UTM et Internet."))
story.append(bullet("<b>ether2 :</b> LAN interne du siege, attache au reseau HQ-LAN."))

story.append(p("5. Configuration de l'adresse LAN", heading))
story.append(p(
    "Apres le redemarrage, la presence de ether2 a ete verifiee dans <b>Interfaces</b>. Une adresse IP a ensuite ete ajoutee dans <b>IP &gt; Addresses</b>.",
    body,
))
address_rows = [
    [p("Adresse", card_title), p("10.10.10.1/24", small)],
    [p("Interface", card_title), p("ether2", small)],
    [p("Reseau calcule", card_title), p("10.10.10.0", small)],
    [p("Commentaire", card_title), p("HQ LAN Gateway", small)],
]
story.append(two_col(address_rows))
story.append(Spacer(1, 2 * mm))
story.append(p(
    "L'adresse <b>10.10.10.1</b> devient la passerelle du reseau HQ. Toutes les machines du siege utiliseront cette adresse pour envoyer leur trafic vers les autres reseaux.",
    body,
))

story.append(p("6. Configuration du serveur DHCP", heading))
story.append(p(
    "Le service DHCP a ete prepare sur ether2 afin de distribuer automatiquement les parametres reseau aux futurs postes du siege.",
    body,
))
dhcp_rows = [
    [p("Parametre DHCP", table_header), p("Valeur configuree", table_header)],
    [p("Interface", small), p("ether2", small)],
    [p("Reseau", small), p("10.10.10.0/24", small)],
    [p("Passerelle", small), p("10.10.10.1", small)],
    [p("Plage dynamique", small), p("10.10.10.100 - 10.10.10.200", small)],
    [p("DNS temporaires", small), p("1.1.1.1 et 9.9.9.9", small)],
    [p("Bail", small), p("Valeur par defaut / laboratoire", small)],
]
dhcp_table = two_col(dhcp_rows, widths=(50 * mm, None))
dhcp_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), TEAL),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
]))
story.append(dhcp_table)
story.append(Spacer(1, 2 * mm))
story.append(p(
    "La plage commence a .100 pour reserver les adresses basses aux serveurs et aux equipements fixes. Par exemple, le futur Windows Server pourra utiliser 10.10.10.10.",
    body,
))

story.append(KeepTogether([
    p("7. Incident rencontre avec Safe Mode", heading),
    card(
        "Message affiche par WebFig",
        "DHCP Setup - setup failed to enter safe mode: safe mode already held by somebody (8)",
        RED_LIGHT,
        colors.HexColor("#DC2626"),
    ),
    Spacer(1, 2 * mm),
    p(
        "Ce message ne signalait pas une erreur d'adressage. Le Safe Mode etait deja actif dans la session WebFig, alors que l'assistant DHCP voulait l'activer lui-meme.",
        body,
    ),
    p(
        "La solution consistait a desactiver le Safe Mode manuel, puis a relancer <b>IP &gt; DHCP Server &gt; DHCP Setup</b>. L'assistant gere ensuite son propre mode de securite.",
        body,
    ),
]))

story.append(p("8. Pourquoi NAT et firewall sont reportes", heading))
story.append(p(
    "Aucune regle NAT ou firewall definitive n'est ajoutee pendant cette etape. Il faut d'abord connecter une machine de test a HQ-LAN et confirmer qu'elle recoit une adresse DHCP et qu'elle peut joindre 10.10.10.1.",
    body,
))
story.append(card(
    "Ordre de travail retenu",
    "1. Construire le LAN  -  2. Connecter un client  -  3. Tester DHCP et ping  -  4. Ajouter le NAT  -  5. Construire le firewall regle par regle.",
    AMBER_LIGHT,
    colors.HexColor("#F59E0B"),
))

story.append(p("9. Sauvegarde de fin d'etape", heading))
story.append(p(
    "Un nouveau point de restauration doit conserver l'etat fonctionnel du LAN avant les tests et le firewall :",
    body,
))
story.append(card(
    "Fichier de sauvegarde",
    "<b>R1-HQ-step2-LAN.backup</b>",
    LIGHT,
))

story.append(p("Resultat de l'etape 2", heading))
result_rows = [
    [p("Element", table_header), p("Etat final", table_header)],
    [p("WAN", small), p("ether1 - Shared Network UTM", small)],
    [p("LAN", small), p("ether2 - Host Network HQ-LAN", small)],
    [p("Passerelle LAN", small), p("10.10.10.1/24", small)],
    [p("DHCP", small), p("10.10.10.100 - 10.10.10.200", small)],
    [p("Etape suivante", small), p("Ajouter une machine cliente et tester le trafic", small)],
]
result_table = two_col(result_rows, widths=(48 * mm, None))
result_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), TEAL),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
]))
story.append(result_table)

doc.build(story)
print(OUTPUT)
