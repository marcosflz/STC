import numpy as np
import trimesh
import matplotlib.pyplot as plt
from tqdm import tqdm
import multiprocessing as mp

# Parámetros generales
earth_radius = 6371  # Radio de la Tierra en km
orbit_altitude = 300  # Altitud de la órbita en km
satellite_orbit_radius = earth_radius + orbit_altitude  # Radio de la órbita

# Cálculo del período orbital (en segundos)
G = 6.67430e-11  # Constante gravitacional (m^3 kg^-1 s^-2)
M = 5.972e24  # Masa de la Tierra (kg)
satellite_orbit_radius_m = satellite_orbit_radius * 1e3  # Convertir a metros
orbit_time = 2 * np.pi * np.sqrt(satellite_orbit_radius_m**3 / (G * M))  # Período orbital en segundos
angular_velocity = 2 * np.pi / orbit_time  # Velocidad angular (rad/s)

# Definir la Tierra como una esfera
def create_earth():
    return trimesh.primitives.Sphere(radius=earth_radius, center=[0, 0, 0])

# Generar el panel solar subdividido
def generate_panel_mesh(n, size=2):
    step = size / n  # Tamaño de cada cuadrado
    vertices = []
    faces = []
    for i in range(n + 1):
        for j in range(n + 1):
            x = -size / 2 + i * step
            y = -size / 2 + j * step
            z = 0
            vertices.append([x, y, z])

    for i in range(n):
        for j in range(n):
            v0 = i * (n + 1) + j
            v1 = v0 + 1
            v2 = v0 + (n + 1)
            v3 = v2 + 1
            faces.append([v0, v1, v3])  # Triángulo 1
            faces.append([v0, v3, v2])  # Triángulo 2

    vertices = np.array(vertices)
    faces = np.array(faces)
    return trimesh.Trimesh(vertices=vertices, faces=faces)

# Función para calcular el área iluminada en un instante de tiempo
def calculate_illuminated_area_at_time(args):
    t, panel_mesh, earth, light_direction = args
    theta = angular_velocity * t
    satellite_position = np.array([
        satellite_orbit_radius * np.cos(theta),
        satellite_orbit_radius * np.sin(theta),
        0  # Órbita en el plano XY
    ])
    
    # Calcular centroides de los triángulos del panel
    centroids = panel_mesh.triangles_center + satellite_position
    rays_directions = np.tile(light_direction, (len(centroids), 1))

    # Lanzar rayos para verificar intersecciones con la Tierra
    hit = earth.ray.intersects_any(
        ray_origins=centroids,
        ray_directions=rays_directions
    )

    # Calcular el área iluminada
    illuminated_mask = ~hit  # Invertir máscara
    triangle_areas = panel_mesh.area_faces  # Áreas de los triángulos
    illuminated_area = np.sum(triangle_areas[illuminated_mask])  # Sumar solo las áreas iluminadas
    return illuminated_area

# Paralelizar el cálculo
def calculate_illuminated_areas(panel_mesh, earth, light_direction, time_step=1.0):
    times = np.arange(0, orbit_time, time_step)  # Generar tiempos con el paso especificado
    args = [(t, panel_mesh, earth, light_direction) for t in times]
    with mp.Pool(processes=mp.cpu_count()-1) as pool:
        illuminated_areas = list(tqdm(pool.imap(calculate_illuminated_area_at_time, args), total=len(times)))
    return times, illuminated_areas

if __name__ == "__main__":
    # Crear la Tierra
    earth = create_earth()

    # Crear un panel solar subdividido (N x N cuadraditos)
    n = 50  # Número de subdivisiones por lado
    panel_mesh = generate_panel_mesh(n)

    # Fuente de luz: Sol
    light_direction = np.array([1, 0, 0])

    # Calcular áreas iluminadas
    time_step = 1  # Paso de tiempo en segundos
    print("Calculando áreas iluminadas con panel subdividido en paralelo...")
    times, illuminated_areas = calculate_illuminated_areas(panel_mesh, earth, light_direction, time_step)

    # Graficar la evolución del área iluminada
    plt.figure(figsize=(10, 6))
    plt.plot(times / 60, np.array(illuminated_areas) / panel_mesh.area, label="Proporción de área iluminada", color="green")
    plt.title(f"Área iluminada del panel solar con {n}x{n} subdivisiones")
    plt.xlabel("Tiempo (min)")
    plt.ylabel("Proporción de área iluminada")
    plt.grid()
    plt.legend()
    plt.show()
