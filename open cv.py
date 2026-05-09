import cv2
import mediapipe as mp
import requests
import time

ESP32_IP = "192.168.4.1"
BASE_URL = f"http://{ESP32_IP}"
REQUEST_TIMEOUT = 0.2
SEND_INTERVAL = 0.3  # seconds between repeated same commands

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


def send_command(cmd):
    try:
        requests.get(f"{BASE_URL}/{cmd}", timeout=REQUEST_TIMEOUT)
        print(f"Sent: {cmd}")
    except Exception as e:
        print(f"Failed to send {cmd}: {e}")


def count_fingers(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    count = 0
    lm = hand_landmarks.landmark

    # Thumb (simple heuristic for mirrored webcam view)
    if lm[tips[0]].x < lm[tips[0] - 1].x:
        count += 1

    # Other four fingers
    for tip in tips[1:]:
        if lm[tip].y < lm[tip - 2].y:
            count += 1

    return count


def fingers_to_command(count):
    return {
        1: "forward",
        2: "backward",
        3: "left",
        4: "right",
        5: "stop"
    }.get(count, "stop")


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    last_command = None
    last_send_time = 0

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        print("Gesture control started.")
        print("1 finger -> Forward")
        print("2 fingers -> Backward")
        print("3 fingers -> Left")
        print("4 fingers -> Right")
        print("5 fingers -> Stop")
        print("No hand -> Stop")
        print("Press 'q' to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            command = "stop"
            finger_count = 0

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
                finger_count = count_fingers(hand_landmarks)
                command = fingers_to_command(finger_count)

            now = time.time()
            if command != last_command or (now - last_send_time) > SEND_INTERVAL:
                send_command(command)
                last_command = command
                last_send_time = now

            cv2.putText(
                frame,
                f"Fingers: {finger_count}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Command: {command.upper()}",
                (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2
            )

            cv2.imshow("ESP32 Hand Gesture RC Car", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Stop car before exiting
    send_command("stop")

    cap.release()
    cv2.destroyAllWindows()
    print("Exited successfully.")


if __name__ == "__main__":
    main()

