# Análise de Ruído do MPU6050 com e sem DMP

Este repositório contém dois códigos que, em conjunto, permitem a análise do ruído do sinal do MPU6050 com e sem o uso do **Digital Motion Processor (DMP)**. O objetivo é comparar a qualidade dos sinais obtidos em cada configuração.

---

## Visão Geral

Este projeto tem como finalidade analisar o ruído no sinal do MPU6050 em duas condições:
- **Com DMP:** Utilizando o processamento interno do sensor para filtrar os sinais.
- **Sem DMP:** Utilizando os dados brutos do sensor.

Para isso, o código em **C++ (DMP_INT)** realiza a aquisição dos dados e grava-os em um cartão SD, enquanto o código em **Python (DMP_50hz)** realiza o processamento e a visualização dos dados, permitindo a comparação entre os sinais com e sem o DMP.

---

## Código Arduino: DMP_INT

### Funcionalidade
- Inicializa o sensor MPU6050 no endereço I2C **0x69**.
- Configura e ativa a **DMP** para obter dados filtrados.
- Lê os sinais brutos do acelerômetro e giroscópio, além dos dados processados pela DMP.
- Grava os dados (tempo, sinais brutos e filtrados) em um arquivo `datalog.txt` em um cartão SD.
- Permite o término da gravação de forma automática (após 10 minutos) ou manual (através de um botão).

### Conexões e Pinos (Arduino)
- **Pino 2:** Botão de parada (configurado como `INPUT_PULLUP`).
- **Pino 3:** Interrupção do MPU6050.
- **Pino 4:** LED de gravação ativa.
- **Pino 5:** LED de gravação finalizada.
- **Pino 10:** Chip Select (CS) do cartão SD (utilizado na inicialização do SD com `SD.begin(10)`).

---

## Código Python: DMP_50hz

### Funcionalidade
- **Carregamento e Processamento dos Dados:**
  - Abre uma janela gráfica (usando Tkinter) para seleção do arquivo `.txt` gerado pelo Arduino.
  - Utiliza **Pandas** para ler e separar as colunas dos dados (tempo, acelerômetro e giroscópio brutos e filtrados pela DMP).
  - Converte os dados para `numpy.ndarray` e ajusta a escala do tempo (de microsegundos para segundos).
  - Calcula a frequência de amostragem a partir das diferenças de tempo.

- **Análise no Domínio da Frequência:**
  - Segmenta os dados e calcula a **FFT** para cada sinal, tanto dos dados brutos quanto dos processados pela DMP.
  - Normaliza os resultados e plota gráficos comparativos para os três eixos.

- **Visualização no Domínio do Tempo:**
  - Converte os sinais de acelerômetro e giroscópio para as unidades corretas (m/s² e °/s, respectivamente).
  - Plota gráficos dos sinais temporais para comparação.
  - Calcula a integral dos sinais do giroscópio para estimar o deslocamento angular, e plota os resultados.

### Bibliotecas Utilizadas (Python)
- **pandas:** Manipulação e análise de dados.
- **tkinter:** Interface gráfica para seleção do arquivo.
- **numpy:** Operações matemáticas e conversão de dados.
- **os:** Manipulação de caminhos e nomes de arquivos.
- **matplotlib.pyplot:** Plotagem de gráficos.
- **scipy.fft:** Cálculo da Transformada de Fourier.
- **scipy.interpolate:** Interpolação dos dados.
- **scipy.integrate:** Cálculo de integrais (deslocamento angular).
- **scipy.signal:** Processamento e filtragem dos sinais.

---

## Conexões e Configurações de Hardware

### Para o Código Arduino (DMP_INT)
- **Comunicação I2C:**
  - Conecte os pinos **SDA** e **SCL** do MPU6050 aos pinos correspondentes do Arduino.
- **Endereço I2C:**  
  - O MPU6050 está configurado para o endereço **0x69** (verifique a documentação do seu sensor para ajustes caso necessário).
- **Botão de Parada:**  
  - Conectado ao **pino 2** com resistor de pull-up interno.
- **Interrupção do Sensor:**  
  - Conectado ao **pino 3** para receber sinais de interrupção do MPU6050.
- **LEDs Indicadores:**  
  - **LED de gravação ativa:** Conectado ao **pino 4**.  
  - **LED de término da gravação:** Conectado ao **pino 5**.
- **Cartão SD:**  
  - Conectado utilizando o **pino 10** como Chip Select (CS) e os pinos padrão do SPI para comunicação.

---

## Bibliotecas Utilizadas

### No Código Arduino (DMP_INT)
- **Wire.h:** Comunicação I2C.
- **I2Cdev.h:** Facilita a comunicação com o MPU6050.
- **MPU6050_6Axis_MotionApps20.h:** Biblioteca para utilizar os recursos da DMP do MPU6050.
- **SD.h:** Gerenciamento de leitura e escrita no cartão SD.
- **SPI.h:** Comunicação SPI para o cartão SD.

### No Código Python (DMP_50hz)
- **pandas:** Leitura e manipulação dos dados do arquivo.
- **tkinter:** Criação da interface gráfica para seleção de arquivo.
- **numpy:** Operações matemáticas e manipulação de arrays.
- **os:** Manipulação de caminhos e nomes de arquivos.
- **matplotlib.pyplot:** Criação de gráficos para visualização dos dados.
- **scipy.fft:** Cálculo da Transformada de Fourier para análise de frequência.
- **scipy.interpolate:** Interpolação dos dados.
- **scipy.integrate:** Cálculo da integral para estimativa do deslocamento angular.
- **scipy.signal:** Processamento e filtragem dos sinais.

---

## Instruções para Uso

### Para o Código Arduino (DMP_INT)
1. Realize as conexões conforme descritas na seção de **Conexões e Configurações de Hardware**.
2. Carregue o código no Arduino.
3. O sistema inicia a gravação dos dados no cartão SD automaticamente.
4. A gravação será encerrada:
   - **Automaticamente:** Após 10 minutos.
   - **Manual:** Através do botão de parada conectado ao pino 2.
5. Os dados serão salvos no arquivo `datalog.txt`.

### Para o Código Python (DMP_50hz)
1. Certifique-se de ter o **Python 3** instalado, juntamente com as bibliotecas necessárias.
2. Execute o script Python.
3. Uma janela gráfica se abrirá para que você selecione o arquivo `datalog.txt` gerado pelo Arduino.
4. Após a seleção, o script:
   - Carregará e processará os dados.
   - Realizará análises no domínio do tempo e da frequência.
   - Exibirá gráficos comparativos entre os sinais com e sem DMP.
5. Utilize os gráficos para avaliar o ruído e a qualidade dos sinais.

---

*Observação: Este projeto visa facilitar a comparação do desempenho do MPU6050 com e sem o uso do DMP. As configurações e conexões podem variar conforme a versão do sensor e do Arduino utilizados.*
