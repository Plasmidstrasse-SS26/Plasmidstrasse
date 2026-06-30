#Magician
import math
import time


# ==========================================
# 1. BEWEGUNGSPARAMETER EINSTELLEN
# ==========================================
dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, 0)
dType.SetPTPCoordinateParams(api, 200, 200, 200, 200, 0)
dType.SetPTPJumpParams(api, 10, 200, 0)
dType.SetPTPCommonParams(api, 30, 30, 0)

# Vorhandene Alarme löschen
dType.ClearAllAlarmsState(api)

# Roboter Homen
dType.SetHOMECmd(api, 0, 1)

# ==========================================
# 2. KONFIGURATION & KOORDINATEN
# ==========================================
# Anzahl der zu befüllenden Eppis (Ablaufplan spricht von 6 bis 8)
NUM_EPPIS = 6

# Globale Sicherheitshöhe für Z (erhöht für kollisionsfreie Fahrten)
SAFE_Z = 145.0

# Pipetten-Greifpositionen (Stationär)
PIPETTE_RUNTER = [179.4025, -90.1608, -10.9367, -22.2193, 1000.0]
PIPETTE_SICHERHEIT = [179.4025, -90.1608, SAFE_Z, -22.2193, 1000.0]

# Gitter-Parameter für 96er Pipettenbox (8 Reihen x 12 Spalten)
SPITZEN_RUNTER = [243.9577, -25.1092, -31.7995, -1.4134, 957.2]
SPITZEN_SICHERHEIT = [243.9577, -25.1092, SAFE_Z, -1.4134, 957.2]

SPITZEN_START_L = 957.2     # L-Koordinate der ersten Spalte (unten)
SPITZEN_OFFSET_L = -9.0     # Abstand der Spalten auf der Schiene
SPITZEN_OFFSET_Y = 9.0      # Reihenabstand quer zur Schiene (Y-Achse)

# Positionen der Flüssigkeitsquellen auf der Schiene
# Flüssigkeit 1 (entspricht der ursprünglichen PROBE-Position)
FLUID1_RUNTER = [204.9158, -26.1754, 45.9524, -2.8164, 783.4]
FLUID1_SICHERHEIT = [204.9158, -26.1754, SAFE_Z, -2.8164, 783.4]

# Abstellplatz grün (ehemals Flüssigkeit 2 & 3)
ABSTELLPLATZ_GRUEN_RUNTER = [204.9158, -26.1754, 45.9524, -2.8164, 402.0]
ABSTELLPLATZ_GRUEN_SICHERHEIT = [204.9158, -26.1754, SAFE_Z, -2.8164, 402.0]

# Ziel: Stationäre Stempelvorrichtung / Eppi-Abgabestelle
# Da Roboter 2 das Eppi hier einspannt, bleibt die L-Koordinate für uns konstant
EPPI_ABGABE_RUNTER = [204.9158, -26.1754, 45.9524, -2.8164, 565.0]
EPPI_ABGABE_SICHERHEIT = [204.9158, -26.1754, SAFE_Z, -2.8164, 565.0]

# Station zur Restentleerung (ehemals Abwurf)
RESTENTLEERUNG_RUNTER = [204.9158, -26.1754, 45.9524, -2.8164, 180.8]
RESTENTLEERUNG_SICHERHEIT = [204.9158, -26.1754, SAFE_Z, -2.8164, 180.8]

# Neue Abwurfstation für Pipettenspitzen
ABWURF_NEU_RUNTER = [-13.0341, -205.6555, 44.6869, -93.6265, 1000.0]
ABWURF_NEU_SICHERHEIT = [-13.0341, -205.6555, SAFE_Z, -93.6265, 1000.0]

# Globaler Zähler für verbrauchte Spitzen, um das 96er Raster fortlaufend abzuarbeiten
tip_index = 0

# ==========================================
# 3. HILFSFUNKTIONEN FÜR PIPETTE & HANDSHAKE
# ==========================================
def pipette_press_first_stop():
    """Drückt den Pipettenkolben bis zum ersten Druckpunkt herunter."""
    print("[Pipette] Kolben bis zum 1. Druckpunkt herunterdrücken...")
    # Stepper 2 (index 0), Geschwindigkeit 1100, Distanz 1300
    dType.SetEMotorS(api, index=0, isEnabled=1, speed=1100, distance=1300, isQueued=0)
    dType.SetWAITCmd(api, 1500, 1)

