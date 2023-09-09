#-------------------------------------------------------------------------------------------------------------
# Carregando os corais
#-------------------------------------------------------------------------------------------------------------

import pandas as pd

def load_chorales(filepaths):
    # Carrega cada arquivo CSV em filepaths usando o pandas e converte o conteúdo para uma lista de listas
    return [pd.read_csv(filepath).values.tolist() for filepath in filepaths]

#-------------------------------------------------------------------------------------------------------------



#-------------------------------------------------------------------------------------------------------------
# Download dos corais
#-------------------------------------------------------------------------------------------------------------

import keras

def download_chorales_file(download_root="https://tinyurl.com/2d2ammnn/",
                           filename="jsb_chorales.tgz"):
    """
    Baixa o arquivo de corais JSB.

    Parâmetros:
    - download_root (str): URL base para download.
    - filename (str): Nome do arquivo para baixar.

    Retorna:
    - str: Caminho para o arquivo baixado e extraído.
    """
    filepath = keras.utils.get_file(filename,
                                    download_root + filename,
                                    cache_subdir="datasets/jsb_chorales",
                                    extract=True)
    return filepath



#-------------------------------------------------------------------------------------------------------------
# Verificando o dataset: notas mínimas e máximas
#-------------------------------------------------------------------------------------------------------------

def get_min_max_notes(train_chorales, valid_chorales, test_chorales):
    """Obtém as notas mínima e máxima a partir dos conjuntos fornecidos.
    
    Parâmetros:
        train_chorales, valid_chorales, test_chorales (list): Listas de conjuntos de chorales.

    Retorna:
        min_note (int): Nota mínima encontrada.
        max_note (int): Nota máxima encontrada.
    """
    
    notes = set()  # Cria um conjunto vazio para armazenar as notas
    
    # Percorre os conjuntos de treinamento, validação e teste
    for chorales in (train_chorales, valid_chorales, test_chorales):
        for chorale in chorales:  # Percorre cada chorale dentro do conjunto
            for chord in chorale:  # Percorre cada chord dentro do chorale
                notes |= set(chord)  # Adiciona as notas do chord ao conjunto 'notes'
    
    n_notes = len(notes)  # Obtém o número total de notas únicas
    min_note = min(notes - {0})  # Encontra a nota mínima, excluindo a nota 0
    max_note = max(notes)  # Encontra a nota máxima
    
    # Verifica se as notas mínima e máxima estão corretas, caso contrário, interrompe
    # a execução do programa
    assert min_note == 36
    assert max_note == 81

    return min_note, max_note, n_notes

    """
    Neste código, um conjunto vazio chamado `notes` é criado para armazenar as notas encontradas nos dados musicais. Em seguida, um loop é realizado sobre os conjuntos de treinamento,         validação e teste. Dentro de cada conjunto, são percorridos os chorales e, em seguida, os chords de cada chorale. As notas de cada chord são adicionadas ao conjunto `notes` usando a       operação de união (`|=`).

    Após o loop, o número total de notas únicas é obtido através do comprimento do conjunto `notes` armazenado na variável `n_notes`. A nota mínima é encontrada usando a função `min`,         excluindo a nota 0 do conjunto `notes - {0}` e armazenada na variável `min_note`. A nota máxima é encontrada usando a função `max` no conjunto `notes` e armazenada na variável             `max_note`.

    Em seguida, o código verifica se as notas mínima e máxima estão corretas usando as declarações assert. Se as verificações falharem, será lançada uma exceção para indicar que algo está     errado. Neste caso, o código verifica se `min_note` é igual a 36 e se `max_note` é igual a 81.
    """
#-------------------------------------------------------------------------------------------------------------



#-------------------------------------------------------------------------------------------------------------
# Visualizando o treinamento
#-------------------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import numpy as np

def plot_metrics(history, metrics=['loss', 'accuracy']):
    """Plota o gráfico das métricas do treinamento e validação a partir de um objeto history.

    Parâmetros:
        history (object): Objeto history retornado por model.fit().
        metrics (list): Lista de métricas que deseja plotar.
    """
    
    # Estilo
    plt.style.use('ggplot')
    
    n_metrics = len(metrics)
    n_cols = 2
    n_rows = (n_metrics + 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 5 * n_rows))

    # Caso tenha apenas uma métrica, ajusta a estrutura do axes para ser indexável
    if n_metrics == 1:
        axes = np.array([axes])

    for i, metric in enumerate(metrics):
        ax = axes[i // n_cols, i % n_cols]

        # Plot metric
        train_metric = history.history[metric]
        ax.plot(train_metric, label=f'Train {metric.capitalize()}', marker='o', linestyle='-', linewidth=2)

        # Plot validation metric
        val_metric_key = f'val_{metric}'
        if val_metric_key in history.history:
            val_metric = history.history[val_metric_key]
            ax.plot(val_metric, label=f'Validation {metric.capitalize()}', marker='o', linestyle='-', linewidth=2)

        # Título, etiquetas e outras configurações
        ax.set_title(f'Model {metric.capitalize()}', fontsize=16)
        ax.set_ylabel(metric.capitalize(), fontsize=14)
        ax.set_xlabel('Epoch', fontsize=14)
        ax.legend(fontsize=12, loc='upper right')
        
        # Grid personalizado
        ax.grid(True, which='both', linestyle=':', linewidth=0.5, color='gray')

    # Remove possíveis subplots vazios
    if n_metrics % 2 == 1:
        fig.delaxes(axes[n_rows - 1, n_cols - 1])
    
    plt.tight_layout()
    plt.show()

# Uso da função:
# plot_metrics(history, metrics=['loss', 'accuracy', 'val_loss', 'val_accuracy'])

#-------------------------------------------------------------------------------------------------------------



#-------------------------------------------------------------------------------------------------------------
# Comparando com o coral de referência
#-------------------------------------------------------------------------------------------------------------

import inspect
import tensorflow as tf
import matplotlib.pyplot as plt

def plot_tensor_series(tensor1, tensor2, title='Gráfico: coral original vs. coral criado'):
    """Plota as séries dos dois tensores fornecidos.

    Parâmetros:
        tensor1, tensor2 (tf.Tensor): Tensores a serem plotados.
        title (str): Título do gráfico.
    """
    
    # Pegando os nomes das variáveis usando inspect
    frame = inspect.currentframe().f_back
    string = inspect.getframeinfo(frame).code_context[0]
    arg_names = string[string.find('(') + 1:-1].split(',')
    tensor1_name = arg_names[0].strip()
    tensor2_name = arg_names[1].strip()

    # Converter tensores para int32
    tensor1 = tf.cast(tensor1, tf.int32)
    tensor2 = tf.cast(tensor2, tf.int32)

    # Converter para numpy array
    data1 = tensor1.numpy()
    data2 = tensor2.numpy()

    # Ajustar o tamanho da figura
    plt.figure(figsize=(15, 8))

    # Plotar cada série (coluna) do primeiro tensor
    for i in range(data1.shape[1]):
        plt.plot(data1[:, i], linestyle='-', label=f'{tensor1_name} - Série {i+1}')

    # Plotar cada série (coluna) do segundo tensor com um estilo diferente
    for i in range(data2.shape[1]):
        plt.plot(data2[:, i], linestyle='--', label=f'{tensor2_name} - Série {i+1}')

    plt.xlabel('Posição do vetor')
    plt.ylabel('Valor')
    plt.title(title)
    plt.legend(ncol=2)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
    plt.show()

#------------------------------------------------------------------------------------------------------------- 