import numpy as np
import trimesh
import matplotlib.pyplot as plt
from tqdm import tqdm

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

# Calcular el factor de vista entre paneles y Tierra
def calculate_view_factor(panel_mesh, earth, satellite_position):
    # Crear rayos que emanan desde los centroides de los triángulos del panel
    centroids = panel_mesh.triangles_center + satellite_position
    directions = np.random.normal(size=(len(centroids), 1000, 3))  # 1000 direcciones por triángulo
    directions /= np.linalg.norm(directions, axis=2)[:, :, None]  # Normalizar direcciones

    hit_count = 0
    total_rays = len(centroids) * 1000

    for i, centroid in enumerate(centroids):
        rays_origins = np.tile(centroid, (1000, 1))
        rays_directions = directions[i]

        # Verificar intersecciones con la Tierra
        hits = earth.ray.intersects_any(
            ray_origins=rays_origins,
            ray_directions=rays_directions
        )

        hit_count += np.sum(hits)

    # Calcular el factor de vista
    view_factor = hit_count / total_rays
    return view_factor

if __name__ == "__main__":
    # Crear la Tierra
    earth = create_earth()

    # Crear un panel solar subdividido (N x N cuadraditos)
    n = 10  # Número de subdivisiones por lado
    panel_mesh = generate_panel_mesh(n)

    # Tiempo y paso
    time_steps = 100
    times = np.linspace(0, orbit_time, time_steps)

    # Calcular el factor de vista a lo largo de la órbita
    view_factors = []

    print("Calculando factor de vista para cada posición en la órbita...")
    for t in tqdm(times):
        theta = angular_velocity * t
        satellite_position = np.array([
            satellite_orbit_radius_m * np.cos(theta),
            satellite_orbit_radius_m * np.sin(theta),
            0  # Órbita en el plano XY
        ])
        view_factor = calculate_view_factor(panel_mesh, earth, satellite_position)
        view_factors.append(view_factor)

    # Graficar el factor de vista a lo largo de la órbita
    plt.figure(figsize=(10, 6))
    plt.plot(times / 60, view_factors, label="Factor de vista", color="blue")
    plt.title("Evolución del factor de vista a lo largo de la órbita")
    plt.xlabel("Tiempo (min)")
    plt.ylabel("Factor de vista")
    plt.grid()
    plt.legend()
    plt.show()
