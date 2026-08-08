from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
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


ROOT = Path("/Users/sofiane/Documents/mikrotik")
OUT = ROOT / "output/pdf/mikrotik_firewall_vpn_beginner_guide.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

PAGE_W, PAGE_H = A4
NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1677B8")
CYAN = colors.HexColor("#DFF4FF")
GREEN = colors.HexColor("#1F8A70")
GREEN_BG = colors.HexColor("#E7F7F1")
ORANGE = colors.HexColor("#D97706")
ORANGE_BG = colors.HexColor("#FFF4DE")
RED = colors.HexColor("#B42318")
RED_BG = colors.HexColor("#FDECEA")
LIGHT = colors.HexColor("#F4F7FA")
MID = colors.HexColor("#D5DEE8")
TEXT = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle", fontName="Helvetica-Bold", fontSize=30, leading=34,
    textColor=colors.white, alignment=TA_LEFT, spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="CoverSub", fontName="Helvetica", fontSize=14, leading=20,
    textColor=colors.HexColor("#D9EEFA"), alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    name="H1x", fontName="Helvetica-Bold", fontSize=21, leading=25,
    textColor=NAVY, spaceBefore=4, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="H2x", fontName="Helvetica-Bold", fontSize=14, leading=18,
    textColor=BLUE, spaceBefore=12, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="Bodyx", fontName="Helvetica", fontSize=10.2, leading=15,
    textColor=TEXT, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="Smallx", fontName="Helvetica", fontSize=8.6, leading=12,
    textColor=MUTED, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="Bulletx", fontName="Helvetica", fontSize=10, leading=14,
    textColor=TEXT, leftIndent=13, firstLineIndent=-7, bulletIndent=4,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="BoxTitle", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
    textColor=NAVY, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="TableHead", fontName="Helvetica-Bold", fontSize=10.2, leading=13,
    textColor=colors.white,
))
styles.add(ParagraphStyle(
    name="BoxBody", fontName="Helvetica", fontSize=9.3, leading=13,
    textColor=TEXT,
))
styles.add(ParagraphStyle(
    name="Diagram", fontName="Helvetica-Bold", fontSize=9.2, leading=12,
    textColor=NAVY, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="Contents", fontName="Helvetica", fontSize=11, leading=17,
    textColor=TEXT,
))


def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(MID)
        canvas.line(18 * mm, PAGE_H - 14 * mm, PAGE_W - 18 * mm, PAGE_H - 14 * mm)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(18 * mm, PAGE_H - 10.5 * mm, "MIKROTIK FIREWALL + VPN BEGINNER GUIDE")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(
    str(OUT), pagesize=A4,
    leftMargin=18 * mm, rightMargin=18 * mm,
    topMargin=20 * mm, bottomMargin=17 * mm,
    title="MikroTik Firewall and VPN - A Beginner's Big-Picture Guide",
    author="OpenAI Codex",
    subject="Beginner guide to a virtual MikroTik firewall and VPN lab in UTM",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates([PageTemplate(id="normal", frames=[frame], onPage=header_footer)])


def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph("• " + text, styles["Bulletx"])


def title(text):
    return P(text, "H1x")


def subtitle(text):
    return P(text, "H2x")


def callout(title_text, body, kind="blue"):
    palettes = {
        "blue": (CYAN, BLUE),
        "green": (GREEN_BG, GREEN),
        "orange": (ORANGE_BG, ORANGE),
        "red": (RED_BG, RED),
    }
    bg, accent = palettes[kind]
    data = [[P(title_text, "BoxTitle")], [P(body, "BoxBody")]]
    t = Table(data, colWidths=[doc.width - 10 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.8, accent),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
    ]))
    return KeepTogether([t, Spacer(1, 7)])


def flow_boxes(labels, widths=None):
    if widths is None:
        widths = [36 * mm] * len(labels)
    cells = []
    for i, label in enumerate(labels):
        cells.append(P(label, "Diagram"))
        if i < len(labels) - 1:
            cells.append(P("->", "Diagram"))
    col_widths = []
    for i, w in enumerate(widths):
        col_widths.append(w)
        if i < len(widths) - 1:
            col_widths.append(8 * mm)
    t = Table([cells], colWidths=col_widths, hAlign="CENTER")
    style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]
    for i in range(0, len(cells), 2):
        style += [
            ("BACKGROUND", (i, 0), (i, 0), LIGHT),
            ("BOX", (i, 0), (i, 0), 1, BLUE),
        ]
    t.setStyle(TableStyle(style))
    return KeepTogether([Spacer(1, 4), t, Spacer(1, 10)])


