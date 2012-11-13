/*
  Blank - does nothing
 */

int acc_value_0 = 0;
int acc_value_1 = 0;
int acc_value_2 = 0;
int acc_value_3 = 1;
String transmit_values;

void setup() {                
  Serial.begin(57600);
  pinMode(11, OUTPUT);
  digitalWrite(11,HIGH);
}

void loop() {
 acc_value_1 = analogRead(0);
 acc_value_2 = analogRead(1);
 acc_value_3 = analogRead(2);
 acc_value_0 = 111;
 transmit_values = String(acc_value_1) + ',' + String(acc_value_1) + ',' + String(acc_value_2) + ',' + String(acc_value_3);
 Serial.println(transmit_values); 

// String(timestamp) + ',' +
 //timestamp = timestamp + 1;
 
 delayMicroseconds(10);
 
}

