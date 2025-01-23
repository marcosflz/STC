import numpy as np
import pyvista as pv
from tqdm import tqdm

# Función para calcular el factor de vista discretizado
def calcular_factor_de_vista(surface1, surface2, area1, area2):
    points1 = surface1.points
    points2 = surface2.points
    normals1 = surface1.point_normals
    normals2 = surface2.point_normals

    factor_de_vista = 0

    dA1 = area1 / len(points1)  # Área de cada punto
    dA2 = area2 / len(points2)  # Área de cada punto

    for i, p1 in enumerate(tqdm(points1, desc="Procesando puntos de surface1")):
        for j, p2 in enumerate(points2):
            r = np.linalg.norm(p2 - p1)  # Distancia entre puntos
            if r == 0:
                continue

            cos_theta1 = np.dot(normals1[i], (p2 - p1) / r)  # Ángulo para surface1
            cos_theta2 = np.dot(normals2[j], (p1 - p2) / r)  # Ángulo para surface2

            if cos_theta1 > 0 and cos_theta2 > 0:
                factor_de_vista += (cos_theta1 * cos_theta2 * dA1 * dA2) / (np.pi * r**2)

    # Normalizar por el área total de surface1
    factor_de_vista /= area1
    return factor_de_vista

if __name__ == "__main__":
    # Crear geometrías con PyVista
    esfera = pv.Sphere(radius=1, center=(0, 0, 0))
    rectangulo_i = pv.Plane(center=(1.5, 0, 0), direction=(1, 0, 0), i_size=2, j_size=2)  # Cara interior
    rectangulo_e = pv.Plane(center=(1.55, 0, 0), direction=(1, 0, 0), i_size=2, j_size=2)  # Cara exterior
    entorno = pv.Sphere(radius=10, center=(0, 0, 0))

    # Áreas predefinidas
    area_esfera = 4 * np.pi * (1**2)  # Área de la esfera con radio 1
    area_rectangulo = 4.0  # Área fija del rectángulo

    # Calcular normales para las superficies
    esfera = esfera.compute_normals()
    rectangulo_i = rectangulo_i.compute_normals(flip_normals=True)  # Normales hacia afuera (default)
    rectangulo_e = rectangulo_e.compute_normals()  # Normales hacia adentro
    entorno = entorno.compute_normals(flip_normals=True)  # Invertir las normales hacia adentro

    # Calcular el factor de vista entre las superficies
    print("Calculando factores de vista...")
    F_esfera_rect_i = calcular_factor_de_vista(esfera, rectangulo_i, area_esfera, area_rectangulo)
    F_esfera_rect_e = calcular_factor_de_vista(esfera, rectangulo_e, area_esfera, area_rectangulo)
    F_esfera_ento = calcular_factor_de_vista(esfera, entorno, area_esfera, 4 * np.pi * (10**2))

    F_rect_i_esfera = calcular_factor_de_vista(rectangulo_i, esfera, area_rectangulo, area_esfera)
    F_rect_e_esfera = calcular_factor_de_vista(rectangulo_e, esfera, area_rectangulo, area_esfera)
    F_rect_i_ento = calcular_factor_de_vista(rectangulo_i, entorno, area_rectangulo, 4 * np.pi * (10**2))
    F_rect_e_ento = calcular_factor_de_vista(rectangulo_e, entorno, area_rectangulo, 4 * np.pi * (10**2))

    # Mostrar resultados
    print("\nResultados:")
    print("Factor de vista entre la esfera y la cara interior del rectángulo:", round(F_esfera_rect_i, 4))
    print("Factor de vista entre la esfera y la cara exterior del rectángulo:", round(F_esfera_rect_e, 4))
    print("Factor de vista entre la esfera y el entorno:", round(F_esfera_ento, 4))
    print("Factor de vista entre la cara interior del rectángulo y la esfera:", round(F_rect_i_esfera, 4))
    print("Factor de vista entre la cara exterior del rectángulo y la esfera:", round(F_rect_e_esfera, 4))
    print("Factor de vista entre la cara interior del rectángulo y el entorno:", round(F_rect_i_ento, 4))
    print("Factor de vista entre la cara exterior del rectángulo y el entorno:", round(F_rect_e_ento, 4))