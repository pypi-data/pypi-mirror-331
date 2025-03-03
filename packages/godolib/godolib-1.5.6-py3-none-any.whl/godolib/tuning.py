import random
import os
import pandas as pd
import numpy as np
from .monitors import ModelManager
from tensorflow.keras.callbacks import EarlyStopping
import math
from itertools import combinations

class GeneticHyperparemeterSearch:
    """
    A class for performing hyperparameter tuning using a genetic algorithm approach.

    Attributes:
        population_size (int): The size of the population in each generation.
        max_generations (int): The maximum number of generations to evolve.
        mutation_rate (float): The probability of mutating a parameter in an individual.
        mutation_scale (dict): A dictionary defining the mutation range for each parameter.
        elitism_count (int): The number of top-performing individuals to retain in each generation.
        parents_per_generation (int): The number of individuals selected as parents for reproduction.
        parents_per_child (int): The number of parents used to generate each child.
        children_per_parents (int): The number of children generated per parent combination.
        evaluator (object): An object of a class that must implement an `evaluate` method. This method takes an individual (a dictionary of feature names and their values) and returns a fitness score.
        generator (object): An object of a class that must implement a `generate` method. This method takes an integer `n` and generates `n` individuals (each as a dictionary of feature names and their values).
        gen_history (list): History of generations with statistical metrics.
        pop_history (list): Detailed history of individuals and scores.
        population (dict): Dictionary storing the population of each generation.
    """
    def __init__ (self, population_size, max_generations, mutation_rate, mutation_scale, elitism_count, parents_per_generation, parents_per_child, children_per_parents, evaluator, generator, seed):
        """
        Initialize the genetic hyperparameter search.

        Args:
            population_size (int): Number of individuals in each generation.
            max_generations (int): Maximum number of generations to evolve.
            mutation_rate (float): Probability of mutation.
            mutation_scale (dict): Range of mutation for each parameter.
            elitism_count (int): Number of top performers to retain in each generation.
            parents_per_generation (int): Number of parents selected for reproduction per generation.
            parents_per_child (int): Number of parents required to produce a child.
            children_per_parents (int): Number of children produced per parent combination.
            evaluator (object): An object of a class with an `evaluate` method for scoring individuals.
            generator (object): An object of a class with a `generate` method for creating individuals.
            seed (int): Random seed for reproducibility.

        Raises:
            ValueError: If the parameters for parents or children are insufficient to produce the required population.
        """
        self.population_size=population_size
        self.max_generations=max_generations
        self.mutation_rate=mutation_rate
        self.mutation_scale=mutation_scale
        self.elitism_count = elitism_count
        self.parents_per_generation=parents_per_generation
        self.parents_per_child = parents_per_child
        self.children_per_parents=children_per_parents
        
        self.evaluator=evaluator
        self.generator = generator
        np.random.seed(seed)
        
        self.gen_history = []
        self.pop_history = []
        self.population = {}
        self.individuals = []

        if parents_per_generation < parents_per_child:
            raise ValueError(f"Not enough parents per generation to satisfy the parents per child")
        if (len(list(combinations(np.arange(parents_per_generation), parents_per_child))) * children_per_parents) < (population_size - elitism_count):
            raise ValueError (f"Not enough breeding rate (parents combinations and children per parents) to produce 'population_size - elitism_count' ({population_size - elitism_count}) children")

    def run (self):
        """
        Execute the genetic algorithm for the specified number of generations.

        This method initializes the population, evaluates its fitness, and iteratively
        applies elitism, selection, crossover, and mutation to evolve the population.
        """
        for generation in range (self.max_generations):
            print (f"\n\nGeneration: {generation}")
            if generation == 0:
                population = self.generator.generate(n=self.population_size)
                print (f"\nEvaluating population")
                scores = self._evaluate_population(population=population)
                self._update_history(population=population, scores=scores, generation=generation)
                continue
            self.population[generation] = population
            keeping_individuals, keeping_individuals_scores = self._extract_top_performers(population=population, scores=scores, num_performers=self.elitism_count, return_scores=True)
            num_offspring = self.population_size - len(keeping_individuals)
            parents = self._select_parents(population=population, scores=scores)
            print (f"\nCrossovering parents")
            children, children_scores = self._crossover_parents(parents=parents, num_offspring=num_offspring)
            population = keeping_individuals + children
            scores = np.concatenate([keeping_individuals_scores, children_scores], axis=0)
            self._update_history(population=population, scores=scores, generation=generation)


    def _crossover_parents (self, parents, num_offspring): 
        """
        Generate offspring by combining parent genes and applying mutation.

        Args:
            parents (list): List of selected parents for reproduction.
            num_offspring (int): Number of offspring to generate.

        Returns:
            tuple: A tuple containing the offspring and their scores.
        """
        parents_combinations = list(combinations(parents, self.parents_per_child))
        children_per_combination = []
        for parents_group in parents_combinations:
            parents_children = self._reproduce_parents(parents=parents_group)
            children_per_combination.append(parents_children)

        children_scores = []
        for children_group in children_per_combination:
            group_scores = self._evaluate_population(children_group)
            children_scores.append(group_scores)

        if num_offspring > len(parents_combinations):
            
            n_children_per_group = num_offspring // len(parents_combinations)
            best_children_per_family = []
            left_children_per_family = []
            left_children_per_family_scores = []
            for idx, family in enumerate(children_per_combination):
                
                family_best_performers = self._extract_top_performers(population=family, scores=children_scores[idx], num_performers=n_children_per_group)
                best_children_per_family += family_best_performers
                
                left_children_per_family.append([child for child in family if child not in family_best_performers])
                family_best_performers_indexes = [family.index(child) for child in family_best_performers]
                left_children_per_family_scores.append(np.delete(children_scores[idx], family_best_performers_indexes))

            if num_offspring%len(parents_combinations) != 0:
                n_missing = num_offspring - len(best_children_per_family)
                left_children = [child for family in range(len(left_children_per_family)) for child in left_children_per_family[family]]
                left_children_scores = np.concatenate([family_score for family_score in left_children_per_family_scores], axis=0)
                best_children_per_family += self._extract_top_performers(population=left_children, scores=left_children_scores, num_performers=n_missing)

            ### Return the children scores in order to not re-evaluate individuals
            best_children_per_family_scores = np.full((len(best_children_per_family),), np.nan)
            for score_idx, child in enumerate(best_children_per_family):
                for family_idx, family in enumerate(children_per_combination):
                    for child_idx, family_child in enumerate(family):
                        if child == family_child:
                            best_children_per_family_scores[score_idx] = children_scores[family_idx][child_idx]
                            
                
            return best_children_per_family, best_children_per_family_scores
        else:
            best_child_per_family = []
            best_children_scores = np.full((len(parents_combinations),), np.nan)
            for family_idx, family in enumerate(children_per_combination):
                family_best_child = self._extract_top_performers(population=family, scores=children_scores[family_idx], num_performers=1)[0]
                family_best_child_score = children_scores[family_idx][family.index(family_best_child)]
                best_children_scores[family_idx] = family_best_child_score
                best_child_per_family.append(family_best_child)
                
            best_children = self._extract_top_performers(population=best_child_per_family, scores=best_children_scores, num_performers=num_offspring)

            best_children_scores = np.full((len(best_children),), np.nan)
            for score_idx, child in enumerate(best_children):
                for family_idx, family in enumerate(children_per_combination):
                    for child_idx, family_child in enumerate(family):
                        if child == family_child:
                            best_children_scores[score_idx] = children_scores[family_idx][child_idx]
                            
            return best_children, best_children_scores

        

    def _reproduce_parents (self, parents):
        """
        Reproduce children from the given parents.

        Args:
            parents (list): List of parent individuals.

        Returns:
            tuple: A tuple of children produced from the parents.
        """
        dna_base = np.full((len(parents), len(list(parents[0].values()))), np.nan)
        for parent_idx, parent in enumerate(parents):
            for attribute_idx, value in enumerate(parent.values()):
                dna_base[parent_idx, attribute_idx] = value
                
        children_dna = []
        for _ in range (self.children_per_parents):
            dna = [dna_base[np.random.randint(dna_base.shape[0]), att] for att in range(dna_base.shape[1])]
            children_dna.append(dna)

        children = []
        for child_dna in children_dna:
            child = {attribute : value for attribute, value in zip(parents[0].keys(), child_dna)}
            child = self._mutate(agent=child)
            children.append(child)

        return tuple(children)

    def _mutate (self, agent):
        """
        Apply mutation to an individual's attributes based on the mutation rate.

        Args:
            agent (dict): The individual to mutate.

        Returns:
            dict: The mutated individual.
        """
        mutated_agent = {}
        for attribute, value in agent.items():
            if np.random.rand() < self.mutation_rate:
                if self.mutation_scale[attribute]['type']=='int':
                    mutation_value = np.random.randint(self.mutation_scale[attribute]['range'][0], self.mutation_scale[attribute]['range'][1])
                elif self.mutation_scale[attribute]['type']=='float':
                    mutation_value = np.random.uniform(self.mutation_scale[attribute]['range'][0], self.mutation_scale[attribute]['range'][1])
                mutated_agent[attribute] = mutation_value
            else:
                mutated_agent[attribute] = value
        return mutated_agent

    def _select_parents (self, population, scores):
        """
        Select parents for reproduction using roulette selection.

        Args:
            population (list): List of individuals in the population.
            scores (array): Fitness scores of the population.

        Returns:
            list: List of selected parents.
        """
        parents = []
        batch_scores=scores
        batch_population = population
        for current_selection in range (self.parents_per_generation):
            selected_parent = self._roulette(population=batch_population, scores=batch_scores)
            parents.append(selected_parent)
            selected_parent_idx = population.index(selected_parent)
            batch_scores = np.concatenate([batch_scores[:selected_parent_idx], batch_scores[selected_parent_idx+1:]], axis=0)
            batch_population = [individual for idx, individual in enumerate(batch_population) if idx != selected_parent_idx]
        return parents
        
    def _roulette(self, population, scores):

        valid_indices = [i for i, score in enumerate(scores) if score >= 0]
        filtered_population = [population[i] for i in valid_indices]
        filtered_scores = [scores[i] for i in valid_indices]

        if len(filtered_scores) == 0:
            raise ValueError("There are no individuals with valid (non-negative) scores for selection")
        probabilities = np.array(filtered_scores) / np.sum(filtered_scores)
        selection_idx = np.random.choice(len(filtered_scores), size=1, p=probabilities).item()
        return filtered_population[selection_idx]

    def _extract_top_performers (self, population, scores, num_performers, return_scores=False):
        population_scores = zip(population, scores)
        sorted_population_scores = sorted(population_scores, key=lambda x: x[1], reverse=True)
        ordered_population, ordered_scores = zip(*sorted_population_scores)
        ordered_population = list(ordered_population)
        ordered_scores = np.array(list(ordered_scores))
        if return_scores:
            return ordered_population[:num_performers], ordered_scores[:num_performers]
        return ordered_population[:num_performers]
            
    def _update_history(self, population, scores, generation):
        self.gen_history.append({
            'Generation': generation,
            'Mean': np.mean(scores),
            'STD': np.std(scores),
            'Min': np.min(scores),
            'Max': np.max(scores)
        })
        for individual_idx, score in zip([i for i in range(len(population))], scores):
            self.pop_history.append({
                'Generation': generation,
                'Individual': individual_idx,
                'Score': score
            })
    def _evaluate_population(self, population):
        """
        Evaluate the fitness of a population.

        Args:
            population (list): List of individuals in the population.

        Returns:
            array: Fitness scores of the population.
        """
        scores = np.full((len(population),), np.nan)
        for individual_idx, individual in enumerate(population):
            if individual_idx==0:
                print()
            print (f"scoring: {individual}")
            if any(individual == _tuple[0] for _tuple in self.individuals):
                tuple_idx = next((i for i, _tuple in enumerate(self.individuals) if _tuple[0] == individual), -1)
                individual_score = self.individuals[tuple_idx][1]
            else:
                individual_score = self.evaluator.evaluate(individual=individual)
            scores[individual_idx] = individual_score
            print (f"{individual_score}")
            self.individuals.append((individual, individual_score))
        return scores


