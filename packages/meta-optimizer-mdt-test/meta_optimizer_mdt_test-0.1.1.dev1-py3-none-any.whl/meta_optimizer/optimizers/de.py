"""
de.py
-----
Differential Evolution optimizer with adaptive parameters.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable
from .base_optimizer import BaseOptimizer
import time
from tqdm.auto import tqdm

class DifferentialEvolutionOptimizer(BaseOptimizer):
    def __init__(self,
                 dim: int,
                 bounds: List[Tuple[float, float]],
                 population_size: int = 50,
                 max_evals: int = 10000,
                 F: float = 0.6,
                 CR: float = 0.7,
                 adaptive: bool = True,
                 verbose: bool = False,
                 **kwargs):
        """
        Initialize DE optimizer.
        
        Args:
            dim: Problem dimensionality
            bounds: Parameter bounds
            population_size: Population size
            max_evals: Maximum function evaluations
            F: Mutation factor
            CR: Crossover rate
            adaptive: Whether to use parameter adaptation
            verbose: Whether to show progress bars
        """
        super().__init__(dim=dim, bounds=bounds, population_size=population_size,
                        adaptive=adaptive)
        
        # Store max_evals as instance variable
        self.max_evals = max_evals
        self.verbose = verbose
        
        # DE parameters
        self.F_init = F
        self.CR_init = CR
        self.F = F
        self.CR = CR
        
        # Initialize population as a (population_size, dim) array
        self.population = np.zeros((self.population_size, self.dim))
        for i, (lower, upper) in enumerate(self.bounds):
            self.population[:, i] = np.random.uniform(lower, upper, self.population_size)
        
        # Initialize scores
        self.population_scores = np.full(self.population_size, np.inf)
        
        # Track best solution
        self.best_solution = None
        self.best_score = np.inf
        
        # Initialize tracking variables
        self.evaluations = 0
        self.start_time = 0
        self.end_time = 0
        
        # Initialize history tracking
        self.convergence_curve = []
        self.time_curve = []
        self.eval_curve = []
        
        # Initialize parameter history
        if adaptive:
            self.param_history = {
                'F': [F],
                'CR': [CR],
                'success_rate': [],
                'diversity': []
            }
        else:
            self.param_history = {
                'diversity': []
            }
        
        # Success tracking
        self.success_history = np.zeros(20)  # Track last 20 iterations
        self.success_idx = 0
        
        # Diversity tracking
        self.diversity_history = []
    
    def _mutate(self, target_idx: int) -> np.ndarray:
        """Generate mutant vector using DE mutation"""
        # Select three random distinct vectors
        idxs = [i for i in range(self.population_size) if i != target_idx]
        r1, r2, r3 = np.random.choice(idxs, size=3, replace=False)
        
        # Get best solution index
        best_idx = np.argmin(self.population_scores)
        
        # Generate mutant using current-to-best/1 strategy
        mutant = (self.population[target_idx] + 
                 self.F * (self.population[best_idx] - self.population[target_idx]) +
                 self.F * (self.population[r1] - self.population[r2]))
        
        return self._bound_solution(mutant)
    
    def _crossover(self, target: np.ndarray, mutant: np.ndarray) -> np.ndarray:
        """Perform binomial crossover"""
        mask = np.random.rand(self.dim) <= self.CR
        # Ensure at least one component is taken from mutant
        if not np.any(mask):
            mask[np.random.randint(0, self.dim)] = True
        return np.where(mask, mutant, target)
    
    def _update_parameters(self):
        """Update optimizer parameters based on performance"""
        if not self.adaptive:
            return
            
        # Calculate success rate
        success_rate = np.mean(self.success_history)
        
        # Update F and CR based on success rate
        if success_rate > 0.5:
            self.F = max(0.4, self.F * 0.95)
            self.CR = max(0.5, self.CR * 0.95)
        else:
            self.F = min(0.8, self.F * 1.05)
            self.CR = min(0.9, self.CR * 1.05)
            
        # Record parameter values
        self.param_history['F'].append(self.F)
        self.param_history['CR'].append(self.CR)
        self.param_history['success_rate'].append(success_rate)
    
    def _update_diversity(self):
        """Track population diversity"""
        diversity = np.mean(np.std(self.population, axis=0))
        self.diversity_history.append(diversity)
        self.param_history['diversity'].append(diversity)
    
    def _evaluate(self, solution: np.ndarray, objective_func: Callable) -> float:
        """
        Evaluate a solution using the objective function.
        
        Args:
            solution: Solution to evaluate
            objective_func: Objective function
            
        Returns:
            Fitness score
        """
        self.evaluations += 1
        return objective_func(solution)
    
    def _record_history(self):
        """Record optimization history"""
        # Record convergence history
        self.convergence_curve.append(self.best_score)
        
        # Record evaluation count
        self.eval_curve.append(self.evaluations)
        
        # Record time
        self.time_curve.append(time.time() - self.start_time)
    
    def reset(self):
        """Reset optimizer state"""
        super().reset()
        
        # Reset parameters
        self.F = self.F_init
        self.CR = self.CR_init
        
        # Reset parameter history
        if self.adaptive:
            self.param_history.update({
                'F': [self.F_init],
                'CR': [self.CR_init],
                'success_rate': [],
                'diversity': []
            })
        else:
            self.param_history.update({
                'diversity': []
            })
    
    def _iterate(self, objective_func: Callable) -> Tuple[np.ndarray, float]:
        """
        Perform one iteration of the optimization algorithm.
        
        Args:
            objective_func: Objective function to minimize
            
        Returns:
            Tuple of (best solution, best score)
        """
        # Start iteration timer
        iter_start_time = time.time()
        
        # Initialize success counter for this iteration
        success_count = 0
        
        # Create trial vectors and evaluate them
        for i in range(self.population_size):
            # Create mutant vector
            mutant = self._mutate(i)
            
            # Create trial vector through crossover
            trial = self._crossover(self.population[i], mutant)
            
            # Evaluate trial vector
            trial_score = self._evaluate(trial, objective_func)
            
            # Selection
            if trial_score <= self.population_scores[i]:
                self.population[i] = trial
                self.population_scores[i] = trial_score
                success_count += 1
                
                # Update best solution if needed
                if trial_score < self.best_score:
                    self.best_score = trial_score
                    self.best_solution = trial.copy()
                    self.last_improvement_iter = self._current_iteration
        
        # Update success history
        success_rate = success_count / self.population_size
        self.success_history.append(success_rate > 0)
        
        # Update selection pressure
        self.selection_pressure.append(success_rate)
        
        # Update parameters based on performance
        self._update_parameters()
        
        # Update diversity metrics
        self._update_diversity()
        
        # Estimate problem characteristics
        self._estimate_problem_characteristics()
        
        # Record time for this iteration
        iter_time = time.time() - iter_start_time
        self.time_per_iteration.append(iter_time)
        
        # Update convergence curve
        self.convergence_curve.append(self.best_score)
        
        # Update stagnation count
        if self._current_iteration - self.last_improvement_iter > 10:
            self.stagnation_count += 1
        
        # Return current best solution and score
        return self.best_solution, self.best_score
    
    def _optimize(self, objective_func: Callable, context: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, float]:
        """Run DE optimization"""
        # Evaluate initial population
        for i in range(self.population_size):
            self.population_scores[i] = self._evaluate(self.population[i], objective_func)
            if self.population_scores[i] < self.best_score:
                self.best_score = self.population_scores[i]
                self.best_solution = self.population[i].copy()
        
        # Track initial diversity
        self._update_diversity()
        
        while not self._check_convergence():
            # Create new population
            new_population = np.zeros_like(self.population)
            
            for i in range(self.population_size):
                # Select three random parents
                a, b, c = np.random.choice(
                    [j for j in range(self.population_size) if j != i],
                    size=3, replace=False
                )
                
                # Create mutant vector
                mutant = self.population[a] + self.F * (self.population[b] - self.population[c])
                
                # Create trial vector through crossover
                trial = np.zeros_like(mutant)
                j_rand = np.random.randint(self.dim)
                for j in range(self.dim):
                    if np.random.rand() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                    else:
                        trial[j] = self.population[i, j]
                
                # Bound trial vector
                trial = self._bound_solution(trial)
                
                # Evaluate trial vector
                trial_score = self._evaluate(trial, objective_func)
                
                # Selection
                if trial_score <= self.population_scores[i]:
                    new_population[i] = trial
                    self.population_scores[i] = trial_score
                    if trial_score < self.best_score:
                        self.best_score = trial_score
                        self.best_solution = trial.copy()
                else:
                    new_population[i] = self.population[i]
            
            # Update population
            self.population = new_population
            
            # Update parameters and track diversity
            self._update_parameters()
            self._update_diversity()
            
            if self._check_convergence():
                break
        
        return self.best_solution, self.best_score

    def optimize(self, objective_func: Callable,
                max_evals: Optional[int] = None,
                record_history: bool = True,
                context: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, float]:
        """
        Run Differential Evolution optimization.
        
        Args:
            objective_func: Function to minimize
            max_evals: Maximum number of function evaluations (overrides init value)
            record_history: Whether to record convergence and parameter history
            context: Optional problem context
            
        Returns:
            Best solution found and its score
        """
        # Update max_evals if provided
        if max_evals is not None:
            self.max_evals = max_evals
            
        self.start_time = time.time()
        
        # Initialize population if not already done
        if self.best_solution is None:
            self.best_solution = np.zeros(self.dim)
            
        # Initialize population
        self.population = np.zeros((self.population_size, self.dim))
        for i, (lower, upper) in enumerate(self.bounds):
            self.population[:, i] = np.random.uniform(lower, upper, self.population_size)
        
        self.population_scores = np.full(self.population_size, np.inf)
        
        # Evaluate initial population
        for i in range(self.population_size):
            self.population_scores[i] = self._evaluate(self.population[i], objective_func)
            if self.population_scores[i] < self.best_score:
                self.best_score = self.population_scores[i]
                self.best_solution = self.population[i].copy()
        
        # Track initial diversity
        self._update_diversity()
        
        # Initialize progress bar
        pbar = None
        if self.verbose:
            pbar = tqdm(total=self.max_evals, desc="DE Optimization")
            pbar.update(0)
        
        # Main optimization loop
        generation = 0
        max_generations = self.max_evals // self.population_size
        
        # Use tqdm for progress bar if verbose is enabled
        gen_range = tqdm(range(max_generations), desc="DE Optimization", disable=not self.verbose)
        
        for generation in gen_range:
            # Check if we've used up our budget
            if self.evaluations >= self.max_evals:
                break
                
            # Create and evaluate trial vectors
            for i in range(self.population_size):
                # Generate trial vector
                mutant = self._mutate(i)
                trial = self._crossover(self.population[i], mutant)
                
                # Evaluate fitness
                trial_score = self._evaluate(trial, objective_func)
                self.evaluations += 1
                
                # Selection (keep the better solution)
                if trial_score <= self.population_scores[i]:
                    self.population[i] = trial
                    self.population_scores[i] = trial_score
                    
                    # Update best solution if needed
                    if trial_score < self.best_score:
                        self.best_score = trial_score
                        self.best_solution = trial.copy()
                
                # Update parameters if using adaptive DE
                if self.adaptive and i % 10 == 0:
                    self._update_parameters()
                
                # Check if we've used up the budget
                if self.evaluations >= self.max_evals:
                    break
            
            # Update progress bar
            if pbar:
                pbar.update(self.population_size)
                pbar.set_postfix({"best_score": f"{self.best_score:.6f}", "evals": self.evaluations})
            
            # Record convergence
            if record_history:
                self._record_history()
        
        # Close progress bar
        if pbar:
            pbar.close()
        
        self.end_time = time.time()
        return self.best_solution, self.best_score

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get optimizer parameters.
        
        Returns:
            Dictionary of optimizer parameters
        """
        return {
            'F': self.F,
            'CR': self.CR,
            'population_size': self.population_size,
            'max_evals': self.max_evals,
            'adaptive': self.adaptive,
            'evaluations': self.evaluations,
            'runtime': self.end_time - self.start_time if self.end_time > 0 else 0,
            'diversity': self.diversity_history[-1] if self.diversity_history else 0
        }
