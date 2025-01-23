import numpy as np
import meshio
from tqdm import tqdm

if __name__ == "__main__":
    # Crear geometrías como diccionarios de nodos y celdas
    esfera_points = []
    esfera_cells = []
    esfera_radius = 1
    esfera_center = (0, 0, 0)

    # Generar esfera usando numpy
    phi = np.linspace(0, np.pi, 10)
    theta = np.linspace(0, 2 * np.pi, 20)
    phi, theta = np.meshgrid(phi, theta)
    x = esfera_radius * np.sin(phi) * np.cos(theta) + esfera_center[0]
    y = esfera_radius * np.sin(phi) * np.sin(theta) + esfera_center[1]
    z = esfera_radius * np.cos(phi) + esfera_center[2]
    esfera_points = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T

    # Crear un rectángulo
    rect_points = [
        [1.5, -1, -1],
        [1.5, 1, -1],
        [1.5, 1, 1],
        [1.5, -1, 1],
    ]
    rect_cells = [[0, 1, 2, 3]]  # Cuadrado simple

    # Crear una esfera grande como entorno
    entorno_radius = 10
    entorno_points = []
    entorno_cells = []
    entorno_center = (0, 0, 0)

    # Generar entorno esfera con numpy
    phi = np.linspace(0, np.pi, 20)
    theta = np.linspace(0, 2 * np.pi, 40)
    phi, theta = np.meshgrid(phi, theta)
    x_env = entorno_radius * np.sin(phi) * np.cos(theta) + entorno_center[0]
    y_env = entorno_radius * np.sin(phi) * np.sin(theta) + entorno_center[1]
    z_env = entorno_radius * np.cos(phi) + entorno_center[2]
    entorno_points = np.vstack([x_env.ravel(), y_env.ravel(), z_env.ravel()]).T

    # Combinar todo para exportar como VTK
    all_points = np.vstack([esfera_points, rect_points, entorno_points])
    all_cells = {
        "triangle": [],  # Espacio para triángulos
        "quad": rect_cells,  # Rectángulo
    }

    # Exportar geometría con meshio
    mesh = meshio.Mesh(points=all_points, cells=all_cells)
    mesh.write("escena_meshio.vtk")

    # Leer geometría exportada
    mesh = meshio.read("escena_meshio.vtk")

    # Para análisis avanzado crear pipeline mesho, conversion and views comparission
   
    # Mostrar resultados
    print("Meshio processionado")