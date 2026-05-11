# System Blueprint (_a.k.a._ "Design Doc")

## TNPG: SARDines
## project: NerdyMap
## Target ship date: {2026-06-xx}

---

#### roster:


| Name | Email | Primary Role | Secondary Role |
|---|---|---|---|
|Rohan Sen |rohans33@nycstudents.net |PM |Backend |
|David Lee |davidl542@nycstudents.net |F Student (Innovator)|Trailblazer |
|Sean Zheng |seanz22@nycstudents.net |F Student (Innovator) |Clicky Clicky |
|Araf Hoque |aoanulh2789@nycstudents.net |ladies man |Tung Tung Tung Sahur |

---


# Summary
A one-stop shop for frequent commuters, or in other words, a multi-purpose transit system guide targetting city folks.

## Problem Being Solved
We are solving the limited functionality provided by simple transit maps provided by apps such as Google or Apple Maps, which are often delayed in updating and timing.

## Target Users

Who will use this system?
- People who utilize public transportation
- People who like cool maps

## Why This Project Matters
Many transit applications such as those integrated into Google/Apple Maps are often unreliable and inaccurate for some unknwon reason (they don't disclose what metrics they use to time the arrivals/departures, i.e. ghost trains, etc.); we want to provide a stable, structured way to deliver transit times to users.

---

# Minimum Viable Product (MVP) Scope

## Core Features (Required for Final Submission)
Features that **must** be completed:
1. An interactive map showcasing transit routes in a given area (NYC)
2. List of active delays across the city
3. Wayfinding between different stops 

## Stretch Features (Only if MVP is Complete)
1. Add LIRR Support
2. Customizeable Interface (Pin lines, change UI parameters, etc)
3. Map changes based on delays

## Explicit Non-Goals
We don't want to recreate Google/Apple Maps. Our intent is to develop a more in-depth transit map, rather than just a clone.

Features intentionally excluded:
- Multiple cities being integrated, since we want to focus on NYC's needs specifically and its unique system

---

# Technology Stack

| Layer | Selected Tool |
|---|---|
| Backend Framework | Flask |
| Frontend Framework | bootstrap |
| Database | SQLite |
| Authentication | Flask sessions |
| ORM / DB Library | SQLAlchemy |

## Why This Stack Was Chosen
We chose this stack because it matches our team’s experience and project needs. Flask is powerful enough to handle routes, API requests, sessions, and transit data without being too complex. Bootstrap helps us quickly build a clean, responsive interface using pre-styled components. SQLite works well because we have more experience with it than MongoDB, and it can store data like users, saved stops, pinned routes, and preferences. Flask sessions support basic login and user-specific features, while SQLAlchemy helps us connect our Python code to the database in a cleaner and more organized way. Overall, this stack lets us focus on building NerdyMap’s transit features instead of spending too much time learning unfamiliar tools.

---

# Team Ownership Plan

Each member must own meaningful deliverables.

| Team Member | Primary Ownership | Secondary Ownership | Specific Deliverables |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |

---

# Component map

{Insert your mermaid(or equivalent)-generated diagram here}

# Site map

{Insert your mermaid(or equivalent)-generated diagram here}
eg...
```
Landing Page
   ↓
Login / Register
   ↓
Dashboard
   ├── Feature A
   ├── Feature B
   └── Profile
```

## Key User Stories
### eg0
As a nerd, I want to watch the trains move around the map so that I can see the city moving around in real-time.

### eg1
As a New Yorker, I want to see where my train is so that I know how long I have to wait in the station, since the time estimates aren't as accurate.

### eg2
As a parent, I want to track a specific train so that I can watch my kids come home.


# Database Design

{Insert your table/document organizational structure here}


# Testing Plan
{Delineate here your plan for testing each component}

# Timeline
## Week 1 Goals: Basic map functionality, pull data from the MTA and other APIs.
## Week 2 Goals: Plotting trains on the map, rendering their movement, use websockets.
## Week 3 Goals: UI perfection, debugging, hopefully no major features pending.
## Internal Deadlines:
{List milestones your team has identified, in the order they must be completed. Set a target completion date for each.}


# Completion Criteria (_a.k.a._ "Definition of 'Done'")
Project is considered complete when all of the following are true:
1.
1.
1.

# Open Questions
- Will we try to implement multiple cities? Presumably, if we can implement NYC transit tracking, we could for other cities, too.

# Appendix
None at the moment.

# Other
None at the moment.
