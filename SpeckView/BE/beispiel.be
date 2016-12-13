[BE]
Version = 3
[Signal]
Rate = 2000000,000000
Sample = 20000,000000
[Signalgenerator]
VISA = USB0::0x0957::0x2C07::MY52801235::INSTR
AC = 1,000000
AC-Offset = 0,000000
f_start = 120000,000000
f_ende = 210000,000000
fenster = 0,200000
t-Faktor = 1,000000
Trigger = FALSE
[USB]
AusgangCP = Dev1/ao0:1
Relais = Dev1/port1/line0
Cantilever = 0,500000
Piezo = 2,000000
[Trigger]
Trigger = TRUE
SRanger = Dev1/port1/line1
GPIO = Dev1/port0/line0
[Manipulation]
Spektroskopie = FALSE
Hysterese = FALSE
auf = TRUE
dU = 0,100000
Umin = -2,000000
Umax = 1,000000
[Raster]
Raster = TRUE
Beginn = 5000,000000
Pixel = 100,000000
Dimension = 0,000002
[Mittelung]
Canti = 10,000000
Piezo = 10,000000
[Vorschau]
Vorschau = FALSE
AusgangCP = Dev0/Ao0:1
[PCI]
Eingang = Dev0/Ai0
Bereich = 1,000000
timeout = 30,000000