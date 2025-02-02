# dos_sandbox

DOSBox 기반의 MS-DOS 4.0 샌드박스 환경 및 x86 하드웨어 디버거 구현 프로젝트

구성요소:
- 인터럽트 컨트롤러 (하드웨어, 소프트웨어, 가상 인터럽트 믹싱)
- 타이머 (클럭 신호, 시드용 시간, 하드웨어 시계)
- 가상 EISA 버스 컨트롤러 (키보드/마우스, ATA/EIDE 프로토콜)
- DMA 컨트롤러 (주 메모리 데이터 이동, 인터럽트 전달)
- 가상 그래픽 장치 (VGA 드라이버, SDL2를 이용한 렌더링)
- 가상 저장장치 (IDE 하드디스크 프로토콜, 동적 디스크 이미지 지원)
- BIOS (시스템 메모리 맵, 부팅 정보 제공)
- i80386 CPU 시뮬레이터 (레지스터, ALU, 디코더, 인터럽트 처리)
- x86 하드웨어 디버거 (Go/Next/Stop 기능)

## 빌드 및 실행
* SDL2 라이브러리가 필요합니다.
make ./dos_sandbox

