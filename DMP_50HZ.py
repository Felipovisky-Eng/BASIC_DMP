import pandas  as pd  #Análise dos dados
import tkinter as tk  #Interface Gráfica
import numpy   as np  #Calculos 
import os             # Para manipulação de caminhos
import matplotlib.pyplot as plt   # Plota os gráficos
import scipy.fft as fft                   # Transformada de Fourier


from tkinter import filedialog            # Busca arquivos
from scipy.interpolate import interp1d    # Calculo de interpolação
from scipy.integrate import cumulative_trapezoid # Calculo da integral
from scipy import signal                  # Calculo de filtros

#
#
#
# Importaçao do arquivo .txt 
#
#
#

def selecionar_arquivo():     #Função vai permitir abrir a janela para selecionar o arquivo                      
    
    root = tk.Tk()                                   # Base para parte gráfica
    root.withdraw()                                  # Oculta a janela principal do Tkinter
    arquivo = filedialog.askopenfilename(            # Abre a janela de seleção
        title="Selecione o arquivo .txt",            # Titulo do arquivo
        filetypes=[("Arquivos de texto", "*.txt")]   # Tipo do arquivo
    )
    return arquivo # Retorna o caminho do arquivo com o titulo na variavel "arquivo"

#
#
#
# Separação do arquivo .txt usando a pandas
#
#
#

def carregar_dados(caminho_arquivo): # Lê o arquivo 
    
    dados = pd.read_csv(caminho_arquivo, delimiter=",", header=None) # Separa o arquivo em duas colunas usando o ","
    tempo   = dados[0]    # Primeira coluna
    AX      = dados[1]    # Segunda coluna
    AY      = dados[2]    # Terceira coluna
    AZ      = dados[3]    # Quarta coluna
    GX      = dados[4]    # Qunita coluna
    GY      = dados[5]    # Sexta primeira coluna
    GZ      = dados[6]    # Setima segunda coluna
    AX_DMP    = dados[7]    # Oitava terceira coluna
    AY_DMP    = dados[8]    # Nona quarta coluna
    AZ_DMP    = dados[9]    # Decima quinta coluna
    GX_DMP    = dados[10]   # Decima sexta coluna
    GY_DMP    = dados[11]   # Decima setima coluna
    GZ_DMP    = dados[12]   # Decima oitava coluna


    return tempo, AX, AY, AZ, GX, GY, GZ, AX_DMP, AY_DMP, AZ_DMP, GX_DMP, GY_DMP, GZ_DMP # Retorna primeiro as colunas de tempo depois as de valores
    
     

if __name__ == "__main__":
    print("Selecione o arquivo .txt do arquivo sem o filtro no explorador de arquivos...")
    caminho = selecionar_arquivo() # Define o caminho para o arquivo com base na função anterior
    
    if caminho:
        print(f"Arquivo selecionado: {caminho}") # Imprime o caminho do arquivo
        tempo, AX, AY, AZ, GX, GY, GZ, AX_DMP, AY_DMP, AZ_DMP, GX_DMP, GY_DMP, GZ_DMP = carregar_dados(caminho) # Carrega as variaveis
        nome_arquivo = os.path.basename(caminho) # Carrega em uma string o nome do arquivo
        print("\nDados carregados com sucesso!")
        #print("Tempo:", tempo.values)           # Imprime os dados do tempo no terminal
        #print("Valores:", valores.values)       # Imprime os dados do valor no terminal
        #print(f"Nome do arquivo: {nome_arquivo}")
    else:
        print("Nenhum arquivo foi selecionado.") # Caso não tenha selecionado nenhum arquivo
#
#
#
# Manipulaçao de dados
#
#
#

# Tratamento do nome do arquivo
Nome = nome_arquivo.replace(".txt", "") # Tira a extensão do arquivo (.txt) do nome dele
Nome = Nome.replace("_", " ") # Tira o "_" e subtitui por um espaço


# Converte os dados para numpy.ndarray com tipo float

tempo = tempo.to_numpy(dtype=float)  # Converte para numpy.ndarray

