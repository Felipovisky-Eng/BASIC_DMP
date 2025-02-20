#include <Wire.h>  // MPU-6050
#include "I2Cdev.h"
#include <MPU6050_6Axis_MotionApps20.h>  // Biblioteca com suporte à DMP
#include <SD.h>                          // Cartão SD
#include <SPI.h>                         // Cartão SD

MPU6050_6Axis_MotionApps20 mpu(0x69);  // Define o objeto MPU6050

File dataFile;

const unsigned long recordingDuration = 12L * 60L * 60L * 1000L;  // 12 horas em milissegundos
unsigned long startTime;                                          // Armazena o tempo inicial
unsigned long lastFlush = 0;                                      // Última vez que os dados foram sincronizados no SD
const unsigned long flushInterval = 300L * 1000L;                 // Sincronizar a cada 300 segundos

void setup() {
  Serial.begin(115200);

  pinMode(2, INPUT_PULLUP);  // Configura o botão com pull-up interno
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);

  Wire.begin();

  //----------------Verificação do funcionamento do MPU-6050-------------------------//
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("Erro ao iniciar o MPU-6050");
    while (1)
      ;
  }
  Serial.println("MPU INICIALIZADO");

  // Configurar a escala do acelerômetro para ±16g
  mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_16);

  // Configurar a escala do giroscópio para ±250°/s
  mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);

  //----------------Configuração da DMP-------------------------//
  // Inicializa a DMP (Digital Motion Processor)
  if (mpu.dmpInitialize() != 0) {
    Serial.println("Falha ao inicializar a DMP");
    while (1)
      ;
  }

  // Ativa a DMP
  mpu.setDMPEnabled(true);

  //----------------Verificação do funcionamento do Cartão SD-------------------------//
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

  // Armazena o tempo de início
  startTime = millis();
  Serial.println("Sistema pronto!");
}

void closeFile() {
  dataFile.close();
  Serial.println("Arquivo fechado corretamente.");
  digitalWrite(3, LOW);
  digitalWrite(4, HIGH);
  while (1)
    ;
}

void lerMPU() {
  // Variáveis para armazenar os dados brutos
  int16_t ax, ay, az, gx, gy, gz;
  uint8_t fifoBuffer[64];  // Buffer de dados FIFO

  // Obtém os dados brutos SEM a DMP
  mpu.getAcceleration(&ax, &ay, &az);
  mpu.getRotation(&gx, &gy, &gz);

  // Verifica se há dados disponíveis na FIFO (DMP)
  if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
    // Aceleração corrigida pela DMP
    VectorInt16 accel;
    mpu.dmpGetAccel(&accel, fifoBuffer);

    // Giroscópio corrigido pela DMP
    VectorInt16 gyro;
    mpu.dmpGetGyro(&gyro, fifoBuffer);

    // Formatar e salvar os dados no SD
    char dataString[128];

    snprintf(dataString, sizeof(dataString), 
             "%lu,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d",
             millis(), 
             ax, ay, az, gx, gy, gz,  // Dados brutos
             accel.x, accel.y, accel.z,  // Aceleração filtrada pela DMP
             gyro.x, gyro.y, gyro.z);  // Velocidade angular filtrada pela DMP

    dataFile.println(dataString);
    Serial.println(dataString);
  }
}


void loop() {
  digitalWrite(3, HIGH);  // LED de gravação ativa
  digitalWrite(4, LOW);   // LED de término apagado

  unsigned long elapsedTime = millis() - startTime;  // Tempo decorrido

  //----------------Verifica se já se passou 48 horas-------------------------//
  if (elapsedTime >= recordingDuration) {
    Serial.println("Tempo máximo atingido, encerrando gravação.");
    closeFile();
  }

  //----------------Verifica o botão para encerrar a gravação antecipadamente-------------------------//
  if (digitalRead(2) == LOW) {  // LOW indica botão pressionado
    Serial.println("Fim manual da gravação.");
    closeFile();
  }

  //----------------Chama a função para ler dados do MPU-------------------------//
  lerMPU();

  //----------------Sincroniza os dados no SD a cada 60 segundos-------------------------//
  if (millis() - lastFlush >= flushInterval) {
    dataFile.flush();
    lastFlush = millis();
    Serial.println("Dados sincronizados no SD.");
    digitalWrite(3, LOW);
  }

  delay(238);  // Pequeno atraso para reduzir a frequência de gravação
}
