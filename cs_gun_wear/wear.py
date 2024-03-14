from itertools import combinations
import numpy as np


class Calculator:
    def __init__(self, filename):
        self.filename = filename
        self.max_val = None
        self.min_val = None
        self.input_numbers = []
        self.target_result = None
        self.running_count = 0

    def read_input(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()
            self.max_val = float(lines[0].strip())
            self.min_val = float(lines[1].strip())
            self.input_numbers = [float(x.strip()) for x in lines[2:-1]]
            self.target_result = float(lines[-1].strip())
        print(self.input_numbers)
        print(self.target_result)

    def calculate_result(self, selected_numbers):
        avg_value = sum(selected_numbers) / len(selected_numbers)
        return ((self.max_val - self.min_val) * avg_value) + self.min_val

    def generate_combinations(self, r):
        for combo in combinations(self.input_numbers, r):
            yield combo

    def find_best_combination(self):
        best_combination = None
        best_wear = None
        best_difference = float('inf')

        for combo in self.generate_combinations(10):
            output = self.calculate_result(combo)
            difference = abs(output - self.target_result)
            if difference < best_difference:
                best_difference = difference
                best_combination = combo
                best_wear = output
            self.running_count += 1
            if self.running_count % 10000 == 0:
                print(self.running_count, '/', '10')

        print("最接近目标结果的组合为:", best_combination)
        print("结果为:", best_wear)


if __name__ == "__main__":
    calculator = Calculator('input.txt')
    calculator.read_input()
    calculator.find_best_combination()
