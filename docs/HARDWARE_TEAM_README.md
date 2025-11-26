# 🔧 Hardware Team - Raspberry Pi Setup Guide

**Team Member:** Anshul  
**Responsibility:** Real-time parking spot monitoring with IR sensors  

---

## 🎯 Your Mission

Build a Raspberry Pi system that monitors 30 parking spots using IR sensors and sends real-time occupancy data to Firebase. This is the foundation of the entire parking system - without your sensors, nothing else works!

---

## 📋 What You're Building

**Input:** IR sensors detect when cars park/leave  
**Output:** Firebase database updates in real-time  
**Result:** Backend and Frontend teams see live parking availability

---

## 🏗️ Parking Lot Layout (30 Spots)

```
Zone A - Premium (10 spots) - Covered, EV Charging
  A-01 → GPIO 17    A-06 → GPIO 10
  A-02 → GPIO 18    A-07 → GPIO 11
  A-03 → GPIO 27    A-08 → GPIO 12
  A-04 → GPIO 22    A-09 → GPIO 13
  A-05 → GPIO 23    A-10 → GPIO 14

Zone B - Regular (15 spots) - Covered
  B-01 → GPIO 15    B-09 → GPIO 4
  B-02 → GPIO 16    B-10 → GPIO 5
  B-03 → GPIO 21    B-11 → GPIO 8
  B-04 → GPIO 26    B-12 → GPIO 9
  B-05 → GPIO 19    B-13 → GPIO 25
  B-06 → GPIO 20    B-14 → GPIO 2
  B-07 → GPIO 6     B-15 → GPIO 3
  B-08 → GPIO 7

Zone C - Budget (5 spots) - Open Air
  C-01 → GPIO 1
  C-02 → GPIO 0
  C-03 → GPIO 24
  C-04 → GPIO 28
  C-05 → GPIO 29

Entry Gate → GPIO 31
Exit Gate  → GPIO 32
```

---

## 🔌 Wiring Diagram

### Each IR Sensor Connects Like This:

```
E18-D80NK IR Sensor          Raspberry Pi GPIO
─────────────────────        ─────────────────
VCC (Brown Wire)        →    5V (Pin 2 or Pin 4)
GND (Blue Wire)         →    GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
OUT (Black Wire)        →    GPIO Pin (see layout above)
```

### Example: Wiring Spot A-01

```
Sensor A-01:
  Brown wire  → Raspberry Pi Pin 2 (5V)
  Blue wire   → Raspberry Pi Pin 6 (GND)
  Black wire  → Raspberry Pi Pin 11 (GPIO 17)
```

### Power Distribution:
- Connect all 30 sensor VCC wires to 5V rail on breadboard
- Connect breadboard 5V rail to Raspberry Pi Pin 2
- Connect all 30 sensor GND wires to GND rail on breadboard
- Connect breadboard GND rail to Raspberry Pi Pin 6

---

## 🔥 Firebase Configuration

### **IMPORTANT: Firebase Credentials**

**Contact Backend Team** to get these files:
1. `parkngo-firebase-adminsdk.json` - Service account credentials
2. Firebase Database URL

### Firebase Project Details:

```
Project Name: parkngo-ai
Database URL: https://parkngo-ai-default-rtdb.asia-southeast1.firebasedatabase.app
Region: asia-southeast1
```

### Where to Store Credentials:

```bash
/home/pi/parkngo/secrets/parkngo-firebase-adminsdk.json
```

**⚠️ NEVER commit this file to GitHub!**

---

## 📝 Firebase Database Schema (What You'll Write)

Your Raspberry Pi will update these Firebase paths:

### 1. Parking Spots Status

