###################################################################################################
#
# This file is part of the ULULA code.
#
# (c) Benedikt Diemer, University of Maryland
#
###################################################################################################

import six
import abc
import numpy as np

import ulula.physics.constants as constants

###################################################################################################

@six.add_metaclass(abc.ABCMeta)
class Setup():
    """
    General setup class
    
    This abstract container must be partially overwritten by child classes, but also contains 
    defaults for a number of standard routines. In particular, the user must implement the routines
    that provide a short name and that set the initial conditions. 
    
    Some optionally overwritten routines determine how plots look and are automatically passed to 
    the plotting functions when using the :func:`~ulula.core.run.run` function.

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

        self.unit_l = unit_l
        self.unit_t = unit_t
        self.unit_m = unit_m
        
        return

    # ---------------------------------------------------------------------------------------------

    @abc.abstractmethod
    def shortName(self):
        """
        Short name for the problem (to be used in output filenames)
        """
        
        return

    # ---------------------------------------------------------------------------------------------
    
    def initialConditions(self, sim, nx):
        """
        Wrapper function to set initial data
        
        This function calls the problem-specific setup, which is assumed to set the primitive 
        variables. Those are also converted to conserved variables.
        
        Parameters
        ----------
        sim: Simulation
            Simulation object in which the ICs are to be set
        nx: int
            Number of cells in the x-direction
        """
        
        # Code units are handled in this base class, set them now
        sim.setCodeUnits(unit_l = self.unit_l, unit_t = self.unit_t, unit_m = self.unit_m)

        # Call the user-defined function to set the initial conditions. Make sure the child class
        # didn't contain bugs that led to blatantly unphysical ICs.
        self.setInitialData(sim, nx)
        if np.any(sim.V[sim.q_prim['DN'], sim.xlo:sim.xhi+1, sim.ylo:sim.yhi+1] <= 0.0):
            raise Exception('Found zero or negative densities in initial conditions.')
        if 'PR' in sim.q_prim:
            if np.any(sim.V[sim.q_prim['PR'], sim.xlo:sim.xhi+1, sim.ylo:sim.yhi+1] <= 0.0):
                raise Exception('Found zero or negative pressure in initial conditions.')
        
        # We need to set the gravitational fields before any prim-cons conversions
        sim.setGravityPotentials()

        # User-defined domain update function. We check whether the child class has overwritten the
        # base class method.
        if self.hasUserUpdateFunction():
            user_update_func = self.updateFunction
        else:
            user_update_func = None
        sim.setUserUpdateFunction(user_update_func = user_update_func)
        
        # User-defined boundary conditions. We check whether the child class has overwritten the
        # base class method.
        if self.hasUserBoundaryConditions():
            user_bc_func = self.boundaryConditions
        else:
            user_bc_func = None
        sim.setUserBoundaryConditions(user_bc_func = user_bc_func)
        
        # Now create the correct conserved initial conditions and BCs
        sim.primitiveToConserved(sim.V, sim.U)
        sim.enforceBoundaryConditions()
        
        return

    # ---------------------------------------------------------------------------------------------

    @abc.abstractmethod
    def setInitialData(self, sim, nx):
        """
        Set the initial conditions (must be overwritten)

        This function 

        Parameters
        ----------
        sim: Simulation
            Simulation object in which the ICs are to be set
        nx: int
            Number of cells in the x-direction
        """
        
        return

    # ---------------------------------------------------------------------------------------------

    def updateFunction(self, sim):
        """
        Interact with the simulation at run-time

        If this function is overwritten by a child class, it will be execute by the Ulula 
        simulation before boundary conditions are enforced. During that time, the setup can
        change the fluid variables in the domain.

        Note that the simulation does not check whether what this function does makes any sense! 
        If the function implements unphysical behavior, an unphysical simulation will result. The 
        overwriting function can manipulate either primitive or conserved variables and thus must
        ensure that primitive and conserved variables are consistent after the function call.
        
        Derived classes should not return any values (and must not return False like this base
        class implementation, because that value is used to determine whether a user function is
        provided in a given setup).
        
        Parameters
        ----------
        sim: Simulation
            Simulation object
        """
        
        return False

    # ---------------------------------------------------------------------------------------------

    def boundaryConditions(self, sim):
        """
        Set boundary conditions at run-time

        If this function is overwritten by a child class, it will be execute by the Ulula 
        simulation after the boundary conditions are enforced. During that time, the setup can
        overwrite the boundary conditions.

        Note that the simulation does not check whether what this function does makes any sense! 
        If the function implements unphysical behavior, an unphysical simulation will result. The 
        overwriting function can manipulate either primitive or conserved variables and thus must
        ensure that primitive and conserved variables are consistent after the function call.
        
        Derived classes should not return any values (and must not return False like this base
        class implementation, because that value is used to determine whether user BCs are
        provided in a given setup).
        
        Parameters
        ----------
        sim: Simulation
            Simulation object
        """
        
        return False

    # ---------------------------------------------------------------------------------------------

    def hasUserUpdateFunction(self):
        """
        Check whether setup provides update function

        A utility function that determines whether a child class has overwritten 
        :func:`updateFunction`. 
        
        Parameters
        ----------
        has_user_updates: bool
            True if an setup implementation is providing a user-defined update function, False 
            otherwise.
        """

        has_user_updates = True
        try:
            ret = self.updateFunction(None)
            if ret == False:
                has_user_updates = False
        except:
            pass
        
        return has_user_updates

    # ---------------------------------------------------------------------------------------------

    def hasUserBoundaryConditions(self):
        """
        Check whether setup provides BCs

        A utility function that determines whether a child class has overwritten 
        :func:`boundaryConditions`. 
        
        Parameters
        ----------
        has_user_bcs: bool
            True if an setup implementation is providing user-defined BCs, False otherwise.
        """

        has_user_bcs = True
        try:
            ret = self.boundaryConditions(None)
            if ret == False:
                has_user_bcs = False
        except:
            pass
        
        return has_user_bcs

    # ---------------------------------------------------------------------------------------------

    def trueSolution(self, sim, x, q_plot, plot_geometry):
        """
        Return a true solution for this setup
        
        If overwritten, this function is passed to the Ulula 1D plotting routine 
        :func:`~ulula.core.plots.plot1d`. The function must return a list with one element for each 
        of the quantities in ``q_plot``. If an element is ``None``, no solution is plotted. Otherwise
        the element must be an array with the same dimensions as ``x_plot``. The true solution
        must be in code units.

        Parameters
        ----------
        sim: Simulation
            Simulation object
        x: array_like
            The coordinates where the true solution is to be computed.
        q_plot: array_like
            List of quantities for which to return the true solution. Quantities are identified via 
            the short strings given in the :data:`~ulula.core.plots.fields` dictionary.
        plot_geometry: str
            If the setup is 2D, the type of cut through the domain that the solution is desired 
            for. Can be ``line`` or ``radius`` (a radially averaged plot from the center). See the 
            documentation of :func:`~ulula.core.plots.plot1d` for details.

        Returns
        -------
        solution: array_like
            A list of length len(q_plot), with elements that are either None or an array with the
            same length as x.
        """
        
        return

    # ---------------------------------------------------------------------------------------------

    def plotLimits(self, q_plot, plot_geometry):
        """
        Return min/max limits for plotted quantities
        
        This function can be passed to the Ulula plotting routines. By default, no limits are 
        returned, which means the plotting functions automatically select limits. The limits must
        be in code units.

        Parameters
        ----------
        q_plot: array_like
            List of quantities for which to return the plot limits. Quantities are identified via 
            the short strings given in the :data:`~ulula.core.plots.fields` dictionary.
        plot_geometry: str
            For 2D plots, this parameter is ``2d``. For 1D plots in a 1D simulation, it is ``line``.
            If the setup is 2D but a 1D plot is created, this parameter gives the cut through the 
            domain, which can be ``line`` or ``radius`` (a radially averaged plot from the center). 
            See the documentation of :func:`~ulula.core.plots.plot1d` for details. 

        Returns
        -------
        limits_lower: array_like
            List of lower limits for the given plot quantities. If ``None``, a limit is chosen 
            automatically. Individual items can also be ``None``.
        limits_upper: array_like
            List of upper limits for the given plot quantities. If ``None``, a limit is chosen 
            automatically. Individual items can also be ``None``.
        log: array_like
            List of True/False that determine whether to plot in log space. If ``None``, all 
            quantities are plotted in linear space. If log is chosen, the limits must be positive.
        """
        
        return None, None, None

    # ---------------------------------------------------------------------------------------------

    def plotColorMaps(self, q_plot):
        """
        Return colormaps for plotted quantities
        
        This function can be passed to the Ulula plotting routines. By default, velocities are 
        plotted with a divergent colormap, whereas density and pressure are plotted with a 
        perceptually uniform colormap.

        Parameters
        ----------
        q_plot: array_like
            List of quantities for which to return the colormaps. Quantities are identified via 
            the short strings given in the :data:`~ulula.core.plots.fields` dictionary.

        Returns
        -------
        cmaps: array_like
            List of colormaps for the given quantities. If ``None``, a colormap is chosen 
            automatically. Individual items can also be ``None``.
        """
        
        return None

    # ---------------------------------------------------------------------------------------------

    def internalEnergyFromTemperature(self, T, mu, gamma):
        """
        Conversion for isothermal EOS
        
        If we are choosing an isothermal EOS, we need to pass the temperature in the form of an
        equivalent internal energy in code units, which can be a little tedious to compute. This
        function takes care of it. The result can be passed as the ``eint_fixed`` parameter to the
        :func:`~ulula.core.simulation.Simulation.setEquationOfState` function.

        Parameters
        ----------
        T: float
            Temperature in Kelvin.
        mu: float
            Mean particle weight in proton masses.

        Returns
        -------
        eint: float
            Internal energy in code units corresponding to the given temperature.
        """
        
        eint = constants.kB_cgs * T / ((gamma - 1.0) * mu * constants.mp_cgs)
        eint *= self.unit_t**2 / self.unit_l**2
        
        return eint

###################################################################################################
