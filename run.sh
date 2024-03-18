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

# lambda ≤ R / (N * mtu)

# base
# python main.py --flows 100 --lambda_param 1000 --rho 1000 --sigma 2

# lambda inferior e superior ao calculado (2031)
# python main.py --flows 100 --lambda_param 2025 --rho 2125 --sigma 5 --fixed_rate 26000000
# python main.py --flows 100 --lambda_param 2050 --rho 2150 --sigma 5 --fixed_rate 26000000

# lambda = rho
# python main.py --flows 100 --lambda_param 2025 --rho 2025 --sigma 5 --fixed_rate 26000000
# python main.py --flows 100 --lambda_param 2050 --rho 2050 --sigma 5 --fixed_rate 26000000

# sigma = 10
# python main.py --flows 100 --lambda_param 2025 --rho 2125 --sigma 10 --fixed_rate 26000000

# número de fluxos = 1000
# base
#python main.py --flows 200 --lambda_param 1000 --rho 1000 --sigma 2

# lambda inferior ao calculado
python main.py --flows 200 --lambda_param 2025 --rho 2125 --sigma 5 --fixed_rate 52000000

# sigma = 10
python main.py --flows 200 --lambda_param 2025 --rho 2125 --sigma 10 --fixed_rate 52000000