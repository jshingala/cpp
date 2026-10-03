# Longest Free Slot — Video Transcript

Video: `longest_free_slot.mp4` (5:58) · Code: `solution.cpp`

## Intro

**[0:00]** In this video, we walk through a C++ solution to the longest free slot problem.

**[0:07]** For every employee and every day, we find the longest stretch of free time inside business hours.


## 1. The problem

**[0:15]** The first line gives the business hours start, the business hours end, and the number of meeting records.

**[0:22]** Each record has an employee ID, a meeting name, a join time, and a leave time.

**[0:29]** For each employee and date, we print the start, the end, and the length in minutes of the longest free gap. Ties go to the earliest gap.


## 2. The plan

**[0:40]** The plan has four steps.

**[0:43]** Parse each record. Split any meeting that crosses midnight. Clip each piece to business hours. Then sort and sweep each day to find the biggest gap.

**[0:55]** Everything is stored in a map from employee and date to that day's list of busy intervals.


## 3. Helpers

**[1:01]** toMinutes turns an HH:MM string into minutes since midnight, and hhmm turns minutes back into HH:MM.

**[1:11]** nextDate adds one day to a date string. It rolls over month ends and year ends, and gives February an extra day in leap years.

**[1:22]** A leap year is divisible by 4 but not by 100, unless it is also divisible by 400.

**[1:30]** Dates are YYYY-MM-DD, so plain string comparison orders them correctly. The loop later relies on that.


## 4. Reading the input

**[1:39]** In solve, we read the business hours and the record count, then call getline to finish that first line.

**[1:47]** Both business times are converted to minutes.

**[1:51]** The map key is a pair: employee ID and date. The value is the list of busy intervals for that day, already clipped to business hours.

**[2:02]** Because it is an ordered map, the output will come out sorted by employee, then by date.

**[2:08]** Blank lines are skipped without counting them as records. Each record is split on commas.

**[2:15]** The first ten characters of each timestamp are the date, and characters eleven to fifteen are the time.


## 5. Meetings that cross midnight

**[2:23]** Now the key trick. A meeting can cross midnight, like employee 102's overnight deploy, from 10 PM on March 11 to 10 AM on March 12.

**[2:36]** We walk the dates from the join date to the leave date. On the first date the piece starts at the join time. On the last date it ends at the leave time. Any date in between is the full 24 hours.

**[2:51]** If a piece has zero length, for example a meeting that ends exactly at midnight, it is skipped.

**[2:58]** Each piece is then clipped to business hours. On March 11, the 10 PM to midnight piece is outside nine to five, so nothing is added.

**[3:09]** On March 12, only nine to ten stays busy, which leaves a free slot from ten to five: 420 minutes.

**[3:19]** Line 31 still creates a map entry for the join date, so March 11 appears in the output as a fully free day of 480 minutes.


## 6. Sort & sweep

**[3:30]** Now the sweep. Here are employee 101's busy intervals on March 11, sorted by start time.

**[3:38]** The cursor marks the end of the busy time merged so far. It starts at 9 AM, and the best gap starts at zero.

**[3:47]** The first meeting starts at 9:30, after the cursor. That leaves a 30 minute gap, which becomes the best so far.

**[3:57]** The cursor moves to the meeting's end, 10:30.

**[4:01]** The next meeting starts at 10, before the cursor, so it overlaps. There is no gap.

**[4:08]** We simply extend the cursor to 11. This is how overlapping and touching meetings merge, without a separate merge step.

**[4:18]** The third meeting starts at 1 PM. The gap from 11 to 1 is 120 minutes, a new best. The cursor moves to 2 PM.

**[4:29]** After the loop, we check the gap from the cursor to the end of business hours. Two to five is 180 minutes, the new best.

**[4:39]** Because the best is only replaced by a strictly longer gap, ties keep the earliest one.


## 7. Edge cases

**[4:46]** A few edge cases. Employee 103 is in an offsite for the whole business day, so no gap is ever found. The output is a zero length slot starting at 9 AM.

**[5:00]** Back to back meetings merge because the next start is not greater than the cursor.

**[5:06]** Meetings entirely outside business hours are clipped away, but their date still shows up. Month ends, year ends, and leap years are handled by next Date.


## 8. Output

**[5:17]** Here is the program's output for the sample input.

**[5:21]** Employee 101 is free from 2 to 5. Employee 102 is free all of March 11, and from 10 to 5 on March 12. Employee 103 has no free time.


## 9. Complexity & takeaways

**[5:36]** Time complexity is O of N log N for parsing and sorting, plus the number of days that meetings span. Space is linear.

**[5:46]** To recap: convert times to minutes, split at midnight, clip to business hours, then sort and sweep with a single cursor. Thanks for watching.

