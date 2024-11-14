import cv2
from pyzbar.pyzbar import decode
import mediapipe as mp
import webbrowser
import platform
import subprocess
import os
import sys
import time
import pyperclip
import tempfile

def main():
    # Start video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam")
        sys.exit(1)
    
    # Set window size
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize Mediapipe Hand Tracking
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils
    
    # Variables
    qr_data = None
    button_list = []
    button_pressed = False
    pressed_button = ''
    
    # QR code data variables
    wifi_info = None
    link_url = None
    plain_text = None
    contact_info = None
    event_info = None
    email_info = None
    sms_info = None
    geo_info = None
    social_media_url = None

    # QR code detection flag
    qr_detected = False
    qr_timeout = 0  # Time to keep the button on screen
    
    # Action messages
    action_message = ''
    action_message_time = 0  # Time when the action message was set
    
    # Cooldown variables to prevent multiple triggers
    button_cooldown = 2  # Seconds
    last_button_press_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Flip the frame horizontally for natural interaction
        frame = cv2.flip(frame, 1)
        
        # Process frame with Mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Decode QR codes in the frame
        decoded_objects = decode(frame)
        if decoded_objects:
            obj = decoded_objects[0]  # Take the first detected QR code
            qr_data = obj.data.decode('utf-8')
            # Draw polygon around QR code
            pts = obj.polygon
            pts = [(pt.x, pt.y) for pt in pts]
            n_pts = len(pts)
            for i in range(n_pts):
                cv2.line(frame, pts[i], pts[(i+1)%n_pts], (0,255,0), 3)
            
            qr_detected = True
            qr_timeout = time.time()  # Reset timeout

            # Process QR code data
            # Clear previous data
            button_list = []
            wifi_info = None
            link_url = None
            plain_text = None
            contact_info = None
            event_info = None
            email_info = None
            sms_info = None
            geo_info = None
            social_media_url = None

            # Set buttons based on QR code content
            if qr_data:
                if qr_data.startswith("WIFI:"):
                    wifi_info = parse_wifi_info(qr_data)
                    button_list = [('Connect to Wi-Fi', (50, 50, 350, 150))]
                elif qr_data.startswith("BEGIN:VCARD"):
                    contact_info = qr_data
                    button_list = [('Save Contact', (50, 50, 350, 150))]
                elif qr_data.startswith("BEGIN:VEVENT"):
                    event_info = qr_data
                    button_list = [('Save Event', (50, 50, 350, 150))]
                elif qr_data.startswith("mailto:"):
                    email_info = qr_data
                    button_list = [('Send Email', (50, 50, 350, 150))]
                elif qr_data.startswith("smsto:"):
                    sms_info = qr_data
                    button_list = [('Send SMS', (50, 50, 350, 150))]
                elif qr_data.startswith("geo:"):
                    geo_info = qr_data
                    button_list = [('Open Map', (50, 50, 350, 150))]
                elif is_social_media_link(qr_data):
                    social_media_url = qr_data
                    button_list = [('Open Profile', (50, 50, 350, 150))]
                elif qr_data.startswith("http://") or qr_data.startswith("https://"):
                    link_url = qr_data
                    button_list = [('Go to Link', (50, 50, 350, 150))]
                else:
                    plain_text = qr_data
                    button_list = [('Copy Text', (50, 50, 350, 150))]
        else:
            qr_detected = False

        # If no QR code is detected, keep the buttons for a certain time
        if not qr_detected and (time.time() - qr_timeout) < 5:
            pass  # Keep the existing buttons
        else:
            if not qr_detected:
                # Time expired, clear the buttons
                button_list = []
                wifi_info = None
                link_url = None
                plain_text = None
                contact_info = None
                event_info = None
                email_info = None
                sms_info = None
                geo_info = None
                social_media_url = None

        # Draw buttons
        for button in button_list:
            text, (x1, y1, x2, y2) = button
            is_pressed = False
            if button_pressed and pressed_button == text:
                is_pressed = True
            draw_button(frame, text, x1, y1, x2, y2, is_pressed)
        
        # Display QR code content
        if wifi_info:
            display_text = f"SSID: {wifi_info['SSID']}"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        elif contact_info:
            display_text = "Contact Information Detected"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        elif event_info:
            display_text = "Event Information Detected"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        elif email_info:
            display_text = "Email Address Detected"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        elif sms_info:
            display_text = "SMS Information Detected"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        elif geo_info:
            display_text = "Geolocation Detected"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        elif social_media_url:
            display_text = "Social Media Profile Detected"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        elif link_url:
            display_text = f"Link: {link_url}"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        elif plain_text:
            display_text = f"Text: {plain_text}"
            cv2.putText(frame, display_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        else:
            cv2.putText(frame, "No QR code detected", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        
        # Display action message
        if action_message and (time.time() - action_message_time) < 3:
            cv2.putText(frame, action_message, (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)
        else:
            action_message = ''  # Clear the message

        # Check for hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get the tip of the index finger
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, c = frame.shape
                index_x, index_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                
                # Draw circle at index finger tip
                cv2.circle(frame, (index_x, index_y), 10, (255, 0, 0), cv2.FILLED)
                
                # Check if index finger tip is over any button
                button_pressed = False
                for button in button_list:
                    text, (x1, y1, x2, y2) = button
                    if x1 < index_x < x2 and y1 < index_y < y2:
                        # Button is being "pressed"
                        current_time = time.time()
                        if current_time - last_button_press_time > button_cooldown:
                            last_button_press_time = current_time
                            pressed_button = text
                            action_message = perform_action(
                                text, wifi_info, link_url, plain_text,
                                contact_info, event_info, email_info,
                                sms_info, geo_info, social_media_url
                            )
                            action_message_time = time.time()
                        button_pressed = True
                        break
                else:
                    button_pressed = False
                
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            button_pressed = False
        
        cv2.imshow('QR Code Scanner', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
def draw_button(frame, text, x1, y1, x2, y2, is_pressed=False):
    if is_pressed:
        color = (0, 255, 0)  # Green when pressed
    else:
        color = (0, 0, 255)  # Red when not pressed
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
    text_x = x1 + (x2 - x1 - text_size[0]) // 2
    text_y = y1 + (y2 - y1 + text_size[1]) // 2
    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

def perform_action(action, wifi_info, link_url, plain_text, contact_info, event_info, email_info, sms_info, geo_info, social_media_url):
    message = ''
    if action == 'Connect to Wi-Fi' and wifi_info:
        success = connect_to_wifi(wifi_info)
        if success:
            message = f"Connected to {wifi_info['SSID']}."
        else:
            message = f"Failed to connect to {wifi_info['SSID']}."
    elif action == 'Go to Link' and link_url:
        webbrowser.open(link_url)
        message = "Opening link..."
    elif action == 'Copy Text' and plain_text:
        pyperclip.copy(plain_text)
        message = "Text copied to clipboard."
    elif action == 'Save Contact' and contact_info:
        success = save_contact(contact_info)
        if success:
            message = "Contact saved."
        else:
            message = "Failed to save contact."
    elif action == 'Save Event' and event_info:
        success = save_event(event_info)
        if success:
            message = "Event saved."
        else:
            message = "Failed to save event."
    elif action == 'Send Email' and email_info:
        success = send_email(email_info)
        if success:
            message = "Opening email client."
        else:
            message = "Failed to send email."
    elif action == 'Send SMS' and sms_info:
        success = send_sms(sms_info)
        if success:
            message = "Opening SMS application."
        else:
            message = "Failed to send SMS."
    elif action == 'Open Map' and geo_info:
        success = open_in_map(geo_info)
        if success:
            message = "Opening location in map."
        else:
            message = "Failed to open location."
    elif action == 'Open Profile' and social_media_url:
        webbrowser.open(social_media_url)
        message = "Opening social media profile..."
    return message

def parse_wifi_info(qr_data):
    """
    Parse Wi-Fi QR code data
    """
    wifi_info = {"SSID": "", "Password": "", "Type": "", "Hidden": False}
    try:
        # Parse format: WIFI:T:WPA;S:SSID;P:password;;
        qr_data = qr_data[5:]
        if qr_data and qr_data[-1] == ';':
            qr_data = qr_data[:-1]
        parts = qr_data.split(';')
        for part in parts:
            if part.startswith("S:"):
                wifi_info["SSID"] = part[2:]
            elif part.startswith("P:"):
                wifi_info["Password"] = part[2:]
            elif part.startswith("T:"):
                wifi_info["Type"] = part[2:]
            elif part.startswith("H:"):
                wifi_info["Hidden"] = part[2:].lower() == "true"
        return wifi_info
    except Exception as e:
        print(f"Error parsing Wi-Fi info: {e}")
    return None

def connect_to_wifi(wifi_info):
    """
    Connect to Wi-Fi network
    """
    ssid = wifi_info["SSID"]
    password = wifi_info["Password"]
    system_os = platform.system()
    try:
        if system_os == "Windows":
            # Windows Wi-Fi connection code
            profile = f"""
            <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                <name>{ssid}</name>
                <SSIDConfig>
                    <SSID>
                        <name>{ssid}</name>
                    </SSID>
                </SSIDConfig>
                <connectionType>ESS</connectionType>
                <connectionMode>auto</connectionMode>
                <MSM>
                    <security>
                        <authEncryption>
                            <authentication>WPA2PSK</authentication>
                            <encryption>AES</encryption>
                            <useOneX>false</useOneX>
                        </authEncryption>
                        <sharedKey>
                            <keyType>passPhrase</keyType>
                            <protected>false</protected>
                            <keyMaterial>{password}</keyMaterial>
                        </sharedKey>
                    </security>
                </MSM>
            </WLANProfile>
            """
            profile_path = "wifi_profile.xml"
            with open(profile_path, "w") as file:
                file.write(profile)
            # Add profile and connect
            subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}"], check=True, capture_output=True)
            subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], check=True, capture_output=True)
            os.remove(profile_path)
            return True
        elif system_os == "Darwin":
            # macOS Wi-Fi connection code
            interface = get_mac_wifi_interface()
            if not interface:
                print("Wi-Fi interface not found")
                return False
            result = subprocess.run(
                ["networksetup", "-setairportnetwork", interface, ssid, password],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True
            else:
                print(f"Error connecting to Wi-Fi: {result.stderr}")
                return False
        elif system_os == "Linux":
            # Linux Wi-Fi connection code
            result = subprocess.run(
                ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True
            else:
                print(f"Error connecting to Wi-Fi: {result.stderr}")
                return False
        else:
            print("Unsupported operating system")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to Wi-Fi: {e}")
        return False

def get_mac_wifi_interface():
    """
    Find the Wi-Fi interface name on macOS
    """
    try:
        result = subprocess.run(
            ["networksetup", "-listallhardwareports"],
            capture_output=True,
            text=True
        )
        output = result.stdout
        interfaces = output.split('\n')
        for i in range(len(interfaces)):
            if 'Wi-Fi' in interfaces[i] or 'AirPort' in interfaces[i]:
                for j in range(i+1, len(interfaces)):
                    if 'Device: ' in interfaces[j]:
                        interface = interfaces[j].split('Device: ')[1]
                        return interface
        return None
    except Exception as e:
        print(f"Error finding Wi-Fi interface: {e}")
        return None

def save_contact(contact_data):
    """
    Save contact information
    """
    try:
        system_os = platform.system()
        if system_os == "Windows":
            temp_dir = tempfile.gettempdir()
            contact_file = os.path.join(temp_dir, "contact.vcf")
            with open(contact_file, "w", encoding="utf-8") as file:
                file.write(contact_data)
            os.startfile(contact_file)
            return True
        elif system_os == "Darwin":
            contact_file = "/tmp/contact.vcf"
            with open(contact_file, "w", encoding="utf-8") as file:
                file.write(contact_data)
            subprocess.run(["open", contact_file])
            return True
        elif system_os == "Linux":
            contact_file = "/tmp/contact.vcf"
            with open(contact_file, "w", encoding="utf-8") as file:
                file.write(contact_data)
            subprocess.run(["xdg-open", contact_file])
            return True
        else:
            print("Unsupported operating system")
            return False
    except Exception as e:
        print(f"Error saving contact: {e}")
        return False

def save_event(event_data):
    """
    Save event to calendar
    """
    try:
        system_os = platform.system()
        if system_os == "Windows":
            temp_dir = tempfile.gettempdir()
            event_file = os.path.join(temp_dir, "event.ics")
            with open(event_file, "w", encoding="utf-8") as file:
                file.write(event_data)
            os.startfile(event_file)
            return True
        elif system_os == "Darwin":
            event_file = "/tmp/event.ics"
            with open(event_file, "w", encoding="utf-8") as file:
                file.write(event_data)
            subprocess.run(["open", event_file])
            return True
        elif system_os == "Linux":
            event_file = "/tmp/event.ics"
            with open(event_file, "w", encoding="utf-8") as file:
                file.write(event_data)
            subprocess.run(["xdg-open", event_file])
            return True
        else:
            print("Unsupported operating system")
            return False
    except Exception as e:
        print(f"Error saving event: {e}")
        return False

def send_email(email_data):
    """
    Send an email
    """
    try:
        email_url = email_data  # Example: mailto:example@example.com?subject=Hello
        webbrowser.open(email_url)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_sms(sms_data):
    """
    Send an SMS
    """
    try:
        # Example: smsto:+1234567890:Your message
        sms_data = sms_data.replace("smsto:", "")
        parts = sms_data.split(':', 1)
        phone_number = parts[0]
        message = parts[1] if len(parts) > 1 else ''
        # Note: Sending SMS is platform-dependent and may require additional implementation.
        print(f"Sending SMS to {phone_number} with message: {message}")
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def open_in_map(geo_data):
    """
    Open location in map
    """
    try:
        # Example: geo:37.7749,-122.4194
        geo_data = geo_data.replace("geo:", "")
        coordinates = geo_data.split(',')
        latitude = coordinates[0]
        longitude = coordinates[1] if len(coordinates) > 1 else ''
        map_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
        webbrowser.open(map_url)
        return True
    except Exception as e:
        print(f"Error opening map: {e}")
        return False

def is_social_media_link(url):
    """
    Check if the URL is a social media profile link
    """
    social_domains = ['instagram.com', 'twitter.com', 'facebook.com', 'linkedin.com', 'tiktok.com']
    for domain in social_domains:
        if domain in url:
            return True
    return False

if __name__ == "__main__":
    main()
