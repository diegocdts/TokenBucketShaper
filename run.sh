# rates
# 26000000.00
# 52000000.00

# flows
# 100
# 150
# 200

# rhos
# 3000
# 5000

# sigmas
# 5
# 10

#python main.py --flows 100 --lambda_param 1000 --rho 1000 --sigma 2

# lambda abaixo do calculado
#python main.py --fixed_rate 26000000.00 --flows 100 --rho 2000 --sigma 5 --lambda_param 2015 #lambda_param max = 2025 # rho < lambda
#python main.py --fixed_rate 26000000.00 --flows 100 --rho 3000 --sigma 5 --lambda_param 2015 #lambda_param max = 2025 # rho > lambda

# lambda acima do calculado
python main.py --fixed_rate 26000000.00 --flows 100 --rho 2000 --sigma 5 --lambda_param 2035 #lambda_param max = 2025 # rho < lambda
python main.py --fixed_rate 26000000.00 --flows 100 --rho 3000 --sigma 5 --lambda_param 2035 #lambda_param max = 2025 # rho > lambda
