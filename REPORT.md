Objective: implementation of a spatially varying wall temperature for a compressible turbulent flat plate using the SU2 Python wrapper

Implementation:
to achieve the dynamic boundary condition, I wrote a custom python script with CSingleZoneDriver from pysu2
we first extract the minium and maximum x coordinates of "wall" marker nodes and normalized spatial coordinate xi is calculated for each node
xi = (x - x_min) / (x_max - x_min)
we write an equation to define the custom temperature profile applied:
T(x) =T_wall * (1.0 + ALPHA * (xi - 0.5))

During solver execution, script halts SU2 driver at start of every iteration, iterates through all the vertices on the wall boundary, updates temperature value at 
each specific vertex using SetMarkerCustomTemperature and then resumes the solver step 

Results:
from the history.csv file we can see that the solver ran for 3000 iterations after which it was stopped as the residuals were barely chaning so we assumed that 
solver reached necessary convergence

from the plot of wall temperature vs x we can see that the temperature varied horizontally proving that our wrapper worked
<img width="726" height="764" alt="{B583BF3A-64FC-40C3-89E1-EBF3B89CA32F}" src="https://github.com/user-attachments/assets/cecdda07-54f9-44fd-a1f8-c5467aa351b6" />

<img width="1470" height="764" alt="tempvariation" src="https://github.com/user-attachments/assets/07ee556b-725e-4783-914c-7055673dcc5c" />