story = []

# Cover
cover = Table([
    [P("MikroTik Firewall<br/>and VPN", "CoverTitle")],
    [P("A complete beginner's big-picture guide", "CoverSub")],
    [Spacer(1, 22 * mm)],
    [P("How a virtual router protects traffic, how VPN encryption fits in, what we have built in UTM, and what the finished security lab should become.", "CoverSub")],
], colWidths=[doc.width - 18 * mm])
cover.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), NAVY),
    ("LEFTPADDING", (0, 0), (-1, -1), 14 * mm),
    ("RIGHTPADDING", (0, 0), (-1, -1), 14 * mm),
    ("TOPPADDING", (0, 0), (0, 0), 24 * mm),
    ("BOTTOMPADDING", (0, -1), (0, -1), 25 * mm),
]))
story += [Spacer(1, 28 * mm), cover, Spacer(1, 14 * mm)]
story += [callout(
    "The central idea",
    "A firewall can only inspect and protect traffic that actually passes through it. Our VM is the security appliance; the next step is to make it the required path between a protected network and an untrusted network.",
    "green",
)]
story += [P("Prepared for the MikroTik CHR lab running in UTM on Apple Silicon.", "Smallx"), PageBreak()]

# Contents
story += [title("Contents")]
contents = [
    ("1", "The goal and the security-gateway idea"),
    ("2", "What we built: Mac, UTM, CHR, and virtual hardware"),
    ("3", "How network traffic and firewall decisions work"),
    ("4", "RouterOS firewall paths: input, forward, and output"),
    ("5", "NAT: address translation versus security"),
    ("6", "VPNs: encryption, authentication, and tunnel designs"),
    ("7", "How the firewall and VPN work together"),
    ("8", "What the current VM can and cannot protect"),
    ("9", "The finished two-interface security lab"),
    ("10", "A safe implementation and testing roadmap"),
    ("11", "Glossary and current lab details"),
]
ct = Table([[P(n, "H2x"), P(text, "Contents")] for n, text in contents], colWidths=[13 * mm, doc.width - 13 * mm])
ct.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LINEBELOW", (0, 0), (-1, -1), 0.3, MID),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [ct, Spacer(1, 12)]
story += [callout("How to read this guide", "Read sections 1-8 first for the concepts. Sections 9-10 describe the practical destination and the safest order of work.", "blue"), PageBreak()]

# 1
story += [title("1. The goal: a virtual security gateway")]
story += [P("The goal is not merely to run MikroTik software. The goal is to create a security checkpoint that controls traffic and provides encrypted VPN access.")]
story += [flow_boxes(["Protected device", "MikroTik security gateway", "Internet / untrusted network"], [43 * mm, 55 * mm, 48 * mm])]
story += [P("When MikroTik sits in the path, RouterOS can inspect each connection, allow legitimate activity, block unwanted traffic, translate addresses with NAT, log suspicious events, and send selected traffic through an encrypted VPN tunnel.")]
story += [subtitle("The non-negotiable principle")]
story += [callout("Traffic must pass through MikroTik", "Simply having RouterOS running does not protect your Mac or other devices. The protected device must use MikroTik as its gateway, or deliberately send traffic into MikroTik through a VPN.", "orange")]
story += [subtitle("What a finished system should do")]
for x in [
    "Protect RouterOS itself from unauthorized management access.",
    "Protect devices behind MikroTik from unsolicited inbound connections.",
    "Control which outbound connections protected devices may create.",
    "Authenticate VPN users and encrypt their traffic.",
    "Limit VPN users to only the internal resources they actually need.",
    "Record important allowed and blocked activity for troubleshooting.",
]: story.append(bullet(x))
story += [PageBreak()]

