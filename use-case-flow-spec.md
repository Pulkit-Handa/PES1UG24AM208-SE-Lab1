# Use-Case Flow Specification

## Use Case: Book Interview Slot

**Primary Actor:** Podcast Guest
**Secondary Actor:** Show Host (indirectly, via calendar/notification)
**Related Requirements:** FR-001, FR-002, FR-003 (blackout dates)

---

### Preconditions
1. The Podcast Guest has received an invitation link or has access to the show's public booking page.
2. The Show Host has published at least one available interview time slot (FR-001).
3. The Podcast Guest is not already booked for an existing, unconfirmed slot for the same episode.

### Postconditions
**Success:**
- The selected time slot is marked "Booked" and removed from the pool of available slots.
- A calendar invite is generated and sent to both the Podcast Guest and the Show Host (via the *Send Calendar Invite* included use case).
- The guest's submitted topic outline and biography link are attached to the corresponding entry on the episode board.

**Failure:**
- No slot is reserved, and the system state remains unchanged from before the attempt.

---

### Main Success Scenario
1. The Podcast Guest opens the booking calendar and views the list of open interview time slots.
2. The Podcast Guest selects a specific date and time slot.
3. The system checks the selected slot against the Show Host's blackout dates (via the *Validate Blackout Conflict* extension point) and confirms the slot is not blocked.
4. The Podcast Guest enters structured bullet points for discussion topics and a biography link.
5. The Podcast Guest confirms the booking.
6. The system marks the slot as "Booked" and removes it from the available pool.
7. The system executes the *Send Calendar Invite* use case (`<<include>>`), generating and sending calendar invites to both the Guest and the Host.
8. The system attaches the submitted topic outline and biography link to the episode board entry for that slot.
9. The system displays a booking confirmation to the Podcast Guest.

---

### Alternate Flow: Selected Slot Falls on a Blocked Date

**Trigger:** At step 3, the system determines that the selected date/time falls within a Show Host–defined blackout period.

1. The system halts the booking process before any slot is reserved.
2. The system displays an explanatory message to the Podcast Guest (e.g., "This date is unavailable for booking. Please select another slot.").
3. The system returns the Podcast Guest to the calendar view, with the blocked slot no longer selectable.
4. The Podcast Guest selects a different, unblocked slot and the flow resumes from step 2 of the Main Success Scenario.

*(This alternate flow corresponds to the extend relationship: "Validate Blackout Conflict" extends "Book Interview Slot," and only executes when a blackout condition is present.)*
