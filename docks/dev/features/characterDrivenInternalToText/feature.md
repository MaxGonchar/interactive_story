## Problem to solve
NPC looses emotional curve trajectory during each fallowing generation.
To generate next step we pass only story content without the internal emotional state of the NPC.
initially such approach was chosen to hide internal from other characters.
However, this leads to the loss of the NPC's emotional continuity over time.

## Proposed solution
Include the NPC's internal emotional state when generating the next step to maintain emotional continuity.
Include the internal emotional state when generating memory items at a scene end.

## Requirements
1. when gathering content for particular character, include **internal** thoughts if available.
2. correct system prompts if needed.

## Example of including internal emotional state
example: ../example.yaml
character: Ember

**Before:**
```
Ember's thumbs hovered over the keyboard for a beat too long, the cursor
blinking with patient indifference. She glanced back at the monitor—the forum
tab still glowing behind her, its bullet points about patience and preparation
burning into her peripheral vision—then snapped her attention back to the phone,
jaw tightening. She typed, deleted, typed again, the words rearranging themselves
on the screen as her cheeks continued to burn. *Yeah sure, no problem. Just leave
me the keys and his food schedule. ...Max and I will be fine.* She hit send, then
immediately locked the phone face-down on the desk and pressed both palms over
it like she was trapping a bug, as though the message might crawl back out and
expose something she wasn't ready to name. The phone sat warm and still beneath
her hands, and behind her the monitor hummed on, its forum tab patient and waiting.
Morning light fell soft and gold across the quiet street as Ember stepped
through the low gate of Megan's small private house, the latch clicking shut behind
her with a sound that felt louder than it should have. The yard was modest—a patch
of browning grass, a few clay pots with herbs nobody had watered in days, and
a short wooden fence that seemed more decorative than functional. Max lay curled
on the porch in a slant of sunlight, a golden retriever with a thick ruff and
one ear twitching against the boards at the sound of her footsteps. He didn't
stir, his ribs rising and falling in the slow tide of deep sleep, and Ember stopped
at the bottom of the porch steps, keys already fished from her pocket, just looking
at him. The morning air smelled like cut grass and someone's coffee two houses
over, and for a long, suspended moment she simply stood there, the keys warm in
her fist, watching the dog sleep.
Ember exhaled slowly through her nose, unclenching the hand that held
the keys until the metal teeth stopped biting into her palm. She took the first
porch step, then the second, her sneakers creaking against the sun-warmed wood,
and crouched down a few feet from Max, resting her forearms on her knees as she
watched the slow rise and fall of his ribs. Her fingers drummed once against her
kneecap—a quick, unconscious staccato—then went still. "Hey, Max," she said, her
voice easy and light, almost the way you'd greet a neighbor's kid. "...Rise and
shine, big guy." The words hung in the warm morning air, and one of Max's ears
rotated toward her like a small golden satellite dish, though his eyes stayed
shut.
One ear swiveled toward her voice, then the other followed like a delayed
echo. Max's eyes cracked open—soft brown, blinking against the slant of sunlight—before
a slow yawn split his muzzle wide, pink tongue curling, back legs stretching out
behind him with a long satisfied tremble that rippled all the way to his tail.
That tail began a lazy, heavy thump against the porch boards as he lifted his
head, regarding Ember with that warm, slightly dopey expression golden retrievers
perfect in the cradle, like they've never once suspected a human of bad intentions.
He rolled onto his chest with a grunt, front paws splayed, and stretched his neck
forward to sniff the air between them—curious, not cautious. A low, friendly "wuh-uff"
rumbled out of him, half-yawn, half-acknowledgment, the sound a dog makes when
he's decided you're acceptable but hasn't fully committed to standing up yet.
The morning sun caught the gold in his ruff as he held her gaze, tail still thumping
its easy, unhurried rhythm against the warm boards.
Ember straightened up from her crouch, brushing her palms against her
jeans as she stepped over Max''s outstretched legs and moved to the front door.
She slid the key in, turned it, and pushed the door open into Megan''s quiet house.
The air inside was stuffy and still—curtains half-drawn, a faint smell of lavender
and dog. She scanned the kitchen counter, spotting a handwritten note taped to
the fridge alongside a bag of kibble and a measuring scoop. Her eyes moved over
the note: *2 cups morning, 1 cup evening, treats in the cabinet above the stove,
walk twice a day.*
```

