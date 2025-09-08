Development Notes (PyLoF)
==================================================

- [Sep. 2025](#2025-09-05)
    - [Everything overthrown...](#2025-09-08)

# 2025-09-05

- For "faster" searching, we will just do it like with covid test.
- We split the elements in groups of strings, checking if element is in there, then going to next split.
- Do not really know, if tht in any way does something with the processing power. But it seemed easier to do for me, then searching for every single element or loop blindely. Dunno, why. A feeling. Let's go with it. Nothing to break here.


# 2025-09-08

Fully overthrown the old parsing idea. It was much too complicated and focused on the form logic.

> You can find the old stuff as `types-<today>.py` in `legacy/`

## New Approach

- We will focus on the drawing itself.

- Because it's easier we will read from *right to left*.

- Every new element will be called a *step* with every step containing either a non-logical or logical element. So some variable or a *rule* (line of a **mark**).

- Will write it more orderly from here in a documentation file...
