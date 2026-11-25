# Language-switch walkthrough

On one open socket, enter the following lines in order using the keyless demo. After each pair verify the Lead profile count and date.

| Input and confirmation | Expected result |
|---|---|
| Three stores on 4 December 2026, then Yes | 3 stores and 2026-12-04 |
| चार दुकानें ५ दिसंबर २०२६, then हाँ | Hindi readback, 4 stores and 2026-12-05 |
| paanch dukaan 6 December 2026, then haan | 5 stores and 2026-12-06 |
| What does Growth cost? then ग्रोथ की कीमत क्या है? then Growth ka price kya hai? | Same Growth citation. The Devanagari question gets the Hindi card. Roman Hinglish gets the English card. |
| My phone is +91 98765 43210, then मेरा फोन +९१ ९८७६५ ४३२१०, then mera phone +91 98765 43210 | Each form normalizes to the same synthetic contact. |
| kal | No date is inferred. Supply an explicit date. |

Use a fresh fictional contact or an isolated CRM database. Turn on live local voice to try each phrase through the mic. The language selector is a transcription hint, so switch it manually. Typed fixture verification does not measure physical microphone accuracy, spoken digit strings, dialects, ambiguous relative dates, or open-ended Roman Hindi translation.
