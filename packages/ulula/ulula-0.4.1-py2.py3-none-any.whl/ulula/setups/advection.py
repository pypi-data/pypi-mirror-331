###################################################################################################
#
# This file is part of the ULULA code.
#
# (c) Benedikt Diemer, University of Maryland
#
###################################################################################################

import numpy as np

import ulula.core.setup_base as setup_base

###################################################################################################

class SetupAdvection(setup_base.Setup):
    """
    Tophat advection test
    
    In this test, an initially overdense tophat is placed at the center of the domain. The entire
    fluid moves towards the northeast direction. The edges of the disk diffuse into the surrounding 
    fluid at a rate that depends on the hydro solver. For example, when using no spatial 
    reconstruction, the hydro scheme will be extremely diffusive (and 1st order in space and time)
    and the tophat will quickly spread into the surrounding fluid. Linear interpolation leads to
    less diffusion, especially if an aggressive slope limiter such as MC is used. However, when
    combining the resulting sharp gradients with a hydro scheme that is 1st-order in time (namely,
    a simple Euler time integrator), the test quickly becomes unstable and fails spectacularly.
    The default hydro scheme in Ulula, namely a MUSCL-Hancock 2nd-order scheme, leads to a stable 
    solution with modest diffusion. This setup demonstrates

    * Stability of time integration schemes
    * Diffusivity of reconstruction schemes
    * Importance of slope limiters.

    Parameters
    ----------
    unit_l: float
        Code unit for length in units of centimeters.
    unit_t: float
        Code unit for time in units of seconds.
    unit_m: float
        Code unit for mass in units of gram.
    """
    
    def __init__(self, unit_l = 1.0, unit_t = 1.0, unit_m = 1.0):

        setup_base.Setup.__init__(self, unit_l = unit_l, unit_t = unit_t, unit_m = unit_m)
        
        self.rho0 = 1.0
        self.rho1 = 2.0
        self.P0 = 1.0
        self.ux = 0.5
        self.uy = 0.3
        self.r_th = 0.1
        
        return 

    # ---------------------------------------------------------------------------------------------

    def shortName(self):
        
        return 'advection'

    # ---------------------------------------------------------------------------------------------
    
    def setInitialData(self, sim, nx):
        
        sim.setDomain(nx, nx, xmin = 0.0, xmax = 1.0, ymin = 0.0, bc_type = 'periodic')

        DN = sim.q_prim['DN']
        VX = sim.q_prim['VX']
        VY = sim.q_prim['VY']
        PR = sim.q_prim['PR']
        
        sim.V[DN] = self.rho0
        sim.V[VX] = self.ux
        sim.V[VY] = self.uy
        sim.V[PR] = self.P0

        # Set tophat into the center of the domain
        x, y = sim.xyGrid()
        r = np.sqrt((x - 0.5)**2 + (y - 0.5)**2)
        mask = (r <= self.r_th)
        sim.V[DN][mask] = self.rho1
        
        return
        
    # ---------------------------------------------------------------------------------------------

    def plotLimits(self, q_plot):

        vmin = []
        vmax = []

        for q in q_plot:
            if q == 'DN':
                vmin.append(self.rho0 * 0.9)
                vmax.append(self.rho1 * 1.05)
            elif q in ['VX', 'VY']:
                vmin.append(0.0)
                vmax.append(1.0)
            elif q == 'PR':
                vmin.append(self.P0 * 0.8)
                vmax.append(self.P0 * 1.2)
            else:
                vmin.append(None)
                vmax.append(None)
        
        return vmin, vmax, None

###################################################################################################
