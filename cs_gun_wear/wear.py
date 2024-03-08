from itertools import combinations


def calculate_result(max_value, min_value, selected_numbers):
    avg_value = sum(selected_numbers) / len(selected_numbers)
    result = ((max_value - min_value) * avg_value) + min_value
    return result


# 从txt文件中读取数据
with open('input.txt', 'r') as file:
    lines = file.readlines()
    max_val = float(lines[0].strip())
    min_val = float(lines[1].strip())
    input_numbers = [float(x.strip()) for x in lines[2:]]
    target_result = float(lines[-1].strip())

# 从输入数字中选择任意10个数字的组合
number_combinations = list(combinations(input_numbers, 10))

running_count = 0
best_combination = None
best_wear = None
best_difference = float('inf')

# 针对每个组合计算结果并找到最接近目标结果的组合
for combo in number_combinations:
    output = calculate_result(max_val, min_val, combo)
    difference = abs(output - target_result)
    if difference < best_difference:
        best_difference = difference
        best_combination = combo
        best_wear = output
    running_count += 1
    if running_count % 10000 == 0:
        print(running_count, '/', len(number_combinations))

print("最接近目标结果的组合为:", best_combination)
print("结果为:", best_wear)
