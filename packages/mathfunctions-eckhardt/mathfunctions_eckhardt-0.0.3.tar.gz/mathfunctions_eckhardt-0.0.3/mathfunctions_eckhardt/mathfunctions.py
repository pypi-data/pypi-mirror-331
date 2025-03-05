def multmat(size, matrizA, matrizB):

    if not isinstance(size, int):
        raise TypeError("O tamanho deve ser do tipo inteiro")

    if size <= 0:
        raise ValueError("Digite um número maior que zero")
    
    if len(matrizA) != size or len(matrizB) != size:
        raise ValueError(f"As matrizes devem possuir a quantidade de valores respectivos a uma matriz {size} x {size}")
    
    for row in matrizA:
        if len(row) != size:
            raise ValueError(f"Todas as linhas da matriz de entrada devem ter tamanho {size}")
    
    for row in matrizB:
        if len(row) != size:
            raise ValueError(f"Todas as linhas da matriz de entrada devem ter tamanho {size}")

    result_matriz = [[0] * size for _ in range(size)]
    
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result_matriz[i][j] += matrizA[i][k] * matrizB[k][j]
    
    for linha in result_matriz:
        print(" ".join(f"{num:4}" for num in linha))

    return result_matriz