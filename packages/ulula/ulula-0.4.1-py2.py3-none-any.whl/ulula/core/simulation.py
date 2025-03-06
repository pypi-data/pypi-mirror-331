###################################################################################################
#
# This file is part of the ULULA code.
#
# (c) Benedikt Diemer, University of Maryland
#
###################################################################################################

import numpy as np
import h5py

import ulula.utils.version as ulula_version
import ulula.utils.utils as utils

###################################################################################################

class HydroScheme():
    """
    Container class for hydro algorithms

    Parameters
    ----------
    reconstruction: string
        Reconstruction algorithm; see listing for valid choices
    limiter: string
        Slope limiter algorithm; see listing for valid choices
    riemann: string
        Riemann solver; see listing for valid choices
    time_integration: string
        Time integration scheme; see listing for valid choices
    cfl: float
        CFL number (must be between 0 and 1), which determines the maximum allowable timestep such 
        that the distance traveled by the maximum signal speed in the domain does not exceed the 
        CFL number times the size of a cell.
    cfl_max: float
        Maximum CFL number (must be between 0 and 1, and greater than ``cfl``). While each timestep
        is (typically) set to satisfy the CFL condition, each timestep actually consists of two
        sweeps in the two dimensions (x and y). Since the fluid state changes during the first 
        sweep, satisfying the CFL condition at first does not guarantee that it is still satisfied 
        during the second sweep. To avoid repeating the first sweep, we tolerate an actual, 
        updated CFL factor that is larger than ``cfl``, but it must still be smaller than
        ``cfl_max`` and smaller than unity, because exceeding unity will definitely break the hydro
        solver. Note, however, that setting ``cfl_max`` to a value close to unity (e.g., 0.99) may 
        still lead to instabilities. On the other hand, choosing ``cfl`` and ``cfl_max`` to be 
        close will mean that more timesteps need to be repeated, which slows down the code.
    cfl_reduce_factor: float
        If ``cfl_max`` is exceeded during the second sweep, we reduce the previous estimate of the
        timestep by this factor. Must be larger than unity.
    cfl_max_attempts: int
        If we still encounter a CFL violation after reducing the timestep, we keep doing so
        ``cfl_max_attempts`` times. After the last attempt, the simulation is aborted.
    """
    
    def __init__(self, reconstruction = 'linear', limiter = 'mc', riemann = 'hll', 
                time_integration = 'hancock', cfl = 0.8, 
                cfl_max = 0.95, cfl_reduce_factor = 1.2, cfl_max_attempts = 3):
        
        if (cfl >= 1.0):
            raise Exception('The CFL number must be smaller than 1.')
        if (cfl_max >= 1.0):
            raise Exception('The maximum CFL number must be smaller than 1.')
        if (cfl >= cfl_max):
            raise Exception('The maximum CFL number must be larger than the CFL number.')
        if (cfl_reduce_factor <= 1.0):
            raise Exception('The CFL reduction factor must be greater than 1.')

        self.reconstruction = reconstruction
        self.limiter = limiter
        self.riemann = riemann
        self.time_integration = time_integration
        self.cfl = cfl
        self.cfl_max = cfl_max
        self.cfl_reduce_factor = cfl_reduce_factor
        self.cfl_max_attempts = cfl_max_attempts
        
        return

###################################################################################################