def pipette_release():
    """Gibt den Pipettenkolben langsam frei (Ansaugen der Flüssigkeit)."""
    print("[Pipette] Kolben langsam freigeben (Ansaugen)...")
    # Zurückdrehen zur Ausgangslage: Geschwindigkeit -1100, Distanz 1300
    dType.SetEMotorS(api, index=0, isEnabled=1, speed=-1100, distance=1300, isQueued=0)
    dType.SetWAITCmd(api, 1500, 1)

def pipette_press_second_stop():
    """Drückt den Pipettenkolben komplett durch (Spitzenabwurf)."""
    print("[Pipette] Kolben bis zum 2. Druckpunkt herunterdrücken (Abwurf)...")
    # Da der Kolben bei 0 steht, komplett um 1900 Schritte herunterfahren (Geschwindigkeit 1100, Distanz 1900)
    dType.SetEMotorS(api, index=0, isEnabled=1, speed=1100, distance=1900, isQueued=0)
    dType.SetWAITCmd(api, 2000, 1)

def pipette_reset():
    """Fährt den Kolbenmotor wieder in die Ausgangslage zurück."""
    print("[Pipette] Kolben zurücksetzen...")
    # Vom zweiten Druckpunkt (1900) komplett zurück auf 0: Geschwindigkeit -1100, Distanz 1900
    dType.SetEMotorS(api, index=0, isEnabled=1, speed=-1100, distance=1900, isQueued=0)
    dType.SetWAITCmd(api, 2000, 1)

def wait_for_eppi_ready(eppi_num):
    """Simuliert das Warten auf Roboter 2 mit einer festen Wartezeit von 3 Sekunden."""
   
    dType.SetWAITCmd(api, 3000, 1)

def signal_pipetting_done(eppi_num):
    """Simuliert das Signal an Roboter 2 (keine Aktion nötig für Einzelbetrieb)."""
    

