/*
  Blank - does nothing
 */

int acc_value_1 = 0;
int acc_value_2 = 0;
int acc_value_3 = 0;
String transmit_values;

void setup() {                
  Serial.begin(9600);
  pinMode(11, OUTPUT);
  digitalWrite(11,HIGH);
}

void loop() {

 acc_value_1 = analogRead(0);
 acc_value_2 = analogRead(1);
 acc_value_3 = analogRead(2);

 transmit_values = String(acc_value_1) + ',' + String(acc_value_2) + ',' + String(acc_value_3);
 Serial.println(transmit_values); 

}