class TrainingSessionManager:
    """
    A class to manage training sessions across multiple configurations, trials, and optional rolling windows.

    Attributes:
        executions_per_configuration (int): 
            Number of trials to run for each hyperparameter configuration.
        configurations (list): 
            A list of dictionaries representing hyperparameter configurations.
        building_func (callable): 
            A function that takes a hyperparameter configuration and returns a compiled model.
        evaluator (callable, optional): 
            An optional callable or object to evaluate a trained model. If provided, it must have an 
            `evaluate(model)` method that overrides the default mechanism for collecting trial results.
        save_weights (bool): 
            Flag indicating whether to save the model weights for each trial and configuration.
        weights_dir (str, optional): 
            Directory to save model weights. Required if save_weights is True.
    """
    def __init__(self, executions_per_configuration, configurations, building_func, evaluator = None, save_weights=False, weights_dir=None):
        """
        Initializes the TrainingSessionManager with configurations, trial counts, and model-building logic.
        
        Parameters:
            executions_per_configuration (int): Number of trials to run per configuration.
            configurations (list): List of dictionaries containing hyperparameter configurations.
            building_func (callable): Function to construct and return a compiled model given a configuration.
            evaluator (callable, optional): Callable or object to evaluate the model after training. Must have an 
                                             `evaluate(model)` method (default: None).
            save_weights (bool): Whether to save model weights after each trial (default: False).
            weights_dir (str, optional): Directory to save model weights, required if save_weights=True.
        
        Raises:
            ValueError: If save_weights is True and weights_dir is not provided or invalid.
        """
        self.executions_per_configuration = executions_per_configuration
        self.configurations = configurations
        self.building_func = building_func
        self.evaluator=evaluator
        self.save_weights=save_weights
        self.weights_dir=weights_dir
        if self.save_weights and not self.weights_dir:
            raise ValueError("If saving weights, must specify the directory")
        if self.save_weights and not os.path.exists(self.weights_dir):
            os.makedirs(self.weights_dir)

    def global_train(self, X, Y, epochs, batch_size, validation_data, verbose, metric, patience, mode):
        """
        Conducts training sessions across all configurations and trials without rolling windows.
        
        Parameters:
            X (array-like): Training input data.
            Y (array-like): Training output data.
            epochs (int): Number of epochs to train.
            batch_size (int): Batch size for training.
            validation_data (tuple): Validation data as a tuple (X_val, Y_val).
            patience (int): Number of epochs with no improvement to wait before early stopping.
            verbose (int): Verbosity level for training logs.
            metric (str): Metric to monitor for early stopping (default: 'val_r2').
            mode (str): One of {'min', 'max'}, defines whether the metric should be minimized or maximized (default: 'max').
        
        Returns:
            dict: Results of all configurations and trials as nested dictionaries.
        """
        results = {}
        print('Searching: ')
        for configuration_idx, configuration in enumerate(self.configurations):
            print(f'configuration: {configuration_idx}')
            configuration_results = {}
            for trial in range(self.executions_per_configuration):
                print(f'trial: {trial}')
                
                model = self.building_func(HyperparametersSelector(configuration))
                if self.save_weights:
                    weights_path = f"{self.weights_dir}/weights_config_{configuration_idx}_trial_{trial}.weights.h5"
                    if os.path.isfile(weights_path):
                        model.load_weights(weights_path)
                        print (f"Configuration {configuration_idx}, Trial {trial} weights loaded")
                    else:
                        current_callbacks = [EarlyStopping(monitor=metric, patience=patience, mode=mode)]
                        trial_history = model.fit(
                            x=X, y=Y, batch_size=batch_size, epochs=epochs, verbose=verbose,
                            callbacks=current_callbacks, validation_data=validation_data
                        )
                        model.save_weights(weights_path)
                        print (f"Configuration {configuration_idx}, Trial {trial} weights saved")
                    if self.evaluator is None:
                        configuration_results[trial] = trial_history.history
                    else:
                        configuration_results[trial] = self.evaluator.evaluate(model)
                else:
                    current_callbacks = [EarlyStopping(monitor=metric, patience=patience, mode=mode)]
                    trial_history = model.fit(
                        x=X, y=Y, batch_size=batch_size, epochs=epochs, verbose=verbose,
                        callbacks=current_callbacks, validation_data=validation_data
                    )
                    if self.evaluator is None:
                        configuration_results[trial] = trial_history.history
                    else:
                        configuration_results[trial] = self.evaluator.evaluate(model)

            results[configuration_idx] = configuration_results
        return results

    def rolling_train(self, X, Y, epochs, batch_size, validation_data, verbose, metric, patience, mode):
        """
        Conducts training sessions across all configurations and trials using rolling windows.
        
        Parameters:
            X (array-like): Training input data, structured for rolling windows.
            Y (array-like): Training output data, structured for rolling windows.
            epochs (int): Number of epochs to train.
            batch_size (int): Batch size for training.
            validation_data (tuple): Validation data as a tuple (X_val, Y_val) for rolling windows.
            patience (int): Number of epochs with no improvement to wait before early stopping.
            verbose (int): Verbosity level for training logs.
            metric (str): Metric to monitor for early stopping (default: 'val_r2').
            mode (str): One of {'min', 'max'}, defines whether the metric should be minimized or maximized (default: 'max').
        
        Returns:
            dict: Results of all configurations, trials, and windows as nested dictionaries.
        """
        results = {}
        print('Searching: ')
        for configuration_idx, configuration in enumerate(self.configurations):
            print(f'configuration: {configuration_idx}')
            configuration_results = {}
            for trial in range(self.executions_per_configuration):
                print(f'trial: {trial}')
                trial_results = {}
                for window in range(X.shape[3]):
                    print(f'window: {window + 1}/{X.shape[3]}')
                    model = self.building_func(HyperparametersSelector(configuration))
                    if self.save_weights:
                        weights_path = f"{self.weights_dir}/weights_config_{configuration_idx}_trial_{trial}_window_{window}.weights.h5"
                        if os.path.isfile(weights_path):
                            model.load_weights(weights_path)
                            print (f"Configuration {configuration_idx}, Trial {trial}, Window {window} weights loaded")
                        else:
                            current_callbacks = [EarlyStopping(monitor=metric, patience=patience, mode=mode)]
                            window_history = model.fit(
                                x=X[..., window], y=Y[..., window], batch_size=batch_size, epochs=epochs, verbose=verbose,
                                callbacks=current_callbacks,
                                validation_data=(validation_data[0][..., window], validation_data[1][..., window])
                            )
                            model.save_weights(weights_path)
                            print (f"Configuration {configuration_idx}, Trial {trial}, Window {window} weights saved")
                        if self.evaluator is None:
                            trial_results[window] = window_history.history
                        else:
                            trial_results[window] = self.evaluator.evaluate(model)
                    else:
                        current_callbacks = [EarlyStopping(monitor=metric, patience=patience, mode=mode)]
                        window_history = model.fit(
                            x=X[..., window], y=Y[..., window], batch_size=batch_size, epochs=epochs, verbose=verbose,
                            callbacks=current_callbacks,
                            validation_data=(validation_data[0][..., window], validation_data[1][..., window])
                        )
                        if self.evaluator is None:
                            trial_results[window] = window_history.history
                        else:
                            trial_results[window] = self.evaluator.evaluate(model)
                configuration_results[trial] = trial_results
            results[configuration_idx] = configuration_results
        return results

    def global_redistribute(self, results):
        """
        Restructures global training results into a Pandas DataFrame.
        
        Parameters:
            results (dict): Results from global training organized by configuration and trial.
        
        Returns:
            pd.DataFrame: Restructured results with columns:
                - Configuration: Index of the hyperparameter configuration.
                - Trial: Index of the trial.
                - Epoch: Epoch number.
                - Metric: Metric name (e.g., loss, accuracy).
                - Value: Metric value.
        """
        redistributed_results = []
        for configuration_idx in results:
            configuration_results = results[configuration_idx]
            for trial_idx in configuration_results:
                trial_results = configuration_results[trial_idx]
                for epoch in range (len(list(trial_results.values())[0])):
                    for metric in trial_results.keys():
                        redistributed_results.append({
                            'Configuration': configuration_idx,
                            'Trial': trial_idx,
                            'Epoch': epoch,
                            'Metric': metric,
                            'Value': trial_results[metric][epoch]
                        })
        return pd.DataFrame(redistributed_results)

    def rolling_redistribute(self, results):
        """
        Restructures rolling training results into a Pandas DataFrame.
        
        Parameters:
            results (dict): Results from rolling training organized by configuration, trial, and window.
        
        Returns:
            pd.DataFrame: Restructured results with columns:
                - Configuration: Index of the hyperparameter configuration.
                - Trial: Index of the trial.
                - Window: Index of the rolling window.
                - Epoch: Epoch number.
                - Metric: Metric name (e.g., loss, accuracy).
                - Value: Metric value.
        """
        redistributed_results = []
        for configuration_idx in results:
            configuration_results = results[configuration_idx]
            for trial_idx in configuration_results:
                trial_results = configuration_results[trial_idx]
                for window_idx in trial_results:
                    window_results = trial_results[window_idx]
                    for epoch in range (len(list(window_results.values())[0])):
                        for metric in window_results:
                            redistributed_results.append({
                                'Configuration': configuration_idx,
                                'Trial': trial_idx,
                                'Window': window_idx,
                                'Epoch': epoch,
                                'Metric': metric,
                                'Value': window_results[metric][epoch]
                            })
        return pd.DataFrame(redistributed_results)

