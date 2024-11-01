int sensorPin = A0;  // Analog input pin
int sensorValue = 0; // Variable to store the value from the sensor
float pressure = 0;  // Variable to store the calculated pressure
float voltage = 0;   // Variable to store the output voltage

const float Vmin = 0.5; // Minimum voltage corresponding to 0 psi
const float Vmax = 4.5; // Maximum voltage corresponding to 2000 psi
const float FSS = 2000.0; // Full Scale Span in psi

void setup() {
  Serial.begin(4800);
}

void loop() {
  sensorValue = analogRead(sensorPin);  // Read the analog input
  voltage = sensorValue * (5.0 / 1023.0);  // Convert the analog value to voltage (0 to 5V range)
  
  // Convert the voltage to pressure based on the FSS and sensor output range
  if (voltage >= Vmin && voltage <= Vmax) {
    pressure = (voltage - Vmin) / (Vmax - Vmin) * FSS;
  } else {
    pressure = 0;  // If voltage is out of expected range, set pressure to 0
  }

  // Print the pressure
  Serial.print("Pressure: ");
  Serial.println(pressure);
  
}