# 2
story += [title("2. What we built")]
story += [P("We created a virtual MikroTik router instead of buying physical router hardware. Each layer has a specific job.")]
layers = [
    [P("Layer", "TableHead"), P("Purpose", "TableHead")],
    [P("Apple Silicon Mac", "BoxBody"), P("The physical computer supplying real CPU, memory, storage, and networking.", "BoxBody")],
    [P("UTM", "BoxBody"), P("The virtual-machine application that creates and manages the virtual hardware.", "BoxBody")],
    [P("QEMU", "BoxBody"), P("The engine UTM uses to emulate the ARM64 computer seen by RouterOS.", "BoxBody")],
    [P("MikroTik CHR", "BoxBody"), P("Cloud Hosted Router: RouterOS packaged to run as a virtual router.", "BoxBody")],
    [P("CHR disk image", "BoxBody"), P("The virtual hard drive containing the RouterOS kernel, services, configuration, WebFig, SSH, and WinBox.", "BoxBody")],
]
lt = Table(layers, colWidths=[42 * mm, doc.width - 42 * mm])
lt.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.4, MID),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
]))
story += [lt, Spacer(1, 10)]
story += [subtitle("The virtual hardware")]
for x in [
    "ARM64 architecture, matching the Apple Silicon host and MikroTik ARM64 image.",
    "Two virtual CPU cores and 2 GiB of RAM.",
    "UEFI firmware to locate and start RouterOS from its system disk.",
    "One non-removable VirtIO system disk containing RouterOS.",
    "One virtio-net-pci Ethernet adapter connected to UTM shared/NAT networking.",
    "One PTTY serial console for boot diagnostics and emergency recovery.",
    "No graphical display and no sound, because a router is managed remotely.",
]: story.append(bullet(x))
story += [callout("Compatibility result", "Apple Hypervisor acceleration caused RouterOS 7.22.1 ARM64 to panic during boot. Software emulation was left enabled because it reaches the RouterOS login prompt and works reliably. VirtIO storage itself works.", "orange"), PageBreak()]

# 3
story += [title("3. How a firewall sees traffic")]
story += [P("Network information is broken into small units called packets. A packet carries facts the firewall can examine: source address, destination address, protocol, port, incoming interface, and connection state.")]
packet = [
    [P("Packet field", "TableHead"), P("Example", "TableHead"), P("Meaning", "TableHead")],
    [P("Source", "BoxBody"), P("192.168.10.20", "BoxBody"), P("The device that sent the packet.", "BoxBody")],
    [P("Destination", "BoxBody"), P("1.1.1.1", "BoxBody"), P("Where the packet is going.", "BoxBody")],
    [P("Protocol", "BoxBody"), P("TCP", "BoxBody"), P("The communication method.", "BoxBody")],
    [P("Destination port", "BoxBody"), P("443", "BoxBody"), P("Usually an HTTPS web connection.", "BoxBody")],
    [P("State", "BoxBody"), P("new", "BoxBody"), P("The connection is being started.", "BoxBody")],
]
pt = Table(packet, colWidths=[38 * mm, 40 * mm, doc.width - 78 * mm])
pt.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.4, MID),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story += [pt, Spacer(1, 10)]
story += [subtitle("Stateful firewalling")]
story += [P("RouterOS remembers active connections. This lets it distinguish a legitimate reply from an unexpected new connection.")]
states = [
    ("new", "A device is trying to begin a connection."),
    ("established", "The packet belongs to a connection already accepted."),
    ("related", "The packet is connected to another legitimate connection."),
    ("invalid", "RouterOS cannot correctly associate or validate the packet."),
]
for name, meaning in states:
    story.append(bullet(f"<b>{name}</b>: {meaning}"))
story += [callout("A common safe pattern", "Allow established and related traffic, drop invalid traffic, carefully allow necessary new connections, then block traffic that was not explicitly allowed.", "green")]
story += [subtitle("Rule order matters")]
story += [P("RouterOS normally checks firewall rules from top to bottom. A broad allow rule placed too early can bypass more specific block rules below it. Clear ordering is part of the security design."), PageBreak()]

# 4
story += [title("4. The three important firewall paths")]
chains = [
    [P("Path", "TableHead"), P("Traffic", "TableHead"), P("What it protects", "TableHead")],
    [P("INPUT", "BoxTitle"), P("Traffic addressed to MikroTik itself: WebFig, WinBox, SSH, VPN handshakes, and ping.", "BoxBody"), P("The router and its management services.", "BoxBody")],
    [P("FORWARD", "BoxTitle"), P("Traffic passing through MikroTik between networks or VPN users and internal systems.", "BoxBody"), P("Devices and networks behind the router.", "BoxBody")],
    [P("OUTPUT", "BoxTitle"), P("Traffic created by MikroTik: update checks, DNS, logging, or an outbound VPN connection.", "BoxBody"), P("What the router itself may contact.", "BoxBody")],
]
cht = Table(chains, colWidths=[27 * mm, 83 * mm, doc.width - 110 * mm])
cht.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.5, MID),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [cht, Spacer(1, 10)]
story += [subtitle("Example: opening a website")]
story += [flow_boxes(["LAN computer", "MikroTik FORWARD + NAT", "Website"], [43 * mm, 59 * mm, 43 * mm])]
story += [P("The computer starts an outbound connection. MikroTik records it, allows it according to the forward policy, and performs NAT. The website's reply is recognized as established traffic and is returned to the correct computer.")]
story += [subtitle("Example: an unexpected inbound attempt")]
story += [flow_boxes(["Unknown internet host", "MikroTik FORWARD", "Protected computer"], [46 * mm, 53 * mm, 46 * mm])]
story += [P("There is no existing approved connection. Unless a deliberate inbound service rule exists, the firewall should block the attempt before it reaches the protected computer.")]
story += [callout("Management protection", "The INPUT policy should allow WebFig, WinBox, and SSH only from trusted networks. A WAN interface should not expose administration services to everyone.", "red"), PageBreak()]

