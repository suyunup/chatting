# chatting
소켓을 이용한 채팅 프로그램

## How to run
final_receiver.py를 실행후 final_sender.py를 실행
실행시 입력 데이터 없음

Code Block 의 구조및 기능
#####final_sender.py#####
Application
scenario1: 1111000011110000의 데이터를 전송
scenario2: ACK 수신확인 메시지 출력

Transport
scenario1:stop and wait protocol
scenario2: ACK메세지를 받은다음 ASCII code를 다시 문자로 변환

Network
scenario1:bypass
scenario2:bypass

Datalink
scenario1:message bit-stuffing, simple protocol , CSMA/CD
scenario2:message bit-unsutffing, simple protocol

physical
scenario1:multi-transition MLT-3scheme
scenario2:Reverse MLT-3 scheme

alarm_handler
transport의 stop and wait protocol에서 사용하는 time out 확인용 함수

binTohex
도착한 ACK 이진 문자열을 십진수로 변환하는 함수


#####final_receiver.py#####

physical
scenario1:Reverse MLT-3 scheme
scenario2:multi-transition MLT-3scheme

Datalink
scenario1:message bit-unsutffing, simple protocol
scenario2:bit-stuffing, simple protocol , CSMA/CD

Network
scenario1:bypass
scenario2:bypass

Transport
scenario1:stop and wait protocol
scenario2:stop and wait protocol, ACK ASCII code 생성

Application
scenario1:1111000011110000 수신 확인
scenario2:메세지 수신완료

alarm_handler
transport의 stop and wait protocol에서 사용하는 time out 확인용 함수