AX    = AX.to_numpy(dtype=float)     # Converte para numpy.ndarray
AY    = AY.to_numpy(dtype=float)     # Converte para numpy.ndarray
AZ    = AZ.to_numpy(dtype=float)     # Converte para numpy.ndarray

GX    = GX.to_numpy(dtype=float)     # Converte para numpy.ndarray
GY    = GY.to_numpy(dtype=float)     # Converte para numpy.ndarray
GZ    = GZ.to_numpy(dtype=float)     # Converte para numpy.ndarray

AX_DMP    = AX_DMP.to_numpy(dtype=float)     # Converte para numpy.ndarray
AY_DMP    = AY_DMP.to_numpy(dtype=float)     # Converte para numpy.ndarray
AZ_DMP    = AZ_DMP.to_numpy(dtype=float)     # Converte para numpy.ndarray

GX_DMP    = GX_DMP.to_numpy(dtype=float)     # Converte para numpy.ndarray
GY_DMP    = GY_DMP.to_numpy(dtype=float)     # Converte para numpy.ndarray
GZ_DMP    = GZ_DMP.to_numpy(dtype=float)     # Converte para numpy.ndarray



# Ajusta a escala do tempo
tempo = tempo - tempo[0]  # Inicia o tempo em zero
tempo = tempo * 1e-6      # Converte de microsegundos para segundos

# Calcula a frequência de amostragem
Diferenca = np.diff(tempo)       # Diferença entre amostras
Mdiferenca = np.mean(Diferenca)  # Média das diferenças
FS = 1 / Mdiferenca              # Frequência de amostragem

N = len(tempo) # Número de pontos

print(f"Frequência de amostragem estimada: {FS:.2f} Hz")          # Calcula a frequência de amostragem
print(f"Número de pontos: {N}")                                   # Calcula o número de pontos
print(f"Tempo total de gravação: {tempo[-1]:.2f} segundos")       # Calcula o tempo total de gravação

print(f"Tempo total de gravação: {((tempo[-1])/60):.2f} minutos")       # Calcula o tempo total de gravação

#
#
#
# Gráficos
#
#
#

# Configurações globais de fontes e DPI
plt.rc('font', family='serif', size=9)   # Altera o tipo e o tamanho da fonte
plt.rcParams['axes.titleweight'] = "bold" # Títulos dos eixos e gráficos em negrito
plt.rcParams['figure.dpi'] = 140          # Define o DPI para todas as figuras
plt.rcParams['axes.labelweight'] = "bold" # Rótulos dos eixos
#plt.rcParams['lines.linestyle'] = '--'    # Linhas tracejadas por padrão
plt.rcParams['lines.linewidth'] = 1.0     # Espessura padrão das linhas
#
#
#
# Análise no domínio da frequência
#
#
#

# Função que divide e calcula a FFT dos sinais

def fft_segmentado(sinal, tamanho_pacote):
    # Calcular FFT para segmentos de tamanho 'tamanho_pacote'
    n = len(sinal)
    fft_total = np.zeros(n, dtype=complex)  # Array para armazenar o resultado final
    
    for i in range(0, n, tamanho_pacote):
        segmento = sinal[i:i + tamanho_pacote]
        if len(segmento) == tamanho_pacote:  # Verifica se o segmento tem o tamanho completo
            fft_total[i:i + tamanho_pacote] = fft.fft(segmento)  # Calcula a FFT do segmento
    return fft_total


# Calcula a FFT dos sinais

FFT_AX = fft_segmentado(AX, 1024) # Calcula a FFT do sinal de aceleração no eixo X
FFT_AY = fft_segmentado(AY, 1024) # Calcula a FFT do sinal de aceleração no eixo Y
FFT_AZ = fft_segmentado(AZ, 1024) # Calcula a FFT do sinal de aceleração no eixo Z

FFT_GX = fft_segmentado(GX, 1024) # Calcula a FFT do sinal de giroscópio no eixo X
FFT_GY = fft_segmentado(GY, 1024) # Calcula a FFT do sinal de giroscópio no eixo Y
FFT_GZ = fft_segmentado(GZ, 1024) # Calcula a FFT do sinal de giroscópio no eixo Z