class ModelTuner ():
    """
    A class to tune machine learning models over multiple hyperparameter configurations and trials.

    This class facilitates the process of hyperparameter tuning by testing multiple configurations of 
    hyperparameters on a provided model architecture over a series of trials. Each configuration is evaluated
    with a rolling window over the data, and the results are cleaned and returned as structured data.

    Attributes:
    -----------
    post_transformation_pipeline : object
        A transformation pipeline to be applied after the main transformations.
        
    transformation_pipeline : object
        A transformation pipeline used to preprocess the original data before model training.
        
    transformed_df : pd.DataFrame
        The transformed DataFrame used for training the models.
        
    recovered_df : pd.DataFrame
        The original DataFrame recovered by applying the inverse transformation to `transformed_df`.
        
    building_func : callable
        A function that builds and returns a machine learning model based on hyperparameters.
        
    directory : str
        Directory path where model weights will be stored after training.

    Methods:
    --------
    search(hyperparameters, X, Y, epochs, num_trials, roll_size, callbacks, verbose=0, batch_size=32, data_freq='D', state='transformed'):
        Performs hyperparameter tuning by iterating over different hyperparameter configurations and trials.
        
    _construct_model_(hps_configuration, X, Y, epochs, batch_size, callbacks, verbose, weights_path=False):
        Builds and trains a model based on a hyperparameter configuration and optionally loads pre-trained weights.
        
    _is_iterable_(obj):
        Helper method to check if the provided object is iterable.
        
    _clean_evaluation_(evaluation):
        Cleans and structures the model evaluation results into a dictionary of dataframes where each key is 
        a metric and each dataframe contains trial results for that metric.
    """
    def __init__ (self, post_transformation_pipeline, transformation_pipeline, transformed_df, building_func, directory):
        """
        Initializes the ModelTuner object with transformation pipelines, data, and model-building function.
        
        Parameters:
        -----------
        post_transformation_pipeline : object
            The pipeline that will be applied to the data after the model predictions.
        
        transformation_pipeline : object
            The pipeline used to transform the input data before training.
        
        transformed_df : pd.DataFrame
            The DataFrame containing the transformed data.
        
        building_func : callable
            A function that takes a hyperparameters object and returns a model.
        
        directory : str
            Path where model weights and logs will be stored.
        """
        self.post_transformation_pipeline=post_transformation_pipeline
        self.transformation_pipeline=transformation_pipeline
        self.transformed_df=transformed_df
        self.recovered_df=transformation_pipeline.inverse_transform(transformed_df)
        self.building_func=building_func
        self.directory=directory
    def search (self, hyperparameters, X, Y, validation_data, epochs, num_trials, roll_size, callbacks, verbose=0, batch_size=32, data_freq='D', state='transformed'):
        """
        Searches over a set of hyperparameter configurations and evaluates models across multiple trials.
        
        Parameters:
        -----------
        hyperparameters : iterable
            A collection of hyperparameter configurations to be tested.
            
        X : np.array or pd.DataFrame
            Input features for training the model.
            
        Y : np.array or pd.DataFrame
            Target values for training the model.

        validation_vata : tuple
            Validation_data
            
        epochs : int
            Number of epochs to train each model.
            
        num_trials : int
            Number of trials for each hyperparameter configuration.
            
        roll_size : int
            Size of the rolling window to use when evaluating model performance.
            
        callbacks : list
            List of callback functions to be used during model training.
            
        verbose : int, optional (default=0)
            Verbosity mode for model training.
            
        batch_size : int, optional (default=32)
            Batch size to use during model training.
            
        data_freq : str, optional (default='D')
            Frequency of the data used for the model.
            
        state : str, optional (default='transformed')
            Indicates whether the state of the data is 'transformed' or 'raw'.
            
        Returns:
        --------
        dict
            A dictionary containing the cleaned evaluation metrics for each hyperparameter configuration and trial.
        """
        if not isinstance(hyperparameters, list):
            raise ValueError(f'hyperparameters parameter must be a list')
        if not all (isinstance(element, dict) for element in hyperparameters):
            raise ValueError(f'hyperparametrs parameter must contain only dictionaries')
        evaluations = {}
        os.makedirs(self.directory, exist_ok=True)
        for hps_idx, hps_configuration in enumerate(hyperparameters):
            print (f'searching configuration: {hps_idx}')
            model_evaluations = {}
            for trial in range (num_trials):
                print (f'trial: {trial}')
                current_callbacks = []
                for callback in callbacks:
                    if isinstance(callback, EarlyStopping):
                        # Crear una nueva instancia de EarlyStopping para este trial
                        new_early_stopping = EarlyStopping(monitor=callback.monitor,
                                                           patience=callback.patience,
                                                           mode=callback.mode,
                                                           restore_best_weights=callback.restore_best_weights)
                        current_callbacks.append(new_early_stopping)
                    else:
                        current_callbacks.append(callback)
                trial_weights_path = f'{self.directory}/{hps_idx}_{trial}.weights.h5'
                if os.path.exists(trial_weights_path):
                    model = self._construct_model_(hps_configuration=hps_configuration,
                                                   X=X,
                                                   Y=Y,
                                                   validation_data=validation_data,
                                                   epochs=epochs,
                                                   batch_size=batch_size,
                                                   callbacks=current_callbacks,
                                                   verbose=verbose,
                                                   weights_path=trial_weights_path
                                                   )
                else:
                    model = self._construct_model_(hps_configuration=hps_configuration,
                                                   X=X,
                                                   Y=Y,
                                                   validation_data=validation_data,
                                                   epochs=epochs,
                                                   batch_size=batch_size,
                                                   callbacks=current_callbacks,
                                                   verbose=verbose
                                                   )
                    model.save_weights(filepath=trial_weights_path)
                manager = ModelManager(post_transformation_pipeline=self.post_transformation_pipeline,
                                       transformation_pipeline=self.transformation_pipeline,
                                       transformed_df=self.transformed_df, model=model)
                evaluation = manager.evaluate(roll_size=roll_size, state=state).iloc[:-1, :]
                model_evaluations[trial] = evaluation
            evaluations[hps_idx] = model_evaluations
        cleaned_evaluations = self._clean_evaluation_(evaluation=evaluations)
        return cleaned_evaluations
    def _construct_model_(self, hps_configuration, X, Y, validation_data, epochs, batch_size, callbacks, verbose, weights_path=False):
        """
        Constructs and trains a model based on the provided hyperparameter configuration.
        
        Parameters:
        -----------
        hps_configuration : dict
            Hyperparameter configuration for the model.
            
        X : np.array or pd.DataFrame
            Input features for training.
            
        Y : np.array or pd.DataFrame
            Target values for training.
            
        validation_vata : tuple
            Validation_data
            
        epochs : int
            Number of epochs to train the model.
            
        batch_size : int
            Batch size to use during training.
            
        callbacks : list
            List of callback functions to be used during training.
            
        verbose : int
            Verbosity mode for model training.
            
        weights_path : str, optional (default=False)
            Path to pre-trained weights. If provided, the model will load these weights before training.
            
        Returns:
        --------
        model
            The constructed and trained machine learning model.
        """
        hp_object = HyperparametersSelector(hps_configuration = hps_configuration)
        model = self.building_func(hp_object)
        if weights_path:
            model.load_weights(filepath=weights_path)
            return model
        model.fit(x=X, y=Y, validation_data=validation_data, epochs=epochs, batch_size=batch_size, callbacks=callbacks, verbose=verbose)
        return model
    def _clean_evaluation_ (self, evaluation):
        """
        Cleans and organizes evaluation results into a structured format.
        
        Parameters:
        -----------
        evaluation : dict
            The raw evaluation data, where keys are hyperparameter configurations and values are dictionaries
            of trial results.
            
        Returns:
        --------
        dict
            A dictionary of DataFrames where each key is a metric and each DataFrame contains results for 
            that metric across different hyperparameter configurations and trials.
        """
        metrics_dict = {}
        for hps_config, trials in evaluation.items():
            for trial, df in trials.items():
                for metric in df.columns:
                    if metric not in metrics_dict:
                        metrics_dict[metric] = pd.DataFrame(columns=['Hps_config', 'trial'] + df.index.tolist())
                    new_row = pd.Series([hps_config, trial] + df[metric].tolist(), index=metrics_dict[metric].columns)
                    metrics_dict[metric] = pd.concat([metrics_dict[metric], new_row.to_frame().T], ignore_index=True)
        return metrics_dict


