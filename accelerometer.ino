/*
  Blank - does nothing
 */

int acc_value_1 = 0;
int acc_value_2 = 0;
int acc_value_3 = 0;
int accel=0;
int accel_new=0;
int incomingByte = 0;   // for incoming serial data
long counter = 0;  


void setup() {                
  Serial.begin(9600);
  int led_pins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10};
  //for (int k = 2;k < 11;k++){
  //  pinMode(k,OUTPUT);
  //}
  pinMode(11, OUTPUT);
  digitalWrite(11,HIGH);
}

void loop() {

 acc_value_1 = analogRead(0);
 acc_value_2 = analogRead(1);
 acc_value_3 = analogRead(2);
 //Serial.println("=========");
 //Serial.println(acc_value_1);
 //Serial.println(acc_value_2);
 
 //Should proabably switch to Serial.write()???
 Serial.print(acc_value_1);
 //Serial.print(',');
 //Serial.print(acc_value_2);
 //Serial.print(',');
 //Serial.print(acc_value_3);
 Serial.print('\n');
 delay(1);
 
 //Serial.println("=========");


 accel = acc_value_3;

 //for (long i = 0; i < 250L; i++){
 //  digitalWrite(9,HIGH);
 //  delayMicroseconds(tone);
 //  digitalWrite(9,LOW);
 //  delayMicroseconds(tone);
// }
//tone(13,accel,100);
//led_bank(accel);
counter++;
}

void led_bank(int accel){
int led_value = accel / 100;
for (int k=2;k<led_value+1;k++){
  digitalWrite(k,HIGH);
}
//delay(500);

for (int k=led_value+1;k<11;k++){
  digitalWrite(k,LOW);
}
}