FFT_AX_DMP = fft_segmentado(AX_DMP, 1024) # Calcula a FFT do sinal de aceleração no eixo X
FFT_AY_DMP = fft_segmentado(AY_DMP, 1024) # Calcula a FFT do sinal de aceleração no eixo Y
FFT_AZ_DMP = fft_segmentado(AZ_DMP, 1024) # Calcula a FFT do sinal de aceleração no eixo Z

FFT_GX_DMP = fft_segmentado(GX_DMP, 1024) # Calcula a FFT do sinal de giroscópio no eixo X
FFT_GY_DMP = fft_segmentado(GY_DMP, 1024) # Calcula a FFT do sinal de giroscópio no eixo Y
FFT_GZ_DMP = fft_segmentado(GZ_DMP, 1024) # Calcula a FFT do sinal de giroscópio no eixo Z

print(len(FFT_AX))
print(len(AX))
# Calcula a frequência para cada ponto da FFT

frequencia = fft.fftfreq(len(tempo), Mdiferenca)

# Normaliza a FFT dividindo pelas magnitudes dos pontos

FFT_AX_norm = np.abs(FFT_AX) / N # Normaliza a FFT da aceleração de eixo X
FFT_AY_norm = np.abs(FFT_AY) / N # Normaliza a FFT da aceleração do eixo Y
FFT_AZ_norm = np.abs(FFT_AZ) / N # Normaliza a FFT da aceleração do eixo Z

FFT_GX_norm = np.abs(FFT_GX) / N # Normaliza a FFT da velocidade angular do eixo X
FFT_GY_norm = np.abs(FFT_GY) / N # Normaliza a FFT da velocidade angular do eixo Y
FFT_GZ_norm = np.abs(FFT_GZ) / N # Normaliza a FFT da velocidade angular do eixo Z

FFT_AX_DMP_norm = np.abs(FFT_AX_DMP) / N # Normaliza a FFT da aceleração de eixo X
FFT_AY_DMP_norm = np.abs(FFT_AY_DMP) / N # Normaliza a FFT da aceleração do eixo Y
FFT_AZ_DMP_norm = np.abs(FFT_AZ_DMP) / N # Normaliza a FFT da aceleração do eixo Z

FFT_GX_DMP_norm = np.abs(FFT_GX_DMP) / N # Normaliza a FFT da velocidade angular do eixo X
FFT_GY_DMP_norm = np.abs(FFT_GY_DMP) / N # Normaliza a FFT da velocidade angular do eixo Y
FFT_GZ_DMP_norm = np.abs(FFT_GZ_DMP) / N # Normaliza a FFT da velocidade angular do eixo Z

# Seleciona apenas as frequências positivas

idx_pos = np.where(frequencia > 0)  # Filtra os índices das frequências positivas

frequencia_pos = frequencia[idx_pos] # Frequências positivas

FFT_AX_pos = FFT_AX_norm   [idx_pos] # Componentes positivas da FFT do eixo X
FFT_AY_pos = FFT_AY_norm   [idx_pos] # Componentes positivas da FFT do eixo Y
FFT_AZ_pos = FFT_AZ_norm   [idx_pos] # Componentes positivas da FFT do eixo Z

FFT_GX_pos = FFT_GX_norm   [idx_pos] # Componentes positivas da FFT do giroscópio no eixo X
FFT_GY_pos = FFT_GY_norm   [idx_pos] # Componentes positivas da FFT do giroscópio no eixo Y
FFT_GZ_pos = FFT_GZ_norm   [idx_pos] # Componentes positivas da FFT do giroscópio no eixo Z

FFT_AX_DMP_pos = FFT_AX_DMP_norm   [idx_pos] # Componentes positivas da FFT do eixo X
FFT_AY_DMP_pos = FFT_AY_DMP_norm   [idx_pos] # Componentes positivas da FFT do eixo Y
FFT_AZ_DMP_pos = FFT_AZ_DMP_norm   [idx_pos] # Componentes positivas da FFT do eixo Z