# ==========================================
# 4. MODULARE PROZESS-FUNKTION (FLÜSSIGKEIT)
# ==========================================
def prozessiere_fluessigkeit(name, fluid_runter, fluid_sicherheit, num_eppis, reps_per_eppi):
    """
    Führt den kompletten Ablauf für eine Flüssigkeit aus:
    Pipette holen -> Für jedes Eppi (Spitze -> Ansaugen -> Abgeben -> Abwurf) -> Pipette ablegen
    """
    global tip_index
    
    
    # A. ZUR PIPETTENSTELLE FAHREN UND PIPETTE AUFNEHMEN
    print("-> Hole Pipette...")
    dType.SetPTPWithLCmd(api, 1, PIPETTE_SICHERHEIT[0], PIPETTE_SICHERHEIT[1], PIPETTE_SICHERHEIT[2], PIPETTE_SICHERHEIT[3], PIPETTE_SICHERHEIT[4], 1)
    dType.SetPTPWithLCmd(api, 1, PIPETTE_RUNTER[0], PIPETTE_RUNTER[1], PIPETTE_RUNTER[2], PIPETTE_RUNTER[3], PIPETTE_RUNTER[4], 1)
    # Hier physikalischer Griff/Verriegelung der Pipette (Magnet/Klemme)
    dType.SetWAITCmd(api, 1500, 1)
    dType.SetPTPWithLCmd(api, 1, PIPETTE_SICHERHEIT[0], PIPETTE_SICHERHEIT[1], PIPETTE_SICHERHEIT[2], PIPETTE_SICHERHEIT[3], PIPETTE_SICHERHEIT[4], 1)
    
    # B. EPPI-LOOP (SCHLEIFE 1)
    for eppi in range(num_eppis):
        # 1. Warten (3 Sekunden Pause), bis das Eppi bereitgestellt/geöffnet ist (der Roboterarm schraubt nicht auf, sondern gibt nur die Probe ab)
        wait_for_eppi_ready(eppi + 1)
        
        # 2. Schleife für eventuelle Mehrfach-Pipettierungen pro Eppi (Schleife 2)
        for rep in range(reps_per_eppi):
            
            
            # Spitzenkoordinaten berechnen
            col = tip_index % 12
            row = tip_index // 12
            l_spitze = SPITZEN_START_L + col * SPITZEN_OFFSET_L
            y_offset = row * SPITZEN_OFFSET_Y
            
            # a. Zu Spitzen-Sicherheit fahren
            dType.SetPTPWithLCmd(api, 1, SPITZEN_SICHERHEIT[0], SPITZEN_SICHERHEIT[1] + y_offset, SPITZEN_SICHERHEIT[2], SPITZEN_SICHERHEIT[3], l_spitze, 1)
            # b. Runterfahren und Spitze aufnehmen
            dType.SetPTPWithLCmd(api, 1, SPITZEN_RUNTER[0], SPITZEN_RUNTER[1] + y_offset, SPITZEN_RUNTER[2], SPITZEN_RUNTER[3], l_spitze, 1)
            dType.SetWAITCmd(api, 1500, 1)
            # c. Zurück auf Sicherheitshöhe fahren
            dType.SetPTPWithLCmd(api, 1, SPITZEN_SICHERHEIT[0], SPITZEN_SICHERHEIT[1] + y_offset, SPITZEN_SICHERHEIT[2], SPITZEN_SICHERHEIT[3], l_spitze, 1)
            
            # d. Kolben zur Vorbereitung auf den 1. Druckpunkt drücken
            pipette_press_first_stop()
            
            # e. Zur Flüssigkeits-Sicherheit fahren
            dType.SetPTPWithLCmd(api, 1, fluid_sicherheit[0], fluid_sicherheit[1], fluid_sicherheit[2], fluid_sicherheit[3], fluid_sicherheit[4], 1)
            # f. In Flüssigkeit eintauchen
            dType.SetPTPWithLCmd(api, 1, fluid_runter[0], fluid_runter[1], fluid_runter[2], fluid_runter[3], fluid_runter[4], 1)
            
            # g. Flüssigkeit ansaugen (Kolben freigeben)
            pipette_release()
            
            # h. Anheben zur Flüssigkeits-Sicherheit
            dType.SetPTPWithLCmd(api, 1, fluid_sicherheit[0], fluid_sicherheit[1], fluid_sicherheit[2], fluid_sicherheit[3], fluid_sicherheit[4], 1)
            
            # i. Zur Eppi-Sicherheit fahren (Stationäre Übergabestelle)
            dType.SetPTPWithLCmd(api, 1, EPPI_ABGABE_SICHERHEIT[0], EPPI_ABGABE_SICHERHEIT[1], EPPI_ABGABE_SICHERHEIT[2], EPPI_ABGABE_SICHERHEIT[3], EPPI_ABGABE_SICHERHEIT[4], 1)
            # j. Ins Eppi eintauchen
            dType.SetPTPWithLCmd(api, 1, EPPI_ABGABE_RUNTER[0], EPPI_ABGABE_RUNTER[1], EPPI_ABGABE_RUNTER[2], EPPI_ABGABE_RUNTER[3], EPPI_ABGABE_RUNTER[4], 1)
            
            # k. Flüssigkeit abgeben (Kolben auf 1. Druckpunkt)
            pipette_press_first_stop()
            
            # l. Anheben zur Eppi-Sicherheit (raus aus dem Eppi)
            dType.SetPTPWithLCmd(api, 1, EPPI_ABGABE_SICHERHEIT[0], EPPI_ABGABE_SICHERHEIT[1], EPPI_ABGABE_SICHERHEIT[2], EPPI_ABGABE_SICHERHEIT[3], EPPI_ABGABE_SICHERHEIT[4], 1)
            
            # Kolben wieder zurückfahren nach dem Abgeben (im angehobenen Zustand)
            pipette_release()
            
            # m. Zur Restentleerungs-Sicherheit fahren (ehemals Abwurf)
            dType.SetPTPWithLCmd(api, 1, RESTENTLEERUNG_SICHERHEIT[0], RESTENTLEERUNG_SICHERHEIT[1], RESTENTLEERUNG_SICHERHEIT[2], RESTENTLEERUNG_SICHERHEIT[3], RESTENTLEERUNG_SICHERHEIT[4], 1)
            # n. Zur Restentleerung runterfahren
            dType.SetPTPWithLCmd(api, 1, RESTENTLEERUNG_RUNTER[0], RESTENTLEERUNG_RUNTER[1], RESTENTLEERUNG_RUNTER[2], RESTENTLEERUNG_RUNTER[3], RESTENTLEERUNG_RUNTER[4], 1)
            
            # o. Restentleerung: Kolben drücken (1. Druckpunkt) und wieder hochfahren
            pipette_press_first_stop()
            pipette_release()
            
            # p. Anheben zur Restentleerungs-Sicherheit
            dType.SetPTPWithLCmd(api, 1, RESTENTLEERUNG_SICHERHEIT[0], RESTENTLEERUNG_SICHERHEIT[1], RESTENTLEERUNG_SICHERHEIT[2], RESTENTLEERUNG_SICHERHEIT[3], RESTENTLEERUNG_SICHERHEIT[4], 1)
            
            # q. Zur NEUEN Abwurf-Sicherheit fahren
            dType.SetPTPWithLCmd(api, 1, ABWURF_NEU_SICHERHEIT[0], ABWURF_NEU_SICHERHEIT[1], ABWURF_NEU_SICHERHEIT[2], ABWURF_NEU_SICHERHEIT[3], ABWURF_NEU_SICHERHEIT[4], 1)
            # r. Zum neuen Abwurf runterfahren
            dType.SetPTPWithLCmd(api, 1, ABWURF_NEU_RUNTER[0], ABWURF_NEU_RUNTER[1], ABWURF_NEU_RUNTER[2], ABWURF_NEU_RUNTER[3], ABWURF_NEU_RUNTER[4], 1)
            
            # s. Spitze abwerfen (Kolben auf 2. Druckpunkt)
            pipette_press_second_stop()
            # t. Kolben wieder zurücksetzen
            pipette_reset()
            
            # u. Anheben zur neuen Abwurf-Sicherheit
            dType.SetPTPWithLCmd(api, 1, ABWURF_NEU_SICHERHEIT[0], ABWURF_NEU_SICHERHEIT[1], ABWURF_NEU_SICHERHEIT[2], ABWURF_NEU_SICHERHEIT[3], ABWURF_NEU_SICHERHEIT[4], 1)
            
            # Globalen Spitzen-Zähler erhöhen
            tip_index += 1
            
        # 3. Dem Eppi-Roboter signalisieren, dass er dieses Eppi zuschrauben/mischen kann
        signal_pipetting_done(eppi + 1)
        
    # C. PIPETTE WIEDER ABLEGEN
    print("-> Lege Pipette ab...")
    dType.SetPTPWithLCmd(api, 1, PIPETTE_SICHERHEIT[0], PIPETTE_SICHERHEIT[1], PIPETTE_SICHERHEIT[2], PIPETTE_SICHERHEIT[3], PIPETTE_SICHERHEIT[4], 1)
    dType.SetPTPWithLCmd(api, 1, PIPETTE_RUNTER[0], PIPETTE_RUNTER[1], PIPETTE_RUNTER[2], PIPETTE_RUNTER[3], PIPETTE_RUNTER[4], 1)
    # Pipettenverriegelung lösen
    dType.SetWAITCmd(api, 1500, 1)
    dType.SetPTPWithLCmd(api, 1, PIPETTE_SICHERHEIT[0], PIPETTE_SICHERHEIT[1], PIPETTE_SICHERHEIT[2], PIPETTE_SICHERHEIT[3], PIPETTE_SICHERHEIT[4], 1)
    
   
