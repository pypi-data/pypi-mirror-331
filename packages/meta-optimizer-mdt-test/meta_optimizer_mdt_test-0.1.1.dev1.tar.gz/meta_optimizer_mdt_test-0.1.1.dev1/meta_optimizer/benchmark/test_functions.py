"""
Test functions for benchmarking optimization algorithms.
"""
import numpy as np


class ClassicalTestFunctions:
    """Collection of classical test functions for optimization."""
    
    @staticmethod
    def sphere(x):
        """
        Sphere function.
        
        Parameters
        ----------
        x : numpy.ndarray
            The point to evaluate
            
        Returns
        -------
        float
            The function value at the given point
        """
        return np.sum(x**2)
    
    @staticmethod
    def rosenbrock(x):
        """
        Rosenbrock function.
        
        Parameters
        ----------
        x : numpy.ndarray
            The point to evaluate
            
        Returns
        -------
        float
            The function value at the given point
        """
        return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (x[:-1] - 1)**2)
    
    @staticmethod
    def rastrigin(x):
        """
        Rastrigin function.
        
        Parameters
        ----------
        x : numpy.ndarray
            The point to evaluate
            
        Returns
        -------
        float
            The function value at the given point
        """
        return 10 * len(x) + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))
    
    @staticmethod
    def ackley(x):
        """
        Ackley function.
        
        Parameters
        ----------
        x : numpy.ndarray
            The point to evaluate
            
        Returns
        -------
        float
            The function value at the given point
        """
        a = 20
        b = 0.2
        c = 2 * np.pi
        
        term1 = -a * np.exp(-b * np.sqrt(np.mean(x**2)))
        term2 = -np.exp(np.mean(np.cos(c * x)))
        
        return term1 + term2 + a + np.exp(1)


# Dictionary of test functions for easy access
TEST_FUNCTIONS = {
    "sphere": ClassicalTestFunctions.sphere,
    "rosenbrock": ClassicalTestFunctions.rosenbrock,
    "rastrigin": ClassicalTestFunctions.rastrigin,
    "ackley": ClassicalTestFunctions.ackley
}
