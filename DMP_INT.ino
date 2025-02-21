#include <Wire.h>
#include "I2Cdev.h"
#include <MPU6050_6Axis_MotionApps20.h>
#include <SD.h>
#include <SPI.h>

MPU6050_6Axis_MotionApps20 mpu(0x69);  // Instância do sensor MPU6050 no endereço I2C 0x69
File dataFile;                         // Objeto para manipulação do arquivo no cartão SD

const unsigned long recordingDuration = 10L * 60L * 1000L;  // Duração máxima de gravação (10 minutos)
unsigned long startTime;                                    // Armazena o tempo inicial do experimento
unsigned long lastFlush = 0;                                // Último momento de sincronização dos dados com o SD
const unsigned long flushInterval = 120L * 1000L;           // Intervalo de sincronização do SD (120 segundos)

uint8_t fifoBuffer[64];              // Buffer FIFO para armazenar os dados da DMP
volatile bool mpuInterrupt = false;  // Variável para indicar interrupção ativa

// Função chamada pela interrupção do MPU6050
void dmpDataReady() {
  mpuInterrupt = true;
}

void setup() {
  Serial.begin(115200);
  pinMode(2, INPUT_PULLUP);  // Botão de parada com pull-up interno
  pinMode(3, INPUT);         // Pino de interrupção do MPU-6050
  pinMode(4, OUTPUT);        // LED de gravação ativa
  pinMode(5, OUTPUT);        // LED de gravação finalizada

  Wire.begin();  // Inicia a comunicação I2C

  // ---------------- Inicializa o MPU-6050 ---------------- //
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("Erro ao iniciar o MPU-6050");
    while (1)
      ;  // Trava a execução caso o sensor não seja detectado
  }
  Serial.println("MPU INICIALIZADO");

  mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);  // Configura escala do acelerômetro para ±2g
  mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);   // Configura escala do giroscópio para ±250°/s

  // **IMPORTANTE:** Desativa a interrupção antes de inicializar a DMP
  detachInterrupt(digitalPinToInterrupt(3));

  // ---------------- Configura a DMP ---------------- //
  int status = mpu.dmpInitialize();
  if (status != 0) {
    Serial.print("Falha ao inicializar a DMP. Código de erro: ");
    Serial.println(status);
    while (1)
      ;  // Trava a execução caso a DMP falhe
  }
  Serial.println("DMP INICIALIZADO");

  mpu.setDMPEnabled(true);  // Ativa a DMP

  // Agora que a DMP está configurada, ativa a interrupção
  attachInterrupt(digitalPinToInterrupt(3), dmpDataReady, RISING);

  // ---------------- Verifica o cartão SD ---------------- //
  if (!SD.begin(10)) {
    Serial.println("Erro ao inicializar o SD!");
    while (1)
      ;
  }
  Serial.println("SD INICIALIZADO");

  dataFile = SD.open("datalog.txt", FILE_WRITE);
  if (!dataFile) {
    Serial.println("Erro ao abrir o arquivo no SD!");
    while (1)
      ;
  }

  startTime = millis();
  Serial.println("Sistema pronto!");

  digitalWrite(4, HIGH);  // LED de gravação ativa ligado
  digitalWrite(5, HIGH);  // LED de término apagado

  delay(2000);

  digitalWrite(4, LOW);  // LED de gravação ativa ligado
  digitalWrite(5, LOW);  // LED de término apagado

}

// ---------------- Função para capturar dados do MPU ---------------- //
void lerMPU() {
  if (mpuInterrupt && mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
    mpuInterrupt = false;  // Reseta a flag de interrupção

    int16_t ax, ay, az, gx, gy, gz;  // Variáveis para dados brutos
    mpu.getAcceleration(&ax, &ay, &az);
    mpu.getRotation(&gx, &gy, &gz);

    VectorInt16 accel;  // Aceleração corrigida pela DMP
    mpu.dmpGetAccel(&accel, fifoBuffer);

    VectorInt16 gyro;  // Velocidade angular corrigida pela DMP
    mpu.dmpGetGyro(&gyro, fifoBuffer);

    // Formata os dados coletados
    char dataString[128];
    snprintf(dataString, sizeof(dataString),
             "%lu,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d",
             micros(),
             ax, ay, az, gx, gy, gz,     // Dados brutos
             accel.x, accel.y, accel.z,  // Aceleração filtrada pela DMP
             gyro.x, gyro.y, gyro.z);    // Velocidade angular filtrada pela DMP

    dataFile.println(dataString);  // Salva os dados no cartão SD
    Serial.println(dataString);    // Exibe no monitor serial
  }
  digitalWrite(4, LOW);  // LED de gravação ativa ligado
}

// ---------------- Loop principal ---------------- //
void loop() {


  digitalWrite(4, HIGH);  // LED de gravação ativa ligado

  if (mpuInterrupt) {
    lerMPU();  // Lê os dados apenas se houver uma interrupção ativa
  }

  unsigned long elapsedTime = millis() - startTime;  // Tempo decorrido

  // ---------------- Verifica tempo máximo de gravação ---------------- //
  if (elapsedTime >= recordingDuration) {
    Serial.println("Tempo máximo atingido, encerrando gravação.");
    closeFile();
  }

  // ---------------- Verifica botão para encerramento manual ---------------- //
  if (digitalRead(2) == LOW) {  // LOW indica botão pressionado
    Serial.println("Fim manual da gravação.");
    closeFile();
  }

  // ---------------- Sincroniza dados no SD periodicamente ---------------- //
  if (millis() - lastFlush >= flushInterval) {
    dataFile.flush();  // Força a gravação dos dados no SD
    lastFlush = millis();
    Serial.println("Dados sincronizados no SD.");
  }
}

// ---------------- Finaliza a gravação e fecha o arquivo ---------------- //
void closeFile() {
  dataFile.close();
  Serial.println("Arquivo fechado corretamente.");

  digitalWrite(4, LOW);   // LED de gravação desativado
  digitalWrite(5, HIGH);  // LED de término ativado

  while (1)
    ;  // Trava a execução após o término
}