# 5
story += [title("5. NAT is not the firewall")]
story += [P("NAT means Network Address Translation. It changes addressing so private devices can share the router's outward-facing connection.")]
story += [flow_boxes(["192.168.10.20", "MikroTik NAT", "Router WAN address", "Internet"], [32 * mm, 38 * mm, 43 * mm, 28 * mm])]
story += [P("When a response returns, MikroTik uses connection tracking to send it back to the correct private device.")]
compare = [
    [P("NAT", "TableHead"), P("Firewall", "TableHead")],
    [P("Changes source or destination addresses and sometimes ports.", "BoxBody"), P("Allows, rejects, drops, logs, or limits traffic.", "BoxBody")],
    [P("Makes private addresses usable behind a shared outward address.", "BoxBody"), P("Enforces the security policy between networks.", "BoxBody")],
    [P("Does not replace deliberate access-control rules.", "BoxBody"), P("Should explicitly control new inbound and outbound connections.", "BoxBody")],
]
cmp = Table(compare, colWidths=[doc.width / 2, doc.width / 2])
cmp.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.5, MID),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [cmp, Spacer(1, 10)]
story += [callout("Remember", "NAT answers 'which address should appear on this packet?' The firewall answers 'should this packet be allowed at all?' A secure gateway normally uses both.", "blue")]
story += [subtitle("Default-deny philosophy")]
story += [P("A strong policy begins by allowing known legitimate needs, then denies traffic that has not been approved. This is safer than trying to predict and list every possible dangerous connection."), PageBreak()]

# 6
story += [title("6. What a VPN adds")]
story += [P("A Virtual Private Network creates an encrypted tunnel through an untrusted network. It protects the contents of traffic while it travels and authenticates the tunnel endpoints.")]
story += [flow_boxes(["Private traffic", "Encrypt + authenticate", "Untrusted internet", "Decrypt"], [34 * mm, 49 * mm, 42 * mm, 28 * mm])]
for name, text in [
    ("Encryption", "Outsiders should not be able to read the protected information inside the tunnel."),
    ("Authentication", "Each side proves its identity using keys, credentials, or certificates."),
    ("Integrity", "Unauthorized changes to tunneled traffic can be detected."),
]: story.append(bullet(f"<b>{name}</b>: {text}"))
story += [callout("A VPN does not replace a firewall", "The VPN decides whether a secure tunnel may be established. The firewall decides what the authenticated VPN user may access after connecting.", "orange")]
story += [subtitle("Three common VPN designs")]
designs = [
    [P("Remote access", "BoxTitle"), P("A laptop or phone connects securely back to MikroTik while the user is away.", "BoxBody")],
    [P("Site to site", "BoxTitle"), P("Two remote networks are joined through an encrypted tunnel between gateways.", "BoxBody")],
    [P("VPN client gateway", "BoxTitle"), P("MikroTik sends selected protected-device traffic through another VPN server or provider.", "BoxBody")],
]
dt = Table(designs, colWidths=[42 * mm, doc.width - 42 * mm])
dt.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, MID),
    ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [dt, PageBreak()]

