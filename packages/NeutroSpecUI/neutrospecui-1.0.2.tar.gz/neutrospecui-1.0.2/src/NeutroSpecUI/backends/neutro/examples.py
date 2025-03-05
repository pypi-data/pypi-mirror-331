import numpy as np

from NeutroSpecUI.material import Material, Parameter

# TODO: delete this file, when the actual materials are implemented in plotting in plot.py


def toMaterial(name, rho, roughness, thickness, fraction):
    return Material(
        name,
        fraction=Parameter(fraction, name="fraction"),
        thickness=Parameter(thickness, name="thickness"),
        roughness=Parameter(roughness, name="roughness"),
        rho=Parameter(rho, name="rho"),
    )


# Dataset 1
mat1_sil = toMaterial(
    name="Material 1 - Silicon",
    rho=2.07e-6,
    roughness=3.0,
    thickness=99,
    fraction=1.0,
)

mat2_wat = toMaterial(
    name="Material 2 - Water",
    rho=6.37e-6,
    roughness=0.01,
    thickness=np.inf,
    fraction=1.0,
)

materials_1 = [mat1_sil, mat2_wat]

# Dataset 2
mat1_wat = toMaterial(
    name="Material 1 - Water",
    rho=6.37e-6,
    roughness=3.0,
    thickness=99,
    fraction=1.0,
)

mat2_oil = toMaterial(
    name="Material 2 - Oil",
    rho=-0.4e-6,
    roughness=0.01,
    thickness=np.inf,
    fraction=1.0,
)

materials_2 = [mat1_wat, mat2_oil]

# Dataset 3
mat1_sil = toMaterial(
    name="Silicon",
    rho=2.07e-6,
    roughness=3,
    thickness=999,
    fraction=1,
)

mat2_wat = toMaterial(
    name="Water",
    rho=6.37e-6,
    roughness=3,
    thickness=50.0,
    fraction=1,
)

mat3_oil = toMaterial(
    name="Oil",
    rho=-0.4e-6,
    roughness=0.01,
    thickness=np.inf,
    fraction=1,
)

materials_3 = [mat1_sil, mat2_wat, mat3_oil]

# SiAir	z axis ------------->
# Material	Silicon	Silicon oxide	Silane	Air
# SLD (ρ) x10^-6	2.07	3.47	-0.3	0
# Thickness, d	0	19.3	3	infinite
# Roughness,  σ	5	1	1.5	N/A
# Volume Fraction, Φ	1	0.83	1	1

mat1_sil = toMaterial(
    name="Silicon",
    rho=2.07e-6,
    roughness=5,
    thickness=99,
    fraction=1,
)

mat2_sio2 = toMaterial(
    name="Silicon Oxide",
    rho=3.47e-6,
    roughness=1,
    thickness=19.3,
    fraction=0.83,
)

mat3_silane = toMaterial(
    name="Silane",
    rho=-0.3e-6,
    roughness=1.5,
    thickness=3,
    fraction=1,
)

mat4_air = toMaterial(
    name="Air",
    rho=0,
    roughness=0,
    thickness=np.inf,
    fraction=1,
)

materials_SiAir = [mat1_sil, mat2_sio2, mat3_silane, mat4_air]


# SiWat	z axis ------------->
# Material	Silicon	Silicon oxide	Silane	Water
# SLD (ρ) x10^-6	2.07	3.47	-0.3	6.4
# Thickness, d	0	19.3	3	infinite
# Roughness,  σ	5	1	1.5	N/A
# Volume Fraction, Φ	1	0.83	1	1

mat1_sil = toMaterial(
    name="Silicon",
    rho=2.07e-6,
    roughness=5,
    thickness=99,
    fraction=1,
)

mat2_sio2 = toMaterial(
    name="Silicon Oxide",
    rho=3.47e-6,
    roughness=1,
    thickness=19.3,
    fraction=0.83,
)

mat3_silane = toMaterial(
    name="Silane",
    rho=-0.3e-6,
    roughness=1.5,
    thickness=3,
    fraction=1,
)

mat4_water = toMaterial(
    name="Water",
    rho=6.4e-6,
    roughness=0.01,
    thickness=np.inf,
    fraction=1,
)

materials_SiWat = [mat1_sil, mat2_sio2, mat3_silane, mat4_water]

# AirWat	z axis ------------->
# Material	Air	sfc head	sfc tail	Water
# SLD (ρ) x10^-6	0	-0.09	0.47	6.4
# Thickness, d	0	8	14	infinite
# Roughness,  σ	3.8	1.5	6	N/A
# Volume Fraction, Φ	1	1	1	1

mat1_air = toMaterial(
    name="Air",
    rho=0,
    roughness=3.8,
    thickness=999,
    fraction=1,
)

mat2_head = toMaterial(
    name="Surfactant Head",
    rho=-0.09e-6,
    roughness=1.5,
    thickness=8,
    fraction=1,
)

mat3_tail = toMaterial(
    name="Surfactant Tail",
    rho=0.47e-6,
    roughness=6,
    thickness=14,
    fraction=0.75,  # TODO: guessed by image check with josh
)

mat4_water = toMaterial(
    name="Water",
    rho=6.4e-6,
    roughness=0.01,
    thickness=np.inf,
    fraction=1,
)

materials_AirWat = [mat1_air, mat2_head, mat3_tail, mat4_water]

# SiSfc	z axis ------------->
# Material	Silicon	Silicon oxide	Silane	sfc head	sfc tail	Water
# SLD (ρ) x10^-6	2.07	3.47	-0.3	-0.09	0.47	6.4
# Thickness, d	0	19.3	3	8	14	infinite
# Roughness,  σ	5	1	1.5	1.5	6	N/A
# Volume Fraction, Φ	1	0.83	1	1	1	1

mat1_sil = toMaterial(
    name="Silicon",
    rho=2.07e-6,
    roughness=5,
    thickness=99,
    fraction=1,
)

mat2_sio2 = toMaterial(
    name="Silicon Oxide",
    rho=3.47e-6,
    roughness=1,
    thickness=19.3,
    fraction=0.83,
)

mat3_silane = toMaterial(
    name="Silane",
    rho=-0.3e-6,
    roughness=1.5,
    thickness=3,
    fraction=1,
)

mat4_head = toMaterial(
    name="Surfactant Head",
    rho=-0.09e-6,
    roughness=1.5,
    thickness=8,
    fraction=1,
)

mat5_tail = toMaterial(
    name="Surfactant Tail",
    rho=0.47e-6,
    roughness=6,
    thickness=14,
    fraction=0.75,  # TODO: guessed by image check with josh
)

mat6_water = toMaterial(
    name="Water",
    rho=6.4e-6,
    roughness=0.01,
    thickness=np.inf,
    fraction=1,
)

materials_SiSfc = [mat1_sil, mat2_sio2, mat3_silane, mat4_head, mat5_tail, mat6_water]
