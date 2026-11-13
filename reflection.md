# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

We have four classes. Scheduler, Owner, Pet, and Task. The scheduler reads the availability of the owner, the care tasks of the pet, and selects the tasks needed. The Owner owns the pet and Task provides the tasks that the pet needs. 
Owner:
- Has availability object
- Can add or remove pets

Scheduler:
- Builds the daily plan for the owner
- Selects and explains tasks

Pet:
- Adds, and removes, and gets tasks needed

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, there was some editing done to the tasks to create constraints that were not previously there.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

Time availability, preference, completion, deadline, priority

- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

A tradeoff the scheduler will make is assigning priority to tasks. It will schedule high priority tasks first, and if one high priority task is long, the scheduler will schedule that first over several lower priority tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used to create the UML diagram, as well as structure the classes for the app. It was also used to check program logic. Questions asking why it decided to write a certain line or add a certain thing to the UML were helpful in learning the code.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I asked AI for constraints to put on the scheduler. It gave a few constraints that I felt were a little out of scope of the project. I had instead given it a couple others.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
