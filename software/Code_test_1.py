import math

# Bewegungsparameter einstellen
dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, 0)
dType.SetPTPCoordinateParams(api, 200, 200, 200, 200, 0)
dType.SetPTPJumpParams(api, 10, 200, 0)
dType.SetPTPCommonParams(api, 30, 30, 0)

# vorhandene Alarm löschen
dType.ClearAllAlarmsState(api)

# Roboter Homen
dType.SetHOMECmd(api, 0, 1)

# Koordinaten
PIPETTE_RUNTER = [201.3597, -7.6319, -3.2755, 2.2924, 1000.0]
PIPETTE_SICHERHEIT = [203.6515, -10.4527, 124.7097, 1.5247, 1000.0]

SPITZEN_RUNTER = [197.1824, -12.4971, -15.0867, 0.8365, 814.8]
SPITZEN_SICHERHEIT = [200.7890, -15.4291, 131.4488, 0.0689, 814.8]

PROBE_RUNTER = [197.1824, -12.4971, 35.0, 0.8365, 647.8]
PROBE_SICHERHEIT = [200.7890, -15.4291, 131.4488, 0.0689, 647.8]

GRUEN_RUNTER = [197.1824, -12.4971, 35.0, 0.8365, 415.8]
GRUEN_SICHERHEIT = [200.7890, -15.4291, 131.4488, 0.0689, 415.8]

ABWURF_RUNTER = [197.1824, -12.4971, 50.0, 0.8365, 150.1]
ABWURF_SICHERHEIT = [200.7890, -15.4291, 131.4488, 0.0689, 150.1]

# Gitter-Parameter für 96er Pipettenbox (8 Reihen x 12 Spalten)
SPITZEN_START_L = 814.8     # L-Koordinate der ersten Spalte (unten)
SPITZEN_OFFSET_L = -9.0     # Abstand der Spalten auf der Schiene
SPITZEN_OFFSET_Y = 9.0      # Reihenabstand quer zur Schiene (Y-Achse)

# Offsets für Proben und Ziele
PROBEN_OFFSET_L = -30.0     # Abstand zwischen den Probenröhrchen
ZIELE_OFFSET_L = -18.0      # Abstand zwischen den Zielgefäßen

print("Start...")

# 1. Zur Sicherheitsposition über der Pipette fahren
dType.SetPTPWithLCmd(
    api, 1,
    PIPETTE_SICHERHEIT[0],
    PIPETTE_SICHERHEIT[1],
    PIPETTE_SICHERHEIT[2],
    PIPETTE_SICHERHEIT[3],
    PIPETTE_SICHERHEIT[4],
    1
)

# 2. zur Pipette herunterfahren
dType.SetPTPWithLCmd(
    api, 1,
    PIPETTE_RUNTER[0],
    PIPETTE_RUNTER[1],
    PIPETTE_RUNTER[2],
    PIPETTE_RUNTER[3],
    PIPETTE_RUNTER[4],
    1
)

# 3. wieder zur Sicherheitsposition anheben
dType.SetPTPWithLCmd(
    api, 1,
    PIPETTE_SICHERHEIT[0],
    PIPETTE_SICHERHEIT[1],
    PIPETTE_SICHERHEIT[2],
    PIPETTE_SICHERHEIT[3],
    PIPETTE_SICHERHEIT[4],
    1
)