```json
{
  "parking_spots": {
    "A-01": {
      "spot_id": "A-01",
      "zone": "A",
      "type": "premium",
      "features": ["covered", "ev_charging"],
      "occupied": false,
      "last_updated": "2025-11-27T10:30:00Z",
      "gpio_pin": 17,
      "sensor_status": "active"
    },
    "B-15": {
      "spot_id": "B-15",
      "zone": "B",
      "type": "regular",
      "features": ["covered"],
      "occupied": true,
      "last_updated": "2025-11-27T10:45:00Z",
      "gpio_pin": 3,
      "sensor_status": "active",
      "current_session": "SES_ABC123"
    }
  }
}
```

### 2. Entry/Exit Events

```json
{
  "entries": {
    "ENTRY_20251127_001": {
      "entry_id": "ENTRY_20251127_001",
      "timestamp": "2025-11-27T10:45:00Z",
      "vehicle_id": "UNKNOWN",
      "entry_gate": "main",
      "status": "entered"
    }
  },
  "exits": {
    "EXIT_20251127_001": {
      "exit_id": "EXIT_20251127_001",
      "timestamp": "2025-11-27T12:30:00Z",
      "vehicle_id": "UNKNOWN",
      "exit_gate": "main",
      "status": "exited"
    }
  }
}
```

### 3. Parking Sessions

```json
{
  "sessions": {
    "SES_ABC123": {
      "session_id": "SES_ABC123",
      "spot_id": "B-15",
      "entry_time": "2025-11-27T10:45:00Z",
      "exit_time": null,
      "status": "active",
      "vehicle_id": "UNKNOWN"
    }
  }
}
```

---

## 💾 Software Installation

### Step 1: Setup Raspberry Pi OS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip -y

# Install GPIO library
sudo apt install python3-rpi.gpio -y
```

### Step 2: Install Firebase SDK

```bash
# Install Firebase Admin SDK
pip3 install firebase-admin

# Install additional dependencies
pip3 install python-dateutil pytz
```

### Step 3: Create Project Structure

```bash
# Create directories
mkdir -p /home/pi/parkngo/secrets
cd /home/pi/parkngo

# Copy Firebase credentials from backend team
# Place parkngo-firebase-adminsdk.json in secrets/ folder
```

---

## 🐍 Python Agent Code

### Create `spot_finder_agent.py`:

```bash
cd /home/pi/parkngo
nano spot_finder_agent.py
```

**Paste this complete code:**

```python
#!/usr/bin/env python3
"""
ParknGo Raspberry Pi Spot Finder Agent
Monitors IR sensors and updates Firebase with parking spot occupancy
"""

import RPi.GPIO as GPIO
import firebase_admin
from firebase_admin import credentials, db
import time
from datetime import datetime
import hashlib
import json

# ============================================
# FIREBASE CONFIGURATION - GET FROM BACKEND TEAM
# ============================================

FIREBASE_CREDS = '/home/pi/parkngo/secrets/parkngo-firebase-adminsdk.json'
FIREBASE_URL = 'https://parkngo-ai-default-rtdb.asia-southeast1.firebasedatabase.app'

# ============================================
# GPIO PIN MAPPING
# ============================================

SPOT_PINS = {
    # Zone A - Premium (10 spots)
    'A-01': 17, 'A-02': 18, 'A-03': 27, 'A-04': 22, 'A-05': 23,
    'A-06': 10, 'A-07': 11, 'A-08': 12, 'A-09': 13, 'A-10': 14,
    
    # Zone B - Regular (15 spots)
    'B-01': 15, 'B-02': 16, 'B-03': 21, 'B-04': 26, 'B-05': 19,
    'B-06': 20, 'B-07': 6,  'B-08': 7,  'B-09': 4,  'B-10': 5,
    'B-11': 8,  'B-12': 9,  'B-13': 25, 'B-14': 2,  'B-15': 3,
    
    # Zone C - Budget (5 spots)
    'C-01': 1, 'C-02': 0, 'C-03': 24, 'C-04': 28, 'C-05': 29,
}

ENTRY_GATE_PIN = 31
EXIT_GATE_PIN = 32

