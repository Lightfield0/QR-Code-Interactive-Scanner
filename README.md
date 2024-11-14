# QR Code Interactive Scanner

![QR Code Scanner](https://github.com/Lightfield0/qr-code-interactive-scanner/blob/main/assets/lightfield_online_qr.png?raw=true)

QR Code Interactive Scanner is a Python-based application that leverages computer vision and hand gesture recognition to provide an intuitive and interactive way to interact with QR codes. By combining **OpenCV**, **PyZbar**, and **Mediapipe**, this tool not only detects and decodes QR codes but also allows users to perform actions through hand gestures, making the experience seamless and hands-free.

## Features

- **Real-time QR Code Detection**: Utilize your webcam to scan and decode QR codes instantly.
- **Interactive Buttons**: Based on the QR code content, relevant action buttons are displayed on the screen.
- **Hand Gesture Control**: Use hand gestures to "press" buttons, triggering actions without touching your device.
- **Wide Range of Actions**:
  - **Wi-Fi Connection**: Connect to Wi-Fi networks directly from the QR code.
  - **Open Links**: Navigate to URLs embedded in QR codes.
  - **Copy Text**: Easily copy plain text from QR codes to your clipboard.
  - **Save Contacts & Events**: Add contacts or calendar events from vCard and vEvent QR codes.
  - **Send Emails & SMS**: Initiate email drafts or SMS messages based on QR content.
  - **Open Maps**: View geolocations in your default map application.
  - **Social Media Profiles**: Open social media profiles directly.

## Demo

![Demo Video](https://github.com/Lightfield0/qr-code-interactive-scanner/blob/main/assets/demo_video.gif?raw=true)

### Prerequisites

- **Python 3.7 or higher**
- **Webcam** connected to your computer

### Clone the Repository

```bash
git clone https://github.com/Lightfield0/qr-code-interactive-scanner.git
cd qr-code-interactive-scanner
```

### Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```


*Note: Ensure that you have the necessary permissions to install and run these packages on your system.*

## Usage

Run the main script:

```bash
python qr_code_scanner.py
```

### Controls

- **Exit**: Press the `q` key to quit the application.

### How It Works

1. **Start Video Capture**: The application accesses your webcam and starts capturing video frames.
2. **QR Code Detection**: Using **PyZbar**, it scans each frame for QR codes and decodes the data.
3. **Display Action Buttons**: Based on the QR code content (e.g., Wi-Fi credentials, URLs, contact info), relevant buttons are displayed on the screen.
4. **Hand Gesture Recognition**: With **Mediapipe**, the application tracks your hand movements. When you gesture to "press" a button, the corresponding action is executed.
5. **Perform Actions**: Actions include connecting to Wi-Fi, opening links, copying text, saving contacts/events, sending emails/SMS, and more.

## Supported QR Code Types

- **Wi-Fi Credentials** (`WIFI:`)
- **vCard Contacts** (`BEGIN:VCARD`)
- **vEvent Calendar Events** (`BEGIN:VEVENT`)
- **Email Links** (`mailto:`)
- **SMS Messages** (`smsto:`)
- **Geolocation** (`geo:`)
- **Social Media Profiles** (e.g., Instagram, Twitter)
- **URLs** (`http://` or `https://`)
- **Plain Text**


## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- **[OpenCV](https://opencv.org/)** for computer vision capabilities.
- **[PyZbar](https://pypi.org/project/pyzbar/)** for QR code decoding.
- **[Mediapipe](https://mediapipe.dev/)** for hand gesture recognition.
- **[Pyperclip](https://pyperclip.readthedocs.io/en/latest/)** for clipboard operations.


*Happy Scanning! 🚀*