**After**
```
Ember's thumbs hovered over the keyboard for a beat too long, the cursor
blinking with patient indifference. She glanced back at the monitor—the forum
tab still glowing behind her, its bullet points about patience and preparation
burning into her peripheral vision—then snapped her attention back to the phone,
jaw tightening. She typed, deleted, typed again, the words rearranging themselves
on the screen as her cheeks continued to burn. *Yeah sure, no problem. Just leave
me the keys and his food schedule. ...Max and I will be fine.* She hit send, then
immediately locked the phone face-down on the desk and pressed both palms over
it like she was trapping a bug, as though the message might crawl back out and
expose something she wasn't ready to name. The phone sat warm and still beneath
her hands, and behind her the monitor hummed on, its forum tab patient and waiting.
Morning light fell soft and gold across the quiet street as Ember stepped
through the low gate of Megan's small private house, the latch clicking shut behind
her with a sound that felt louder than it should have. The yard was modest—a patch
of browning grass, a few clay pots with herbs nobody had watered in days, and
a short wooden fence that seemed more decorative than functional. Max lay curled
on the porch in a slant of sunlight, a golden retriever with a thick ruff and
one ear twitching against the boards at the sound of her footsteps. He didn't
stir, his ribs rising and falling in the slow tide of deep sleep, and Ember stopped
at the bottom of the porch steps, keys already fished from her pocket, just looking
at him. The morning air smelled like cut grass and someone's coffee two houses
over, and for a long, suspended moment she simply stood there, the keys warm in
her fist, watching the dog sleep.

**INTERNAL:** He''s just a dog. He''s just a dog sleeping on a porch
in the sun, and I''m standing here like I''m approaching a wild animal. Get
it together.

Ember exhaled slowly through her nose, unclenching the hand that held
the keys until the metal teeth stopped biting into her palm. She took the first
porch step, then the second, her sneakers creaking against the sun-warmed wood,
and crouched down a few feet from Max, resting her forearms on her knees as she
watched the slow rise and fall of his ribs. Her fingers drummed once against her
kneecap—a quick, unconscious staccato—then went still. "Hey, Max," she said, her
voice easy and light, almost the way you'd greet a neighbor's kid. "...Rise and
shine, big guy." The words hung in the warm morning air, and one of Max's ears
rotated toward her like a small golden satellite dish, though his eyes stayed
shut.
One ear swiveled toward her voice, then the other followed like a delayed
echo. Max's eyes cracked open—soft brown, blinking against the slant of sunlight—before
a slow yawn split his muzzle wide, pink tongue curling, back legs stretching out
behind him with a long satisfied tremble that rippled all the way to his tail.
That tail began a lazy, heavy thump against the porch boards as he lifted his
head, regarding Ember with that warm, slightly dopey expression golden retrievers
perfect in the cradle, like they've never once suspected a human of bad intentions.
He rolled onto his chest with a grunt, front paws splayed, and stretched his neck
forward to sniff the air between them—curious, not cautious. A low, friendly "wuh-uff"
rumbled out of him, half-yawn, half-acknowledgment, the sound a dog makes when
he's decided you're acceptable but hasn't fully committed to standing up yet.
The morning sun caught the gold in his ruff as he held her gaze, tail still thumping
its easy, unhurried rhythm against the warm boards.

**INTERNAL:** He''s just a dog. A normal, sleepy, dopey golden retriever
who needs someone to feed him for a week. That''s all this is. Stop making it
weird in your head.

Ember straightened up from her crouch, brushing her palms against her
jeans as she stepped over Max''s outstretched legs and moved to the front door.
She slid the key in, turned it, and pushed the door open into Megan''s quiet house.
The air inside was stuffy and still—curtains half-drawn, a faint smell of lavender
and dog. She scanned the kitchen counter, spotting a handwritten note taped to
the fridge alongside a bag of kibble and a measuring scoop. Her eyes moved over
the note: *2 cups morning, 1 cup evening, treats in the cabinet above the stove,
walk twice a day.*
```
