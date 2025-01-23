import numpy as np
import pyvista as pv
import pyviewfactor as pvf

# Crear geometrías arbitrarias
sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))
plane = pv.Plane(center=(0, 0, 2.0), direction=(0, 0, 1), i_size=4.0, j_size=4.0)

# Convertir geometrías a UnstructuredGrid para compatibilidad
sphere_unstructured = sphere.cast_to_unstructured_grid()
plane_unstructured = plane.cast_to_unstructured_grid()

# Convertir a PolyData con PyViewFactor
sphere_mesh = pvf.fc_unstruc2poly(sphere_unstructured)
plane_mesh = pvf.fc_unstruc2poly(plane_unstructured)

# Dividir las caras de cada geometría
sphere_faces = sphere_mesh.faces.reshape(-1, 4)[:, 1:]  # Extraer triángulos
plane_faces = plane_mesh.faces.reshape(-1, 4)[:, 1:]    # Extraer triángulos

# Calcular el factor de vista total cara a cara
F_total = 0
for i, sphere_face in enumerate(sphere_faces):
    for j, plane_face in enumerate(plane_faces):
        # Extraer parches individuales (caras)
        sphere_patch = sphere_mesh.extract_cells([i])
        plane_patch = plane_mesh.extract_cells([j])

        # Calcular el factor de vista para este par
        try:
            F_ij = pvf.compute_viewfactor(sphere_patch, plane_patch)
            F_total += F_ij
        except Exception as e:
            print(f"Error en el cálculo del factor de vista entre cara {i} y {j}: {e}")

# Mostrar el resultado total
print(f"Factor de vista total calculado cara a cara: {F_total}")

# Comparar con el cálculo directo para el mesh completo
try:
    F_mesh_to_mesh = pvf.compute_viewfactor(sphere_mesh, plane_mesh)
    print(f"Factor de vista calculado para el mesh completo: {F_mesh_to_mesh}")
except Exception as e:
    print(f"Error al calcular el factor de vista para el mesh completo: {e}")
