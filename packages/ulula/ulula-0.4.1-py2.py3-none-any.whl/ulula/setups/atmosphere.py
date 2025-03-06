###################################################################################################
#
# This file is part of the ULULA code.
#
# (c) Benedikt Diemer, University of Maryland
#
###################################################################################################

import numpy as np 

import ulula.core.setup_base as setup_base
import ulula.physics.constants as constants

###################################################################################################

class SetupAtmosphere(setup_base.Setup):
    """
    Earth's hydrostratic atmosphere

    This setup represents the Earth's atmosphere in 1D, which settles into an exponential density
    and pressure profile (for an isothermal equation of state). The initial density is perturbed 
    away from the true solution by assuminh a "wrong" scale height. After some time, it settles to
    the correct solution. By default, the code units are set to kilometers, hours, and tons. This 
    setup demonstrates
    
    * Fixed-acceleration gravity with wall boundary conditions
    * Isothermal equation of state
    * Code units suitable to Earth conditions, including Earth gravity. 
    
    Depending on the initial conditions, this setup can be numerically unstable due to very strong
    motions that develop into shocks. For example, if too much mass is initially placed in the 
    upper atmosphere, that mass falls to the surface. Similarly, extending the upper limit to 
    much higher altitude than the default 30 km can lead to difficulties due to the very low
    pressure and density. 

    Parameters
    ----------
    unit_l: float
        Code unit for length in units of centimeters.
    unit_t: float
        Code unit for time in units of seconds.
    unit_m: float
        Code unit for mass in units of gram.
    T_K: float
        Air temperature in Kelvin.
    """
    
    def __init__(self, unit_l = 1E5, unit_t = 3600.0, unit_m = 1E12, T_K = 300.0):

        setup_base.Setup.__init__(self, unit_l = unit_l, unit_t = unit_t, unit_m = unit_m)
        
        # Chosen constants
        self.xmax = 30.0
        self.gamma = 7.0 / 5.0
        self.mu = constants.mu_air
        
        # Derive code units
        self.T_K = T_K
        self.rho0_cu = constants.rho_air_cgs / unit_m * unit_l**3
        self.g_cu = constants.g_earth_cgs / unit_l * unit_t**2
        self.eint_cu = self.internalEnergyFromTemperature(self.T_K, self.mu, self.gamma)
        
        print('Atmosphere setup: in code units, rho_air = %.2e, g = %.2e, eint = %.2e.' \
              % (self.rho0_cu, self.g_cu, self.eint_cu))
        
        return 

    # ---------------------------------------------------------------------------------------------

    def shortName(self):
        
        return 'atmosphere'

    # ---------------------------------------------------------------------------------------------
    
    def setInitialData(self, sim, nx):
        
        sim.setEquationOfState(eos_mode = 'isothermal', eint_fixed = self.eint_cu, 
                               gamma = self.gamma, mu = self.mu)
        sim.setGravityMode(gravity_mode = 'fixed_acc', g = self.g_cu)
        sim.setDomain(nx, 1, xmin = 0.0, xmax = self.xmax, bc_type = 'wall')

        DN = sim.q_prim['DN']
        x, _ = sim.xyGrid()

        # Compute the total mass in the true solution
        rho_true, h0 = self.hydrostaticDensity(x, sim)
        m_tot_sol = np.sum(rho_true)
        
        # Now create ICs that are offset from the true solution and normalize to the same total mass
        sim.V[DN] = self.rho0_cu * np.exp(-x / h0 * 0.5) 
        m_tot_ics = np.sum(sim.V[DN])
        sim.V[DN] *= m_tot_sol / m_tot_ics
        
        return
  
    # ---------------------------------------------------------------------------------------------

    # Since eint = kT / ((gamma - 1) mu mp), we have that h0 = kT g / mu mp = eint * (gamma - 1) / g
    
    def hydrostaticDensity(self, x, sim):
        
        h0 = self.eint_cu * (self.gamma - 1.0) / sim.gravity_g
        rho = self.rho0_cu * np.exp(-x / h0)
        
        return rho, h0
  
    # ---------------------------------------------------------------------------------------------

    def plotLimits(self, q_plot, plot_geometry):
        
        vmin = []
        vmax = []

        for q in q_plot:
            if q == 'DN':
                vmin.append(0.0)
                vmax.append(self.rho0_cu * 1.2)
            elif q in ['VX', 'VY']:
                vmin.append(-3E2)
                vmax.append(3E2)
            elif q in ['PR', 'ET']:
                vmin.append(0.0)
                vmax.append(self.rho0_cu * self.eint_cu * (self.gamma - 1.0) * 1.2)
            elif q == 'EI':
                vmin.append(0.0)
                vmax.append(self.eint_cu * (self.gamma - 1.0) * 1.2)
            else:
                vmin.append(None)
                vmax.append(None)
        
        return vmin, vmax, None

    # ---------------------------------------------------------------------------------------------

    def trueSolution(self, sim, x, q_plot, plot_geometry):
        
        rho_true, _ = self.hydrostaticDensity(x, sim)
        
        sol_list = []
        for i in range(len(q_plot)):
            q = q_plot[i]
            sol = np.zeros((len(x)), float)
            if q == 'DN':
                sol[:] = rho_true
            elif q == 'VX':
                sol[:] = 0.0
            elif q == 'PR': 
                sol[:] = rho_true * self.eint_cu * (self.gamma - 1.0)
            else:
                sol = None
            sol_list.append(sol)
        
        return sol_list

###################################################################################################