class Simulation():
    """
    Main class for the Ulula hydro solver
    
    This class contains all simulation data and routines. The internal fields have the following 
    meaning (after the hydro scheme, domain, fluid properties, and initial conditions have been set):
    
    =======================  =====================
    Field                    Meaning
    =======================  =====================
    Domain and fluid variables
    ----------------------------------------------
    ``is_2d``                Whether we are running a 1D or 2D simulation
    ``dx``                   Width of cells (same in both x and y directions)
    ``nx``                   Number of cells in the x-direction
    ``ny``                   Number of cells in the y-direction
    ``nghost``               Number of ghost cells around each edge
    ``xlo``                  First index of physical grid in x-direction (without left ghost zone)
    ``xhi``                  Last index of physical grid in x-direction (without right ghost zone)
    ``ylo``                  First index of physical grid in y-direction (without bottom ghost zone)
    ``yhi``                  Last index of physical grid in y-direction (without top ghost zone)
    ``q_prim``               Dictionary containing the indices of the primitive fluid variables in the ``V`` array
    ``q_cons``               Dictionary containing the indices of the conserved fluid variables in the ``U`` array
    ``track_pressure``       Whether we need to explicitly track pressure
    ``nq_hydro``             Number of hydro fluid variables (typically 4 for rho, vx, vy, P)
    ``nq_all``               Total number of fluid variables (including gravitational pot.)
    ``bc_type``              Type of boundary condition ('periodic', 'outflow', 'wall')
    ``domain_set``           Once the domain is set, numerous settings cannot be changed any more
    -----------------------  ---------------------
    Hydro scheme and timestepping
    ----------------------------------------------
    ``hs``                   HydroScheme object
    ``use_source_term``      Whether any source terms are active (gravity etc.)
    ``t``                    Current time of the simulation
    ``step``                 Current step counter
    ``last_dir``             Direction of last sweep in previous timestep (x=0, y=1)
    -----------------------  ---------------------
    Equation of state
    ----------------------------------------------
    ``eos_mode``             Type of equation of state ('ideal', 'isothermal)
    ``eos_gamma``            Adiabatic index 
    ``eos_gm1``              gamma - 1
    ``eos_gm1_inv``          1 / (gamma - 1)
    ``eos_mu``               Mean particle mass in proton masses (can be None)
    ``eos_eint_fixed``       Fixed internal energy per unit mass (if isothermal)
    -----------------------  ---------------------
    Code units
    ----------------------------------------------
    ``unit_l``               Code unit length in centimeters
    ``unit_t``               Code unit time in seconds
    ``unit_m``               Code unit mass in grams
    -----------------------  ---------------------
    Gravity
    ----------------------------------------------
    ``gravity_mode``         Type of gravity ('none', 'fixed_acc', 'fixed_pot')
    ``gravity_g``            Gravitational acceleration (for mode 'fixed_acc')
    ``gravity_dir``          Direction of fixed acceleration (0 for x, 1 for y)
    -----------------------  ---------------------
    User-defined boundary conditions
    ----------------------------------------------
    ``do_user_updates``      True if the user has supplied a custom domain update function
    ``do_user_bcs``          True if the user has supplied a custom boundary condition function
    ``user_update_func``     A function to be called before the boundary conditions are enforced
    ``user_bc_func``         A function to be called after the boundary conditions are enforced
    -----------------------  ---------------------
    1D vectors
    ----------------------------------------------
    ``x``                    Array of x values at cell centers (dimensions [nx + 2 ng])
    ``y``                    Array of y values at cell centers (dimensions [ny + 2 ng])
    -----------------------  ---------------------
    3D vectors
    ----------------------------------------------
    ``U``                    Vector of conserved fluid variables (dimensions [nq, nx + 2 ng, ny + 2 ng])
    ``V``                    Vector of primitive fluid variables (dimensions [nq, nx + 2 ng, ny + 2 ng])
    ``V_im12``               Cell-edge states at left side (same dimensions as V)
    ``V_ip12``               Cell-edge states at right side (same dimensions as V)
    -----------------------  ---------------------
    Slices
    ----------------------------------------------
    ``slc1dL``               1D slices for idir [0, 1], physical domain, shifted one cell left
    ``slc1dR``               1D slices for idir [0, 1], physical domain, shifted one cell right
    ``slc1dC``               1D slices for idir [0, 1], physical domain
    ``slc3dL``               3D slices for idir [0, 1], physical domain, shifted one cell left
    ``slc3dR``               3D slices for idir [0, 1], physical domain, shifted one cell right
    ``slc3dC``               3D slices for idir [0, 1], physical domain
    ``slc3aL``               3D slices for idir [0, 1], total domain, shifted one cell left
    ``slc3aR``               3D slices for idir [0, 1], total domain, shifted one cell right
    ``slc3aC``               3D slices for idir [0, 1], total domain
    ``slc3fL``               3D slice of flux vector from left interface
    ``slc3fR``               3D slice of flux vector from right interface    
    =======================  =====================
    
    The constructor takes the following parameters:
    
    Parameters
    ----------
    hydro_scheme: HydroScheme
        Container class for algorithmic choices
    """

    def __init__(self):

        # The domain has not yet been set, which will be checked in functions below.    
        self.domain_set = False

        # Set all settings to their defaults
        self.setHydroScheme()
        self.setEquationOfState()
        self.setCodeUnits()
        self.setGravityMode()
        self.setUserBoundaryConditions()
        
        return
    
    # ---------------------------------------------------------------------------------------------

    def setHydroScheme(self, hydro_scheme = None):
        """
        Set the hydro solver scheme
        
        This function must be executed before the :func:`~ulula.core.simulation.Simulation.setDomain` 
        function.
        
        Parameters
        ----------
        hydro_scheme: HydroScheme
            :class:`HydroScheme` object that contains the settings for the hydro solver.
        """
    
        if self.domain_set:
            raise Exception('The setHydroScheme() function must be called before setDomain().')
    
        if hydro_scheme is None:
            hydro_scheme = HydroScheme()
        self.hs = hydro_scheme
    
        # Set functions based on reconstruction scheme. If we are reconstructing, we need two
        # ghost zones instead of one due to slope calculations.
        if self.hs.reconstruction == 'const':
            self.reconstruction = self.reconstructionConst
            self.nghost = 1
        elif self.hs.reconstruction == 'linear':
            self.reconstruction = self.reconstructionLinear
            self.nghost = 2
        else:
            raise Exception('Unknown reconstruction scheme, %s.' % (self.hs.reconstruction))

        # Set limiter
        if self.hs.limiter == 'none':
            self.limiter = self.limiterNone
        elif self.hs.limiter == 'minmod':
            self.limiter = self.limiterMinMod
        elif self.hs.limiter == 'vanleer':
            self.limiter = self.limiterVanLeer
        elif self.hs.limiter == 'mc':
            self.limiter = self.limiterMC
        else:
            raise Exception('Unknown limiter, %s.' % (self.hs.limiter))
        
        # Set functions related to Riemann solver        
        if self.hs.riemann == 'hll':
            self.riemannSolver = self.riemannSolverHLL
        elif self.hs.riemann == 'hllc':
            self.riemannSolver = self.riemannSolverHLLC
        else:
            raise Exception('Unknown Riemann solver, %s.' % self.hs.riemann)

        # Check the time integration scheme for invalid values    
        if not self.hs.time_integration in ['euler', 'hancock', 'hancock_cons']:
            raise Exception('Unknown time integration scheme, %s.' % self.hs.time_integration)

        return
    
    # ---------------------------------------------------------------------------------------------

    def setEquationOfState(self, eos_mode = 'ideal', gamma = 5.0 / 3.0, mu = None, eint_fixed = None):
        """
        Choose an equation of state
        
        The equation of state (EOS) captures the microphysics of the gas that is being simulated.
        This function must be executed before the :func:`~ulula.core.simulation.Simulation.setDomain` 
        function.
        
        The default is an ideal gas EOS with :math:`\\gamma = 5/3`. If an isothermal EOS is chosen,
        the fixed temperature must be specified as an internal energy per unit mass, which can be
        computed from temperature using the 
        :func:`~ulula.core.setup_base.Setup.internalEnergyFromTemperature` function.
        
        Parameters
        ----------
        eos_mode: str
            Can be ``ideal`` or ``isothermal``.
        gamma: float
            Adiabatic index of the ideal gas to be simulated; should be 5/3 for atomic gases or
            7/5 for diatomic molecular gases.
        mu: float
            Mean particle mass in units of proton masses. Must be specified if temperature is to 
            be plotted, regardless of the EOS.
        eint_fixed: float
            A fixed internal energy per unit mass in code units for an isothermal EOS, ignored
            otherwise.
        """

        if self.domain_set:
            raise Exception('The setEquationOfState() function must be called before setDomain().')
    
        self.eos_mode = eos_mode
        self.eos_gamma = gamma
        self.eos_mu = mu
        
        self.eos_gm1 = self.eos_gamma - 1.0
        self.eos_gm1_inv = 1.0 / self.eos_gm1
    
        # To avoid repeated string comparisons, we set the track_pressure field which indicates 
        # whether we need to explicitly track pressure and energy in the code. In practice, we 
        # assume an ideal equation of state if track_pressure == True and an isothermal one if 
        # track_pressure == False because those are the only EOSs implemented.
        if self.eos_mode == 'ideal':
            self.track_pressure = True
            self.eos_eint_fixed = None
            self.eos_T_fixed = None
        elif self.eos_mode == 'isothermal':
            if eint_fixed is None:
                raise Exception('In isothermal EOS mode, eint_fixed must be set.')
            self.eos_eint_fixed = eint_fixed
            self.track_pressure = False
        else:
            raise Exception('Unknown EOS mode, %s.' % (eos_mode))
    
        return
    
    # ---------------------------------------------------------------------------------------------

    def setCodeUnits(self, unit_l = 1.0, unit_t = 1.0, unit_m = 1.0):
        """
        Define the meaning of the internal units
        
        The pure Euler equations (i.e., ignoring viscosity, cooling, etc.) are invariant under 
        multiplications of up to three scale quantities, meaning that the solution of a hydro 
        problem remains unchanged independent of what physical length, time, and mass scales the 
        given numbers represent. One can alternatively think of rescalings in other, combined 
        quantities such as density, pressure, and so on. 

        This function lets the user define the meaning of the internal length, time, and mass 
        scales. The solution will not change unless the problem in question depends on physics 
        beyond the pure Euler equations, such as gravity, cooling, and so on. As a result, the 
        values of the code units are not used at all in the simulation class. However, plots of 
        the solution will change if a unit system other than code units is used.
        
        The code units are given in cgs units. Some common units are defined in the 
        :mod:`~ulula.physics.units` module. For example, to set time units of years, 
        ``unit_t = units.units_t['yr']['in_cgs']``. However, the code units can take on any 
        positive, non-zero number chosen by the user.
        
        This function must be executed before the :func:`~ulula.core.simulation.Simulation.setDomain` 
        function.
        
        Parameters
        ----------
        unit_l: float
            Code unit for length in units of centimeters.
        unit_t: float
            Code unit for time in units of seconds.
        unit_m: float
            Code unit for mass in units of gram.
        """

        if self.domain_set:
            raise Exception('The setCodeUnits() function must be called before setDomain().')
        
        self.unit_l = unit_l
        self.unit_t = unit_t
        self.unit_m = unit_m
        
        return

    # ---------------------------------------------------------------------------------------------

    def setGravityMode(self, gravity_mode = 'none', g = 1.0, gravity_dir = 1, compute_gradients = True):
        """
        Add gravity to the simulation
        
        This function must be executed before the :func:`~ulula.core.simulation.Simulation.setDomain` 
        function. If the user chooses the ``fixed_acc`` mode, an acceleration ``g`` must be set,
        which acts in the negative x or y direction. The potential and gradients are 
        computed automatically.
        
        If the chosen mode is ``fixed_pot``, the user must subsequently set the initial
        potential at the same time as the other initial conditions (in primitive variables).
        
        Afterwards, the function :func:`~ulula.core.simulation.Simulation.setGravityPotentials` must be
        called to propagate the information. If the ``fixed_pot`` mode and ``compute_gradients``
        are chosen, this function computes the spatial gradients of the user-defined potential.
        Otherwise, the user needs to set them manually. The latter can be more accurate if the 
        analytical form of the gradients is known.

        Parameters
        ----------
        gravity_mode: str
            The type of gravity to be added. Can be ``fixed_acc`` or ``fixed_pot``.
        g: float
            If ``gravity_mode == 'fixed_acc'``, then ``g`` gives the constant acceleration in code
            units.
        gravity_dir: int
            The direction of a fixed acceleration, 0 meaning x and 1 meaning y. For a 1D 
            simulation, the direction is forced to be x. For a 2D simulation, the direction is 
            typically 1 (y) so that gravity points downwards.
        compute_gradients: bool
            If ``gravity_mode == 'fixed_pot'``, this parameter determines whether spatial gradients
            will be automatically computed or must be set by the user.
        """

        if self.domain_set:
            raise Exception('The setGravityMode() function must be called before setDomain().')
        if not gravity_mode in ['none', 'fixed_acc', 'fixed_pot']:
            raise Exception('Unknown gravity mode, %s.' % (gravity_mode))
        
        self.gravity_mode = gravity_mode
        self.gravity_g = g
        if not gravity_dir in [0, 1]:
            raise Exception('Invalid direction for gravity (%d), must be 0 (x) or 1 (y).' % (gravity_dir))
        self.gravity_dir = gravity_dir
        self.gravity_compute_gradients = compute_gradients
        self.use_source_terms = (self.gravity_mode != 'none')
        
        return

    # ---------------------------------------------------------------------------------------------

    def setUserUpdateFunction(self, user_update_func = None):
        """
        Set user-defined updates in the domain
        
        If a function is passed for ``user_update_func``, that function will be called with the 
        simulation object as an argument before boundary conditions are enforced. This 
        mechanism allows the phyiscal setup to influence the simulation while it is running, while
        the boundary conditions are still automatically enforced.
        
        The code does not check whether what this function does makes any sense! If the function
        implements unphysical behavior, an unphysical simulation will result. The user-supplied
        function must ensure that primitive and conserved variables are consistent after the 
        function call.

        Parameters
        ----------
        user_update_func: func
            Function pointer that takes the simulation object as an argument.
        """
        
        self.user_update_func = user_update_func
        self.do_user_updates = (self.user_update_func is not None)
        
        return

    # ---------------------------------------------------------------------------------------------

    def setUserBoundaryConditions(self, user_bc_func = None):
        """
        Set user-defined boundary conditions
        
        If a function is passed for ``user_bc_func``, that function will be called with the 
        simulation object as an argument every time boundary conditions are enforced. This 
        mechanism allows the phyiscal setup to influence the simulation while it is running, most
        commonly by implementing custom boundary conditions. For example, by supplying a
        time-dependent density and pressure, the user can create a wave.
        
        The code does not check whether what this function does makes any sense! If the function
        implements unphysical behavior, an unphysical simulation will result. The user-supplied
        function must ensure that primitive and conserved variables are consistent after the 
        function call.

        Parameters
        ----------
        user_bc_func: func
            Function pointer that takes the simulation object as an argument.
        """
        
        self.user_bc_func = user_bc_func
        self.do_user_bcs = (self.user_bc_func is not None)
        
        return

    # ---------------------------------------------------------------------------------------------

    def setDomain(self, nx, ny, xmin = 0.0, xmax = 1.0, ymin = 0.0, bc_type = 'periodic'):
        """
        Set the physical and numerical size of the domain
        
        This function creates the memory structure for the simulation as well as pre-computed 
        slices that index the arrays.

        Parameters
        ----------
        nx: int
            Number of grid points in x-direction; must be at least 2.
        ny: int
            Number of grid points in y-direction; choosing ``ny = 1`` leads to a 1D simulation.
        xmin: float
            Left edge in physical coordinates (code units)
        xmax: float
            Right edge in physical coordinates (code units)
        ymin: float
            Bottom edge in physical coordinates (code units)
        ymax: float
            Top edge in physical coordinates (code units)
        bc_type: string
            Type of boundary conditions; can be ``periodic`` or ``outflow``
        """

        # Make sure choices set so far have been consistent
        if (self.hs.riemann == 'hllc') and (not self.track_pressure):
            raise Exception('Cannot combine HLLC Riemann solver and isothermal EOS; use HLL instead.')

        # Compute dimensions. We ensure that the domain spans integer numbers of cells in each
        # dimension.
        if not isinstance(nx, int):
            raise Exception('Got nx = %s, expected integer.' % (str(nx)))
        if not isinstance(ny, int):
            raise Exception('Got ny = %s, expected integer.' % (str(ny)))
        if nx < 2:
            raise Exception('Got nx = %d, must be at least 2.' % (nx))
        if ny < 1:
            raise Exception('Got ny = %d, expected a positive number.' % (ny))
        
        self.nx = nx
        self.xmin = xmin
        self.xmax = xmax
        self.dx = (xmax - xmin) / float(nx)
        
        self.ny = ny
        self.ymin = ymin
        self.ymax = self.ymin + ny * self.dx
        
        print('Grid setup %d x %d, dimensions x = [%.2e .. %.2e] y =  [%.2e .. %.2e]' \
            % (self.nx, self.ny, self.xmin, self.xmax, self.ymin, self.ymax))

        # Set indices for lower and upper domain boundaries. If the domain is 1D, we do not create 
        # ghost cells in the y-direction.
        self.is_2d = (ny > 1)
        ng = self.nghost
        self.xlo = ng
        self.xhi = ng + self.nx - 1
        self.nx_tot = self.nx + 2 * ng
        self.x = xmin + (np.arange(self.nx_tot) - ng) * self.dx + 0.5 * self.dx
        
        if self.is_2d:
            self.ylo = ng
            self.yhi = ng + self.ny - 1
            self.ny_tot = self.ny + 2 * ng
            self.y = ymin + (np.arange(self.ny_tot) - ng) * self.dx + 0.5 * self.dx
        else:
            self.ylo = 0
            self.yhi = 1
            self.ny_tot = 1
            self.y = np.array([ymin + 0.5 * self.dx])

        self.bc_type = bc_type

        # Create the indexing of the variable vectors. This should be kept general so that code 
        # extensions can change the length or ordering of the vectors if necessary. We store the
        # indices of the primitive and conserved fields in dictionaries, which can be used by 
        # routines such as plotting. Density and velocity/momentum are always necessary.
        self.q_prim = {}
        self.q_cons = {}

        idx = 0
        self.DN = self.MS = idx
        self.q_prim['DN'] = self.DN
        self.q_cons['MS'] = self.DN
        
        idx += 1
        self.VX = self.MX = idx
        self.q_prim['VX'] = self.VX
        self.q_cons['MX'] = self.MX

        idx += 1
        self.VY = self.MY = idx
        self.q_prim['VY'] = self.VY
        self.q_cons['MY'] = self.MY
        
        # Pressure and energy can be computed from density for a barotropic EOS, so the pressure
        # and conserved energy fields only exist for non-barotropic EOSs.
        if self.track_pressure:
            idx += 1
            self.PR = self.ET = idx
            self.q_prim['PR'] = self.PR
            self.q_cons['ET'] = self.ET

        # Record the length of the hydro variable vector, without any gravitational potentils        
        self.nq_hydro = len(self.q_prim)
        nqh = self.nq_hydro
        self.nq_cpy = self.nq_hydro
        
        # For gravity, we add a potential field.
        self.GP = self.GX = self.GY = None
        if self.gravity_mode == 'none':
            pass
        else:
            idx += 1
            self.GP = idx
            self.q_prim['GP'] = self.GP
            self.q_cons['GP'] = self.GP
            if self.gravity_mode == 'fixed_acc':
                pass
            elif self.gravity_mode == 'fixed_pot':
                idx += 1
                self.GX = idx
                self.q_prim['GX'] = self.GX
                self.q_cons['GX'] = self.GX
                idx += 1
                self.GY = idx
                self.q_prim['GY'] = self.GY
                self.q_cons['GY'] = self.GY
            else:
                raise Exception('Unknown type of gravity, %s.' % (self.gravity_mode))
        
        # Record the length of the total vector of variables
        self.nq_all = len(self.q_prim)

        # Storage for the primitive and conserved fluid variables and other arrays. We create a
        # duplicate backup array for each where the solution at the beginning of a timestep is 
        # stored so that we can restore it if an error occurs.
        self.U = self.emptyArray()
        self.V = self.emptyArray()
        self.U_cpy = self.emptyArray()
        self.V_cpy = self.emptyArray()
    
        # Storage for the cell-edge states and conservative fluxes. If we are using 
        # piecewise-constant, both states are the same (and the same as the cell centers).
        if self.hs.reconstruction == 'const':
            self.V_im12 = self.V
            self.V_ip12 = self.V
        elif self.hs.reconstruction == 'linear':
            self.V_im12 = self.emptyArray()
            self.V_ip12 = self.emptyArray()
        else:
            raise Exception('Unknown reconstruction scheme, %s.' % (self.hs.reconstruction))
        
        # Set up slices that can be reused. The names are slc<dims><daf><LRC> which means the
        # dimensionality of the slice (1, 2, 3), whether it covers the physical domain (d), the
        # entire domain including ghost cells (a), or the flux vector (f), and whether it selects
        # the cells (C), there left (L) or right (R) neighbors. The flux-related masks include only
        # hydro variables but not gravitational potentials.
        self.slc1dL = []
        self.slc1dR = []
        self.slc1dC = []

        self.slc3dL = []
        self.slc3dR = []
        self.slc3dC = []

        self.slc3aL = []
        self.slc3aR = []
        self.slc3aC = []

        self.slc3fL = []
        self.slc3fR = []
            
        for idir in range(2):
            
            if idir == 0:
                lo = self.xlo
                hi = self.xhi
            else:
                lo = self.ylo
                hi = self.yhi
                
            slc1dL = slice(lo - 1, hi + 1)
            slc1dR = slice(lo, hi + 2)
            slc1dC = slice(lo, hi + 1)
            
            if idir == 0:
                slc3dL = (slice(None),   slc1dL,         slice(None))
                slc3dR = (slice(None),   slc1dR,         slice(None))
                slc3dC = (slice(0, nqh), slc1dC,         slice(None))

                slc3aL = (slice(None),   slice(0, -2),   slice(None))
                slc3aR = (slice(None),   slice(2, None), slice(None))
                slc3aC = (slice(None),   slice(1, -1),   slice(None))
                
                slc3fL = (slice(0, nqh), slice(0, -1),   slice(None))
                slc3fR = (slice(0, nqh), slice(1, None), slice(None))
            else:
                slc3dL = (slice(None),   slice(None), slc1dL)
                slc3dR = (slice(None),   slice(None), slc1dR)
                slc3dC = (slice(0, nqh), slice(None), slc1dC)

                slc3aL = (slice(None),   slice(None), slice(0, -2))
                slc3aR = (slice(None),   slice(None), slice(2, None))
                slc3aC = (slice(None),   slice(None), slice(1, -1))
                
                slc3fL = (slice(0, nqh), slice(None), slice(0, -1))
                slc3fR = (slice(0, nqh), slice(None), slice(1, None))
            
            self.slc1dL.append(slc1dL)
            self.slc1dR.append(slc1dR)
            self.slc1dC.append(slc1dC)
            
            self.slc3dL.append(slc3dL)
            self.slc3dR.append(slc3dR)
            self.slc3dC.append(slc3dC)

            self.slc3aL.append(slc3aL)
            self.slc3aR.append(slc3aR)
            self.slc3aC.append(slc3aC)
            
            self.slc3fL.append(slc3fL)
            self.slc3fR.append(slc3fR)
        
        # Time
        self.t = 0.0
        self.step = 0
        self.last_dir = -1
        
        # We are done setting up the domain. After this point, the fundamental settings cannot be
        # changed any more.
        self.domain_set = True
        
        return
    
    # ---------------------------------------------------------------------------------------------
    
    def emptyArray(self, nq = None):
        """
        Get an empty array for fluid variables

        Parameters
        ----------
        nq: int
            The number of quantities for which the array should contain space. If ``None``, the
            number of fluid quantities is used (4 in two dimensions).

        Returns
        -------
        ret: array_like
            Float array of size nq times the size of the domain including ghost cells. If 
            ``nq == 1``, the first dimension is omitted.
        """
            
        if nq is None:
            nq = self.nq_all
            
        if nq == 1:
            ret = np.zeros((self.nx_tot, self.ny_tot), float)
        else:
            ret = np.zeros((nq, self.nx_tot, self.ny_tot), float)
            
        return ret 

    # ---------------------------------------------------------------------------------------------

    def xyGrid(self):
        """
        Get a grid of the x and y cell center positions
        
        This function returns two arrays with the x and y positions at each grid point. These 
        arrays can be convenient when setting the initial conditions.

        Returns
        -------
        x: array_like
            2D array with x positions of all cells (including ghost cells)
        y: array_like
            2D array with x positions of all cells (including ghost cells)
        """
    
        return np.meshgrid(self.x, self.y, indexing = 'ij')

    # ---------------------------------------------------------------------------------------------

    def setGravityPotentials(self):
        """
        Prepare gravitational potentials
        
        This function must be executed after the :func:`~ulula.core.simulation.Simulation.setDomain` 
        function. If the gravity mode is ``fixed_acc``, we automatically compute the potential.
        If it is ``fixed_pot``, we expect that the user has set the potential and possibly the 
        spatial gradients; if not, we compute them.
        
        If the simulation is 1D, we interpret a constant acceleration as pointing to the negative
        x-direction, otherwise in the negative y-direction.
        """
        
        if self.gravity_mode == 'none':
            fields_cpy = []
        
        elif self.gravity_mode == 'fixed_acc':
            x, y = self.xyGrid()
            if not self.is_2d:
                self.gravity_dir = 0
            if self.gravity_dir == 0:
                self.V[self.GP] = self.gravity_g * x
            else:
                self.V[self.GP] = self.gravity_g * y
            fields_cpy = [self.GP]
            
        elif self.gravity_mode == 'fixed_pot':
            if self.gravity_compute_gradients:
                self.V[self.GX, 1:-1, :] = (self.V[self.GP, 2:, :] - self.V[self.GP, :-2, :]) / (2.0 * self.dx)
                if self.is_2d:
                    self.V[self.GY, :, 1:-1] = (self.V[self.GP, :, 2:] - self.V[self.GP, :, :-2]) / (2.0 * self.dx)                
            fields_cpy = [self.GP, self.GX]
            if self.is_2d:
                fields_cpy.append(self.GY)

        else:
            raise Exception('Unknown type of gravity, %s.' % (self.gravity_mode))

        for f in fields_cpy:
            self.U[f, ...] = self.V[f, ...]
            self.V_cpy[f, ...] = self.V[f, ...]
            self.U_cpy[f, ...] = self.V[f, ...]
            
        return

    # ---------------------------------------------------------------------------------------------
    
    def enforceBoundaryConditions(self):
        """
        Enforce boundary conditions after changes
        
        This function fills the ghost cells with values from the physical domain to achieve certain
        behaviors. This function must be executed at each timestep. In particular:

        * Periodic: cells are rolled over from the other side of the domain so that it looks to the
          hydro solver as if the domain just continues on the other side.
        * Outflow: we take the value of the physical cells at the edge and copy them into the 
          adjacent ghost cells, leading to flows that just continue across the edge.
        * Wall: the goal is to ensure that no mass or energy flux moves across the boundary. We 
          achieve this condition by setting the ghost cells to a mirror image of the adjacent cells
          in the domain and inverting the perpendicular velocity, creating a counter-flow that 
          balances any motion onto the edge.
        """
        
        if self.do_user_updates:
            self.user_update_func(self)

        xlo = self.xlo
        xhi = self.xhi
        ylo = self.ylo
        yhi = self.yhi
        ng = self.nghost
        slc_x = self.slc1dC[0]
        slc_y = self.slc1dC[1]
        is_2d = self.is_2d
        nqh = self.nq_hydro
        
        for v in [self.V, self.U]:
            
            if self.bc_type == 'periodic':
                # Left/right ghost
                v[:nqh, 0:ng, slc_y] = v[:nqh, xhi-ng+1:xhi+1, slc_y]        
                v[:nqh, -ng:, slc_y] = v[:nqh, xlo:xlo+ng,     slc_y]
                if is_2d:
                    # Bottom/top ghost
                    v[:nqh, slc_x, 0:ng] = v[:nqh, slc_x, yhi-ng+1:yhi+1]        
                    v[:nqh, slc_x, -ng:] = v[:nqh, slc_x,     ylo:ylo+ng]
                    # Corners
                    v[:nqh, 0:ng,  0:ng] = v[:nqh, xhi-ng+1:xhi+1, yhi-ng+1:yhi+1]
                    v[:nqh, 0:ng,  -ng:] = v[:nqh, xhi-ng+1:xhi+1, ylo:ylo+ng]
                    v[:nqh, -ng:,  0:ng] = v[:nqh, xlo:xlo+ng,     yhi-ng+1:yhi+1]
                    v[:nqh, -ng:,  -ng:] = v[:nqh, xlo:xlo+ng,     ylo:ylo+ng]
            
            elif self.bc_type == 'outflow':
                # Left/right ghost
                v[:nqh, 0:ng, slc_y] = v[:nqh, xlo, slc_y][:, None, :]
                v[:nqh, -ng:, slc_y] = v[:nqh, xhi, slc_y][:, None, :]
                if is_2d:
                    # Bottom/top ghost
                    v[:nqh, slc_x, 0:ng] = v[:nqh, slc_x, ylo][:, :, None]
                    v[:nqh, slc_x, -ng:] = v[:nqh, slc_x, yhi][:, :, None]
                    # Corners
                    v[:nqh, 0:ng, 0:ng]  = v[:nqh, xlo, ylo][:, None, None]
                    v[:nqh, 0:ng, -ng:]  = v[:nqh, xlo, yhi][:, None, None]
                    v[:nqh, -ng:, 0:ng]  = v[:nqh, xhi, ylo][:, None, None]
                    v[:nqh, -ng:, -ng:]  = v[:nqh, xhi, yhi][:, None, None]

            elif self.bc_type == 'wall':
                # Left/right ghost
                v[:nqh, 0:ng, slc_y] = v[:nqh, xlo+ng-1:xlo-1:-1, slc_y]
                v[:nqh, -ng:, slc_y] = v[:nqh, xhi:xhi-ng:-1,     slc_y]
                if is_2d:
                    # Bottom/top ghost
                    v[:nqh, slc_x, 0:ng] = v[:nqh, slc_x, ylo+ng-1:ylo-1:-1]
                    v[:nqh, slc_x, -ng:] = v[:nqh, slc_x, yhi:yhi-ng:-1]
                    # Corners
                    v[:nqh, 0:ng, 0:ng]  = v[:nqh, xlo+ng-1:xlo-1:-1, ylo+ng-1:ylo-1:-1]
                    v[:nqh, 0:ng, -ng:]  = v[:nqh, xlo+ng-1:xlo-1:-1, yhi:yhi-ng:-1]
                    v[:nqh, -ng:, 0:ng]  = v[:nqh, xhi:xhi-ng:-1,     ylo+ng-1:ylo-1:-1]
                    v[:nqh, -ng:, -ng:]  = v[:nqh, xhi:xhi-ng:-1,     yhi:yhi-ng:-1]
                # Invert velocities
                v[self.VX, 0:ng, :] *= -1
                v[self.VX, -ng:, :] *= -1
                if is_2d:
                    v[self.VY, :, 0:ng] *= -1
                    v[self.VY, :, -ng:] *= -1
                
            else:
                raise Exception('Unknown type of boundary condition, %s.' % (self.bc_type))
        
        if self.do_user_bcs:
            self.user_bc_func(self)
        
        return

    # ---------------------------------------------------------------------------------------------

    def primitiveToConserved(self, V, U):
        """
        Convert primitive to conserved variables
        
        This function takes the input and output arrays as parameters instead of assuming that it
        should use the main V and U arrays. In some cases, conversions need to be performed on 
        other fluid states.

        Parameters
        ----------
        V: array_like
            Input array of primitive fluid variables with first dimension nq (rho, vx, vy, P...)
        U: array_like
            Output array of fluid variables with first dimension nq (rho, u * vx...)
        """
                            
        rho = V[self.DN]
        ux = V[self.VX]
        uy = V[self.VY]
        
        U[self.MS] = rho
        U[self.MX] = ux * rho
        U[self.MY] = uy * rho        

        if self.track_pressure:
            U[self.ET] = 0.5 * (ux**2 + uy**2) * rho + V[self.PR] * self.eos_gm1_inv
            if self.gravity_mode != 'none':
                U[self.ET] += rho * V[self.GP]
            
        return

    # ---------------------------------------------------------------------------------------------
    
    def primitiveToConservedRet(self, V):
        """
        Convert primitive to new conserved array
        
        Same as :func:`primitiveToConserved`, but creating the conserved output array.

        Parameters
        ----------
        V: array_like
            Input array of primitive fluid variables with first dimension nq (rho, vx, vy, P...)

        Returns
        -------
        U: array_like
            Array of fluid variables with first dimension nq (rho, u * vx...) and same dimensions as
            input array.
        """
        
        U = np.zeros_like(V)

        if self.gravity_mode != 'none':
            U[self.GP, ...] = V[self.GP, ...]
            
        self.primitiveToConserved(V, U)
        
        return U

    # ---------------------------------------------------------------------------------------------
    
    def conservedToPrimitive(self, U, V):
        """
        Convert conserved to primitive variables
        
        This function takes the input and output arrays as parameters instead of assuming that it
        should use the main U and V arrays. In some cases, conversions need to be performed on 
        other fluid states.

        Parameters
        ----------
        U: array_like
            Input array of conserved fluid variables with first dimension nq (rho, u * vx...)
        V: array_like
            Output array of primitive fluid variables with first dimension nq (rho, vx, vy, P...)
        """

        rho = U[self.DN]
        ux = U[self.MX] / rho
        uy = U[self.MY] / rho
        
        V[self.DN] = rho
        V[self.VX] = ux
        V[self.VY] = uy
        
        if self.track_pressure:
            e_int_rho = U[self.ET] - 0.5 * rho * (ux**2 + uy**2)
            if self.gravity_mode != 'none':
                e_int_rho -= rho * U[self.GP]
            V[self.PR] = e_int_rho * self.eos_gm1
    
            if np.min(V[self.PR]) <= 0.0:
                raise Exception('Zero or negative pressure found. Aborting.')
            
        return

    # ---------------------------------------------------------------------------------------------

    def fluxVector(self, idir, V, F = None):
        """
        Convert the flux vector F(V)
        
        The flux of the conserved quantities density, momentum, and total energy as a function of 
        a primitive fluid state.

        Parameters
        ----------
        idir: int
            Direction of sweep (0 = x, 1 = y)
        V: array_like
            Input array of primitive fluid variables with first dimension nq (rho, vx, vy, P...)

        Returns
        -------
        F: array_like
            Array of fluxes with first dimension nq and same dimensions as input array.
        """

        if F is None:
            F = np.zeros_like(V)

        DN = self.DN
        VX = self.VX
        idir2 = (idir + 1) % 2
        
        rho = V[DN]
        u1 = V[VX + idir]
        u2 = V[VX + idir2]
        rho_u1 = rho * u1
        
        if self.track_pressure:
            P = V[self.PR]
            etot = 0.5 * rho * (u1**2 + u2**2) + P * self.eos_gm1_inv
            if self.gravity_mode != 'none':
                etot += rho * V[self.GP]
        else:
            P = rho * self.eos_eint_fixed * self.eos_gm1
            
        F[DN] = rho_u1
        F[VX + idir] = rho_u1 * u1 + P
        F[VX + idir2] = rho_u1 * u2
        if self.track_pressure:
            F[self.ET] = (etot + P) * u1
        
        return F

    # ---------------------------------------------------------------------------------------------

    def primitiveEvolution(self, idir, V, dV_dx):
        """
        Linear approximation of the Euler equations
        
        Instead of the conservation-law form, we can also think of the Euler equations as 
        :math:`dV/dt + A(V) dV/dx = S`. This function returns :math:`\\Delta V/ \\Delta t` given an
        input state and a vector of spatial derivatives :math:`\\Delta V/ \\Delta x`. The result is
        used in the Hancock step.

        Parameters
        ----------
        idir: int
            Direction of sweep (0 = x, 1 = y)
        V: array_like
            Array of primitive fluid variables with first dimension nq (rho, vx, vy, P...)
        dV_dx: array_like
            Array of derivative of fluid variables with first dimension nq

        Returns
        -------
        dV_dt: array_like
            Array of linear approximation to time evolution of fluid variables, with same dimensions
            as input arrays.
        """
        
        DN = self.DN
        VX = self.VX

        idir2 = (idir + 1) % 2
        V1 = VX + idir
        V2 = VX + idir2

        if self.track_pressure:
            PR = self.PR
            dP_dx = dV_dx[PR]
        else:
            dP_dx = dV_dx[DN] * self.eos_eint_fixed * self.eos_gm1
        
        dV_dt = np.zeros_like(dV_dx)
        dV_dt[DN] = -(V[V1] * dV_dx[DN] + dV_dx[V1] * V[DN])
        dV_dt[V1] = -(V[V1] * dV_dx[V1] + dP_dx / V[DN])
        dV_dt[V2] = -(V[V1] * dV_dx[V2])
        if self.track_pressure:
            dV_dt[PR] = -(V[V1] * dP_dx + dV_dx[V1] * V[PR] * self.eos_gamma)

        return dV_dt

    # ---------------------------------------------------------------------------------------------

    def soundSpeed(self, V):
        """
        Sound speed
        
        Parameters
        ----------
        V: array_like
            Input array of primitive fluid variables with first dimension nq (rho, vx, vy, P...)

        Returns
        -------
        cs: array_like
            Array of sound speed with first dimension nq and same dimensions as input array.
        """

        if self.eos_mode == 'ideal':
            cs = np.sqrt(self.eos_gamma * V[self.PR] / V[self.DN])
        elif self.eos_mode == 'isothermal':
            cs = np.ones_like(V[self.DN]) * np.sqrt(self.eos_eint_fixed * self.eos_gm1)
        else:
            raise Exception('Unknown EOS mode, %s.' % (self.eos_mode))
        
        if np.any(np.isnan(cs)):
            raise Exception('Encountered invalid inputs while computing sound speed (input min DN %.2e, min PR %.2e). Try reducing the CFL number.' \
                        % (np.min(V[self.DN]), np.min(V[self.PR])))
        
        return cs

    # ---------------------------------------------------------------------------------------------

    def maxSpeedInDomain(self):
        """
        Largest signal speed in domain
        
        This function returns the largest possible signal speed anywhere in the domain. It
        evaluates the sound speed and adds it to the absolute x and y velocities. We do not need to
        add those velocities in quadrature since we are taking separate sweeps in the x and y 
        directions. Thus, the largest allowed timestep is determined by the largest speed in 
        either direction.
        
        Parameters
        ----------
        V: array_like
            Input array of primitive fluid variables with first dimension nq (rho, vx, vy, P...)

        Returns
        -------
        c_max: float
            Largest possible signal speed in the domain.
        """
        
        cs = self.soundSpeed(self.V)
        c_max = np.max(np.maximum(np.abs(self.V[self.VX]), np.abs(self.V[self.VY])) + cs)
        
        if np.isnan(c_max):
            raise Exception('Could not compute fastest speed in domain. Aborting.')
        
        return c_max

    # ---------------------------------------------------------------------------------------------

    def reconstructionConst(self, idir, dt):
        """
        Piecewise-constant reconstruction
        
        Piecewise-constant means no reconstruction. The left/right cell edge value arrays are already
        set to the cell-centered values so that this function does nothing at all. It serves as a 
        placeholder to which the reconstruction function pointer can be set.
        
        Parameters
        ----------
        idir: int
            Direction of sweep (0 = x, 1 = y)
        dt: float
            Timestep
        """
        
        return

    # ---------------------------------------------------------------------------------------------

    def reconstructionLinear(self, idir, dt):
        """
        Piecewise-linear reconstruction
        
        This function creates left and right cell-edge states based on the cell-centered states. It
        first computes the left and right slopes, uses a slope limiter to determine the limited
        slope to use, and interpolates linearly within each cell.
        
        If the time integration scheme is Hancock, the reconstructed edge states are also advanced
        by half a timestep to get 2nd-order convergence in the flux calculation. There are two ways 
        to perform the Hancock step. The more conventionally described way is to take the fluxes 
        according to the L/R states as an approximation for the flux differential across the cell 
        (the ``hancock_cons`` integration scheme). The differential is then used to updated the 
        conserved cell-edge states. However, this method necessitates a 
        primitive->conserved->primitive conversion and a flux calculation. By contrast, the 
        so-called primitive Hancock method uses the Euler equations in primitive variables to 
        estimate the change in time from the change across the cell (see 
        :func:`primitiveEvolution`). The two methods should give almost identical results, but the 
        primitive version is noticeably faster.
        
        Parameters
        ----------
        idir: int
            Direction of sweep (0 = x, 1 = y)
        dt: float
            Timestep
        """
        
        slc3aL = self.slc3aL[idir]
        slc3aR = self.slc3aR[idir]
        slc3aC = self.slc3aC[idir]

        # Compute undivided derivatives
        sL = (self.V[slc3aC] - self.V[slc3aL])
        sR = (self.V[slc3aR] - self.V[slc3aC])
        
        # Apply slope limiter. 
        slim = np.zeros_like(sL)
        self.limiter(sL, sR, slim)
    
        # Set left and right edge states in each cell (except one layer of ghost cells)
        self.V_im12[slc3aC] = self.V[slc3aC] - slim * 0.5
        self.V_ip12[slc3aC] = self.V[slc3aC] + slim * 0.5        
        
        # The Hancock step advances the left/right cell edge states by 1/2 timestep to get 2nd
        # order in the flux calculation. There are two ways to perform the Hancock step. The more
        # conventionally quoted way is to take the fluxes according to the L/R states as an
        # approximation for the flux differential across the cell ('hancock_cons'). We use the 
        # differential to update the conserved cell-edge states. However, this method necessitates
        # a prim->cons->prim conversion and a flux calculation. By contrast, the "primitive 
        # Hancock" method uses the Euler equations in primitive variables to estimate the change in
        # time from the change across the cell. Both methods give identical results, but the 
        # primitive version is noticeably faster.
        
        if self.hs.time_integration == 'hancock':
            fac = 0.5 * dt / self.dx
            self.V_im12[slc3aC] += fac * self.primitiveEvolution(idir, self.V_im12[slc3aC], slim)
            self.V_ip12[slc3aC] += fac * self.primitiveEvolution(idir, self.V_ip12[slc3aC], slim)
    
        elif self.hs.time_integration == 'hancock_cons':
            fac = 0.5 * dt / self.dx
            U_im12 = self.primitiveToConservedRet(self.V_im12[slc3aC])
            U_ip12 = self.primitiveToConservedRet(self.V_ip12[slc3aC])
            F_im12 = self.fluxVector(idir, self.V_im12[slc3aC])
            F_ip12 = self.fluxVector(idir, self.V_ip12[slc3aC])
            Fdiff = (F_im12 - F_ip12)
            U_im12 += fac * Fdiff
            U_ip12 += fac * Fdiff
            self.conservedToPrimitive(U_im12, self.V_im12[slc3aC])
            self.conservedToPrimitive(U_ip12, self.V_ip12[slc3aC])

        return

    # ---------------------------------------------------------------------------------------------

    def limiterNone(self, sL, sR, slim):
        """
        Non-limiter (central derivative)
        
        This limiter is the absence thereof: it does not limit the left and right slopes but 
        returns their average (the central derivative). This generally produces unstable schemes
        but is implemented for testing and demonstration purposes.
        
        Parameters
        ----------
        sL: array_like
            Array of left slopes
        sR: array_like
            Array of right slopes
        slim: array_like
            Output array of limited slope; must have same dimensions as sL and sR.
        """
            
        slim[:] = 0.5 * (sL + sR)    
        
        return

    # ---------------------------------------------------------------------------------------------

    def limiterMinMod(self, sL, sR, slim):
        """
        Minimum-modulus limiter
        
        The most conservative limiter, which always chooses the shallower out of the left and 
        right slopes.
        
        Parameters
        ----------
        sL: array_like
            Array of left slopes
        sR: array_like
            Array of right slopes
        slim: array_like
            Output array of limited slope; must have same dimensions as sL and sR.
        """
        
        sL_abs = np.abs(sL)
        sR_abs = np.abs(sR)
        mask = (sL * sR > 0.0) & (sL_abs <= sR_abs)
        slim[mask] = sL[mask]
        mask = (sL * sR > 0.0) & (sL_abs > sR_abs)
        slim[mask] = sR[mask]        
        
        return

    # ---------------------------------------------------------------------------------------------

    def limiterVanLeer(self, sL, sR, slim):
        """
        The limiter of van Leer
        
        An intermediate limiter that is less conservative than minimum modulus but more 
        conservative than monotonized central.
        
        Parameters
        ----------
        sL: array_like
            Array of left slopes
        sR: array_like
            Array of right slopes
        slim: array_like
            Output array of limited slope; must have same dimensions as sL and sR.
        """
        
        mask = (sL * sR > 0.0)
        slim[mask] = 2.0 * sL[mask]* sR[mask] / (sL[mask] + sR[mask])    
        
        return

    # ---------------------------------------------------------------------------------------------

    def limiterMC(self, sL, sR, slim):
        """
        Monotonized-central limiter
        
        As the name suggests, this limiter chooses the central derivative wherever possible, but 
        reduces its slope where it would cause negative cell-edge values. This limiter leads to the
        sharpest solutions but is also the least stable.
        
        Parameters
        ----------
        sL: array_like
            Array of left slopes
        sR: array_like
            Array of right slopes
        slim: array_like
            Output array of limited slope; must have same dimensions as sL and sR.
        """
        
        sC = (sL + sR) * 0.5
        sL_abs = np.abs(sL)
        sR_abs = np.abs(sR)
        mask = (sL * sR > 0.0) & (sL_abs <= sR_abs)
        slim[mask] = 2.0 * sL[mask]
        mask = (sL * sR > 0.0) & (sL_abs > sR_abs)
        slim[mask] = 2.0 * sR[mask]
        mask = np.abs(slim) > np.abs(sC)
        slim[mask] = sC[mask]
        
        return

    # ---------------------------------------------------------------------------------------------
    
    def riemannSolverHLL(self, idir, VL, VR):
        """
        The HLL Riemann solver
        
        The Riemann solver computes the fluxes across cell interfaces given two discontinuous 
        states on the left and right sides of each interface. The Harten-Lax-van Leer (HLL) 
        Riemann solver is one of the simplest such algorithms. It takes into account the 
        fastest waves traveling left and right, but it computes only one intermediate state that
        ignores contact discontinuities.
        
        Parameters
        ----------
        idir: int
            Direction of sweep (0 = x, 1 = y)
        VL: array_like
            Array of primitive state vectors on the left sides of the interfaces
        VR: array_like
            Array of primitive state vectors on the right sides of the interfaces
    
        Returns
        -------
        flux: array_like
            Array of conservative fluxes across interfaces; has the same dimensions as VL and VR.
        """
    
        # Sound speed to the left and right of the interface
        csL = self.soundSpeed(VL)
        csR = self.soundSpeed(VR)
        
        # Maximum negative velocity to the left and positive velocity to the right
        SL = VL[self.VX + idir] - csL
        SR = VR[self.VX + idir] + csR
        
        # Get conserved states for left and right states
        UL = self.primitiveToConservedRet(VL)
        UR = self.primitiveToConservedRet(VR)
        
        # F(V) on the left and right
        FL = self.fluxVector(idir, VL)
        FR = self.fluxVector(idir, VR)
        
        # Formula for the HLL Riemann solver. We first set all fields to the so-called HLL flux, i.e.,
        # the flux in the intermediate state between the two fastest waves SL and SR. If even SL is 
        # positive (going to the right), then we take the flux from the left cell, FL. If even SR is
        # going to the left, we take the right flux. Since these cases can be rare in some problems,
        # we first do a quick check whether there are any cells that match the condition before setting
        # them to the correct fluxes.
        flux = (SR * FL - SL * FR + SL * SR * (UR - UL)) / (SR - SL)

        # Check for cases where all speeds are on one side of the fan, in which case we overwrite
        # the values computed above. This may seem a little wasteful, but in practice, excuting the
        # operation above only for the needed entries costs more time than is typically saved.    
        if np.any(SL >= 0.0):
            mask_L = (SL >= 0.0)
            flux[:, mask_L] = FL[:, mask_L]
        if np.any(SR <= 0.0):
            mask_R = (SR <= 0.0)
            flux[:, mask_R] = FR[:, mask_R]

        return flux

    # ---------------------------------------------------------------------------------------------
    
    def riemannSolverHLLC(self, idir, VL, VR):
        """
        The HLLC Riemann solver
        
        Similar to the HLL Riemann solver, but with an additional distinction of whether the 
        interface lies to the left or right of contact discontinuities. The implementation follows
        Chapter 10.4 in Toro 2009.
        
        This Riemann solver explicitly uses pressure and total energy in its calculations and is 
        thus not compatible with an isothermal EOS where we do not track those variables. This is,
        in some sense, by construction: in an isothermal gas, there are no contact discontinuities,
        and the HLLC solver yields no advantage over HLL.
        
        Parameters
        ----------
        idir: int
            Direction of sweep (0 = x, 1 = y)
        VL: array_like
            Array of primitive state vectors on the left sides of the interfaces
        VR: array_like
            Array of primitive state vectors on the right sides of the interfaces
    
        Returns
        -------
        flux: array_like
            Array of conservative fluxes across interfaces; has the same dimensions as VL and VR.
        """
    
        # Shortcuts to indices
        idir2 = (idir + 1) % 2
        iDN = self.DN
        iU1 = self.VX + idir
        iU2 = self.VX + idir2
        iPR = self.PR
        iET = self.ET
    
        # The first steps are the same as for the HLL Riemann solver
        csL = self.soundSpeed(VL)
        csR = self.soundSpeed(VR)
        SL = VL[iU1] - csL
        SR = VR[iU1] + csR
        UL = self.primitiveToConservedRet(VL)
        UR = self.primitiveToConservedRet(VR)
        FL = self.fluxVector(idir, VL)
        FR = self.fluxVector(idir, VR)
        
        # Calculate the velocity of a contact discontinuity between the left and right star states
        rhoL = VL[iDN]
        rhoR = VR[iDN]
        uL = VL[iU1]
        uR = VR[iU1]
        PL = VL[iPR]
        PR = VR[iPR]
        rhoL_SL_m_uL = rhoL * (SL - uL)
        rhoR_SR_m_uR = rhoR * (SR - uR)
        Sstar = (PR - PL + uL * rhoL_SL_m_uL - uR * rhoR_SR_m_uR) / (rhoL_SL_m_uL - rhoR_SR_m_uR)
        
        # Construct star states. Since the computation is relatively involved, we only do it for those 
        # cells where it is actually needed.
        flux = np.zeros_like(VL)
        
        mask = (SL >= 0.0)
        if np.any(mask):
            flux[:, mask] = FL[:, mask]
        
        mask = (SL < 0.0) & (Sstar >= 0.0)
        if np.any(mask):
            UL_star = np.zeros_like(UL[:, mask])
            rho_star_L = rhoL_SL_m_uL[mask] / (SL[mask] - Sstar[mask])
            UL_star[iDN] = rho_star_L
            UL_star[iU1] = rho_star_L * Sstar[mask]
            UL_star[iU2] = rho_star_L * VL[iU2][mask]
            UL_star[iET] = rho_star_L * (UL[iET][mask] / rhoL[mask] + (Sstar[mask] - uL[mask]) * (Sstar[mask] + PL[mask] / rhoL_SL_m_uL[mask]))
            flux[:, mask] = FL[:, mask] + SL[mask] * (UL_star - UL[:, mask])
        
        mask = (SR > 0.0) & (Sstar < 0.0)
        if np.any(mask):
            UR_star = np.zeros_like(UL[:, mask])
            rho_star_R = rhoR_SR_m_uR[mask] / (SR[mask] - Sstar[mask])
            UR_star[iDN] = rho_star_R
            UR_star[iU1] = rho_star_R * Sstar[mask]
            UR_star[iU2] = rho_star_R * VR[iU2][mask]
            UR_star[iET] = rho_star_R * (UR[iET][mask] / rhoR[mask] + (Sstar[mask] - uR[mask]) * (Sstar[mask] + PR[mask] / rhoR_SR_m_uR[mask]))
            flux[:, mask] = FR[:, mask] + SR[mask] * (UR_star - UR[:, mask])
            
        mask = (SR <= 0.0)
        if np.any(mask):
            flux[:, mask] = FR[:, mask]
        
        return flux

    # ---------------------------------------------------------------------------------------------

    def cflCondition(self):
        """
        Compute the size of the next timestep
        
        This function computes the maximum signal speed anywhere in the domain and sets a timestep
        based on the CFL condition. This routine 
        
        Returns
        -------
        dt: float
            Size of the next timestep
        """
        
        u_max = self.maxSpeedInDomain()
        dt = self.hs.cfl * self.dx / u_max
        
        return dt
            
    # ---------------------------------------------------------------------------------------------    
    
    def addSourceTerms(self, dt):
        """
        Add source terms to conserved quantities

        This function implements adding the source terms S in dU / dt + div(F(U)) = S(U), namely we
        add the time-integrated source term to U. For a vector of conserved quantities
        
        U = (rho, rho * ux, rho * uy, E)
        
        the source term for gravity reads 
        
        S_grav = (0, -rho * dPhi/dx, -rho * dPhi/dy, rho * dPhi/dt).
        
        For fixed-g gravity, we dPhi/dy = g and all other terms are zero. It might seem counter-
        intuitive that we are adding to the y-momentum and not to the energy. However, changes in 
        momentum should be balanced by "falling," i.e., by changes in the gravitational potential.
        
        Parameters
        ----------
        dt: float
            The time over which the source term should be integrated.
        """
        
        if self.gravity_mode == 'fixed_acc':
            self.U[self.MX + self.gravity_dir] += -self.U[self.MS] * self.gravity_g * dt
    
        elif self.gravity_mode == 'fixed_pot':
            self.U[self.MX] += -self.U[self.MS] * self.U[self.GX] * dt
            self.U[self.MY] += -self.U[self.MS] * self.U[self.GY] * dt
            
        else:
            raise Exception('Unknown type of gravity, %s.' % (self.gravity_mode))

        return

    # ---------------------------------------------------------------------------------------------
    
    def timestep(self, dt = None):
        """
        Advance the fluid state by a timestep dt
        
        This timestepping routine implements a dimensionally split scheme, meaning that we execute
        two sweeps in the two dimensions. We alternate the ordering of the sweeps with each timestep 
        (xy-yx-xy and so on). This so-called Strang splitting maintains 2nd-order accuracy, but only 
        if the timestep is the same for the two sweeps.
        
        In each direction, we reconstruct the cell-edge states, compute the conservative Godunov 
        fluxes with the Riemann solver, and add the flux difference to the converved fluid variables. 
        
        The function internally handles the case of a CFL violation during the second sweep, which 
        can occur even if the timestep was initially set to obey the CFL criterion. In this case,
        the returned timestep will be different from the input timestep (if given).
        
        Parameters
        ----------
        dt: float
            Size of the timestep to be taken; if ``None`` the timestep is computed from the CFL
            condition using the :func:`~ulula.core.simulation.Simulation.cflCondition` function. This 
            timestep should be used in most circumstances, but sometimes we wish to take a manually 
            set timestep, for example, to output a file or plot. Thus, the two functions are 
            separated. The user is responsible for ensuring that dt does not exceed the CFL 
            criterion!
        
        Returns
        -------
        dt: float
            The timestep taken
        """
        
        # Copy current state in case an error occurs. We do not need to copy fixed gravitational
        # potentials, which is why the first dimension may not include all variables.
        self.V_cpy[:self.nq_cpy:, ...] = self.V[:self.nq_cpy:, ...]
        self.U_cpy[:self.nq_cpy:, ...] = self.U[:self.nq_cpy:, ...]

        # If the initial timestep is not given, compute it from the CFL condition
        if dt is None:
            dt = self.cflCondition()

        # Use Strang splitting to maintain 2nd order accuracy; we go xy-yx-xy-yx and so on. For a 
        # 1D simulation, there is no need to perform the y-sweep.
        is_2d = self.is_2d
        if is_2d:
            sweep_idxs = [0, 1]
            if self.last_dir == 0:
                sweep_dirs = [0, 1]
            else:
                sweep_dirs = [1, 0]
        else:
            sweep_idxs = [0]
            sweep_dirs = [0]
        
        # Iterate until we obtain a valid solution. Hopefully, the while loop should only be
        # executed once, but we might run into a CFL violation on the second sweep.
        success = False
        i_try = 0
        while not success:
        
            # We are fundamentally solving the conserved hydro equation dU / dt + div(F(U)) = S(U). 
            # If S(U) != 0, we need to add the time integral of S(U) to U (since it is not obvious
            # that we can pull it into the flux vector, given the div(F(U)) term). In order to
            # maintain 2nd-order accuracy, we do not add the entire source term before or after the
            # other operations but split it into two half-timesteps. 
            if self.use_source_terms:
                self.addSourceTerms(0.5 * dt)
                self.conservedToPrimitive(self.U, self.V)
                self.enforceBoundaryConditions()

            # Now perform the hydro step (without source terms) by sweeping in the two dimensions.
            for sweep_idx in sweep_idxs:
                sweep_dir = sweep_dirs[sweep_idx]

                # If we are on the second sweep, there is a possibility that we are violating the
                # CFL condition, i.e., that the maximum measured CFL number exceeds the maximum. 
                # If so, we re-set the solution, reduce the timestep, and try again.
                if sweep_idx == 1:
                    u_max = self.maxSpeedInDomain()
                    cfl_real = dt * u_max / self.dx
                    if (cfl_real > self.hs.cfl_max):
                        reduce_factor = cfl_real / self.hs.cfl_max * self.hs.cfl_reduce_factor
                        i_try += 1
                        if i_try >= self.hs.cfl_max_attempts:
                            raise Exception('Could not find solution after %d iterations.' % (i_try))
                        print('WARNING: CFL violation on timestep %4d, iteration %d, reducing dt by %.2f from %2e to %.2e.' \
                            % (self.step, i_try, reduce_factor, dt, dt / reduce_factor))
                        dt = dt / reduce_factor
                        self.V[:self.nq_cpy:, ...] = self.V_cpy[:self.nq_cpy:, ...]
                        self.U[:self.nq_cpy:, ...] = self.U_cpy[:self.nq_cpy:, ...]
                        continue
                    else:
                        success = True
                elif not is_2d:
                    success = True

                # Load slices for this dimension
                slc3dL = self.slc3dL[sweep_dir]
                slc3dR = self.slc3dR[sweep_dir]
                slc3dC = self.slc3dC[sweep_dir]
                slc3fL = self.slc3fL[sweep_dir]
                slc3fR = self.slc3fR[sweep_dir]
                
                # Reconstruct states at left and right cell edges.
                self.reconstruction(sweep_dir, dt)
                
                # Use states at cell edges (right edges in left cells, left edges in right cells) as 
                # input for the Riemann solver, which computes the Godunov fluxes at the interface 
                # walls. Here, we call interface i the interface between cells i-1 and i.
                flux = self.riemannSolver(sweep_dir, self.V_ip12[slc3dL], self.V_im12[slc3dR])
            
                # Update conserved fluid state. We are using Godunov's scheme, as in, we difference the 
                # fluxes taken from the Riemann solver. Note the convention that index i in the flux array
                # means the left interface of cell i, and i+1 the right interface of cell i.
                self.U[slc3dC] = self.U[slc3dC] + dt / self.dx * (flux[slc3fL] - flux[slc3fR])
                
                # If necessary, we perform the second source term addition here during the second
                # sweep so that we do not convert to primitive variables twice.
                if self.use_source_terms and (sweep_idx == 1 or (not is_2d)):
                    self.addSourceTerms(0.5 * dt)
                    
                # Convert U -> V; this way, we are sure that plotting functions etc find both the correct
                # conserved and primitive variables.
                self.conservedToPrimitive(self.U, self.V)
            
                # Impose boundary conditions. This needs to happen after each dimensional sweep rather
                # than after each timestep, otherwise the second sweep will encounter some less 
                # advanced cells near the boundaries.
                self.enforceBoundaryConditions()
            
        # Increase timestep
        self.t += dt
        self.step += 1
        self.last_dir = sweep_dir
    
        return dt

    # ---------------------------------------------------------------------------------------------
    
    def save(self, filename = None):
        """
        Save the current state of a simulation
        
        Parameters
        ----------
        filename: str
            Output filename; auto-generated if ``None``
        """
        
        if filename is None:
            filename = 'ulula_%04d.hdf5' % (self.step)
    
        print('Saving to file %s' % (filename))
    
        f = h5py.File(filename, 'w')

        f.create_group('code')
        f['code'].attrs['file_version'] = ulula_version.__version__
        
        f.create_group('hydro_scheme')
        f['hydro_scheme'].attrs['reconstruction'] = self.hs.reconstruction
        f['hydro_scheme'].attrs['limiter'] = self.hs.limiter
        f['hydro_scheme'].attrs['riemann'] = self.hs.riemann
        f['hydro_scheme'].attrs['time_integration'] = self.hs.time_integration
        f['hydro_scheme'].attrs['cfl'] = self.hs.cfl
        f['hydro_scheme'].attrs['cfl_max'] = self.hs.cfl_max
        f['hydro_scheme'].attrs['cfl_reduce_factor'] = self.hs.cfl_reduce_factor
        f['hydro_scheme'].attrs['cfl_max_attempts'] = self.hs.cfl_max_attempts
    
        f.create_group('eos')
        f['eos'].attrs['eos_mode'] = self.eos_mode
        f['eos'].attrs['eos_gamma'] = self.eos_gamma
        if self.eos_mu is None:
            f['eos'].attrs['eos_mu'] = 0.0
        else:
            f['eos'].attrs['eos_mu'] = self.eos_mu
        if self.eos_mode == 'isothermal':
            f['eos'].attrs['eos_eint_fixed'] = self.eos_eint_fixed

        f.create_group('units')
        f['units'].attrs['unit_l'] = self.unit_l
        f['units'].attrs['unit_t'] = self.unit_t
        f['units'].attrs['unit_m'] = self.unit_m

        f.create_group('gravity')
        f['gravity'].attrs['gravity_mode'] = self.gravity_mode
        f['gravity'].attrs['gravity_g'] = self.gravity_g
        f['gravity'].attrs['gravity_dir'] = self.gravity_dir
        f['gravity'].attrs['gravity_compute_gradients'] = self.gravity_compute_gradients

        f.create_group('user_bcs')
        f['user_bcs'].attrs['do_user_updates'] = self.do_user_updates
        f['user_bcs'].attrs['do_user_bcs'] = self.do_user_bcs
    
        f.create_group('domain')
        f['domain'].attrs['is_2d'] = self.is_2d
        f['domain'].attrs['xmin'] = self.xmin
        f['domain'].attrs['xmax'] = self.xmax
        f['domain'].attrs['ymin'] = self.ymin
        f['domain'].attrs['ymax'] = self.ymax
        f['domain'].attrs['dx'] = self.dx
        f['domain'].attrs['nx'] = self.nx
        f['domain'].attrs['ny'] = self.ny
        f['domain'].attrs['nghost'] = self.nghost
        f['domain'].attrs['bc_type'] = self.bc_type
    
        f.create_group('run')
        f['run'].attrs['t'] = self.t
        f['run'].attrs['step'] = self.step
        f['run'].attrs['last_dir'] = self.last_dir
        
        f.create_group('grid')
        for q in self.q_prim:
            f['grid'][q] = self.V[self.q_prim[q], :, :]
        
        f.close()
        
        return