FFT_GX_DMP_pos = FFT_GX_DMP_norm   [idx_pos] # Componentes positivas da FFT do giroscópio no eixo X
FFT_GY_DMP_pos = FFT_GY_DMP_norm   [idx_pos] # Componentes positivas da FFT do giroscópio no eixo Y
FFT_GZ_DMP_pos = FFT_GZ_DMP_norm   [idx_pos] # Componentes positivas da FFT do giroscópio no eixo Z


#
#
#
# Plotagem dos gráficos da fft
#
#
#

# Criação do gráfico com FFT normalizada para acelaração nos três eixos
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

# Plot da FFT normalizada do eixo X com e sem DMP
axs[0].plot(frequencia_pos, FFT_AX_pos,          color="#1f77b4", label="Acelerômetro")
axs[0].plot(frequencia_pos, FFT_AX_DMP_pos,      color="#aec7e8", label="Acelerômetro com DMP")
axs[0].set_title('FFT Normalizada - Comparação Acelerômetro come sem  DMP no Eixo X')
axs[0].set_xlabel('Frequência (Hz)')
axs[0].set_ylabel('Magnitude Normalizada')
axs[0].legend()
axs[0].grid(True)

# Plot da FFT normalizada do eixo Y com e sem DMP
axs[1].plot(frequencia_pos, FFT_AY_pos,      color="#ff7f0e", label="Acelerômetro")
axs[1].plot(frequencia_pos, FFT_AY_DMP_pos,  color="#ffbb78", label="Acelerômetro com DMP")
axs[1].set_title('FFT Normalizada - Comparação Acelerômetro come sem  DMP no Eixo Y')
axs[1].set_xlabel('Frequência (Hz)')
axs[1].set_ylabel('Magnitude Normalizada')
axs[1].legend()
axs[1].grid(True)

# Plot da FFT normalizada do eixo Z com e sem DMP
axs[2].plot(frequencia_pos, FFT_AZ_pos,      color="#d62728", label="Acelerômetro")
axs[2].plot(frequencia_pos, FFT_AZ_DMP_pos,  color="#ff9896", label="Acelerômetro com DMP")
axs[2].set_title('FFT Normalizada - Comparação Acelerômetro come sem  DMP no Eixo Z')
axs[2].set_xlabel('Frequência (Hz)')
axs[2].set_ylabel('Magnitude Normalizada')
axs[2].legend()
axs[2].grid(True)

# Ajuste para não sobrepor os subgráficos
plt.tight_layout()

# Exibe os gráficos
plt.show()


# Criação do gráfico com FFT normalizada para velocidade angular nos três eixos
# Criação do gráfico com FFT normalizada para acelaração nos três eixos
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

# Plot da FFT normalizada do eixo X com e sem DMP
axs[0].plot(frequencia_pos, FFT_GX_pos,      color="#1f77b4", label="Giroscópio")
axs[0].plot(frequencia_pos, FFT_GX_DMP_pos,  color="#aec7e8", label="Giroscópio com DMP")
axs[0].set_title('FFT Normalizada - Giroscópio com e sem DMP no Eixo X')
axs[0].set_xlabel('Frequência (Hz)')
axs[0].set_ylabel('Magnitude Normalizada')
axs[0].legend()
axs[0].grid(True)

# Plot da FFT normalizada do eixo Y com e sem DMP
axs[1].plot(frequencia_pos, FFT_GY_pos,      color="#ff7f0e", label="Giroscópio")
axs[1].plot(frequencia_pos, FFT_GY_DMP_pos,  color="#ffbb78", label="Giroscópio com DMP")
axs[1].set_title('FFT Normalizada - Giroscópio com e sem DMP no Eixo Y')
axs[1].set_xlabel('Frequência (Hz)')
axs[1].set_ylabel('Magnitude Normalizada')
axs[1].legend()
axs[1].grid(True)

