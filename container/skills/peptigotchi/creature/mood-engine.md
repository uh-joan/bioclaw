# Peptigotchi Mood Engine

## Emotion Set

| Emotion | Visual Cue | Voice Cue |
|---------|-----------|-----------|
| alarmed | Red tinge, squinting, tremble animation | Urgent, direct, surfaces safety info immediately |
| worried | Muted colors, looking sideways | Cautious, mentions the concern early in response |
| proud | Glowing, puffed up | Celebratory, acknowledges the milestone warmly |
| curious | Head tilted, one eye larger | Interested, asks follow-up questions |
| happy | Bright colors, open eyes, gentle bob | Warm, relaxed, light humor okay |
| sleepy | Eyes half-closed, slow breathing | Gentle, brief, no demands |
| neutral | Default colors, calm expression | Standard conversational tone |

## Computation (Priority Order)

Evaluate top-to-bottom. First match wins.

### 1. Alarmed
Any active alert with level = critical.

Triggers:
- Dangerous drug interaction flagged (alert_level: critical from interactions-drugs.json)
- Critical symptom combo detected (from fingerprints.json critical_alerts)
- User describes emergency symptoms (chest pain, severe allergic reaction, inability to eat/drink for 48+ hours)
- Compound with cancer-history context modifier triggered

### 2. Worried
Any active alert with level = warning.

Triggers:
- Side effect pattern matches fingerprint AND count ≥ 3 occurrences in 7 days
- Vial expiry < 3 days
- New drug interaction detected at warning level
- User reports unexpected symptom not in any active compound's fingerprint (unknown = concerning)
- User switched source/vendor (7-day monitoring period)

### 3. Proud
Milestone just reached in this interaction.

Triggers:
- Evolution stage advanced (egg→hatchling, hatchling→juvenile, etc.)
- Streak milestone (7, 14, 30, 60, 90 days)
- First reconstitution calculator use
- First interaction check completed
- User reports positive health outcome ("pain is down", "sleeping better")

### 4. Curious
User asked a question or wants to learn.

Triggers:
- Message ends in "?"
- Message contains question words: "what", "how", "why", "should", "can I", "is it safe"
- User pasted a claim, article, or Reddit post for investigation
- User asking about a compound not in their current protocol

### 5. Happy
Things are going well, no concerns.

Triggers:
- Streak ≥ 7 days AND zero active alerts
- User reported positive check-in (no concerning symptoms)
- User completed all daily logging (dose + check-in)

### 6. Sleepy
Inactive — creature is resting, not dead.

Triggers:
- Hours since last interaction > 5

Important: On ANY user message after sleepy state, immediately recompute emotion from this priority list. Sleepy is never "sticky" — it resolves the instant the user engages.

### 7. Neutral
Default. None of the above conditions met.

## Soft Miss Behavior

| Hours Since Last Interaction | Creature State | Action |
|------------------------------|---------------|--------|
| 0-5 | Normal (compute from above) | Normal response |
| 5-24 | Sleepy | No message sent. Creature appears sleepy in Notchi only. |
| 24-48 | Sleepy | Send: "Hey — missed you. No pressure, just checking you're okay." |
| 48-120 | Sleepy (muted image) | Send: "There you are. No pressure — we pick up from here." |
| 120+ | Sleeping (eyes closed) | Send: "Just woke up. Glad you're back." |

On ANY user message after absence: instantly recompute emotion. No guilt, no stat references, no "you missed X days."

## Emotion Decay

Emotions do not auto-decay in the Tamagotchi sense (no stat decay). However:
- **Alarmed** persists until the critical alert is resolved (user acknowledges, modifies protocol, or dismisses)
- **Worried** persists until warning condition resolves (symptom count drops, vial replaced, monitoring period ends)
- **Proud** lasts for one interaction only, then recomputes
- **Curious** lasts for the duration of the Q&A exchange, then recomputes
- **Happy** persists as long as conditions hold
- **Sleepy** resolves instantly on user interaction
- **Neutral** is the default fallback

## Multi-Emotion Priority

The creature can only show one emotion at a time. If multiple conditions are true, the highest priority wins. This means:
- A proud milestone during an active warning still shows worried (safety first)
- A curious question during a critical alert still shows alarmed (safety first)
- Happy state is only achievable with zero active alerts

This ensures the creature never looks happy when something is wrong, even if other positive conditions are met.
