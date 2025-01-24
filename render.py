import numpy as np
import pyrender
import trimesh

# Crear una esfera grande
radius_large = 10.0  # Radio de la esfera grande
data_large_sphere = trimesh.creation.icosphere(subdivisions=4, radius=radius_large)

# Crear una esfera pequeña
radius_small = 0.1  # Radio de la esfera pequeña
small_sphere_offset = [10.1, 0, 0]  # Desplazamiento de la esfera pequeña respecto a la grande
data_small_sphere = trimesh.creation.icosphere(subdivisions=4, radius=radius_small)
data_small_sphere.apply_translation(small_sphere_offset)

# Crear nodos de malla para pyrender
mesh_large_sphere = pyrender.Mesh.from_trimesh(data_large_sphere, smooth=True)
mesh_small_sphere = pyrender.Mesh.from_trimesh(data_small_sphere, smooth=True)

# Crear la escena
scene = pyrender.Scene()
scene.add(mesh_large_sphere, name="large_sphere")
scene.add(mesh_small_sphere, name="small_sphere")

# Agregar una luz puntual en la posición de la esfera pequeña
light = pyrender.PointLight(color=np.ones(3), intensity=10.0)
light_pose = np.eye(4)
light_pose[:3, 3] = small_sphere_offset  # Colocar la luz en la posición de la esfera pequeña
scene.add(light, pose=light_pose)

# Agregar una cámara
camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
camera_pose = np.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, -1.0],
    [0.0, 0.0, 1.0, 3.0],
    [0.0, 0.0, 0.0, 1.0],
])
scene.add(camera, pose=camera_pose)

# Renderizar la escena
viewer = pyrender.Viewer(scene, use_raymond_lighting=False, run_in_thread=True)

# Calcular rayos normales hacia afuera desde la superficie de la esfera pequeña
vertices = data_small_sphere.vertices  # Puntos en la superficie de la esfera pequeña
normals = (vertices - np.array(small_sphere_offset)) / np.linalg.norm(vertices, axis=1)[:, np.newaxis]  # Normales hacia afuera
ray_origins = vertices  # Desplazar los puntos al lugar de la esfera pequeña

# Usar Trimesh ray_triangle para calcular intersecciones
ray_intersector = trimesh.ray.ray_triangle.RayMeshIntersector(data_large_sphere)
intersections, index_ray, index_tri = ray_intersector.intersects_location(ray_origins, normals)

# Puntos de intersección
print(f"Puntos de intersección (los primeros 10): {intersections[:10]}")

# Calcular la proporción de rayos que impactan en la esfera grande
proportion_of_rays = len(index_ray) / len(vertices)
print(f"Proporción de rayos que alcanzan la esfera grande: {proportion_of_rays}")