# ============================================
# SPOT METADATA
# ============================================

SPOT_METADATA = {
    'A-01': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-02': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-03': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-04': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-05': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-06': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-07': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-08': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-09': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    'A-10': {'zone': 'A', 'type': 'premium', 'features': ['covered', 'ev_charging']},
    
    'B-01': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-02': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-03': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-04': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-05': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-06': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-07': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-08': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-09': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-10': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-11': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-12': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-13': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-14': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    'B-15': {'zone': 'B', 'type': 'regular', 'features': ['covered']},
    
    'C-01': {'zone': 'C', 'type': 'budget', 'features': []},
    'C-02': {'zone': 'C', 'type': 'budget', 'features': []},
    'C-03': {'zone': 'C', 'type': 'budget', 'features': []},
    'C-04': {'zone': 'C', 'type': 'budget', 'features': []},
    'C-05': {'zone': 'C', 'type': 'budget', 'features': []},
}

DEBOUNCE_TIME = 2.0  # Prevents false triggers

# ============================================
# FIREBASE INITIALIZATION
# ============================================

def init_firebase():
    """Initialize Firebase connection"""
    print("🔥 Initializing Firebase...")
    
    cred = credentials.Certificate(FIREBASE_CREDS)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_URL
    })
    
    print("✅ Firebase connected!")

# ============================================
# GPIO SETUP
# ============================================

def setup_gpio():
    """Configure GPIO pins for IR sensors"""
    print("🔌 Setting up GPIO pins...")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for spot_id, pin in SPOT_PINS.items():
        GPIO.setup(pin, GPIO.IN)
        print(f"  ✓ {spot_id} → GPIO {pin}")
    
    GPIO.setup(ENTRY_GATE_PIN, GPIO.IN)
    GPIO.setup(EXIT_GATE_PIN, GPIO.IN)
    
    print("✅ GPIO setup complete!")

# ============================================
# FIREBASE OPERATIONS
# ============================================

def update_spot_status(spot_id, occupied):
    """Update parking spot status in Firebase"""
    try:
        ref = db.reference(f'parking_spots/{spot_id}')
        metadata = SPOT_METADATA.get(spot_id, {})
        
        data = {
            'spot_id': spot_id,
            'zone': metadata.get('zone', 'Unknown'),
            'type': metadata.get('type', 'regular'),
            'features': metadata.get('features', []),
            'occupied': occupied,
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'gpio_pin': SPOT_PINS[spot_id],
            'sensor_status': 'active'
        }
        
        ref.set(data)
        print(f"📍 {spot_id}: {'OCCUPIED' if occupied else 'AVAILABLE'}")
        
    except Exception as e:
        print(f"❌ Error updating {spot_id}: {e}")

def create_entry_event():
    """Create vehicle entry event"""
    try:
        timestamp = datetime.utcnow()
        entry_id = f"ENTRY_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        ref = db.reference(f'entries/{entry_id}')
        ref.set({
            'entry_id': entry_id,
            'timestamp': timestamp.isoformat() + 'Z',
            'vehicle_id': 'UNKNOWN',
            'entry_gate': 'main',
            'status': 'entered'
        })
        
        print(f"🚗 Vehicle ENTRY: {entry_id}")
        
    except Exception as e:
        print(f"❌ Error creating entry: {e}")

def create_exit_event():
    """Create vehicle exit event"""
    try:
        timestamp = datetime.utcnow()
        exit_id = f"EXIT_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        ref = db.reference(f'exits/{exit_id}')
        ref.set({
            'exit_id': exit_id,
            'timestamp': timestamp.isoformat() + 'Z',
            'vehicle_id': 'UNKNOWN',
            'exit_gate': 'main',
            'status': 'exited'
        })
        
        print(f"🚗 Vehicle EXIT: {exit_id}")
        
    except Exception as e:
        print(f"❌ Error creating exit: {e}")

