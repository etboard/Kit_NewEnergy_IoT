/******************************************************************************************
 * FileName     : NewEnergy_IoT
 * Description  : 이티보드 스마트 신재생 에너지 코딩 키트(IoT)
 * Author       : SCS
 * Created Date : 2022.08.18
 * Reference    : 
 * Modified     : 2022.08.19 : LSC
 * Modified     : 2022.12.28 : YSY : 변수 명명법 통일
 * Modified     : 2024.08.29 : PEJ : 프로그램 구조 변경
 * Modified     : 2024.09.02 : PEJ : 메시지 key 변경
 * Modified     : 2024.09.02 : PEJ : 메시지 수신 함수 추가
******************************************************************************************/
const char* board_firmware_verion = "newEnergy_0.92";


//==========================================================================================
// IoT 프로그램 사용하기
//==========================================================================================
#include "ET_IoT_App.h"
ET_IoT_App app;


//==========================================================================================
// 전역 변수 선언
//==========================================================================================
const int solar_pin = A3;                                // 태양광 발전량 측정 센서
const int wind_pin  = A5;                                // 풍력 발전량 측정 센서

float solar_power;                                       // 태양광 발전기 값(V)
float wind_power;                                        // 풍력 발전기 값(V)
float solar_sensor_value = 0;
float wind_sensor_value = 0;

float solar_max = 0;                                     // 태양광 발전기 최댓값
float wind_max  = 0;                                     // 풍력 발전기 최댓값

const double c_value = 0.000806;                         // 전압 보정 변수 선언 (3.3v / 4096)

int led_red = D2;                                        // PWM용 Motor-L
int led_blue = D4;                                       // PWM용 Motor-R

//==========================================================================================
void et_setup()                                          // 사용자 맞춤형 설정
//==========================================================================================
{
  pinMode(solar_pin, INPUT);                             // 모터 제어핀1: 입력 모드
  pinMode(wind_pin, INPUT);                              // 모터 제어핀2; 입력 모드

  ledcAttachPin(led_red, 0);                             // PWM 채널 0번 설정
  ledcSetup(0, 5000, 8);
  ledcAttachPin(led_blue, 1);                            // PWM 채널 1번 설정
  ledcSetup(1, 5000, 8);  
}

//=========================================================================================
void solar_convert() 
//=========================================================================================
{
  int value = solar_sensor_value;
  value = value / 1.5;
  if (value >= 1023) {
    value = 1023;
  }
  if (value >= 30) {
    value = 1023;
  }
  ledcWrite(0, value);  // Solar PWM 출력
}

//=========================================================================================
void wind_convert() 
//=========================================================================================
{
  int value = wind_sensor_value;
  value = value / 4;
  if (value >= 1023) {
    value = 1023;
  }
  ledcWrite(1, value);  // Wind PWM 출력
}

//==========================================================================================
void et_loop()                                           // 사용자 반복 처리
//==========================================================================================
{
  do_sensing_process();                                  // 센싱 처리
  do_automatic_process();
}


//==========================================================================================
void do_sensing_process()                                // 센싱 처
//==========================================================================================
{
  //float solar_sensor_value = analogRead(solar_pin);    // 태양광 발전 센서 값 읽기
  solar_sensor_value = analogRead(solar_pin);          // 태양광 발전 센서 값 읽기
  solar_power = solar_sensor_value * c_value;          // 전압 보정
  if(solar_power > solar_max)                          // 최댓값 저장
    solar_max = solar_power;

  //float wind_sensor_value = analogRead(wind_pin);      // 풍력 발전 센서 값 읽기
  wind_sensor_value = analogRead(wind_pin);            // 풍력 발전 센서 값 읽기
  wind_power = wind_sensor_value * c_value;            // 전압 보정
  if(wind_power > wind_max)                            // 최댓값 저장
    wind_max = wind_power;
}

//==========================================================================================
void do_automatic_process()                       // 자동화 처리 함수
//==========================================================================================
// 여기에 자동화 처리를 코딩하세요.
//------------------------------------------------------------------------------------------
{  
  solar_convert();
  wind_convert();
}


//==========================================================================================
void et_short_periodic_process()                         // 사용자 주기적 처리 (예 : 1초마다)
//==========================================================================================
{
  display_information();                                 // 표시 처리
}


//==========================================================================================
void et_long_periodic_process()                          // 사용자 주기적 처리 (예 : 5초마다)
//==========================================================================================
{
  send_message();                                        // 메시지 송신
}


//==========================================================================================
void display_information()                               // OLED 표시
//==========================================================================================
{
  String string_solar = String(solar_power);             // 태양광 발전 값을 문자열로 변환
  String string_wind = String(wind_power);               // 풍력 발전 값을 문자열로 변환

  app.oled.setLine(1, board_firmware_verion);            // 1번째 줄에 펌웨어 버전
  app.oled.setLine(2, "solar: " + string_solar + "v");   // 2번재 줄에 태양광
  app.oled.setLine(3, "wind: " + string_wind + "v");     // 3번재 줄에 풍력
  app.oled.display();                                    // OLED에 표시
}


//==========================================================================================
void send_message()                                      // 메시지 송신
//==========================================================================================
{
  app.add_sensor_data("solar", solar_power);             // 센서 데이터 추가
  app.add_sensor_data("wind", wind_power);               // 센서 데이터 추가
  app.add_sensor_data("solar_max", solar_max);           // 센서 데이터 추가
  app.add_sensor_data("wind_max", wind_max);             // 센서 데이터 추가
  app.send_sensor_data();                                // 센서 데이터 송신
}


//==========================================================================================
void recv_message()                                      // 메시지 수신
//==========================================================================================
{
  // 메시지를 수신받으면 처리할 동작을 작성하세요.
}


//==========================================================================================
//                                                    
// (주)한국공학기술연구원 http://et.ketri.re.kr       
//                                                    
//==========================================================================================