# 7
story += [title("7. Firewall and VPN working together")]
story += [P("Imagine that you are away from home and need to reach a private server. The complete process is:")]
steps = [
    "Your laptop contacts the MikroTik VPN service.",
    "MikroTik verifies the laptop's VPN identity and keys.",
    "An encrypted tunnel is established.",
    "The laptop receives a private VPN address.",
    "Traffic enters RouterOS through the VPN interface.",
    "Firewall rules decide which internal systems and services are allowed.",
    "Allowed traffic is forwarded; unauthorized traffic is blocked and may be logged.",
    "Responses return through the encrypted tunnel.",
]
for i, s in enumerate(steps, 1): story.append(bullet(f"<b>{i}.</b> {s}"))
story += [Spacer(1, 6), flow_boxes(["Remote laptop", "Encrypted VPN", "MikroTik firewall", "Allowed server"], [34 * mm, 37 * mm, 43 * mm, 34 * mm])]
story += [subtitle("Least privilege")]
story += [P("A VPN user should not automatically receive unrestricted access to every internal system. The safer approach is to grant only the networks, servers, and ports required for that user's purpose.")]
story += [callout("Two separate questions", "VPN: 'Is this user or device authenticated, and is the path encrypted?' Firewall: 'Now that it is connected, exactly what may it reach?'", "green")]
story += [subtitle("WireGuard as a learning choice")]
story += [P("WireGuard is often a good modern starting point because its design is comparatively small: each peer has keys, tunnel addresses, and explicitly allowed IP ranges. Even with WireGuard, routing and firewall policy still need to be designed correctly."), PageBreak()]

# 8
story += [title("8. What the current VM can and cannot protect")]
story += [subtitle("What is already working")]
for x in [
    "RouterOS 7.22.1 boots and reaches its login prompt.",
    "The VM is reachable from the Mac at 192.168.64.2.",
    "WebFig on port 80, SSH on port 22, and WinBox on port 8291 are reachable.",
    "The serial console provides a recovery path if network access is broken.",
    "RouterOS is ready for firewall and VPN configuration.",
]: story.append(bullet(x))
story += [subtitle("The current limitation")]
story += [P("The VM currently has one virtual Ethernet adapter. It is connected to UTM's shared/NAT network. That is enough to manage RouterOS and learn its features, but it does not automatically place your Mac's normal internet traffic behind the MikroTik firewall.")]
story += [callout("Why one interface is limited", "A traditional gateway needs an untrusted side and a protected side. With only one interface, there is not yet a separate LAN behind MikroTik through which ordinary client traffic must pass.", "orange")]
story += [subtitle("Two ways to make protection real")]
ways = [
    [P("Gateway design", "BoxTitle"), P("Add a second MikroTik interface and place a test computer or VM behind it. That client uses MikroTik as its default gateway, so its traffic must pass through the firewall.", "BoxBody")],
    [P("VPN-path design", "BoxTitle"), P("Connect a device to MikroTik through a VPN and route selected traffic into the tunnel. MikroTik then filters that VPN traffic.", "BoxBody")],
]
wt = Table(ways, colWidths=[39 * mm, doc.width - 39 * mm])
wt.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, MID),
    ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [wt, PageBreak()]

# 9
story += [title("9. The finished two-interface lab")]
story += [P("The most educational next design is a small, isolated two-sided network.")]
story += [flow_boxes(["Internet / UTM NAT", "ether1: WAN", "MikroTik firewall + NAT + VPN", "ether2: LAN", "Test computer"], [27 * mm, 23 * mm, 40 * mm, 23 * mm, 26 * mm])]
story += [subtitle("Interface roles")]
for x in [
    "<b>ether1 - WAN:</b> connected to UTM's shared/NAT network; treated as untrusted.",
    "<b>ether2 - LAN:</b> connected to an isolated virtual network; treated as protected.",
    "<b>Test computer:</b> connected only to the protected LAN and configured to use MikroTik as its default gateway.",
]: story.append(bullet(x))
story += [subtitle("Example packet journey")]
journey = [
    "The test computer asks to open a website.",
    "The packet arrives on MikroTik's LAN interface.",
    "RouterOS checks connection tracking and forward firewall rules.",
    "If allowed, RouterOS performs NAT and sends the packet through the WAN interface.",
    "The reply returns to MikroTik.",
    "RouterOS recognizes it as established traffic and returns it to the test computer.",
]
for i, s in enumerate(journey, 1): story.append(bullet(f"<b>{i}.</b> {s}"))
story += [callout("Why this is a safe lab", "The protected LAN is virtual and isolated. You can learn routing, NAT, firewall rules, logging, and VPN access without immediately replacing your real home router.", "green")]
story += [subtitle("What the firewall would enforce")]
for x in [
    "Allow required LAN-to-internet connections.",
    "Block unsolicited WAN-to-LAN connections.",
    "Restrict management to trusted LAN or VPN addresses.",
    "Permit only approved VPN-to-LAN access.",
    "Log selected denied connections without flooding the logs.",
]: story.append(bullet(x))
story += [PageBreak()]

