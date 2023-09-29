# TokenBucket

## Argumentos e valores padrão

--seed: Semente para números aleatórios.

--flows: Especifica o número total de fluxos (padrão: 10).

--lambda_param: Parâmetro lambda para os valores aleatórios de distribuição exponencial (padrão: 1000).

--tokens: Especifica o número de tokens a serem criados por segundo (padrão: 128000 bytes).

--bucket_capacity: Especifica a capacidade máxima do bucket (padrão: 12800 bytes).

--max_queue_occupancy: Especifica o tamanho máximo da fila de transmissão em bytes (padrão: 999999999999999999999999 bytes).

--delay_sla: Especifica o atraso máximo permitido (padrão: 0.01s).

--max_time: Especifica o tempo máximo de execução do programa em segundos (padrão: 2000 segundos).

--mtu: Maximum Transmission Unit (padrão: 128 bytes).

--rate_percentage: Percentual da taxa calculada de transmissão a ser usada (padrão: 100%).

--sampling_interval: Intervalo de amostragem (padrão: 0.001s).

--sampling_window: Janela de tempo para criar novo conjunto de arquivos de amostras (padrão: 200s)