class HyperparametersSelector:
    """
    A class for selecting hyperparameters based on given configurations.

    Attributes:
        hps (dict): A dictionary to store hyperparameter names and their selected values.

    Methods:
        Int(name, min_value, max_value, step): Returns an integer hyperparameter.
        Float(name, min_value, max_value, step): Returns a floating-point hyperparameter.
        Choice(name, values): Returns a choice from given possible values.
        _get_values_(): Returns the dictionary of all hyperparameter values.
    """

    def __init__(self, hps_configuration=None):
        """
        Initializes the HyperparametersSelection with an optional hyperparameters configuration.

        Args:
            hps_configuration (dict, optional): A pre-defined dictionary of hyperparameters. Defaults to None.
        """
        self.hps = {} if hps_configuration is None else hps_configuration

    def Int(self, name, min_value, max_value, step):
        """
        Generates or retrieves an integer hyperparameter within the specified range, using the specified step.

        Args:
            name (str): The name of the hyperparameter.
            min_value (int): The minimum value of the range.
            max_value (int): The maximum value of the range.
            step (int): The step between possible values within the range.

        Returns:
            int: The chosen or retrieved integer value for the hyperparameter.

        Raises:
            ValueError: If min_value is greater than max_value or if step is not positive.
        """
        if name in self.hps:
            return self.hps[name]
        if min_value > max_value:
            raise ValueError("min_val must be less than or equal to max_val")
        if step <= 0:
            raise ValueError("step must be a positive number")
        number = random.choice(range(min_value, max_value + 1, step))
        self.hps[name] = number
        return number

    def Float(self, name, min_value, max_value, step):
        """
        Generates or retrieves a floating-point hyperparameter within the specified range, using the specified step.

        Args:
            name (str): The name of the hyperparameter.
            min_value (float): The minimum value of the range.
            max_value (float): The maximum value of the range.
            step (float): The step between possible values within the range.

        Returns:
            float: The chosen or retrieved floating-point value for the hyperparameter.

        Raises:
            ValueError: If min_value is greater than max_value or if step is not positive.
        """
        if name in self.hps:
            return self.hps[name]
        if min_value > max_value:
            raise ValueError("min_val must be less than or equal to max_val")
        if step <= 0:
            raise ValueError("step must be a positive number")
        number = random.choice([min_value + i * step for i in range(int((max_value - min_value) / step) + 1)])
        self.hps[name] = number
        return number

    def Choice(self, name, values):
        """
        Chooses or retrieves a value from a list of possible values for a hyperparameter.

        Args:
            name (str): The name of the hyperparameter.
            values (list): A list of possible values from which to choose.

        Returns:
            Any: The chosen or retrieved value from the list.

        Raises:
            ValueError: If the list of possible values is empty.
        """
        if name in self.hps:
            return self.hps[name]
        if isinstance(values, list):
            if not values:
                raise ValueError("list cannot be empty")
        elif isinstance(values, np.ndarray):
            if values.size == 0:
                raise ValueError("array cannot be empty")
        election = random.choice(values)
        self.hps[name] = election
        return election

    def _get_values_(self):
        """
        Retrieves the dictionary containing all hyperparameter names and their selected values.

        Returns:
            dict: The dictionary of hyperparameter names and values.
        """
        return self.hps


