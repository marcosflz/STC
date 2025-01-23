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
    t, panel_mesh, earth, sun_position = args
    theta = angular_velocity * t
    satellite_position = np.array([
        satellite_orbit_radius * np.cos(theta),
        satellite_orbit_radius * np.sin(theta),
        0  # Órbita en el plano XY
    ])

    # Calcular centroides de los triángulos del panel
    centroids = panel_mesh.triangles_center + satellite_position
    rays_origins = np.tile(sun_position, (len(centroids), 1))  # Sol como origen de todos los rayos
    rays_directions = centroids - rays_origins  # Direcciones desde el Sol a los centroides

    # Normalizar las direcciones
    rays_directions /= np.linalg.norm(rays_directions, axis=1)[:, None]

    # Lanzar rayos para verificar intersecciones con la Tierra
    hit = earth.ray.intersects_any(
        ray_origins=rays_origins,
        ray_directions=rays_directions
    )

    # Calcular el área iluminada
    illuminated_mask = ~hit  # Invertir máscara
    triangle_areas = panel_mesh.area_faces  # Áreas de los triángulos
    illuminated_area = np.sum(triangle_areas[illuminated_mask])  # Sumar solo las áreas iluminadas
    return illuminated_area

# Paralelizar el cálculo
def calculate_illuminated_areas(panel_mesh, earth, sun_position, time_step=1.0):
    times = np.arange(0, orbit_time, time_step)  # Generar tiempos con el paso especificado
    args = [(t, panel_mesh, earth, sun_position) for t in times]
    with mp.Pool(processes=mp.cpu_count()) as pool:
        illuminated_areas = list(tqdm(pool.imap(calculate_illuminated_area_at_time, args), total=len(times)))
    return times, illuminated_areas

if __name__ == "__main__":
    # Crear la Tierra
    earth = create_earth()

    # Crear un panel solar subdividido (N x N cuadraditos)
    n = 506  # Número de subdivisiones por lado
    panel_mesh = generate_panel_mesh(n)

    # Posición del Sol (muy lejos en la dirección -X)
    sun_position = np.array([1e8, 0, 0])  # Ejemplo de posición del Sol

    # Calcular áreas iluminadas
    time_step = 1.0  # Paso de tiempo en segundos
    print("Calculando áreas iluminadas con panel subdividido en paralelo...")
    times, illuminated_areas = calculate_illuminated_areas(panel_mesh, earth, sun_position, time_step)

    # Graficar la evolución del área iluminada
    plt.figure(figsize=(10, 6))
    plt.plot(times / 60, np.array(illuminated_areas) / panel_mesh.area, label="Proporción de área iluminada", color="green")
    plt.title(f"Área iluminada del panel solar con {n}x{n} subdivisiones")
    plt.xlabel("Tiempo (min)")
    plt.ylabel("Proporción de área iluminada")
    plt.grid()
    plt.legend()
    plt.show()
