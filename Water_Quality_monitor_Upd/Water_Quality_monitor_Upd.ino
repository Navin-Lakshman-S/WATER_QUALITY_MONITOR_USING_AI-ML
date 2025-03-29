#include <ArduinoJson.h>
#include <ArduinoJson.hpp>
#include <OneWire.h>
#include <DallasTemperature.h>

const int oneWireBus = 4;  // GPIO where the DS18B20 is connected to

//TDS Sensor
#define TdsSensorPin 34
#define VREF 3.3   // analog reference voltage(Volt) of the ADC
#define SCOUNT 30  // sum of sample point

int analogBuffer[SCOUNT];  // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0;
int copyIndex = 0;

float averageVoltage = 0;
float tdsValue = 0;
float temperature = 25;  // current temperature for compensation

float voltontu(float voltage){
  float ntu = -1120.4 * pow(voltage, 3) + 5742.3 * pow(voltage, 2) - 4352.9 * voltage + 1179.6;
  return ntu;
}

// median filtering algorithm
int getMedianNum(int bArray[], int iFilterLen){
  int bTab[iFilterLen];
  for (byte i = 0; i<iFilterLen; i++)
  bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++) {
    for (i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0){
    bTemp = bTab[(iFilterLen - 1) / 2];
  }
  else {
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  }
  return bTemp;
}

// TDS algorithm end

int turbidity = 35;
float turbidityRead = 0;

OneWire oneWire(oneWireBus);  // Setup a oneWire instance to communicate with any OneWire devices

DallasTemperature sensors(&oneWire);  // Pass our oneWire reference to Dallas Temperature sensor

void setup() {
  Serial.begin(115200);
  pinMode(turbidity, INPUT);
  pinMode(TdsSensorPin, INPUT);
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  sensors.begin();
  Serial1.begin(9600, SERIAL_8N1, 16, 17);
  Serial.println("YOYO Serial Monitor initialised! ");
}

void loop() {
  //turbidity sensor reading
  turbidityRead = analogRead(turbidity);
  turbidityRead = turbidityRead * (3.3 / 4095.0) ;
  // turbidityRead = (turbidityRead/4095.0)*3.3;
  // turbidityRead = voltontu(turbidityRead);
  if(turbidityRead<0){turbidityRead=abs(turbidityRead);}
  
  float PH;
  if (Serial1.available()) {
    String sdata = Serial1.readStringUntil(':');
    // Serial.println(sdata);
    if (sdata != "") {
      // Serial.println(sdata);
      String t_pH = Serial1.readStringUntil('$');
      PH = t_pH.toFloat();
      // Serial.println(PH);
    }}

    sensors.requestTemperatures();
    float temperature = sensors.getTempCByIndex(0);

      static unsigned long analogSampleTimepoint = millis();
  if(millis()-analogSampleTimepoint > 40U){     //every 40 milliseconds,read the analog value from the ADC
    analogSampleTimepoint = millis();
    analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin);    //read the analog value and store into the buffer
    analogBufferIndex++;
    if(analogBufferIndex == SCOUNT){ 
      analogBufferIndex = 0;
    }
  }   
  
  static unsigned long printTimepoint = millis();
  if(millis()-printTimepoint > 800U){
    printTimepoint = millis();
    for(copyIndex=0; copyIndex<SCOUNT; copyIndex++){
      analogBufferTemp[copyIndex] = analogBuffer[copyIndex];
      
      // read the analog value more stable by the median filtering algorithm, and convert to voltage value
      averageVoltage = getMedianNum(analogBufferTemp,SCOUNT) * (float)VREF / 4096.0;
      
      //temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0)); 
      float compensationCoefficient = 1.0+0.02*(temperature-25.0);
      //temperature compensation
      float compensationVoltage=averageVoltage/compensationCoefficient;
      
      //convert voltage value to tds value
      tdsValue=(133.42*compensationVoltage*compensationVoltage*compensationVoltage - 255.86*compensationVoltage*compensationVoltage + 857.39*compensationVoltage)*0.5;
      
      //Serial.print("voltage:");
      //Serial.print(averageVoltage,2);
      //Serial.print("V   ");
      // Serial.print("TDS Value:");
      // Serial.print(tdsValue,0);
      // Serial.println("ppm");
    }
  }

    // readTdsQuick();
    JsonDocument doc;
    doc["PH"] = PH;
    doc["TDS"] = tdsValue;
    // doc["EC"] = sensor::ec;
    doc["Turbidity"]=turbidityRead;
    doc["Temperature"]=temperature;

    serializeJson(doc,Serial);

    Serial.println();
  // }
}
