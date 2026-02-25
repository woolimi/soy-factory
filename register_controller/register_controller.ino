/*
 * RegisterController — 작업자를 등록하는 키트 (Arduino + RFID)
 * 관리자 PC와 Serial 통신 (USB 시리얼)
 * 보드: Arduino Uno
 *
 * Typical pin layout used:
 * -----------------------------------------------------------------------------------------
 *             MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
 *             Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
 * Signal      Pin          Pin           Pin       Pin        Pin              Pin
 * -----------------------------------------------------------------------------------------
 * RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
 * SPI SS      SDA(SS)      10            53        D10        10               10
 * SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
 * SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
 * SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15
 * 3.3v -> VIN
 *
 * More pin layouts for other boards can be found here: https://github.com/miguelbalboa/rfid#pin-layout
 */

#include <SPI.h>
#include <MFRC522.h>

#define SERIAL_BAUD 9600
#define RST_PIN     9   // Configurable, see typical pin layout above
#define SS_PIN      10  // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(SERIAL_BAUD);
  for (unsigned long t = millis(); !Serial && (millis() - t < 2000);)
    ;  // 시리얼 포트 최대 2초 대기 (무한 대기 방지)

	// Initialize SPI and RFID reader
	SPI.begin();
	mfrc522.PCD_Init();
	delay(4); // Optional delay for some boards
	mfrc522.PCD_DumpVersionToSerial();
}

// 프로토콜: NDJSON 한 줄 (docs/soy-kit-protocol.md)
// {"type":"card_read","source":"register_controller","uid":"XXXXXXXX"}
void sendCardRead(const byte* uidByte, byte uidSize) {
  Serial.print("{\"type\":\"card_read\",\"source\":\"register_controller\",\"uid\":\"");
  for (byte i = 0; i < uidSize; i++) {
    if (uidByte[i] < 0x10) Serial.print("0");
    Serial.print(uidByte[i], HEX);
  }
  Serial.println("\"}");
}

void loop() {
  // 카드가 없으면 다음 루프
  if (!mfrc522.PICC_IsNewCardPresent())
    return;
  if (!mfrc522.PICC_ReadCardSerial())
    return;

  sendCardRead(mfrc522.uid.uidByte, mfrc522.uid.size);

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  delay(300);  // 연속 읽기 방지
}
