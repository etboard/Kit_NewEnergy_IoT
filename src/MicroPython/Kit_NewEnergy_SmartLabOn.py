# ******************************************************************************************
# FileName     : Kit_NewEnergy_SmartLabOn.py
# Description  : 
# Author       : 박은정
# Created Date : 2025.08.11 : PEJ
# Reference    :
# Modified     : 
# ******************************************************************************************
board_firmware_verion = "newEnergy_0.91";


#===========================================================================================
# 기본 모듈 사용하기
#===========================================================================================
from machine import Pin
from ETboard.lib.pin_define import *                     # ETboard 핀 관련 모듈


#===========================================================================================
# IoT 프로그램 사용하기
#===========================================================================================
from ET_IoT_App import ET_IoT_App, setup, loop
app = ET_IoT_App()


#===========================================================================================
# OLED 표시 장치 사용하기
#===========================================================================================
from ETboard.lib.OLED_U8G2 import *
oled = oled_u8g2()


#===========================================================================================
# 전역 변수 선언
#===========================================================================================
solar_pin = ADC(Pin(A3))                                 # 태양광 발전 센서 핀: A3
wind_pin = ADC(Pin(A5))                                  # 풍력 발전 센서 핀: A5

solar_power = 0                                          # 태양광 발전 전압
wind_power = 0                                           # 풍력 발전 전압

solar_max = 0                                            # 태양광 발전 최댓값
wind_max = 0                                             # 풍력 발전 최댓값

c_value = 0.000806                                       # 전압 보정 값(3.3v / 4096)


#===========================================================================================
def et_setup():                                          #  사용자 맞춤형 설정
#===========================================================================================
    solar_pin.atten(ADC.ATTN_11DB)                       # 태양광 발전 센서 입력 모드 설정
    wind_pin.atten(ADC.ATTN_11DB)                        # 풍력 발전 센서 입력 모드 설정

    recv_message()                                       # 메시지 수신


#===========================================================================================
def et_loop():                                           # 사용자 반복 처리
#===========================================================================================
    do_sensing_process()                                 # 센싱 처리


#===========================================================================================
def do_sensing_process():                                # 센싱 처리
#===========================================================================================
    global solar_power, wind_power, solar_max, wind_max

    solar_value = solar_pin.read()                       # 태양광 발전량 측정값 저장
    solar_power = solar_value * c_value                  # 전압 보정
    if solar_power > solar_max:                          # 최댓값 저장
        solar_max = solar_power;

    wind_value = wind_pin.read()                         # 풍력 발전량 측정값 저장
    wind_power = wind_value * c_value                    # 전압 보정
    if wind_power > wind_max:                            # 최댓값 저장
        wind_max = wind_power;


#===========================================================================================
def et_short_periodic_process():                         # 사용자 주기적 처리 (예 : 1초마다)
#===========================================================================================    
    display_information()                                # 표시 처리


#===========================================================================================
def et_long_periodic_process():                          # 사용자 주기적 처리 (예 : 5초마다)
#===========================================================================================    
    send_message()                                       # 메시지 송신


#===========================================================================================
def display_information():                               # OLED 표시
#===========================================================================================
    global board_firmware_verion, solar_power, wind_power, solar_max, wind_max

    string_solar = "%0.2f" % solar_power                 # 태양광 발전 값을 문자열로 변환
    string_wind = "%0.2f" % wind_power                   # 풍력 발전 값을 문자열로 변환

    oled.clear()                                         # OLED 초기화
    oled.setLine(1, board_firmware_verion)               # 1번째 줄에 태양광
    oled.setLine(2, 'solar: ' + string_solar + 'v')      # 2번째 줄에 풍력
    oled.setLine(3, 'wind: '  + string_wind + 'v')       # 3번쩨 줄에 펌프 작동 상태
    oled.display()                                       # OLED에 표시


#===========================================================================================
def send_message():                                      # 메시지 송신
#===========================================================================================
    global solar_power, wind_power, solar_max, wind_max
    app.add_sensor_data("solar", solar_power);           # 센서 데이터 추가
    app.add_sensor_data("wind", wind_power);             # 센서 데이터 추가
    app.add_sensor_data("solar_max", solar_max);         # 센서 데이터 추가
    app.add_sensor_data("wind_max", wind_max);           # 센서 데이터 추가
    app.send_sensor_data();                              # 센서 데이터 송신


#===========================================================================================
def recv_message():                                      # 메시지 수신
#===========================================================================================
    # "get_sensor_type" 메시지를 받으면 send_sensor_type() 실행
    app.setup_recv_message('get_sensor_type', handle_get_sensor_type_request)


#===========================================================================================
def json_to_unicode_escaped(data):                       # 직렬화, 이스케이프
#===========================================================================================
    # JSON 직렬화
    json_string = ujson.dumps(data)

    # JSON 문자열에서 비-ASCII 문자를 Unicode 이스케이프 형식으로 변환
    return ''.join(f'\\u{ord(c):04x}' if ord(c) > 127 else c for c in json_string)


#===========================================================================================
def handle_get_sensor_type_request(topic, msg):          # 센서 타입 송신 처리
#===========================================================================================
    send_sensor_type()


#===========================================================================================
def send_sensor_type():                                  # 센서 타입 전송
#===========================================================================================
    sensor_type = {
        "sensorId": "solar",
        "sensorType": "solar",
        "sensorNicNm": "태양광 발전량",
        "channelCode": "01",
        "collectUnit": "V",
    }
    payload = json_to_unicode_escaped(sensor_type)
    app.send_data("sensor_types", "solar", payload)

    sensor_type = {
        "sensorId": "wind",
        "sensorType": "wind",
        "sensorNicNm": "풍력 발전량",
        "channelCode": "01",
        "collectUnit": "V",
    }
    payload = json_to_unicode_escaped(sensor_type)
    app.send_data("sensor_types", "wind", payload)
    sensor_type = {
        "sensorId": "solar_max",
        "sensorType": "solar_max",
        "sensorNicNm": "태양광 최대 발전량",
        "channelCode": "01",
        "collectUnit": "V",
    }
    payload = json_to_unicode_escaped(sensor_type)
    app.send_data("sensor_types", "solar_max", payload)

    sensor_type = {
        "sensorId": "wind_max",
        "sensorType": "wind_max",
        "sensorNicNm": "풍력 최대  발전량",
        "channelCode": "01",
        "collectUnit": "V",
    }
    payload = json_to_unicode_escaped(sensor_type)
    app.send_data("sensor_types", "wind_max", payload)


#===========================================================================================
# 시작 지점                     
#===========================================================================================
if __name__ == "__main__":
    setup(app, et_setup)
    while True:
        loop(app, et_loop, et_short_periodic_process, et_long_periodic_process)


#===========================================================================================
#                                                    
# (주)한국공학기술연구원 http://et.ketri.re.kr       
#
#===========================================================================================