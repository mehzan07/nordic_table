# Test Restaurant — Version 7

Version 7 is based on the tested Version 6.

## Changes
- Language selector is displayed as **Svenska | English**. Swedish remains the default.
- English review data is fully localized: dates and the empty special-request value use English.
- Swedish review data uses Swedish date formatting and “Inga”.
- Language changes update an existing reservation review immediately.
- Email still uses the standard `mailto:` mechanism, but the page now immediately provides a visible copy fallback. A real automatic reservation email requires a server/email service.
- SMS still uses the standard `sms:` mechanism. Desktop systems may show “Select an app” when no SMS handler is installed; the page provides a copy fallback.
- Visual design remains based on the V3/V5/V6 design.


## Version 8
- Built from Version 7.
- Keeps the Version 7 design.
- Swedish default with Svenska | English.
- Existing reservation review can refresh when language changes.
- Date and empty special requests are localized dynamically.
- Windows desktop SMS links show a copy-details fallback instead of forcing an SMS app.
- Email still uses mailto:, so Windows needs a configured default mail application.


## Version 9
- Built from Version 8.
- Keeps the same visual design.
- Fixes live language switching for reservation review values.
- Empty special requests now switch correctly between Inga and None.
- Reservation dates are re-localized without Ctrl+F5.
- Existing Windows SMS fallback is preserved.
- Email still uses mailto:, so a configured mail app is required.


## Version 10 fixed
- Adds a visible Svenska | English selector immediately above the reservation card.
- Keeps the header and reservation language controls synchronized.
- Preserves Version 9 reservation behavior.


## Version 11
- Built from Version 10 fixed.
- Moves the Svenska | English selector inside the reservation card.
- The selector remains visible both while filling the form and while viewing the reservation review.
- Keeps Swedish as the default language.
- Keeps Version 9/10 reservation language behavior.


## Version 12
- Built from Version 11.
- Adds Svenska | English inside the reservation form itself.
- Adds the same selector inside the review screen.
- Both selectors stay synchronized with the header selector.
- Uses a fresh V12 language preference key, so the first V12 visit starts in Swedish even if older versions stored English.
- After the visitor chooses English, V12 remembers that choice.


## Version 13
- Built from Version 12.
- Forces the reservation language buttons to remain visible and clickable.
- Keeps Swedish as the default language.
- Preserves the form/review synchronization from Version 12.


## Version 14
- Built from stable Version 13.
- Keeps the same UI and synchronized language selectors.
- Adds a demo reservation reference number to the review screen.
- Adds Ny bokning / New reservation to clear the form and start over.
- The new action follows the selected language.


## Version 15
- Built from stable Version 14.
- Prevents selecting past reservation dates.
- Adds friendly Swedish/English validation messages.
- Validates required fields, email, phone, guests, and date before opening the review screen.
- Preserves the existing design and all V14 features.


## Version 16
- Built from Version 15.
- Stronger email validation: requires a proper domain and a 2–63 letter top-level domain.
- Stronger phone validation: 7–15 digits, with common phone punctuation allowed.
- Strict date validation: malformed dates cannot open the review screen.
- Invalid dates show a localized Swedish/English message instead of `Invalid Date`.
- Keeps all V14/V15 UI and language features.


## Version 17
- Built from stable Version 16.
- Adds demo opening-hours-aware reservation times.
- Monday is closed.
- Tue–Thu offers lunch and dinner through 20:30.
- Fri–Sat offers lunch and dinner through 21:30.
- Sunday offers lunch and early dinner through 19:30.
- Available times update automatically after selecting a date.
- Swedish/English availability messages follow the selected language.


## Version 18
- Built from Version 17.
- Monday is shown as closed in the opening-hours display.
- Weekday hours now start at Tuesday instead of Monday.
- Every fresh browser/tab session starts in Swedish.
- Language changes remain synchronized during the current session.


## Version 19
- Built from Version 18.
- Corrects the actual translated opening-hours text in app.js.
- Swedish: Måndag Stängt; Tis–Tor 11:00–22:00.
- English: Monday Closed; Tue–Thu 11:00–22:00.
- Friday–Saturday and Sunday hours are unchanged.


## Version 20
- Built from Version 19.
- Swedish is now forced as the default every time the website is opened/reloaded.
- A visitor can still switch to English while using the site.
- All Version 19 opening-hours fixes are preserved.


## Version 21
- Built from Version 20.
- Opening hours are formatted as clean separate rows.
- Monday: Closed.
- Tuesday–Thursday: 11:00–22:00.
- Friday–Saturday: 11:00–23:00.
- Sunday: 12:00–21:00.
- Reservation times now follow those exact opening hours.
- Time slots are offered every 30 minutes, with the final slot 30 minutes before closing.


## Version 22
- Built from Version 21.
- Fixes the opening-hours layout so Monday and Tuesday–Thursday always appear on separate lines.
- All Version 21 reservation-time behavior is unchanged.


## Version 23
- Built from Version 22.
- Rebuilds opening-hours display using separate block rows instead of relying on inline spans/CSS wrapping.
- Monday and Tuesday–Thursday are guaranteed to be separate rows.
- Times are preserved and right-aligned.
- Reservation-time logic from Version 21 remains unchanged.


## Version 24
- Monday and Tuesday–Thursday are now two separate HTML rows.
- Swedish and English translations use separate keys for those rows.
- Opening-hours layout is forced to one row per day group.
- Reservation-time logic remains unchanged.


## Version 25
- Built from stable Version 24.
- The top opening-status message is now day-aware and bilingual.
- Monday: Closed today / Stängt idag.
- Tuesday–Thursday: Open today / Öppet idag 11:00–22:00.
- Friday–Saturday: 11:00–23:00.
- Sunday: 12:00–21:00.
- Existing reservation times, language behavior, validation, review, email/SMS/copy, and opening-hours layout are preserved.


## Version 26
- Built from stable Version 25.
- Adds a polished reservation confirmation card in the review area.
- Shows localized date, time, guests, and reservation number.
- Swedish/English text updates automatically with the language selector.
- Existing V25 design, validation, opening hours, time logic, Email/SMS/Copy, and New Reservation behavior are preserved.


## Version 27
- Built from Version 26.
- Fixes the confirmation-card guest count so the selected number of guests is displayed.
- Fixes the reservation number so only the code (for example TR-260901-4035) is shown.
- All other Version 26 behavior is unchanged.
