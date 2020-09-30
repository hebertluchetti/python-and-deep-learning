from builtins import Exception

import torch
import random
import numpy as np
import copy
import os
from neural_network import CompressedModel

class DeepGA:
    MODEL_FILE_NAME = 'epoch_'

    def __init__(self, population_size):
        self.models = [CompressedModel() for _ in range(population_size)]
        self.population_size = population_size

        self.fitness_truncation = population_size//4
        if self.fitness_truncation < 1:
            self.fitness_truncation = 1

    def get_models(self):
        return self.models

    # The reward is used for sorting the neural networks from worst to best.
    def get_best_models(self, cars):
        fitness_scores = [car.reward() for car in cars]
        indexes = [car.index for car in cars]
        names = [car.name for car in cars]
        scored_models = list(zip(self.models, fitness_scores, indexes, names))
        scored_models.sort(key=lambda x: x[1], reverse=True)
        return scored_models

    def select_best_models(self, cars):
        # Apply sorting of the neural networks according to biggest reward
        scored_models = self.get_best_models(cars)

        # Get only the sorted fitness scores
        best_model = scored_models[0][0]
        best_score = scored_models[0][1]
        best_car = cars[scored_models[0][2]]
        best_car_name = scored_models[0][3]

        #print("---------------- select_best_models=", best_car_name, ", score=", best_score, "Number of cars:",len(cars),"\n")

        # for model in scored_models:
        #     print("Car=", model[3], ", index=", model[2], ", score=", model[1])


        return scored_models, best_score, best_model, best_car

    def reward_score_models(self, cars, truncation):
        # Apply sorting of the neural networks according to biggest reward
        scored_models, best_score, best_model, best_car = self.select_best_models(cars)

        #best_scores = [s for _, s, _, _ in scored_models]

        # Get only the sorted fitness scores
        best_scores = [s for _, s, _, _ in scored_models]
        # Calculate the reward parameters to evolve the populations
        median_score = np.median(best_scores)
        mean_score = np.mean(best_scores)

        # Get only the N=truncation best individuals
        scored_models = scored_models[:truncation]

        return (median_score, mean_score, best_score), scored_models, best_model, best_car

    def evolve_population(self, cars, truncation=None, sigma=0.05, best_model_path=None):
        if truncation is None:
            truncation = self.fitness_truncation

        # Calculate the reward values to evolve the population and
        # get the best models and cars according to biggest reward
        scores, scored_models, best_model, best_car = self.reward_score_models(cars, truncation)

        best_model_file_name = None
        if best_model_path is not None:
            best_model_file_name = self.save_model(best_model_path, best_model)

        # Process the evolution by Elitism
        self.models = self.process_elitism(sigma, self.population_size, best_model, scored_models)

        return scores, best_car, best_model_file_name, best_model

    def process_elitism(self, sigma, population_size, best_model, scored_models):
        # Create the new population with the first individual as the best one
        car_models = [best_model]

        # Populate with individuals best rewarded except the first one
        for _ in range(population_size-1):
            # Process crossover randomly
            random_child_model = random.choice(scored_models)[0]
            car_models.append(copy.deepcopy(random_child_model))

            # Process evolution only to the last individual
            car_models[-1].evolve(sigma)

        return car_models

    def save_model(self, best_model_path, model):
        if best_model_path is not None:
            epoch = best_model_path[1]
            path = best_model_path[0]
            file_name_path = os.path.join(path, self.MODEL_FILE_NAME + str(epoch) + '.pth')
            car_model = model.uncompress_model()

            if os.path.isdir(path) is False:
                os.makedirs(path)

            # checkpoint = {
            #     "epoch": epoch,
            #     "model_state": model.state_dict(),
            #     "optim_state": None #optimizer.state_dict()
            # }

            torch.save(car_model, file_name_path)
            return file_name_path

        return None

    def load_model(self, best_model_path):
        print('Loading model ...')
        if best_model_path is not None:
            file_name_path = best_model_path

            try:
                loaded_model = torch.load(file_name_path)
                loaded_model.eval()
                return loaded_model
            except Exception as e:
                pass

        return None