# Plot da FFT normalizada do eixo Z com e sem DMP
axs[2].plot(frequencia_pos, FFT_GZ_pos,      color="#d62728", label="Giroscópio")
axs[2].plot(frequencia_pos, FFT_GZ_DMP_pos,  color="#ff9896", label="Giroscópio com DMP")
axs[2].set_title('FFT Normalizada - Giroscópio com e sem DMP no Eixo Z')
axs[2].set_xlabel('Frequência (Hz)')
axs[2].set_ylabel('Magnitude Normalizada')
axs[2].legend()
axs[2].grid(True)

# Ajuste para não sobrepor os subgráficos
plt.tight_layout()

# Exibe os gráficos
plt.show()


#
#
#
# Converção dos dados dos sensores
#
#
#

G = 9.81  # Aceleração da gravidade (m/s²)

Escala_Acelerometro = (2 / 32768)* G  # Escala do acelerômetro (16g)
Escala_Giroscopio =  250 / 32768      # Escala do giroscópio (250°/s)

# Converte os dados do acelerômetro
AX = AX * Escala_Acelerometro  # Converte o acelerômetro no eixo X
AY = AY * Escala_Acelerometro  # Converte o acelerômetro no eixo Y
AZ = AZ * Escala_Acelerometro  # Converte o acelerômetro no eixo Z

# Converte os dados do giroscópio
GX = GX * Escala_Giroscopio  # Converte o giroscópio no eixo X
GY = GY * Escala_Giroscopio  # Converte o giroscópio no eixo Y
GZ = GZ * Escala_Giroscopio  # Converte o giroscópio no eixo z

# Converte os dados do acelerômetro com DMP
AX_DMP = AX_DMP * Escala_Acelerometro  # Converte o acelerômetro no eixo X
AY_DMP = AY_DMP * Escala_Acelerometro  # Converte o acelerômetro no eixo Y
AZ_DMP = AZ_DMP * Escala_Acelerometro  # Converte o acelerômetro no eixo Z

# Converte os dados do giroscópio com DMP
GX_DMP = GX_DMP * Escala_Giroscopio  # Converte o giroscópio no eixo X
GY_DMP = GY_DMP * Escala_Giroscopio  # Converte o giroscópio no eixo Y
GZ_DMP = GZ_DMP * Escala_Giroscopio  # Converte o giroscópio no eixo Z

#
#
#
# Plotagem dos gráficos
#
#
#

# Criação do gráfico com aceleração nos três eixos
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

# Plot da aceleração no eixo X com e sem DMP
axs[0].plot(tempo, AX,      color="#1f77b4", label="Acelerômetro")
axs[0].plot(tempo, AX_DMP,  color="#aec7e8", label="Acelerômetro com DMP")
axs[0].set_title('Aceleração - Eixo X')
axs[0].set_xlabel('Tempo (s)')
axs[0].set_ylabel('Aceleração (m/s²)')
axs[0].legend()
axs[0].grid(True)

# Plot da aceleração no eixo Y com e sem DMP
axs[1].plot(tempo, AY,      color="#ff7f0e",label="Acelerômetro")
axs[1].plot(tempo, AY_DMP,  color="#ffbb78",label="Acelerômetro com DMP")
axs[1].set_title('Aceleração - Eixo Y')
axs[1].set_xlabel('Tempo (s)')
axs[1].set_ylabel('Aceleração (m/s²)')
axs[1].legend()
axs[1].grid(True)

# Plot da aceleração no eixo Z com e sem DMP
axs[2].plot(tempo, AZ,      color="#d62728", label="Acelerômetro")
axs[2].plot(tempo, AZ_DMP,  color="#ff9896", label="Acelerômetro com DMP")
axs[2].set_title('Aceleração - Eixo Z')
axs[2].set_xlabel('Tempo (s)')
axs[2].set_ylabel('Aceleração (m/s²)')
axs[2].legend()
axs[2].grid(True)

# Ajuste para não sobrepor os subgráficos
plt.tight_layout()

# Exibe os gráficos
plt.show()

