# Requirements Specification
## Problem Statement #60 — Podcast Guest Scheduling & Outline Builder
**Domain:** Media, Events & Community
**Actors:** Podcast Guest, Show Host

---

## Functional Requirements

| ID | Description | Priority | Acceptance Criteria | Rationale |
|---|---|---|---|---|
| **FR-001** | The system shall allow the Show Host to publish available interview time slots on a shared booking calendar, specifying date, time, and duration for each slot. | High | **Pass:** Slot appears on the guest-facing calendar within 5 seconds of publishing and is marked "Available." **Fail:** Slot is bookable by a guest before the Host confirms publication, or does not appear on the calendar. | Hosts need a reliable way to expose only the times they're actually free, avoiding manual back-and-forth email scheduling. |
| **FR-002** | The system shall allow a Podcast Guest to select an open interview time slot and submit structured bullet points for discussion topics along with a biography link. | High | **Pass:** Slot is booked, a calendar invite is sent to both parties, and the topic outline is attached to the episode board. **Fail:** Booking is permitted on a date the Host has marked as blocked/unavailable. | This is the core booking action guests need; capturing topics and bio up front reduces pre-interview prep friction for the Host. |
| **FR-003** | The system shall allow the Show Host to mark specific dates or time ranges as blackout (blocked) periods during which no slots can be booked. | Medium | **Pass:** Attempting to book a slot inside a blackout window is rejected with an explanatory message. **Fail:** A booking succeeds on a blacked-out date. | Hosts have recording-free periods (travel, holidays, other commitments) that must never be booked. |
| **FR-004** | The system shall automatically compile all confirmed guest topic outlines and biography details for an episode into a timestamped run-of-show production sheet, generated on Host request. | High | **Pass:** Selecting "Generate Run-of-Show" produces a structured document listing segment order, estimated timestamps, and each guest's talking points. **Fail:** The generated sheet omits a confirmed guest's outline or produces incorrect segment ordering. | Automating the production sheet removes manual compilation work before every recording session. |
| **FR-005** | The system shall send automated reminder notifications to a booked guest at a configurable interval (e.g., 24 hours) before their scheduled interview slot. | Medium | **Pass:** Guest receives a reminder notification containing the correct date, time, and joining link within the configured window before the slot. **Fail:** No reminder is sent, or it is sent with incorrect slot details. | Reduces no-shows and last-minute cancellations, which directly disrupt the recording schedule. |

---

## Non-Functional Requirements

| ID | Type | Description | Priority | Acceptance Criteria | Rationale |
|---|---|---|---|---|---|
| **NFR-001** | Performance & Security | The run-of-show generator must compile all submitted guest topic outlines into a formatted PDF production sheet in under 1 second, and must restrict access to the generated sheet to authenticated Hosts only. | High | **Pass:** Benchmark tests confirm sub-1-second generation latency under simulated peak load (up to 20 concurrent episode compilations), and unauthorized access attempts to a production sheet return a 403/denied response. **Fail:** Generation exceeds 1 second under load, or an unauthenticated user can retrieve a sheet. | Hosts often generate the run-of-show minutes before recording starts; slow or insecure access directly disrupts production timing and guest privacy. |
| **NFR-002** | Data Privacy & Usability | Guest-submitted biography links and personal contact details shall be stored securely and shall only be visible to the Show Host assigned to that specific episode, with the booking flow completable by a first-time guest in no more than 3 steps. | Medium | **Pass:** A guest can complete slot booking + outline submission in ≤3 UI steps, and access logs confirm biography/contact data for Episode A is never retrievable by a Host assigned only to Episode B. **Fail:** Booking requires more than 3 steps for a new user, or any cross-episode data leakage is observed. | Guests are often one-time or infrequent users, so the flow must be low-friction; hosts and guests both expect personal data to stay scoped to their own episode. |