def create_session(spot_id):
    """Create new parking session when spot becomes occupied"""
    try:
        timestamp = datetime.utcnow()
        session_data = f"{spot_id}_{timestamp.isoformat()}"
        session_id = f"SES_{hashlib.sha256(session_data.encode()).hexdigest()[:12].upper()}"
        
        ref = db.reference(f'sessions/{session_id}')
        ref.set({
            'session_id': session_id,
            'spot_id': spot_id,
            'entry_time': timestamp.isoformat() + 'Z',
            'exit_time': None,
            'status': 'active',
            'vehicle_id': 'UNKNOWN'
        })
        
        spot_ref = db.reference(f'parking_spots/{spot_id}')
        spot_ref.update({'current_session': session_id})
        
        print(f"📝 Session created: {session_id}")
        
    except Exception as e:
        print(f"❌ Error creating session: {e}")

def end_session(spot_id):
    """End parking session when spot becomes available"""
    try:
        spot_ref = db.reference(f'parking_spots/{spot_id}')
        spot_data = spot_ref.get()
        
        if spot_data and 'current_session' in spot_data:
            session_id = spot_data['current_session']
            
            session_ref = db.reference(f'sessions/{session_id}')
            session_ref.update({
                'exit_time': datetime.utcnow().isoformat() + 'Z',
                'status': 'completed'
            })
            
            spot_ref.update({'current_session': None})
            
            print(f"✅ Session ended: {session_id}")
        
    except Exception as e:
        print(f"❌ Error ending session: {e}")

# ============================================
# SENSOR MONITORING
# ============================================

previous_states = {}
last_trigger_time = {}

def monitor_spot(spot_id, pin):
    """Monitor individual spot sensor"""
    current_state = GPIO.input(pin)
    
    if spot_id not in previous_states:
        previous_states[spot_id] = current_state
        last_trigger_time[spot_id] = 0
        update_spot_status(spot_id, current_state == GPIO.HIGH)
        return
    
    if current_state != previous_states[spot_id]:
        current_time = time.time()
        if current_time - last_trigger_time.get(spot_id, 0) < DEBOUNCE_TIME:
            return
        
        occupied = (current_state == GPIO.HIGH)
        update_spot_status(spot_id, occupied)
        
        if occupied:
            create_session(spot_id)
        else:
            end_session(spot_id)
        
        previous_states[spot_id] = current_state
        last_trigger_time[spot_id] = current_time

def monitor_entry_gate():
    """Monitor entry gate sensor"""
    if 'entry_gate' not in previous_states:
        previous_states['entry_gate'] = GPIO.LOW
    
    current_state = GPIO.input(ENTRY_GATE_PIN)
    
    if current_state == GPIO.HIGH and previous_states['entry_gate'] == GPIO.LOW:
        create_entry_event()
        previous_states['entry_gate'] = GPIO.HIGH
    elif current_state == GPIO.LOW:
        previous_states['entry_gate'] = GPIO.LOW

def monitor_exit_gate():
    """Monitor exit gate sensor"""
    if 'exit_gate' not in previous_states:
        previous_states['exit_gate'] = GPIO.LOW
    
    current_state = GPIO.input(EXIT_GATE_PIN)
    
    if current_state == GPIO.HIGH and previous_states['exit_gate'] == GPIO.LOW:
        create_exit_event()
        previous_states['exit_gate'] = GPIO.HIGH
    elif current_state == GPIO.LOW:
        previous_states['exit_gate'] = GPIO.LOW

# ============================================
# MAIN LOOP
# ============================================