class RandomSearch:
    """
    A class to perform random hyperparameter search for machine learning models.

    Attributes:
        building_func (callable): 
            A function that generates and compiles a machine learning model based on hyperparameter configurations.
        max_trials (int): 
            The maximum number of random hyperparameter configurations to evaluate.
        executions_per_trial (int): 
            The number of training trials to execute for each configuration.
        evaluator (callable, optional): 
            An optional callable or object to evaluate trained models. If provided, it must have an `evaluate(model)` method.
        save_weights (bool): 
            Flag indicating whether to save model weights for each trial and configuration.
        weights_dir (str, optional): 
            Directory to save model weights. Required if save_weights is True.
    """
    
    def __init__(self, building_func, max_trials, executions_per_trial):
        """
        Initializes the RandomSearch class with the required parameters.

        Parameters:
            building_func (callable): 
                A function that takes a hyperparameter object and returns a compiled model.
            max_trials (int): 
                The maximum number of random hyperparameter configurations to generate.
            executions_per_trial (int): 
                The number of training trials to run for each configuration.
            evaluator (callable, optional): 
                Callable or object to evaluate trained models. Must have an `evaluate(model)` method (default: None).
            save_weights (bool): 
                Whether to save model weights after each trial (default: False).
            weights_dir (str, optional): 
                Directory to save model weights. Required if save_weights=True.

        Raises:
            ValueError: If save_weights is True and weights_dir is not provided or invalid.
        """
        self.building_func = building_func
        self.max_trials = max_trials
        self.executions_per_trial = executions_per_trial

    def search(self, X, Y, epochs, batch_size, validation_data, verbose, metric, patience, mode):
        """
        Performs the random search by generating configurations, training models, and collecting results.

        Parameters:
            X (array-like): 
                Training input data. If `X` has 3 dimensions, global training is used. Otherwise, rolling training is applied.
            Y (array-like): 
                Training output data.
            epochs (int): 
                Number of epochs for training.
            batch_size (int): 
                Batch size for training.
            validation_data (tuple): 
                Validation data as a tuple `(X_val, Y_val)`.
            patience (int): 
                Number of epochs with no improvement to wait before stopping early.
            metric (str): 
                Metric to monitor for early stopping (default: 'val_r2').
            mode (str): 
                One of {'min', 'max'}. Defines whether the monitored metric should be minimized or maximized (default: 'max').
            verbose (int, optional): 
                Verbosity level for training logs (default: 1).

        Returns:
            configurations (list): 
                List of randomly generated hyperparameter configurations.
            results (pd.DataFrame): 
                Consolidated results of all configurations and trials.
        """
        configurations = []
        # Generate random configurations
        for trial in range(self.max_trials):
            hp_object = HyperparametersSelector()
            _ = self.building_func(hp_object)  # Build model to validate the configuration
            configurations.append(hp_object._get_values_())  # Store configuration
        
        # Initialize TrainingSessionManager
        self.session_manager = TrainingSessionManager(
            executions_per_configuration=self.executions_per_trial,
            configurations=configurations,
            building_func=self.building_func
        )
        
        # Perform training
        if X.ndim == 3:  # Global training for 3D input
            results = self.session_manager.global_train(
                X=X, Y=Y, epochs=epochs, batch_size=batch_size, 
                validation_data=validation_data, verbose=verbose,
                metric=metric, patience=patience, mode=mode
            )
        else:  # Rolling training for higher-dimensional input
            results = self.session_manager.rolling_train(
                X=X, Y=Y, epochs=epochs, batch_size=batch_size, 
                validation_data=validation_data, verbose=verbose,
                metric=metric, patience=patience, mode=mode
            )
        
        return configurations, results