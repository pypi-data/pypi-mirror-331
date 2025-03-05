"""
Command Line Interface for the Meta-Optimizer package.
This module serves as the main entry point when running the package from the command line.
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add the root directory to the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Import main function from root main.py
from main import main as main_func

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Meta-Optimizer Framework: A comprehensive framework for optimization, '
                    'meta-learning, explainability, and drift detection'
    )
    
    # Core functionality
    parser.add_argument('--optimize', action='store_true',
                        help='Run optimization with multiple optimizers on benchmark functions')
    parser.add_argument('--evaluate', action='store_true',
                        help='Evaluate a trained model on test data')
    parser.add_argument('--meta', action='store_true',
                        help='Run meta-learning to find the best optimizer for different problems')
    parser.add_argument('--summary', action='store_true',
                        help='Print summary of results for any operation')
    
    # Drift detection
    parser.add_argument('--drift', action='store_true',
                        help='Run drift detection on synthetic data')
    parser.add_argument('--drift-window', type=int, default=50,
                        help='Window size for drift detection')
    parser.add_argument('--drift-threshold', type=float, default=0.5,
                        help='Threshold for drift detection')
    parser.add_argument('--drift-significance', type=float, default=0.05,
                        help='Significance level for drift detection')
    parser.add_argument('--run-meta-learner-with-drift', action='store_true',
                        help='Run meta-learner with drift detection')
    parser.add_argument('--explain-drift', action='store_true',
                        help='Explain drift when detected')
    
    # Explainability
    parser.add_argument('--explain', action='store_true',
                        help='Run explainability analysis on a trained model')
    parser.add_argument('--explainer', type=str, default='shap',
                        choices=['shap', 'lime', 'feature_importance', 'optimizer'],
                        help='Explainer type (shap, lime, feature_importance, optimizer)')
    parser.add_argument('--explain-plots', action='store_true',
                        help='Generate and save explainability plots')
    parser.add_argument('--explain-plot-types', type=str, nargs='+',
                        help='Plot types to generate')
    parser.add_argument('--explain-samples', type=int, default=5,
                        help='Number of samples to use for explainability')
    
    # Meta-learning parameters
    parser.add_argument('--method', type=str, default='bayesian',
                        choices=['bayesian', 'random', 'grid', 'genetic'],
                        help='Method for meta-learner')
    parser.add_argument('--surrogate', type=str, default=None,
                        choices=[None, 'rf', 'gb', 'nn', 'gp'],
                        help='Surrogate model for meta-learner')
    parser.add_argument('--selection', type=str, default=None,
                        choices=[None, 'ucb', 'ei', 'pi', 'random'],
                        help='Selection strategy for meta-learner')
    parser.add_argument('--exploration', type=float, default=0.2,
                        help='Exploration factor for meta-learner')
    parser.add_argument('--history', type=float, default=0.7,
                        help='History weight for meta-learner')
    
    # Visualization
    parser.add_argument('--visualize', action='store_true',
                        help='Enable visualization of results')
    
    return parser.parse_args()


def main():
    """
    Main entry point for the CLI when used as meta-optimizer command.
    This simply calls the main function from the root project's main.py
    for consistency with the existing project structure.
    """
    return main_func()


if __name__ == "__main__":
    main()