def main():
    """Main monitoring loop"""
    print("\n" + "="*60)
    print("  ParknGo Raspberry Pi Spot Finder Agent")
    print("="*60 + "\n")
    
    init_firebase()
    setup_gpio()
    
    print("\n🚀 Monitoring started...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            for spot_id, pin in SPOT_PINS.items():
                monitor_spot(spot_id, pin)
            
            monitor_entry_gate()
            monitor_exit_gate()
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping agent...")
    
    finally:
        GPIO.cleanup()
        print("✅ GPIO cleaned up. Agent stopped.")

if __name__ == '__main__':
    main()
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🚀 Running the Agent

### Test Run:

```bash
python3 spot_finder_agent.py
```

**Expected output:**
```
🔥 Initializing Firebase...
✅ Firebase connected!
🔌 Setting up GPIO pins...
  ✓ A-01 → GPIO 17
  ✓ A-02 → GPIO 18
  ... (all 30 spots)
✅ GPIO setup complete!
🚀 Monitoring started...
```

### Setup Auto-Start on Boot:

```bash
sudo nano /etc/systemd/system/parkngo-agent.service
```

**Paste this:**

```ini
[Unit]
Description=ParknGo Spot Finder Agent
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/parkngo
ExecStart=/usr/bin/python3 /home/pi/parkngo/spot_finder_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable parkngo-agent
sudo systemctl start parkngo-agent
sudo systemctl status parkngo-agent
```

---

## 🧪 Testing Checklist

- [ ] All 30 sensors wired correctly
- [ ] Firebase credentials in `/home/pi/parkngo/secrets/`
- [ ] Agent runs without errors
- [ ] Block sensor with hand → Firebase shows `occupied: true`
- [ ] Remove hand → Firebase shows `occupied: false`
- [ ] Session created when spot occupied
- [ ] Session ended when spot available
- [ ] Entry/exit gate sensors working
- [ ] Auto-start service enabled
- [ ] Logs accessible: `sudo journalctl -u parkngo-agent -f`

---

## 🔧 Troubleshooting

### GPIO Permission Error:
```bash
sudo usermod -a -G gpio pi
sudo reboot
```

### Firebase Connection Error:
```bash
# Check credentials file exists
ls -la /home/pi/parkngo/secrets/parkngo-firebase-adminsdk.json

# Verify Firebase URL with backend team
```

### Sensor Not Triggering:
```bash
# Test GPIO pin directly
gpio -g read 17  # Should return 0 or 1

# Check wiring:
# VCC → 5V (Pin 2)
# GND → GND (Pin 6)
# OUT → GPIO Pin
```

### False Triggers:
```python
# Increase debounce time in code
DEBOUNCE_TIME = 5.0  # Change from 2.0 to 5.0
```

---

## 📞 Communication with Other Teams

### What Backend Team Needs from You:
1. ✅ Firebase URL confirmation
2. ✅ Service account JSON file
3. ✅ Confirmation that sensors are updating Firebase
4. ✅ Test data showing spot occupancy changes

### What Frontend Team Will See:
- Real-time spot availability
- Entry/exit events
- Session data

### Integration Testing:
Once your Raspberry Pi is running, notify both teams so they can test their Firebase listeners.

---

## 📅 Timeline

**Week 1:**
- [ ] Order hardware (Day 1-2)
- [ ] Receive components (Day 3-5)
- [ ] Install Raspberry Pi OS (Day 6)
- [ ] Wire 5 test sensors (Day 7)

**Week 2:**
- [ ] Get Firebase credentials from backend team
- [ ] Test Python agent with 5 sensors
- [ ] Wire remaining 25 sensors
- [ ] Setup auto-start service
- [ ] Integration testing with backend/frontend teams

---

## ✅ Deliverables

When you're done, you should have:

1. ✅ Raspberry Pi monitoring 30 parking spots
2. ✅ Real-time Firebase updates (100ms intervals)
3. ✅ Entry/exit gate detection
4. ✅ Session tracking (entry/exit times)
5. ✅ 24/7 operation with auto-restart
6. ✅ Accessible logs for debugging

---

**Questions? Contact Backend Team for Firebase setup or Frontend Team for integration testing.**

**🎯 Your work is CRITICAL - the entire system depends on your real-time sensor data!**