###################################################################################################

def load(filename, user_update_func = None, user_bc_func = None):
    """
    Load a snapshot file into a simulation object
    
    Parameters
    ----------
    filename: str
        Input filename
    user_update_func: func
        Function pointer that takes the simulation object as an argument. See 
        :func:`~ulula.core.simulation.Simulation.setUserUpdateFunction` for details. Since a function 
        pointer cannot be stored in a file, this parameter must be given as an additional argument 
        when loading a simulation with user-defined update function. 
    user_bc_func: func
        Function pointer that takes the simulation object as an argument. See 
        :func:`~ulula.core.simulation.Simulation.setUserBoundaryConditions` for details. Since a function 
        pointer cannot be stored in a file, this parameter must be given as an additional argument 
        when loading a simulation with user-defined boundary conditions. 

    Returns
    -------
    sim: Simulation
        Object of type :data:`~ulula.core.simulation.Simulation`
    """

    print('Loading simulation from file %s' % (filename))

    f = h5py.File(filename, 'r')
    
    # The current file version is written to each Ulula file. If the code tries to open a file that
    # is too old to be compatible, an error is thrown.
    file_version_oldest = '0.4.1'
    file_version = f['code'].attrs['file_version']
    if utils.versionIsOlder(file_version_oldest, file_version):
        raise Exception('Cannot load simulation from file %s because version %s is too old (allowed %s).' \
                    % (filename, file_version, file_version_oldest))

    # Create simulation object
    sim = Simulation()

    # Load hydro scheme parameters
    hs_pars = {}
    hs_pars['reconstruction'] = f['hydro_scheme'].attrs['reconstruction']
    hs_pars['limiter'] = f['hydro_scheme'].attrs['limiter']
    hs_pars['riemann'] = f['hydro_scheme'].attrs['riemann']
    hs_pars['time_integration'] = f['hydro_scheme'].attrs['time_integration']
    hs_pars['cfl'] = f['hydro_scheme'].attrs['cfl']
    hs_pars['cfl_max'] = f['hydro_scheme'].attrs['cfl_max']
    hs_pars['cfl_reduce_factor'] = f['hydro_scheme'].attrs['cfl_reduce_factor']
    hs_pars['cfl_max_attempts'] = f['hydro_scheme'].attrs['cfl_max_attempts']
    hs = HydroScheme(**hs_pars)    
    sim.setHydroScheme(hs)
    
    # Load fluid parameters
    eos_mode = f['eos'].attrs['eos_mode']
    eos_gamma = f['eos'].attrs['eos_gamma']
    eos_mu = f['eos'].attrs['eos_mu']
    if eos_mu == 0.0:
        eos_mu = None
    if eos_mode == 'isothermal':
        eos_eint_fixed = f['eos'].attrs['eos_eint_fixed']
    else:
        eos_eint_fixed = None
    sim.setEquationOfState(eos_mode = eos_mode, gamma = eos_gamma, eint_fixed = eos_eint_fixed,
                           mu = eos_mu)
    
    # Load code units
    unit_l = f['units'].attrs['unit_l']
    unit_t = f['units'].attrs['unit_t']
    unit_m = f['units'].attrs['unit_m']
    sim.setCodeUnits(unit_l = unit_l, unit_t = unit_t, unit_m = unit_m)

    # Load gravity parameters
    gravity_mode = f['gravity'].attrs['gravity_mode']
    gravity_g = f['gravity'].attrs['gravity_g']
    gravity_dir = f['gravity'].attrs['gravity_dir']
    gravity_compute_gradients = f['gravity'].attrs['gravity_compute_gradients']
    sim.setGravityMode(gravity_mode = gravity_mode, g = gravity_g, gravity_dir = gravity_dir,
                       compute_gradients = gravity_compute_gradients)

    # Load user BC settings. If a function was passed, we cannot restore it at this point.
    if f['user_bcs'].attrs['do_user_updates'] and user_update_func is None:
        raise Exception('Simulation loaded from file %s has user-defined update function; need user_update_func parameter to restore the simulation.' \
                        % (filename))
    sim.setUserUpdateFunction(user_update_func)
    if f['user_bcs'].attrs['do_user_bcs'] and user_bc_func is None:
        raise Exception('Simulation loaded from file %s has user-defined boundary conditions; need user_bc_func parameter to restore the simulation.' \
                        % (filename))
    sim.setUserBoundaryConditions(user_bc_func)

    # Load domain parameters and initialize domain
    nx = int(f['domain'].attrs['nx'])
    ny = int(f['domain'].attrs['ny'])
    xmin = f['domain'].attrs['xmin']
    xmax = f['domain'].attrs['xmax']
    ymin = f['domain'].attrs['ymin']
    bc_type = f['domain'].attrs['bc_type']
    sim.setDomain(nx, ny, xmin = xmin, xmax = xmax, ymin = ymin, bc_type = bc_type)

    # Ensure gravitational potentials are set
    sim.setGravityPotentials()

    # Load and reset time and step
    sim.t = f['run'].attrs['t']
    sim.step = f['run'].attrs['step']
    sim.last_dir = f['run'].attrs['last_dir']
    
    # Set grid variables
    for q in sim.q_prim:
        sim.V[sim.q_prim[q], :, :] = f['grid'][q]
        
    # Initialize the conserved variables and ghost cells
    sim.primitiveToConserved(sim.V, sim.U)
    sim.enforceBoundaryConditions()

    f.close()
    
    return sim

###################################################################################################