# ==========================================
# 5. HAUPTAPLAUF DES PROGRAMMS
# ==========================================
print("=== PROGRAMMSTART (PLASMIDSTRASSE ROBOTER 1) ===")

# --- 1. Flüssigkeit 1 ---
prozessiere_fluessigkeit(
    name="Flüssigkeit 1",
    fluid_runter=FLUID1_RUNTER,
    fluid_sicherheit=FLUID1_SICHERHEIT,
    num_eppis=NUM_EPPIS,
    reps_per_eppi=1
)

# --- 2. Flüssigkeit 2 (von Abstellplatz grün) ---
prozessiere_fluessigkeit(
    name="Abstellplatz grün (Flüssigkeit 2)",
    fluid_runter=ABSTELLPLATZ_GRUEN_RUNTER,
    fluid_sicherheit=ABSTELLPLATZ_GRUEN_SICHERHEIT,
    num_eppis=NUM_EPPIS,
    reps_per_eppi=1
)

# --- Wartezeit von 3 Minuten zwischen Flüssigkeit 2 und Flüssigkeit 3 ---
print("==========================================")
print("PAUSE: Warte 3 Minuten (180 Sekunden) vor Flüssigkeit 3...")
print("==========================================")
# Der Roboter wartet in seiner Bewegungsschlange
dType.SetWAITCmd(api, 180000, 1)

# --- 3. Flüssigkeit 3 (von Abstellplatz grün) ---
prozessiere_fluessigkeit(
    name="Abstellplatz grün (Flüssigkeit 3)",
    fluid_runter=ABSTELLPLATZ_GRUEN_RUNTER,
    fluid_sicherheit=ABSTELLPLATZ_GRUEN_SICHERHEIT,
    num_eppis=NUM_EPPIS,
    reps_per_eppi=1
)

print("=== PROGRAMMENDE ===")