# 10
story += [title("10. Safe implementation roadmap")]
roadmap = [
    ("1. Secure management", "Set a strong password, create a separate administrator, restrict management services to trusted sources, and back up the configuration."),
    ("2. Add the protected LAN", "Add a second virtual adapter, define WAN and LAN roles, assign a LAN address, and provide DHCP to a test client."),
    ("3. Build the firewall", "Allow established/related traffic, drop invalid traffic, protect INPUT, control FORWARD, then add a final default deny."),
    ("4. Configure NAT", "Translate protected LAN addresses for internet access and verify replies return correctly."),
    ("5. Configure the VPN", "Create keys, tunnel addresses, peers, allowed IP ranges, routes, and tightly scoped firewall access."),
    ("6. Test from both sides", "Verify allowed traffic works, blocked traffic fails, management is restricted, VPN access is encrypted, and logs are useful."),
    ("7. Reboot and retest", "Confirm the VM starts cleanly and the complete policy survives a restart."),
]
rd = Table([[P(a, "BoxTitle"), P(b, "BoxBody")] for a, b in roadmap], colWidths=[46 * mm, doc.width - 46 * mm])
rd.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, MID),
    ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story += [rd, Spacer(1, 10)]
story += [callout("Why incremental changes matter", "A firewall mistake can lock you out, break DHCP or DNS, or expose a service. Add and test small groups of rules. Keep serial-console recovery available until the final policy is proven.", "red")]
story += [subtitle("A sensible first test")]
story += [P("Use a disposable test VM behind the MikroTik LAN. Confirm it can obtain an address, reach allowed destinations, cannot receive unexpected inbound connections, and can reach only the management or VPN resources you intentionally permit."), PageBreak()]

# 11
story += [title("11. Glossary and current lab details")]
glossary = [
    ("CHR", "Cloud Hosted Router; RouterOS packaged for virtual machines."),
    ("Firewall", "Rules that decide whether network traffic is allowed, blocked, rejected, limited, or logged."),
    ("Gateway", "The router a device sends traffic to when the destination is outside its local network."),
    ("WAN", "The untrusted or outward-facing network side."),
    ("LAN", "The trusted or protected local-network side."),
    ("NAT", "Address translation, commonly used to let private devices share an outward address."),
    ("VPN", "An authenticated and encrypted tunnel through an untrusted network."),
    ("Packet", "A small unit of network data carrying addresses, protocol, ports, and content."),
    ("Port", "A numbered endpoint associated with a network service, such as SSH port 22."),
    ("Connection tracking", "RouterOS memory of active connections and their states."),
    ("Default deny", "Block traffic unless a rule explicitly allows it."),
    ("Least privilege", "Grant only the access needed for a specific purpose."),
]
gt = Table([[P(k, "BoxTitle"), P(v, "BoxBody")] for k, v in glossary], colWidths=[36 * mm, doc.width - 36 * mm])
gt.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.35, MID),
    ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [gt, Spacer(1, 10)]
story += [subtitle("Current MikroTik lab")]
current = [
    [P("VM name", "BoxTitle"), P("MikroTik CHR Automated", "BoxBody")],
    [P("RouterOS", "BoxTitle"), P("7.22.1 stable, ARM64", "BoxBody")],
    [P("Management IP", "BoxTitle"), P("192.168.64.2 on UTM's private shared/NAT network", "BoxBody")],
    [P("WebFig", "BoxTitle"), P("http://192.168.64.2", "BoxBody")],
    [P("Other access", "BoxTitle"), P("SSH port 22, WinBox port 8291, serial /dev/ttys000 while running", "BoxBody")],
    [P("Current topology", "BoxTitle"), P("One Ethernet adapter; ready for management and learning, not yet a two-sided gateway", "BoxBody")],
]
cur = Table(current, colWidths=[42 * mm, doc.width - 42 * mm])
cur.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, MID),
    ("BACKGROUND", (0, 0), (0, -1), CYAN),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story += [cur, Spacer(1, 12)]
story += [callout("Final takeaway", "We have built and verified the security appliance. The next major step is to build the traffic path around it: WAN -> MikroTik firewall/VPN -> protected LAN. Only then does MikroTik become the required checkpoint for client traffic.", "green")]

doc.build(story)
print(OUT)
