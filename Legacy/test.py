import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Definir constantes
earth_radius = 6371  # Radio de la Tierra en km
satellite_altitude = 300  # Altitud del satélite en km
satellite_orbit_radius = earth_radius + satellite_altitude  # Radio de la órbita del satélite
satellite_diameter = 2  # Diámetro del satélite en m

# Crear Tierra (esfera)
theta = np.linspace(0, np.pi, 50)
phi = np.linspace(0, 2 * np.pi, 50)
x_earth = earth_radius * np.outer(np.sin(theta), np.cos(phi))
y_earth = earth_radius * np.outer(np.sin(theta), np.sin(phi))
z_earth = earth_radius * np.outer(np.cos(theta), np.ones_like(phi))

# Crear órbita del satélite (círculo alrededor de la Tierra en el plano XY)
theta_orbit = np.linspace(0, 2 * np.pi, 100)
x_orbit = satellite_orbit_radius * np.cos(theta_orbit)
y_orbit = satellite_orbit_radius * np.sin(theta_orbit)
z_orbit = np.zeros_like(x_orbit)

# Posición del satélite en un punto de la órbita
satellite_position_angle = np.pi / 4  # Ángulo arbitrario (45°) en la órbita
x_satellite = satellite_orbit_radius * np.cos(satellite_position_angle)
y_satellite = satellite_orbit_radius * np.sin(satellite_position_angle)
z_satellite = 0

# Vector apuntando al Sol (en el eje X positivo)
sun_vector = np.array([1, 0, 0]) * 1.5 * satellite_orbit_radius  # Escalar para visualizar mejor

# Corregir la escala para que sea uniforme
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d', aspect='auto')

# Dibujar la Tierra
ax.plot_surface(x_earth, y_earth, z_earth, color='b', alpha=0.5, edgecolor='k')

# Dibujar la órbita del satélite
ax.plot(x_orbit, y_orbit, z_orbit, 'g--', label='Órbita del satélite')

# Dibujar el satélite
ax.scatter(x_satellite, y_satellite, z_satellite, color='r', s=100, label='Satélite')

# Dibujar el vector hacia el Sol
ax.quiver(x_satellite, y_satellite, z_satellite, sun_vector[0], sun_vector[1], sun_vector[2],
          color='orange', label='Dirección al Sol', length=earth_radius, normalize=True)

# Etiquetas y leyenda
ax.set_title("Modelado 3D: Tierra, Sol y Satélite en Órbita")
ax.set_xlabel("X (km)")
ax.set_ylabel("Y (km)")
ax.set_zlabel("Z (km)")
ax.legend()

# Ajustar escala uniforme
scale = satellite_orbit_radius * 1.5
ax.set_xlim([-scale, scale])
ax.set_ylim([-scale, scale])
ax.set_zlim([-scale, scale])
ax.set_box_aspect([1, 1, 1])  # Aspecto uniforme

plt.show()
