import sys
try:
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
except ImportError:
    comm = 0

import pysu2


CONFIG_FILE = "flatplate.cfg"
WALL_MARKER = "wall"
ALPHA = 0.2  


def read_config_value(cfg_path, *keys):
    with open(cfg_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('%') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            if k.strip().upper() in [key.upper() for key in keys]:
                return float(v.split('%')[0].strip())
    return None

T_wall = read_config_value(CONFIG_FILE,
                           "WALL_TEMPERATURE",
                           "ISOTHERMAL_TEMPERATURE",
                           "MARKER_ISOTHERMAL_TEMPERATURE")
if T_wall is None:
    T_wall = 300.0
    print(f"  WARNING: T_wall not found in config, using fallback {T_wall} K")
else:
    print(f"  T_wall read from config : {T_wall:.4f} K")


print(f"Initialising SU2 with '{CONFIG_FILE}' ...")
driver = pysu2.CSinglezoneDriver(CONFIG_FILE, 1, comm)


marker_dict = driver.GetMarkerIndices()
print(f"  Available markers: {list(marker_dict.keys())}")

if WALL_MARKER not in marker_dict:
    raise RuntimeError(f"Marker '{WALL_MARKER}' not found. "
                       f"Available: {list(marker_dict.keys())}")

marker_id  = marker_dict[WALL_MARKER]
n_vertices = driver.GetNumberMarkerNodes(marker_id)
print(f"  Marker '{WALL_MARKER}' -> id={marker_id}, vertices={n_vertices}")


coords_matrix = driver.MarkerCoordinates(marker_id)
x_coords = [coords_matrix(i, 0) for i in range(n_vertices)]

x_min = min(x_coords)
x_max = max(x_coords)
print(f"  Plate x range : [{x_min:.4f}, {x_max:.4f}] m")

def T_wall_varying(x):
    """Linear ramp: 0.9*T_wall at x_min, 1.1*T_wall at x_max."""
    xi = (x - x_min) / (x_max - x_min)
    return T_wall * (1.0 + ALPHA * (xi - 0.5))

T_profile = [T_wall_varying(x) for x in x_coords]

print("\nSample temperature profile (every 10th vertex):")
print(f"  {'vertex':>8}  {'x [m]':>10}  {'T [K]':>10}")
for i in range(0, n_vertices, max(1, n_vertices // 10)):
    print(f"  {i:>8}  {x_coords[i]:>10.4f}  {T_profile[i]:>10.4f}")

print("\nStarting manual iteration loop ...")
n_iter = int(read_config_value(CONFIG_FILE, "ITER", "EXT_ITER", "MAX_OUTER_ITER"))
print(f"  Running for {n_iter} iterations (from config)")


for i_iter in range(n_iter):
    for i_vert in range(n_vertices):
        driver.SetMarkerCustomTemperature(marker_id, i_vert, T_profile[i_vert])

    driver.Preprocess(i_iter)
    driver.Run()
    driver.Postprocess()
    driver.Update()

    if driver.Monitor(i_iter):
        print(f"  Converged at iteration {i_iter}.")
        break

print("\nWriting output and finalising ...")
driver.Output(n_iter)
driver.Finalize()
print("Done.")