# Criação do gráfico com velocidade angular nos três eixos
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

# Plot da velocidade angular no eixo X com e sem DMP
axs[0].plot(tempo, GX,      color="#1f77b4", label="Giroscópio")
axs[0].plot(tempo, GX_DMP,  color="#aec7e8", label="Giroscópio com DMP")
axs[0].set_title('Velocidade Angular - Eixo X')
axs[0].set_xlabel('Tempo (s)')
axs[0].set_ylabel('Velocidade Angular (°/s)')
axs[0].legend()
axs[0].grid(True)

# Plot da velocidade angular no eixo Y com e sem DMP
axs[1].plot(tempo, GY,      color="#ff7f0e", label="Giroscópio")
axs[1].plot(tempo, GY_DMP,  color="#ffbb78", label="Giroscópio com DMP")
axs[1].set_title('Velocidade Angular - Eixo Y')
axs[1].set_xlabel('Tempo (s)')
axs[1].set_ylabel('Velocidade Angular (°/s)')
axs[1].legend()
axs[1].grid(True)

# Plot da velocidade angular no eixo Z com e sem DMP
axs[2].plot(tempo, GZ,      color="#d62728", label="Giroscópio")
axs[2].plot(tempo, GZ_DMP,  color="#ff9896", label="Giroscópio com DMP")
axs[2].set_title('Velocidade Angular - Eixo Z')
axs[2].set_xlabel('Tempo (s)')
axs[2].set_ylabel('Velocidade Angular (°/s)')
axs[2].legend()
axs[2].grid(True)

# Ajuste para não sobrepor os subgráficos
plt.tight_layout()

# Exibe os gráficos
plt.show()


#
#
# Calculo da integral simples da velcidade angular em cada eixo
#
#
#

# Calcula a integral da velocidade angular para obter o ângulo

Ang_GX = cumulative_trapezoid(GX, tempo, initial=0)
Ang_GY = cumulative_trapezoid(GY, tempo, initial=0)
Ang_GZ = cumulative_trapezoid(GZ, tempo, initial=0)

Ang_GX_DMP = cumulative_trapezoid(GX_DMP, tempo, initial=0)
Ang_GY_DMP = cumulative_trapezoid(GY_DMP, tempo, initial=0)
Ang_GZ_DMP = cumulative_trapezoid(GZ_DMP, tempo, initial=0)

# Criação dos gráficos para deslocamento angular nos três eixos
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

# Plot do deslocamento angular no eixo X
axs[0].plot(tempo, Ang_GX,      color="#1f77b4", label="Giroscópio")
axs[0].plot(tempo, Ang_GX_DMP,  color="#aec7e8", label="Giroscópio com DMP")
axs[0].set_title('Deslocamento Angular - Eixo X')
axs[0].set_xlabel('Tempo (s)')
axs[0].set_ylabel('Deslocamento Angular (°)')
axs[0].legend()
axs[0].grid(True)

# Plot do deslocamento angular no eixo Y
axs[1].plot(tempo, Ang_GY,      color="#ff7f0e", label="Giroscópio")
axs[1].plot(tempo, Ang_GY_DMP,  color="#ffbb78", label="Giroscópio com DMP")
axs[1].set_title('Deslocamento Angular - Eixo Y')
axs[1].set_xlabel('Tempo (s)')
axs[1].set_ylabel('Deslocamento Angular (°)')
axs[1].legend()
axs[1].grid(True)

# Plot do deslocamento angular no eixo Z
axs[2].plot(tempo, Ang_GZ,      color="#d62728", label="Giroscópio")
axs[2].plot(tempo, Ang_GZ_DMP,  color="#ff9896", label="Giroscópio com DMP")
axs[2].set_title('Deslocamento Angular - Eixo Z')
axs[2].set_xlabel('Tempo (s)')
axs[2].set_ylabel('Deslocamento Angular (°)')
axs[2].legend()
axs[2].grid(True)

# Ajuste para não sobrepor os subgráficos
plt.tight_layout()

# Exibe os gráficos
plt.show()