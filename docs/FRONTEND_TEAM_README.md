# 📱 Frontend Team - Mobile/Web App

**Team Member:** [Frontend Friend's Name]  
**Responsibility:** Customer-facing mobile/web app  
**Timeline:** Week 2-4

---

## 🎯 Your Mission

Build a mobile or web app where customers can:
1. View real-time parking availability
2. Reserve spots with dynamic pricing
3. Make blockchain payments via Masumi
4. Get QR codes for parking entry
5. Monitor live parking sessions
6. Dispute charges if needed

---

## 📋 What You're Building

**Input:** Customer actions (search, reserve, pay, dispute)  
**Processing:** Backend API + Firebase real-time updates  
**Output:** Beautiful UI showing live parking data, payments, QR codes

---

## 🏗️ Tech Stack Recommendations

### Option A: React Native (Mobile App - iOS/Android)

```bash
npx react-native init ParknGoApp
cd ParknGoApp
npm install firebase axios react-native-qrcode-svg
```

### Option B: Next.js (Web App)

```bash
npx create-next-app@latest parkngo-web
cd parkngo-web
npm install firebase axios qrcode.react
```

### Option C: Flutter (Cross-Platform)

```bash
flutter create parkngo_app
cd parkngo_app
flutter pub add firebase_core firebase_database http qr_flutter
```

**Recommendation:** React Native for mobile-first experience

---

## 🔥 Firebase Configuration

### Firebase Setup:

1. **Add Firebase to Your App:**

```bash
npm install firebase
```

2. **Firebase Config File (`firebase-config.js`):**

```javascript
import { initializeApp } from 'firebase/app';
import { getDatabase } from 'firebase/database';

const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "parkngo-ai.firebaseapp.com",
  databaseURL: "https://parkngo-ai-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "parkngo-ai",
  storageBucket: "parkngo-ai.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456"
};

const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

export { database };
```

**⚠️ Get actual config from Backend Team!**

3. **Real-Time Listeners:**

```javascript
import { ref, onValue } from 'firebase/database';
import { database } from './firebase-config';

// Listen to parking spot availability
const spotsRef = ref(database, 'parking_spots');
onValue(spotsRef, (snapshot) => {
  const spots = snapshot.val();
  console.log('Available spots:', spots);
  // Update UI
});

// Listen to active session
const sessionRef = ref(database, 'sessions/SES_ABC123');
onValue(sessionRef, (snapshot) => {
  const session = snapshot.val();
  console.log('Session status:', session.status);
  console.log('Accrued charges:', session.accrued_cents / 100);
  // Update UI with live charges
});
```

---

## 🌐 Backend API Integration

### API Base URL:

```javascript
const API_BASE_URL = 'http://localhost:5000/api/v1';  // Development
// const API_BASE_URL = 'https://parkngo-api.example.com/api/v1';  // Production
```

### API Endpoints You'll Use:

#### 1. **Create Parking Reservation**

```javascript
// POST /api/v1/parking/reserve
const createReservation = async (customerWallet, preferences) => {
  const response = await fetch(`${API_BASE_URL}/parking/reserve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      customer_wallet: customerWallet,
      preferences: {
        spot_type: 'premium',        // 'premium', 'regular', 'budget'
        features: ['covered', 'ev_charging'],
        max_distance_m: 100,
        accessibility: 'wheelchair'  // 'wheelchair', 'stroller', null
      },
      duration_hours: 2
    })
  });

  const data = await response.json();
  
  return data;
  // {
  //   "reservation_id": "RES_XYZ789",
  //   "spot": {
  //     "spot_id": "A-05",
  //     "type": "premium",
  //     "price_usd": 23.85,
  //     "features": ["covered", "ev_charging"]
  //   },
  //   "pricing": {
  //     "base_price": 8.0,
  //     "final_price": 23.85,
  //     "breakdown": { ... }
  //   },
  //   "route": {
  //     "distance_m": 45,
  //     "walking_time_sec": 32,
  //     "directions": ["Turn left", "Spot A-05 on right"]
  //   },
  //   "qr_code": "QR_ABC123XYZ",
  //   "masumi_payment": {
  //     "amount_ada": 1.5,
  //     "payment_address": "addr_test1...",
  //     "status": "pending"
  //   }
  // }
};
```

#### 2. **Get Reservation Details**

```javascript
// GET /api/v1/parking/reservation/{id}
const getReservation = async (reservationId) => {
  const response = await fetch(`${API_BASE_URL}/parking/reservation/${reservationId}`);
  const data = await response.json();
  return data;
};
```

#### 3. **Create Dispute**

```javascript
// POST /api/v1/disputes/create
const createDispute = async (sessionId, reason, evidence) => {
  const response = await fetch(`${API_BASE_URL}/disputes/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      customer_wallet: "addr_test1...",
      reason: reason,  // "spot_unavailable", "overcharged", "unauthorized_charge"
      evidence: evidence,  // Text description or image URLs
      disputed_amount: 15.00
    })
  });

  const data = await response.json();
  
  return data;
  // {
  //   "dispute_id": "DIS_001",
  //   "customer_stake": "5 ADA",
  //   "operator_stake": "5 ADA",
  //   "status": "investigating",
  //   "bilateral_escrow_address": "addr_test1..."
  // }
};
```

#### 4. **Get Security Violations**

```javascript
// GET /api/v1/security/violations?session_id=SES_ABC123
const getViolations = async (sessionId) => {
  const response = await fetch(`${API_BASE_URL}/security/violations?session_id=${sessionId}`);
  const data = await response.json();
  return data;
  // [
  //   {
  //     "violation_id": "VIO_001",
  //     "type": "overstay",
  //     "fine_usd": 8.0,
  //     "status": "pending"
  //   }
  // ]
};
```

---

## 🎨 UI/UX Flow

### Screen 1: Home - Parking Availability

**What to Show:**
- Map view of parking lot
- Real-time spot availability (green = available, red = occupied)
- Filter by zone (Premium/Regular/Budget)
- Search by features (Covered, EV Charging, Accessible)

**Firebase Listener:**
```javascript
const spotsRef = ref(database, 'parking_spots');
onValue(spotsRef, (snapshot) => {
  const spots = snapshot.val();
  const availableSpots = Object.values(spots).filter(s => !s.occupied);
  setAvailableCount(availableSpots.length);
  updateMapMarkers(spots);
});
```

**UI Example:**
```
┌─────────────────────────────────────┐
│  ParknGo                         🔔 │
├─────────────────────────────────────┤
│  📍 Mall Parking - Zone A/B/C       │
│                                     │
│  Available: 18/30 spots             │
│                                     │
│  🟢 A-01  🔴 A-02  🟢 A-03         │
│  🟢 A-04  🔴 A-05  🟢 A-06         │
│                                     │
│  Filters:                           │
│  [ ] Covered  [ ] EV Charging       │
│  [ ] Accessible                     │
│                                     │
│  [   Find Parking   ]               │
└─────────────────────────────────────┘
```

---

### Screen 2: Spot Selection & Pricing

**What to Show:**
- Top 5 recommended spots (from backend API)
- Dynamic pricing breakdown
- Walking distance and time
- Features (covered, EV charging)
- Live price updates

**API Call:**
```javascript
const reservation = await createReservation(customerWallet, preferences);
```

**UI Example:**
```
┌─────────────────────────────────────┐
│  ← Recommended Spots                │
├─────────────────────────────────────┤
│  🅰️ Spot A-05 - PREMIUM             │
│  💰 $23.85 (2 hours)                │
│  🚶 45m walk (32 sec)               │
│  ✓ Covered  ✓ EV Charging           │
│                                     │
│  Price Breakdown:                   │
│  Base:        $8.00                 │
│  Peak time:   +$4.00 (1.5x)         │
│  High demand: +$7.20 (90%)          │
│  Event nearby: +$0.80 (10%)         │
│  Rain premium: +$2.00 (25%)         │
│  EV charging: +$2.00                │
│  ────────────────────                │
│  Total:       $23.85                │
│                                     │
│  [   Reserve & Pay   ]              │
└─────────────────────────────────────┘
```

---

### Screen 3: Payment & QR Code

**What to Show:**
- Masumi payment details (1.5 ADA)
- Payment address (copy to wallet)
- QR code for parking entry
- Reservation timer (reserved for 15 minutes)

**Payment Flow:**
1. Backend creates Masumi escrow (1.5 ADA locked)
2. Show payment address to customer
3. Customer sends ADA from wallet
4. Backend verifies transaction (Payment Verifier Agent)
5. Show QR code when payment confirmed

**UI Example:**
```
┌─────────────────────────────────────┐
│  ✅ Reservation Confirmed           │
├─────────────────────────────────────┤
│  Spot: A-05 (Premium)               │
│  Amount Paid: 1.5 ADA (~$24)        │
│                                     │
│  Entry QR Code:                     │
│  ┌───────────────────┐              │
│  │   █▀▀▀▀▀█  ▀█▀   │              │
│  │   █ ███ █ ▄ █▄▀  │              │
│  │   █ ▀▀▀ █ ▀▄█ █  │              │
│  │   QR_ABC123XYZ    │              │
│  └───────────────────┘              │
│                                     │
│  Valid until: 15:45 PM              │
│                                     │
│  Directions:                        │
│  1. Enter main entrance             │
│  2. Turn left                       │
│  3. Spot A-05 on right              │
│                                     │
│  [   Start Navigation   ]           │
└─────────────────────────────────────┘
```

---

### Screen 4: Live Parking Session

**What to Show:**
- Real-time parking duration
- Live accrued charges (updated every minute)
- Payment status (locked in escrow)
- Exit button

**Firebase Listener:**
```javascript
const sessionRef = ref(database, `sessions/${sessionId}`);
onValue(sessionRef, (snapshot) => {
  const session = snapshot.val();
  
  const entryTime = new Date(session.entry_time);
  const duration = Math.floor((Date.now() - entryTime) / 1000 / 60); // minutes
  
  setDuration(duration);
  setAccruedCharges((session.accrued_cents || 0) / 100);
  setPaymentStatus(session.payment_status);
});
```

**UI Example:**
```
┌─────────────────────────────────────┐
│  🚗 Active Session - Spot A-05      │
├─────────────────────────────────────┤
│  ⏱️  Duration: 45 minutes           │
│  💰 Charges: $5.50                  │
│                                     │
│  Payment Status: ✅ Locked          │
│  Escrow: 1.5 ADA                    │
│                                     │
│  Reserved until: 16:00 PM           │
│  Remaining: 1h 15m                  │
│                                     │
│  ⚠️  Overstay fine: $2 per 15min    │
│                                     │
│  [   Exit & Pay   ]                 │
│  [   Extend Time   ]                │
└─────────────────────────────────────┘
```

---

### Screen 5: Dispute Resolution

**What to Show:**
- Dispute creation form
- Bilateral escrow explanation (both stake 5 ADA)
- AI investigation status
- Final ruling and payout

**API Calls:**
```javascript
// Create dispute
const dispute = await createDispute(sessionId, reason, evidence);

// Get investigation status
const status = await fetch(`${API_BASE_URL}/disputes/${dispute.dispute_id}`);
```

**UI Example:**
```
┌─────────────────────────────────────┐
│  ⚖️  Dispute Resolution              │
├─────────────────────────────────────┤
│  Session: SES_ABC123                │
│  Disputed Amount: $15.00            │
│                                     │
│  Reason:                            │
│  [ ] Spot unavailable               │
│  [x] Overcharged                    │
│  [ ] Unauthorized charge            │
│                                     │
│  Evidence:                          │
│  "Spot was occupied when I          │
│   arrived at 10:45 AM. Sensor       │
│   showed available but car was      │
│   parked there."                    │
│                                     │
│  Bilateral Escrow:                  │
│  You stake:     5 ADA               │
│  Operator stakes: 5 ADA             │
│  Winner gets:   10 ADA + refund     │
│                                     │
│  [   Submit Dispute   ]             │
└─────────────────────────────────────┘
```

**Investigation Status:**
```
┌─────────────────────────────────────┐
│  🔍 AI Investigation in Progress... │
├─────────────────────────────────────┤
│  Evidence Analyzed:                 │
│  ✅ Customer claim verified         │
│  ✅ Sensor data reviewed            │
│  ✅ Payment records checked         │
│  ✅ Session timeline confirmed      │
│                                     │
│  Confidence: 85% (Customer wins)    │
│                                     │
│  Estimated ruling: 2-5 minutes      │
└─────────────────────────────────────┘
```

**Final Ruling:**
```
┌─────────────────────────────────────┐
│  ✅ Ruling: Customer Wins           │
├─────────────────────────────────────┤
│  Confidence: 85%                    │
│                                     │
│  Payout:                            │
│  Refund:        $15.00              │
│  Your stake:    5 ADA (returned)    │
│  Operator stake: 5 ADA (awarded)    │
│  ────────────────────                │
│  Total:         10 ADA + $15        │
│                                     │
│  Transaction: a1b2c3d4e5...         │
│                                     │
│  [   View on Blockchain   ]         │
└─────────────────────────────────────┘
```

---

## 📊 Firebase Real-Time Data

### Data You'll Listen To:

#### 1. **Parking Spots (Hardware Team Updates)**

```javascript
{
  "parking_spots": {
    "A-01": {
      "spot_id": "A-01",
      "zone": "A",
      "type": "premium",
      "occupied": false,        // ← Real-time from Raspberry Pi
      "last_updated": "2025-11-27T10:30:00Z"
    }
  }
}
```

**Use Case:** Update map markers, availability count

---

#### 2. **Reservations (Backend Team Writes)**

```javascript
{
  "reservations": {
    "RES_XYZ789": {
      "reservation_id": "RES_XYZ789",
      "customer_wallet": "addr_test1...",
      "spot": {
        "spot_id": "A-05",
        "price_usd": 23.85
      },
      "qr_code": "QR_ABC123XYZ",
      "status": "confirmed"       // ← Watch for changes
    }
  }
}
```

**Use Case:** Show QR code, reservation details

---

#### 3. **Sessions (Backend Team Updates)**

```javascript
{
  "sessions": {
    "SES_ABC123": {
      "session_id": "SES_ABC123",
      "spot_id": "A-05",
      "status": "active",
      "accrued_cents": 550,      // ← Updates every minute
      "payment_status": "locked"  // ← "locked", "released", "refunded"
    }
  }
}
```

**Use Case:** Show live charges, payment status

---

#### 4. **Violations (Security Agent Writes)**

```javascript
{
  "violations": {
    "VIO_001": {
      "violation_id": "VIO_001",
      "session_id": "SES_ABC123",
      "type": "overstay",
      "fine_usd": 8.0,
      "status": "pending"        // ← Show alert to user
    }
  }
}
```

**Use Case:** Show violation alerts, fines

---

#### 5. **Disputes (Backend Team Updates)**

```javascript
{
  "disputes": {
    "DIS_001": {
      "dispute_id": "DIS_001",
      "status": "investigating",  // ← Watch for "ruled"
      "ruling": null,
      "payout": null
    }
  }
}
```

**Use Case:** Show investigation progress, final ruling

---

## 🎨 Design Guidelines

### Color Scheme:

```css
/* Primary */
--primary-blue: #2563EB;
--primary-dark: #1E40AF;

/* Status */
--success-green: #10B981;
--warning-yellow: #F59E0B;
--error-red: #EF4444;

/* Neutral */
--gray-50: #F9FAFB;
--gray-900: #111827;

/* Spot Status */
--available-green: #34D399;
--occupied-red: #F87171;
--reserved-yellow: #FBBF24;
```

### Typography:

- **Headings:** Inter Bold, 24px
- **Body:** Inter Regular, 16px
- **Captions:** Inter Medium, 14px
- **Prices:** Inter Bold, 20px

### Icons:

Use **Heroicons** or **Material Icons**

---

## 🧪 Testing Strategy

### Test Scenarios:

1. **Happy Path:**
   - Search for parking → Select spot → Pay → Get QR code → Park → Exit

2. **Spot Unavailable:**
   - Reserve spot → Spot becomes occupied → Auto-refund

3. **Overstay:**
   - Park → Exceed reserved time → See fine → Pay fine

4. **Dispute:**
   - Charged incorrectly → Create dispute → AI investigation → Get refund

### Mock Data:

```javascript
// For testing without backend
const mockReservation = {
  reservation_id: "RES_TEST123",
  spot: {
    spot_id: "A-05",
    type: "premium",
    price_usd: 23.85
  },
  qr_code: "QR_TEST123",
  status: "confirmed"
};
```

---

## 📞 Communication with Other Teams

### From Hardware Team:
- ✅ Firebase real-time spot updates
- ✅ Entry/exit gate events
- ✅ Session occupancy data

### From Backend Team:
- ✅ API endpoint documentation
- ✅ Firebase config credentials
- ✅ Payment flow integration
- ✅ QR code format

### Integration Testing:
- **Week 2:** Test with mock API responses
- **Week 3:** Test with real backend API
- **Week 4:** End-to-end testing with hardware sensors

---

## 📅 Timeline

**Week 2: Foundation**
- [ ] Setup React Native / Next.js project
- [ ] Firebase integration
- [ ] Home screen (parking availability)
- [ ] API integration setup

**Week 3: Core Features**
- [ ] Spot selection & pricing screen
- [ ] Payment & QR code screen
- [ ] Live session monitoring
- [ ] Real-time Firebase listeners

**Week 4: Advanced Features**
- [ ] Dispute resolution flow
- [ ] Violation alerts
- [ ] Navigation integration
- [ ] End-to-end testing

---

## ✅ Deliverables

When you're done, you should have:

1. ✅ Mobile/web app with 5 main screens
2. ✅ Firebase real-time updates
3. ✅ Backend API integration (10 endpoints)
4. ✅ QR code generation and display
5. ✅ Payment flow (Masumi blockchain)
6. ✅ Dispute resolution UI
7. ✅ Responsive design (mobile + tablet)
8. ✅ Tested on iOS/Android or modern browsers

---

**🎯 Your work is the FACE of the system - customers see your UI first!**
