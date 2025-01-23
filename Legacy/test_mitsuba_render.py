import numpy as np
import mitsuba as mi
import matplotlib.pyplot as plt
from tqdm import tqdm
import trimesh
import tempfile

# Inicializar Mitsuba
mi.set_variant("scalar_rgb")

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

# Crear escena con Mitsuba
def create_scene(panel_mesh, sun_position, satellite_position):
    # Guardar la malla como un archivo temporal en formato .obj
    with tempfile.NamedTemporaryFile(suffix=".obj", delete=False) as temp_obj:
        panel_mesh.export(temp_obj.name)
        panel_path = temp_obj.name

    # Crear la Tierra
    earth = mi.load_dict({
        "type": "sphere",
        "radius": earth_radius * 1e3,
        "center": [0, 0, 0],
        "bsdf": {"type": "diffuse", "reflectance": 0.0}
    })

    # Cargar panel solar desde el archivo .obj
    panel = mi.load_dict({
        "type": "obj",
        "filename": panel_path,
        "bsdf": {"type": "diffuse", "reflectance": 0.8}
    })

    # Crear luz puntual para el Sol
    sun_light = mi.load_dict({
        "type": "point",
        "position": sun_position.tolist(),
        "intensity": [1e8, 1e8, 1e8]  # Intensidad de la luz
    })

    # Crear escena completa
    scene = mi.load_dict({
        "type": "scene",
        "objects": {
            "earth": earth,
            "panel": panel,
            "sun": sun_light
        }
    })

    return scene

# Simular interacciones de luz
def simulate_lighting(scene):
    # Crear sensor para medir la iluminación
    sensor = mi.load_dict({
        "type": "perspective",
        "to_world": mi.ScalarTransform4f.look_at(
            origin=[0, 0, satellite_orbit_radius_m],
            target=[0, 0, 0],
            up=[0, 1, 0]
        ),
        "film": {
            "type": "hdrfilm",
            "width": 1280,
            "height": 720,
            "pixel_format": "rgb"
        }
    })

    # Renderizar la escena
    integrator = mi.load_dict({"type": "path"})
    rendered_image = mi.render(scene, integrator=integrator, sensor=sensor)

    return rendered_image

if __name__ == "__main__":
    # Crear un panel solar subdividido (N x N cuadraditos)
    n = 10  # Número de subdivisiones por lado
    size = 2.0  # Tamaño del panel solar en metros
    step = size / n
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
    panel_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Definir posiciones iniciales
    sun_position = np.array([-1e9, 0, 0])  # Sol muy lejos en -X
    satellite_position = np.array([satellite_orbit_radius_m, 0, 0])

    # Crear escena
    scene = create_scene(panel_mesh, sun_position, satellite_position)

    # Simular iluminación
    print("Simulando iluminación en la escena...")
    image = simulate_lighting(scene)

    # Mostrar imagen renderizada
    plt.imshow(image)
    plt.title("Iluminación simulada del satélite")
    plt.axis("off")
    plt.show()
