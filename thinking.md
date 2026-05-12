# Crisis Response Framework

## Question A — The Immediate Response

> Hi [Name of the  guest], I am incredibly sorry to hear about the hot water issue. This is highly prioritized. I have immediately alerted our emergency caretaker who will reach out momentarily. Regarding your refund request, our management team will review it first thing in the morning. We are working on getting the water running right now.

**Why it works:** At 3am, you need empathy, proof of action, and honesty about limits. Validate frustration, show the caretaker is being contacted (concrete), and defer the refund to humans without slamming the door. It's direct, not robotic.

---

## Question B — The System Design

**Trigger & Classification:** The webhook classifies the message as `complaint`. The confidence score is capped and action flips to `escalate`, no auto-responses for crises.

**Notification Engine:** At 3am (outside 8am–10pm caretaker hours), the system triggers Twilio to call the night-duty manager immediately.

**SLA Timer:** A 30-minute acknowledgment countdown starts. No ghost tickets.

**Escalation Protocol:** If the manager doesn't acknowledge within 30 minutes, a secondary call automatically routes to the property owner or upper management.

---

## Question C — The Learning Layer

**Analytics:** The system tags `query_type: complaint` + `keyword: hot water` + `property: Villa B1`. When patterns emerge, the dashboard flags Villa B1 as "High-Risk Maintenance." 

**Preventative Build:** Create a "Pre-Arrival Verification System" where caretakers can't check guests in without completing a mandatory checklist. For Villa B1, inject a required field: **"Record a 5-second video of hot water running from the master bathroom tap."**

This catches failures before guests arrive, not at 3am when you're already in damage control.