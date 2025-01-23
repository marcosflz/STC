import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from tqdm import tqdm  # Importar tqdm para mostrar progreso

# Parámetros de la Tierra y el satélite
earth_radius = 6371  # Radio de la Tierra en km
orbit_altitude = 300  # Altitud de la órbita en km
satellite_orbit_radius = earth_radius + orbit_altitude  # Radio de la órbita
satellite_orbit_time = 90 * 60  # Tiempo orbital (90 min en segundos)
angular_velocity = 2 * np.pi / satellite_orbit_time  # Velocidad angular (rad/s)

# Definir la Tierra (esfera)
planet_center = np.array([0, 0, 0])  # Centro de la Tierra
planet_radius = earth_radius  # Radio de la Tierra

# Definir el panel solar (hexaedro)
panel_vertices = np.array([
    [1, 1, 2], [1, -1, 2], [-1, -1, 2], [-1, 1, 2],  # Base inferior
    [1, 1, 2.05], [1, -1, 2.05], [-1, -1, 2.05], [-1, 1, 2.05]  # Base superior
])
panel_faces = ConvexHull(panel_vertices).simplices  # Calcular las caras del panel

# Fuente de luz: Sol
light_direction = np.array([1, 0, 0])  # Dirección hacia el Sol

# Función para verificar intersección rayo-esfera
def ray_intersects_sphere(ray_origin, ray_direction, sphere_center, sphere_radius):
    oc = ray_origin - sphere_center
    a = np.dot(ray_direction, ray_direction)
    b = 2.0 * np.dot(oc, ray_direction)
    c = np.dot(oc, oc) - sphere_radius**2
    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        return False
    t1 = (-b - np.sqrt(discriminant)) / (2.0 * a)
    t2 = (-b + np.sqrt(discriminant)) / (2.0 * a)
    return t1 > 0 or t2 > 0  # Verdadero si hay intersección

# Función para calcular área iluminada (sin sombra) en un momento específico
def calculate_illuminated_area(satellite_position):
    total_area_illuminated = 0.0
    for face in panel_faces:
        # Obtener vértices de la cara y desplazar con la posición del satélite
        face_vertices = panel_vertices[face]
        face_vertices = face_vertices + satellite_position
        v0, v1, v2 = face_vertices[:3]  # Triángulo

        # Subdividir la cara en puntos
        subdivision = 10
        u = np.linspace(0, 1, subdivision)
        v = np.linspace(0, 1, subdivision)
        u, v = np.meshgrid(u, v)
        u, v = u.flatten(), v.flatten()
        mask = u + v <= 1
        u, v = u[mask], v[mask]
        points = np.outer(1 - u - v, v0) + np.outer(u, v1) + np.outer(v, v2)

        # Verificar sombra para cada subdivisión
        for point in points:
            ray_origin = point - light_direction * 1e5  # Punto lejano
            ray_direction = light_direction
            if not ray_intersects_sphere(ray_origin, ray_direction, planet_center, planet_radius):
                total_area_illuminated += (
                    0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0)) / len(points)
                )  # Fracción de área
    return total_area_illuminated

# Calcular el área iluminada a lo largo de la órbita
time_steps = 100
times = np.linspace(0, satellite_orbit_time, time_steps)  # Tiempo a lo largo de la órbita
illuminated_areas = []

print("Calculando áreas iluminadas...")
for t in tqdm(times):  # Usar tqdm para mostrar el progreso
    # Posición del satélite en la órbita circular
    theta = angular_velocity * t
    satellite_position = np.array([
        satellite_orbit_radius * np.cos(theta),
        satellite_orbit_radius * np.sin(theta),
        0  # Órbita en el plano XY
    ])
    illuminated_areas.append(calculate_illuminated_area(satellite_position))

# Graficar la evolución del área iluminada
plt.figure(figsize=(10, 6))
plt.plot(times / 60, illuminated_areas, label="Área iluminada (m^2)", color="green")
plt.title("Área iluminada del panel solar a lo largo de la órbita")
plt.xlabel("Tiempo (min)")
plt.ylabel("Área iluminada (m^2)")
plt.grid()
plt.legend()
plt.show()
