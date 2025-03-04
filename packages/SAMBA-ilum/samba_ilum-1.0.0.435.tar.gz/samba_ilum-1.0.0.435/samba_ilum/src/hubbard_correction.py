# SAMBA_ilum Copyright (C) 2024 - Closed source


import sys
import os


with open('POSCAR', "r") as file: lines = file.readlines()
elements  = lines[5].split()

U_VALORES = {"Sc": 3.0, "Ti": 4.0, "V": 3.1, "Cr": 3.5, "Mn": 3.9, "Fe": 5.3, "Co": 3.3, "Ni": 6.2,
             "Cu": 4.0, "Zn": 0.0, "Y": 3.2, "Zr": 2.0, "Nb": 1.5, "Mo": 2.0, "Ru": 1.5, "Rh": 1.5,
             "Ag": 1.5, "Cd": 0.0, "W": 2.0, "Pb": 0.5, "O": 5.3, "La": 6.0, "Ce": 5.0, "Nd": 5.0,
             "Sm": 5.0, "Eu": 5.0, "Gd": 5.0, "Tb": 5.0, "Dy": 5.0, "Ho": 5.0, "Er": 5.0, "Tm": 5.0,
             "Yb": 5.0, "U": 4.0}

LDAUL_VALORES = {"Sc": 2, "Ti": 2, "V": 2, "Cr": 2, "Mn": 2, "Fe": 2, "Co": 2, "Ni": 2, "Cu": 2,
                 "Zn": 2, "Y": 2, "Zr": 2, "Nb": 2, "Mo": 2, "Ru": 2, "Rh": 2, "Ag": 2, "Cd": 2,
                 "W": 2, "Pb": 1, "O": 1, "La": 3, "Ce": 3, "Nd": 3, "Sm": 3, "Eu": 3, "Gd": 3,
                 "Tb": 3, "Dy": 3, "Ho": 3, "Er": 3, "Tm": 3, "Yb": 3, "U": 3}

lmaxmix = 2
if any(LDAUL_VALORES.get(el, -1) == 2 for el in elementos): lmaxmix = 3  # d-orbitals
if any(LDAUL_VALORES.get(el, -1) == 3 for el in elementos): lmaxmix = 4  # f-orbitals

#============================================
# LDA+U/GGA+U Configuration =================
#============================================
LDAU = ".TRUE."
LDAUTYPE = "2"
LDAUL = " ".join(str(LDAUL_VALORES.get(el, -1)) for el in elements )
LDAUU = " ".join(str(U_VALORES.get(el, 0.0)) for el in elements )
LDAUJ = " ".join("0.0" for _ in elements )
LDAUPRINT = "1"

#============================================
# Updating INCAR file =======================
#============================================
with open("INCAR", "a") as output_file:
    output_file.write(f"# GGA+U =================\n")
    output_file.write(f"LDAU = {LDAU}\n")
    output_file.write(f"LMAXMIX = {lmaxmix}\n")
    output_file.write(f"LDAUTYPE = {LDAUTYPE}\n")
    output_file.write(f"LDAUL = {LDAUL}\n")
    output_file.write(f"LDAUU = {LDAUU}\n")
    output_file.write(f"LDAUJ = {LDAUJ}\n")
    output_file.write(f"LDAUPRINT = {LDAUPRINT}\n")
    output_file.write(f"# =======================\n")
