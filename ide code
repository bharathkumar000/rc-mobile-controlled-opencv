/*
  ESP32 RC Car Control via Wi-Fi Access Point
  Compatible with latest ESP32 core (uses ledcAttach + ledcWrite)

  Wi-Fi AP:
    SSID     : RC_CAR
    Password : 12345678
    URL      : http://192.168.4.1

  Motor Driver:
    L293D / L298N

  Left Motor:
    IN1 -> GPIO 26
    IN2 -> GPIO 27
    ENA -> GPIO 14

  Right Motor:
    IN3 -> GPIO 32
    IN4 -> GPIO 33
    ENB -> GPIO 25
*/

#include <WiFi.h>
#include <WebServer.h>

// ==========================
// Access Point Credentials
// ==========================
const char* ssid = "RC_CAR";
const char* password = "12345678";

// ==========================
// Motor Pins
// ==========================
#define IN1 26
#define IN2 27
#define ENA 14

#define IN3 32
#define IN4 33
#define ENB 25

// ==========================
// PWM Settings
// ==========================
const int pwmFreq = 1000;
const int pwmResolution = 8;     // 0-255
const int motorSpeed = 220;      // Speed value

// ==========================
// Web Server
// ==========================
WebServer server(80);

// ==========================
// Debug Helper
// ==========================
void debug(const String &msg) {
  Serial.print("[DEBUG] ");
  Serial.println(msg);
}

// ==========================
// Motor Control
// ==========================
void setSpeed(int speedValue) {
  debug("Setting speed to " + String(speedValue));
  ledcWrite(ENA, speedValue);   // New ESP32 core API
  ledcWrite(ENB, speedValue);
}

void moveForward() {
  debug("Moving FORWARD");

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  setSpeed(motorSpeed);
}

void moveBackward() {
  debug("Moving BACKWARD");

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  setSpeed(motorSpeed);
}

void turnLeft() {
  debug("Turning LEFT");

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  setSpeed(motorSpeed);
}

void turnRight() {
  debug("Turning RIGHT");

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  setSpeed(motorSpeed);
}

void stopMotors() {
  debug("STOPPING motors");

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  setSpeed(0);
}

// ==========================
// HTML Page
// ==========================
String getHTML() {
  return R"rawliteral(
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ESP32 RC Car</title>
<style>
  body {
    font-family: Arial;
    text-align: center;
    background: #111;
    color: white;
    margin-top: 30px;
  }
  h1 { margin-bottom: 30px; }
  button {
    width: 120px;
    height: 60px;
    font-size: 20px;
    margin: 10px;
    border: none;
    border-radius: 12px;
    font-weight: bold;
    cursor: pointer;
    background: #00c853;
    color: white;
  }
  .stop {
    background: #d50000;
  }
</style>
</head>
<body>
  <h1>ESP32 RC Car</h1>

  <div>
    <button
      onmousedown="send('forward')"
      onmouseup="send('stop')"
      ontouchstart="send('forward')"
      ontouchend="send('stop')">
      Forward
    </button>
  </div>

  <div>
    <button
      onmousedown="send('left')"
      onmouseup="send('stop')"
      ontouchstart="send('left')"
      ontouchend="send('stop')">
      Left
    </button>

    <button class="stop" onclick="send('stop')">
      Stop
    </button>

    <button
      onmousedown="send('right')"
      onmouseup="send('stop')"
      ontouchstart="send('right')"
      ontouchend="send('stop')">
      Right
    </button>
  </div>

  <div>
    <button
      onmousedown="send('backward')"
      onmouseup="send('stop')"
      ontouchstart="send('backward')"
      ontouchend="send('stop')">
      Backward
    </button>
  </div>

<script>
function send(cmd) {
  fetch('/' + cmd)
    .then(response => response.text())
    .then(text => console.log(text))
    .catch(err => console.error(err));
}
</script>
</body>
</html>
)rawliteral";
}

// ==========================
// HTTP Handlers
// ==========================
void handleRoot() {
  debug("Client connected to root page");
  server.send(200, "text/html", getHTML());
}

void handleForward() {
  debug("HTTP Request: /forward");
  moveForward();
  server.send(200, "text/plain", "FORWARD");
}

void handleBackward() {
  debug("HTTP Request: /backward");
  moveBackward();
  server.send(200, "text/plain", "BACKWARD");
}

void handleLeft() {
  debug("HTTP Request: /left");
  turnLeft();
  server.send(200, "text/plain", "LEFT");
}

void handleRight() {
  debug("HTTP Request: /right");
  turnRight();
  server.send(200, "text/plain", "RIGHT");
}

void handleStop() {
  debug("HTTP Request: /stop");
  stopMotors();
  server.send(200, "text/plain", "STOP");
}

void handleNotFound() {
  debug("404 Not Found: " + server.uri());
  server.send(404, "text/plain", "Not Found");
}

// ==========================
// Setup
// ==========================
void setup() {
  Serial.begin(115200);
  delay(1000);

  debug("Booting ESP32 RC Car Controller");

  // Configure motor direction pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  debug("Motor pins configured");

  // Attach PWM directly to pins (new ESP32 core API)
  if (!ledcAttach(ENA, pwmFreq, pwmResolution)) {
    debug("ERROR: Failed to attach PWM to ENA");
  } else {
    debug("PWM attached to ENA (GPIO " + String(ENA) + ")");
  }

  if (!ledcAttach(ENB, pwmFreq, pwmResolution)) {
    debug("ERROR: Failed to attach PWM to ENB");
  } else {
    debug("PWM attached to ENB (GPIO " + String(ENB) + ")");
  }

  // Ensure motors are stopped
  stopMotors();

  // Start Access Point
  debug("Starting Wi-Fi Access Point...");
  WiFi.softAP(ssid, password);

  IPAddress ip = WiFi.softAPIP();

  Serial.println();
  Serial.println("=================================");
  Serial.println("      ESP32 RC CAR READY");
  Serial.println("=================================");
  Serial.print("SSID      : ");
  Serial.println(ssid);
  Serial.print("Password  : ");
  Serial.println(password);
  Serial.print("IP Address: ");
  Serial.println(ip);
  Serial.println("Open your browser and go to:");
  Serial.println("http://192.168.4.1");
  Serial.println("=================================");
  Serial.println();

  // Configure web routes
  server.on("/", handleRoot);
  server.on("/forward", handleForward);
  server.on("/backward", handleBackward);
  server.on("/left", handleLeft);
  server.on("/right", handleRight);
  server.on("/stop", handleStop);
  server.onNotFound(handleNotFound);

  // Start server
  server.begin();
  debug("Web server started successfully");
}

// ==========================
// Loop
// ==========================
void loop() {
  server.handleClient();
}