# Schleife zum wiederholen
for i in range(2):
    # Spalte (0-11) und Reihe (0-7) aus dem Schleifen-Index i berechnen
    col = i % 12
    row = i // 12
    
    # Berechnete L-Schienenkoordinate und Y-Armkoordinate für diese Spitze
    l_spitze = SPITZEN_START_L + col * SPITZEN_OFFSET_L
    y_offset = row * SPITZEN_OFFSET_Y
    
    # Offsets für die Proben und Ziele berechnen
    l_probe = PROBE_SICHERHEIT[4] + i * PROBEN_OFFSET_L
    l_ziel = GRUEN_SICHERHEIT[4] + i * ZIELE_OFFSET_L
    
    # 4. zur Sicherheitsposition über den Pipettenspitzen fahren
    dType.SetPTPWithLCmd(
        api, 1,
        SPITZEN_SICHERHEIT[0],
        SPITZEN_SICHERHEIT[1] + y_offset,
        SPITZEN_SICHERHEIT[2],
        SPITZEN_SICHERHEIT[3],
        l_spitze,
        1
    )
    
    # 5. zu den Pipettenspitzen herunterfahren
    dType.SetPTPWithLCmd(
        api, 1,
        SPITZEN_RUNTER[0],
        SPITZEN_RUNTER[1] + y_offset,
        SPITZEN_RUNTER[2],
        SPITZEN_RUNTER[3],
        l_spitze,
        1
    )
    
    # 6. Sicherheitsposition
    dType.SetPTPWithLCmd(
        api, 1,
        SPITZEN_SICHERHEIT[0],
        SPITZEN_SICHERHEIT[1] + y_offset,
        SPITZEN_SICHERHEIT[2],
        SPITZEN_SICHERHEIT[3],
        l_spitze,
        1
    )
    
    # 7. Zur Sicherheitsposition über der Probe fahren
    dType.SetPTPWithLCmd(
        api, 1,
        PROBE_SICHERHEIT[0],
        PROBE_SICHERHEIT[1],
        PROBE_SICHERHEIT[2],
        PROBE_SICHERHEIT[3],
        l_probe,
        1
    )
    
    # 8. Zur Probe herunterfahren (Eintauchen)
    dType.SetPTPWithLCmd(
        api, 1,
        PROBE_RUNTER[0],
        PROBE_RUNTER[1],
        PROBE_RUNTER[2],
        PROBE_RUNTER[3],
        l_probe,
        1
    )
    
    # Hier später: Flüssigkeit ansaugen (z.B. dType.SetEMotor)
    dType.SetWAITCmd(api, 1000, 1)
    
    # 9. Wieder zur Sicherheitsposition anheben
    dType.SetPTPWithLCmd(
        api, 1,
        PROBE_SICHERHEIT[0],
        PROBE_SICHERHEIT[1],
        PROBE_SICHERHEIT[2],
        PROBE_SICHERHEIT[3],
        l_probe,
        1
    )
    
    # 10. Zur Sicherheitsposition über dem grünen Gefäß fahren
    dType.SetPTPWithLCmd(
        api, 1,
        GRUEN_SICHERHEIT[0],
        GRUEN_SICHERHEIT[1],
        GRUEN_SICHERHEIT[2],
        GRUEN_SICHERHEIT[3],
        l_ziel,
        1
    )
    
    # 11. Zum grünen Gefäß herunterfahren (Abgeben)
    dType.SetPTPWithLCmd(
        api, 1,
        GRUEN_RUNTER[0],
        GRUEN_RUNTER[1],
        GRUEN_RUNTER[2],
        GRUEN_RUNTER[3],
        l_ziel,
        1
    )
    
    # Hier später: Flüssigkeit abgeben (z.B. dType.SetEMotor)
    dType.SetWAITCmd(api, 1000, 1)
    
    # 12. Wieder zur Sicherheitsposition anheben
    dType.SetPTPWithLCmd(
        api, 1,
        GRUEN_SICHERHEIT[0],
        GRUEN_SICHERHEIT[1],
        GRUEN_SICHERHEIT[2],
        GRUEN_SICHERHEIT[3],
        l_ziel,
        1
    )
    
    # 13. Zur Sicherheitsposition über dem Abwurf fahren
    dType.SetPTPWithLCmd(
        api, 1,
        ABWURF_SICHERHEIT[0],
        ABWURF_SICHERHEIT[1],
        ABWURF_SICHERHEIT[2],
        ABWURF_SICHERHEIT[3],
        ABWURF_SICHERHEIT[4],
        1
    )
    
    # 14. Zum Abwurf herunterfahren (Abwerfen)
    dType.SetPTPWithLCmd(
        api, 1,
        ABWURF_RUNTER[0],
        ABWURF_RUNTER[1],
        ABWURF_RUNTER[2],
        ABWURF_RUNTER[3],
        ABWURF_RUNTER[4],
        1
    )
    
    # Hier später: Spitze abwerfen (z.B. dType.SetEMotor)
    dType.SetWAITCmd(api, 1000, 1)
    
    # 15. Wieder zur Sicherheitsposition anheben
    dType.SetPTPWithLCmd(
        api, 1,
        ABWURF_SICHERHEIT[0],
        ABWURF_SICHERHEIT[1],
        ABWURF_SICHERHEIT[2],
        ABWURF_SICHERHEIT[3],
        ABWURF_SICHERHEIT[4],
        1
    )
