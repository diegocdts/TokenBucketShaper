# TokenBucket

## Argumentos e valores padrão

--seed: Semente para números aleatórios.

--flows: Especifica o número total de fluxos

--lambda_param: Parâmetro lambda para os valores aleatórios de distribuição exponencial

--rho: Especifica o número de tokens a serem criados por segundo (cada byte consome um token)

--sigma: Especifica a capacidade máxima do bucket (em bytes)

--max_queue_occupancy: Especifica o tamanho máximo da fila de transmissão

--delay_sla: Especifica o atraso máximo permitido (padrão: 0.01s).

--max_time: Especifica o tempo máximo de execução do programa em segundos (padrão: 300 segundos).

--mtu: Maximum Transmission Unit (padrão: 1 byte)

--rate_percentage: Percentual da taxa calculada de transmissão a ser usada (padrão: 100%).

--sampling_interval: Intervalo de amostragem (padrão: 0.001s).

--sampling_window: Janela de tempo para criar novo conjunto de arquivos de amostras (padrão: 60 segundos)