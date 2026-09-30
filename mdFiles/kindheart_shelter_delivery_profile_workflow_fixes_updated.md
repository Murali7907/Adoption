# KINDHEART — SHELTER, DELIVERY & PROFILE WORKFLOW FIXES

## PURPOSE

This specification fixes the current Shelter and Delivery modules so that:

- Dashboard metrics show only real database-backed data.
- Adoption journeys are created only from real adoption records.
- Delivery data is shown only when real delivery boys exist.
- Delivery module does not incorrectly show partner shelters.
- Delivery partner registration does not ask for an unnecessary affiliated shelter field.
- Shelter documents can be uploaded from the frontend and stored in the backend/database.
- Shelter verification is completed by Admin before the shelter can add pets or delivery partners.
- Adopter Profile and Shelter Dossier use clearly different UI structures.
- Frontend, backend, Django models, database, permissions, and Django Admin remain synchronized.

IMPORTANT:

Do not create fake/sample records to make the UI look populated.

Do not hardcode dashboard values.

Do not create duplicate models, APIs, components, forms, or pages when an existing implementation can be repaired.

---

# PHASE 1 — SHELTER DASHBOARD: REMOVE FAKE DATA

## 1.1 My Adopted Pets

Current issue:

> My Adopted Pets 02

This is displaying fake/static data in the Shelter Dashboard.

### Required behavior

The value must come from the database.

Count only real adoption records where:

- the shelter is the current shelter
- the adoption actually belongs to a real pet
- the adopter/customer is real
- the adoption relationship is valid
- the record is not a deleted/test/fake record

Do NOT use a hardcoded value such as `02` or `2`.

If there are zero real adopted pets, display `0` or a meaningful empty state.

The dashboard must remain correct after refresh, login/logout, new adoption, adoption completion, and cancellation/rejection where applicable.

---

# PHASE 2 — REMOVE FAKE "YOUR ADOPTION JOURNEY"

Current fake data:

> Your Adoption Journey  
> Application #KHD-1024  
> Bruno (Golden Retriever)

This must NOT be shown unless there is a real adoption application in the database.

## 2.1 Required logic

The Adoption Journey must be generated from a real adoption record.

It should only appear when all necessary relationships exist, such as:

```text
Customer / Adopter
+
Pet
+
Shelter
+
Adoption Request / Order
```

If delivery is part of the actual KindHeart adoption workflow, do NOT imply delivery progress unless a real delivery record exists.

### Real adoption with no delivery assigned

Show real adoption information such as:

```text
Adoption Application
Pet: [real pet]
Application ID: [real database ID]
Status: Approved / Ready for Handover
Delivery: Not Yet Assigned
```

Do NOT show courier-assigned, out-for-delivery, in-transit, or GPS states until those records actually exist.

### Real adoption + real delivery assignment

Then show real delivery information:

- Pet
- Shelter
- Customer
- Delivery Boy
- Delivery Status
- Scheduled Date
- Destination

Only show GPS/tracking information if a real tracking implementation exists.

---

# PHASE 3 — ADOPTION JOURNEY STATUS MODEL

Use the existing KindHeart business workflow.

Example state flow:

```text
ADOPTION REQUEST CREATED
        ↓
UNDER REVIEW
        ↓
APPROVED
        ↓
READY FOR HANDOVER
        ↓
DELIVERY ASSIGNED
        ↓
OUT FOR DELIVERY
        ↓
DELIVERED / HANDED OVER
        ↓
ADOPTION COMPLETED
```

IMPORTANT:

Not every adoption necessarily has a delivery.

Therefore:

- Do not force a delivery record just to make the UI look complete.
- If handover is pickup-based, show the appropriate handover state.
- Only show delivery stages when delivery is actually selected/created.
- Do not invent courier data.

Use the existing model/status system if these statuses already exist. If statuses are inconsistent across frontend/backend/database, normalize them using the existing architecture instead of creating a second status system.

---

# PHASE 4 — DELIVERY BOYS DETAILS NOT SHOWING

Current issue:

> Delivery Boys Details

is not displaying registered delivery boys.

Fix the complete data flow:

```text
Shelter Frontend
↓
Delivery Partner API / View
↓
Django Model
↓
Database
↓
Response
↓
Delivery Boys Details UI
```

## 4.1 Required fields

Show real database-backed data such as:

- Delivery boy name
- Photo
- Phone
- Email if stored
- License details
- Availability/status
- Documents/proofs
- Registration date
- Current assignment if applicable

Do not show placeholder people or hardcoded names.

## 4.2 Empty state

When there are no registered delivery boys:

> No delivery boys registered yet.

Do not display fake data.

## 4.3 After registering a delivery boy

Verify:

```text
Register Delivery Boy
→ backend save
→ database record
→ Delivery Boys Details list
```

The record must still appear after browser refresh.

---

# PHASE 5 — DELIVERY MODULE: REMOVE PARTNER SHELTERS

Current issue:

The Delivery module incorrectly displays:

> Partner Shelters

Remove this from the Delivery module.

The Delivery role should focus on delivery operations and assigned work.

Do not show a shelter directory or partner-shelter management block inside the Delivery module unless that specific feature is genuinely required by the existing business workflow.

Remove:

- Partner Shelters section
- Shelter list if it is only decorative/placeholder data
- Shelter cards from delivery dashboard
- Unrelated shelter affiliation information

Do not delete actual database relationships if they are required for delivery assignments. This requirement concerns the incorrect UI responsibility, not necessarily the backend relationship.

---

# PHASE 6 — REMOVE "AFFILIATED SHELTER (BELONGS TO)" FROM REGISTER DELIVERY PARTNER

Current issue:

The registration form contains:

> Affiliated Shelter (Belongs To) *

Remove this field from the frontend registration form.

Reason:

The delivery partner is being registered from the current shelter context.

The current shelter should be derived from the authenticated shelter/user relationship instead of asking the user to manually choose a shelter.

## Required behavior

When Shelter A registers a delivery boy:

```text
Logged-in Shelter = Shelter A
```

The backend automatically associates the new delivery boy with Shelter A.

The user should NOT have to select from a shelter dropdown.

Remove the field from:

- registration form
- modal
- edit form if it is not required
- frontend validation
- API payload if it should be derived from authentication

## Backend requirement

The backend must determine the shelter from the authenticated user/session/relationship.

Do not trust a frontend-provided arbitrary shelter ID.

This prevents a shelter from assigning a delivery boy to another shelter.

---

# PHASE 7 — SHELTER DOCUMENT UPLOAD WORKFLOW

Current issue:

> Adoption Documents & Certificates

cannot upload documents because there is no usable upload option.

Implement a complete document upload workflow from Shelter frontend to backend/database.

## 7.1 Shelter should upload documents FIRST

The intended workflow is:

```text
SHELTER CREATED
        ↓
UPLOAD REQUIRED DOCUMENTS
        ↓
DOCUMENTS STORED
        ↓
ADMIN REVIEWS DOCUMENTS
        ↓
ADMIN VERIFIES SHELTER
        ↓
SHELTER BECOMES VERIFIED / APPROVED
        ↓
PET MANAGEMENT ENABLED
        ↓
DELIVERY PARTNER MANAGEMENT ENABLED
```

A shelter must be able to upload documents before adding:

- Pets
- Delivery partners

## 7.2 Required frontend functionality

Create a usable:

> Adoption Documents & Certificates

section.

It must provide:

- Upload button
- File picker
- Document type
- File name
- Upload status
- Upload date
- Review/verification status
- View/download option if appropriate
- Replace/re-upload option where appropriate
- Delete option where appropriate
- Empty state when no documents exist

Use a modern file-upload UI.

Do not use a non-functional decorative upload button.

## 7.3 Document examples

Use the existing business requirements and model structure.

Possible document categories:

- Shelter registration/proof
- Government/identity proof
- Address proof
- Authorization document
- Adoption-related certification
- Other required shelter documents

Do not invent unnecessary legal requirements.

Make the list configurable using the existing model if possible.

---

# PHASE 8 — DOCUMENT STORAGE

When a shelter uploads a document:

```text
Frontend
↓
Multipart/Form Upload
↓
Django Endpoint
↓
Document Model
↓
File Storage
↓
Database Metadata
```

Store at minimum:

- shelter
- uploaded by
- document type
- original file name
- stored file path/reference
- upload date
- verification status
- admin reviewer where applicable
- review date where applicable

Do not store only the filename in the frontend.

The file must be accessible through the backend/storage configuration.

---

# PHASE 9 — ADMIN DOCUMENT VERIFICATION

Admin must be able to see shelter-uploaded documents.

Admin workflow:

```text
Shelter uploads documents
        ↓
Admin sees documents
        ↓
Admin reviews
        ↓
Admin verifies / rejects
        ↓
Shelter verification status updates
```

Admin must be able to determine whether the shelter has completed the required documentation.

## Verification statuses

Use clear factual statuses, for example:

```text
Documents Pending
Under Review
Verified
Rejected
```

Use the project's existing status model when available.

Do not create multiple conflicting verification fields.

---

# PHASE 10 — GATE PET AND DELIVERY ACCESS UNTIL VERIFICATION

This is a critical business rule.

Before Admin verification:

### Shelter CAN

- Login
- View dashboard
- Upload documents
- View document statuses
- Receive admin feedback where implemented
- Update required profile information

### Shelter CANNOT

- Add pets
- Register delivery boys
- Add delivery partners
- Access actions that require verified shelter status

The frontend must clearly communicate the reason.

Example:

> Complete and submit your shelter documents for Admin verification before adding pets or delivery partners.

Do not simply hide features without explaining why.

---

# PHASE 11 — BACKEND ENFORCEMENT OF VERIFICATION

This restriction must NOT be frontend-only.

Even if a shelter manually calls the API, the backend must reject pet/delivery creation when the shelter is not verified/approved.

Implement permission checks in the backend using the existing KindHeart authentication and shelter models.

Conceptually:

```text
if shelter is not verified:
    reject pet creation
    reject delivery partner creation
```

Do not create a second independent verification system.

---

# PHASE 12 — DATABASE STATE MACHINE

The following data relationship must be consistent:

```text
Shelter
    ↓
Documents
    ↓
Admin Verification Status
    ↓
Permissions
    ├── Pet Creation
    └── Delivery Partner Creation
```

The shelter status in:

- frontend
- Django backend
- database
- Django Admin

must match.

Refreshing the page must not reset verification.

---

# PHASE 13 — PET CREATION GATE

When a shelter attempts to add a pet:

### Verified shelter

Allow:

```text
Add Pet
→ save
→ database
→ pet visible in shelter list
```

### Unverified shelter

Block the operation and show:

> Shelter verification is required before adding pets.

Do not create the pet record.

---

# PHASE 14 — DELIVERY PARTNER CREATION GATE

When a shelter attempts to register a delivery boy:

### Verified shelter

Allow:

```text
Register Delivery Boy
→ automatically associate with current shelter
→ save
→ database
→ Delivery Boys Details
```

### Unverified shelter

Block the operation and show:

> Shelter verification is required before registering delivery partners.

Do not create the delivery record.

---

# PHASE 15 — SHELTER DOCUMENTS UI

Redesign the document section so it does not look like a placeholder.

Suggested structure:

```text
------------------------------------------------
Adoption Documents & Certificates
------------------------------------------------

Verification Status
[ Under Review ]

Required Documents

[ Shelter Registration ]     Uploaded
[ Identity Proof ]           Uploaded
[ Address Proof ]            Pending
[ Other Document ]            Uploaded

[ + Upload Document ]

Recent Uploads

Document Name | Type | Uploaded | Status | Action
------------------------------------------------
```

Use actual data.

Do not show example documents as real records.

---

# PHASE 16 — ADOPTER PROFILE & SHELTER DOSSIER MUST BE DIFFERENT

Current issue:

> Adopter Profile & Shelter Dossier

needs a clearly different UI.

Do NOT reuse the same card structure for both.

These represent different types of information.

---

# PHASE 17 — ADOPTER PROFILE UI

The Adopter Profile should focus on the individual customer/adopter.

Suggested sections:

### Profile Header

- Profile photo
- Full name
- Email
- Phone
- Account status

### Contact Details

- Phone
- Email
- Address
- City
- State
- Postal code

### Adoption Activity

- Adoption requests
- Active adoption
- Completed adoptions
- Favorites if implemented
- Messages

### Adoption History

Show real adoption records:

```text
Pet
Shelter
Application Date
Status
Handover / Delivery Status
```

Keep it customer-focused.

---

# PHASE 18 — SHELTER DOSSIER UI

The Shelter Dossier should focus on the organization/shelter.

Suggested sections:

### Shelter Header

- Shelter name
- Shelter logo/photo
- Verification status
- Shelter registration date

### Shelter Information

- Shelter type
- Address
- City
- State
- Contact information
- Description

### Verification & Documents

- Verification status
- Required documents
- Uploaded documents
- Admin review state

### Shelter Operations

- Total pets
- Available pets
- Adoption requests
- Completed adoptions
- Registered delivery boys

Only show actual database-backed counts.

### Shelter Activity

- Recent pets
- Recent adoption requests
- Recent completed adoptions
- Recent delivery assignments

This should clearly look different from an adopter profile.

---

# PHASE 19 — DO NOT MIX PROFILE DATA

Do not display shelter-specific data in an adopter profile.

Do not display adopter-specific information in a shelter dossier unless required by a specific workflow.

### Adopter Profile should NOT contain

- Shelter documents
- Shelter verification
- Shelter registration details
- Shelter operational metrics

### Shelter Dossier should NOT contain

- Personal adopter-only metrics
- Customer profile sections
- Customer favorites
- Customer personal adoption preferences unless intentionally required

---

# PHASE 20 — DYNAMIC DATA RULE

All dashboard/profile/dossier values must come from actual data.

Do not hardcode values such as:

```text
02 adopted pets
KHD-1024
Bruno
Golden Retriever
4 delivery boys
2 active deliveries
4.95 rating
```

unless those values actually exist in the database.

The application must generate these values dynamically.

---

# PHASE 21 — REMOVE OLD SAMPLE / DEMO DATA

Search the project for sample values related to:

- Bruno
- Golden Retriever
- KHD-1024
- Fake adoption journeys
- Fake delivery boys
- Fake shelter affiliations
- Fake adoption documents
- Fake dashboard counts
- Fake shipment/tracking values

Determine whether each value comes from:

1. Database seed/demo data
2. Backend hardcoded data
3. Frontend hardcoded data
4. Test data

Remove demo data from production-facing UI.

Do not delete legitimate test fixtures if they are required for development; instead ensure they are not presented as real user data.

---

# PHASE 22 — FRONTEND + BACKEND + DATABASE VERIFICATION

For every affected feature verify:

```text
Frontend
↓
API / URL
↓
Django view
↓
Model
↓
Database
↓
Response
↓
Frontend refresh
```

Test:

- Shelter document upload
- Document persistence
- Admin document visibility
- Admin verification
- Shelter verification persistence
- Pet creation before verification
- Pet creation after verification
- Delivery partner creation before verification
- Delivery partner creation after verification
- Automatic shelter association for delivery boy
- Delivery Boys Details list
- Adoption dashboard count
- Adoption Journey
- Delivery assignment visibility
- Adopter Profile
- Shelter Dossier

---

# PHASE 23 — DJANGO ADMIN VERIFICATION

Confirm Django Admin reflects the same data.

Admin should be able to inspect:

- Shelter
- Shelter verification status
- Shelter documents
- Delivery boys
- Pet records
- Adoption records
- Delivery assignments
- Related users

Do not create a separate frontend-only database state.

---

# PHASE 24 — FINAL UI REQUIREMENTS

Keep the KindHeart UI modern and professional.

Use:

- Clear cards
- Consistent typography
- Consistent spacing
- Modern upload controls
- Clear status badges
- Proper empty states
- Clear permissions messaging
- Responsive layout

Do not use:

- Fake metrics
- Decorative fake records
- Old browser alerts
- Unnecessary technical wording
- Placeholder names presented as actual data
- Duplicate UI components

---

# FINAL TEST CHECKLIST

## Shelter Dashboard

- [ ] `My Adopted Pets` is database-backed
- [ ] Fake `02` removed
- [ ] Fake `KHD-1024` removed
- [ ] Fake Bruno adoption removed
- [ ] Adoption Journey only appears when a real record exists
- [ ] Delivery stage appears only when a real delivery assignment exists

## Delivery

- [ ] Delivery Boys Details displays real registered delivery boys
- [ ] Delivery boy list persists after refresh
- [ ] Partner Shelters removed from Delivery module
- [ ] Affiliated Shelter field removed from registration form
- [ ] Current shelter is assigned automatically from authenticated context

## Documents

- [ ] Shelter has a real document upload option
- [ ] Files are stored correctly
- [ ] Metadata is stored in database
- [ ] Admin can view uploaded documents
- [ ] Admin can verify/reject documents
- [ ] Verification status persists after refresh

## Permissions

- [ ] Unverified shelter cannot add pets
- [ ] Unverified shelter cannot register delivery boys
- [ ] Verified shelter can add pets
- [ ] Verified shelter can register delivery boys
- [ ] Backend enforces the restriction
- [ ] Frontend communicates the restriction clearly

## Profiles

- [ ] Adopter Profile has dedicated adopter-focused UI
- [ ] Shelter Dossier has dedicated shelter-focused UI
- [ ] The two layouts are visually and structurally different
- [ ] Both use real database data

## Data Integrity

- [ ] No fake dashboard values
- [ ] No fake adoption records
- [ ] No fake delivery records
- [ ] No fake documents
- [ ] No hardcoded names used as real records
- [ ] Frontend matches backend
- [ ] Backend matches database
- [ ] Django Admin matches application state

---

# FINAL IMPLEMENTATION RULE

Do not fix these requirements by changing only visible frontend text.

For every issue, trace and repair the complete system:

```text
UI
→ frontend state
→ API
→ Django backend
→ permissions
→ model
→ database
→ response
→ frontend
```

Fix the root cause.

Reuse existing KindHeart architecture whenever possible.

Do not create duplicate models, duplicate endpoints, duplicate components, or parallel workflows.

The final system must behave like a real application, not a static dashboard mockup.

---

# PHASE 25 — ADOPTION TO DELIVERY DISPATCH WORKFLOW

Implement the complete real-world delivery workflow for an adopted pet.

The system must work as:

```text
CUSTOMER ADOPTS PET
        ↓
ADOPTION APPROVED / READY FOR HANDOVER
        ↓
DELIVERY ORDER CREATED (if delivery is required)
        ↓
DELIVERY ORDER = UNASSIGNED
        ↓
SHELTER SEES DELIVERY ORDER
        ↓
SHELTER SELECTS AN AVAILABLE DELIVERY BOY
        ↓
BACKEND VALIDATES THE DELIVERY BOY
        ↓
DELIVERY BOY = BUSY
        ↓
DELIVERY ORDER = ASSIGNED
        ↓
DELIVERY ORDER = OUT FOR DELIVERY
        ↓
DELIVERY COMPLETED
        ↓
DELIVERY ORDER = DELIVERED
        ↓
DELIVERY BOY = AVAILABLE
        ↓
ADOPTION / HANDOVER = COMPLETED
```

Do not implement this as frontend-only state.

The database must be the source of truth.

---

# PHASE 26 — WHEN A DELIVERY ORDER IS CREATED

Do NOT create a delivery order when the customer merely submits an adoption request.

Create it only after the adoption reaches the appropriate state, such as:

```text
APPROVED
```

or:

```text
READY FOR HANDOVER
```

Use the existing KindHeart adoption status model if available.

When the adoption is ready:

```text
Adoption approved
→ backend creates delivery order
→ delivery order = UNASSIGNED
```

The delivery boy is NOT assigned automatically.

This allows the Shelter to decide which delivery boy should handle the order.

If the adoption is pickup/handover-at-shelter and no delivery is required, do not create a delivery order.

---

# PHASE 27 — DELIVERY ORDER DATA

Reuse the existing delivery/order model if present. Extend it rather than creating a duplicate delivery system.

A delivery order should relate to:

- Adoption record
- Pet
- Customer/adopter
- Shelter
- Delivery boy (nullable until assignment)
- Pickup/source location
- Destination
- Delivery status
- Assignment timestamp
- Scheduled date/time where applicable
- Started timestamp
- Completed timestamp
- Created/updated timestamps

Suggested lifecycle:

```text
UNASSIGNED
→ ASSIGNED
→ OUT_FOR_DELIVERY
→ DELIVERED
```

Optional states such as `CANCELLED`, `FAILED`, or `RESCHEDULED` should only be added if the existing business workflow needs them.

---

# PHASE 28 — SHELTER DELIVERY QUEUE

Add/fix the Shelter delivery queue so real approved adoptions waiting for delivery are visible.

Example:

```text
Delivery Outgoing

--------------------------------------------------------------
Order       Pet       Customer     Delivery Boy     Status
--------------------------------------------------------------
#DLV-102    Bruno     Murali       Not Assigned     UNASSIGNED
#DLV-103    Max       Arun         Rahul             ASSIGNED
#DLV-104    Bella     Anu          Suresh            OUT FOR DELIVERY
--------------------------------------------------------------
```

All rows must come from the database.

Do not hardcode example pets, customers, orders, or delivery boys.

---

# PHASE 29 — DELIVERY BOY AVAILABILITY

Every delivery boy participating in dispatch needs a real operational state.

At minimum:

```text
AVAILABLE
BUSY
INACTIVE
```

Reuse the existing model/status field where possible.

## AVAILABLE

Can be assigned a new active delivery.

## BUSY

Currently has an active delivery assignment.

Cannot receive another active delivery.

## INACTIVE

Cannot be assigned.

Examples include disabled/removed delivery personnel according to the existing system.

---

# PHASE 30 — HOW THE SHELTER ASSIGNS AN ORDER

When the Shelter clicks:

> Assign Delivery

the backend must retrieve eligible delivery boys belonging to the currently authenticated Shelter.

The frontend may display the list, but the backend must perform the final validation.

Only delivery boys belonging to the current Shelter may be assigned.

Never allow:

```text
Shelter A → Delivery Boy from Shelter B
```

The backend must verify ownership from authenticated user/shelter relationships.

Do not trust a shelter ID sent by the browser.

---

# PHASE 31 — AVAILABLE DELIVERY BOYS IN THE ASSIGNMENT UI

The assignment UI should clearly separate available and unavailable people.

Example:

```text
Assign Delivery

Pet: Bruno
Customer: Murali
Order: #DLV-102

AVAILABLE
○ Rahul
○ Arun

BUSY
Suresh — Current order #DLV-099

INACTIVE
Ravi
```

Only AVAILABLE delivery boys should be selectable.

BUSY and INACTIVE delivery boys must not be assignable.

The displayed status must come from backend/database data.

---

# PHASE 32 — ASSIGNMENT TRANSACTION

When the Shelter chooses a delivery boy:

```text
Frontend
→ assignment API
→ Django backend
→ validate adoption
→ validate delivery order
→ validate Shelter ownership
→ validate delivery boy
→ validate delivery boy availability
→ create/update assignment
→ mark delivery boy BUSY
→ commit transaction
→ return updated data
→ refresh/update UI
```

Use an atomic transaction.

Conceptually:

```text
BEGIN TRANSACTION

1. Lock/check delivery boy.
2. Confirm delivery boy is AVAILABLE.
3. Confirm no active delivery already exists.
4. Confirm delivery order is UNASSIGNED.
5. Confirm delivery order belongs to current Shelter.
6. Assign delivery boy.
7. Set delivery order = ASSIGNED.
8. Set delivery boy = BUSY.

COMMIT
```

If any validation fails, roll back the operation.

Do not leave:

```text
delivery order = assigned
delivery boy = available
```

or the reverse.

---

# PHASE 33 — DELIVERY BOY BECOMES BUSY

The moment a delivery order is successfully assigned:

```text
Delivery Order = ASSIGNED
Delivery Boy = BUSY
```

The BUSY state must be persisted in the database.

Do not merely change a JavaScript variable.

Refreshing the browser must continue to show:

```text
BUSY
```

---

# PHASE 34 — BUSY DELIVERY BOY CANNOT RECEIVE ANOTHER ORDER

A delivery boy should have at most one active delivery unless the business rules are explicitly changed later.

The backend must reject a second active assignment.

Example:

```text
Rahul = BUSY
Rahul already assigned to #DLV-102

Shelter tries to assign #DLV-103 to Rahul
        ↓
Backend checks Rahul
        ↓
Reject
```

Show:

> Delivery boy is currently busy with another delivery.

Do not overwrite the existing assignment.

Do not silently reassign the delivery boy.

---

# PHASE 35 — PREVENT DOUBLE ASSIGNMENT / RACE CONDITIONS

Two users or two browser tabs may try to assign the same delivery boy at nearly the same time.

Example:

```text
User A → Rahul
User B → Rahul
```

Only one assignment may succeed.

Use Django/database transaction safety and appropriate locking/constraints.

Required result:

```text
Request A → succeeds
Request B → rejected safely
```

The database must never end up with two active delivery orders for the same delivery boy.

---

# PHASE 36 — ACTIVE DELIVERY DEFINITION

Use one consistent definition of an active delivery.

For example:

```text
ASSIGNED
OUT_FOR_DELIVERY
```

are active.

These are completed/inactive:

```text
DELIVERED
CANCELLED
FAILED
```

The exact statuses should follow the existing project model.

A historical delivered order must not keep a delivery boy BUSY.

---

# PHASE 37 — WHEN THE DELIVERY BOY BECOMES AVAILABLE AGAIN

When the active delivery is completed:

```text
Delivery Order = DELIVERED
```

then:

```text
Delivery Boy = AVAILABLE
```

provided the delivery boy has no other active assignment.

Also allow the existing cancellation workflow to release the delivery boy when appropriate.

Do not blindly set AVAILABLE without checking for other active assignments.

The backend should recalculate:

```text
Does this delivery boy still have any active delivery?
```

If no:

```text
AVAILABLE
```

If yes:

```text
BUSY
```

---

# PHASE 38 — DELIVERY STATUS AND DELIVERY BOY STATUS MUST STAY SYNCHRONIZED

Valid examples:

```text
UNASSIGNED
→ Delivery Boy = AVAILABLE

ASSIGNED
→ Delivery Boy = BUSY

OUT_FOR_DELIVERY
→ Delivery Boy = BUSY

DELIVERED
→ Delivery Boy = AVAILABLE
```

Invalid example:

```text
Delivery Order = DELIVERED
Delivery Boy = BUSY
```

unless that delivery boy has another separate active delivery.

The backend must derive/check this relationship from real records.

---

# PHASE 39 — DELIVERY BOYS DETAILS

Update the existing:

> Delivery Boys Details

section to show real operational availability.Read the referenced KindHeart   [kindheart_shelter_delivery_profile_workflow_fixes_updated.md](file;file:///c%3A/Users/HP/OneDrive/Desktop/PetADOPTION/mdFiles/kindheart_shelter_delivery_profile_workflow_fixes_updated.md)  file.

Find the and implement phase 43

Before coding:

- Inspect the existing implementation.
- Reuse existing models, views, URLs, APIs, templates, and components.
- Do not duplicate existing functionality.
- Do not modify unrelated phases.
- Do not add fake/sample data.

For this phase:

1. Implement the requirements exactly as defined in the [kindheart_shelter_delivery_profile_workflow_fixes_updated.md](file;file:///c%3A/Users/HP/OneDrive/Desktop/PetADOPTION/mdFiles/kindheart_shelter_delivery_profile_workflow_fixes_updated.md)
2. Enforce backend/database rules, not just frontend behavior.
3. Preserve existing functionality.
4. Run relevant Django checks/tests.
5. Fix errors caused by this phase.

Do not proceed to the next phase automatically.

At the end, report only:

- Phase completed
- Files changed
- Migration created, if any
- Tests/checks passed
- Remaining issue, if any

Example:

```text
Delivery Boys

---------------------------------------------------------------
Name       Phone        Status        Current Delivery
---------------------------------------------------------------
Rahul      98xxxxxx     AVAILABLE     -
Suresh     97xxxxxx     BUSY          #DLV-102
Arun       96xxxxxx     INACTIVE      -
---------------------------------------------------------------
```

Use database-backed values only.

When BUSY, show the active delivery reference where appropriate.

Do not show fake people or fake statuses.

---

# PHASE 40 — DELIVERY OUTGOING

Use:

> Delivery Outgoing

for the dispatch/active delivery section.

It should show real records:

```text
Order
Pet
Customer
Delivery Boy
Status
Scheduled Date
Destination
```

Example:

```text
#DLV-102 | Bruno | Murali | Suresh | OUT FOR DELIVERY
```

Do not add fake GPS/telemetry values.

Do not restore the old:

> Live Shipments & GPS Telematics

wording.

---

# PHASE 41 — WHAT HAPPENS WHEN THE CUSTOMER ADOPTS A PET?

Implement this complete logic:

```text
1. Customer submits adoption request.
2. Shelter/Admin processes the request.
3. Adoption becomes APPROVED / READY FOR HANDOVER.
4. Backend determines whether delivery is required.
5. If delivery is required, create a Delivery Order.
6. Delivery Order starts as UNASSIGNED.
7. Shelter sees the order in Delivery Outgoing.
8. Shelter opens Assign Delivery.
9. Backend returns delivery boys belonging to that Shelter.
10. UI shows AVAILABLE delivery boys as selectable.
11. Shelter selects one.
12. Backend re-checks availability and ownership.
13. Backend atomically assigns the delivery boy.
14. Delivery Order becomes ASSIGNED.
15. Delivery Boy becomes BUSY.
16. Delivery Boy starts delivery.
17. Delivery Order becomes OUT_FOR_DELIVERY.
18. Delivery is completed.
19. Delivery Order becomes DELIVERED.
20. Delivery Boy becomes AVAILABLE if no other active delivery exists.
21. Adoption/handover moves to the appropriate completed state.
22. Shelter and customer views update from database state.
```

Do not skip the database steps.

---

# PHASE 42 — WHAT IF ALL DELIVERY BOYS ARE BUSY?

Do NOT block or cancel the adoption.

Example:

```text
Approved adoption
↓
Delivery Order = UNASSIGNED
↓
Rahul = BUSY
Suresh = BUSY
```

Show:

> No delivery boys are currently available.

Keep the order in the unassigned queue.

Do not assign a BUSY delivery boy.

Do not create fake availability.

When a delivery boy becomes AVAILABLE, the Shelter can assign the waiting order.

---

# PHASE 43 — WHAT IF THERE ARE NO DELIVERY BOYS?

The approved adoption should still exist.

The delivery order, when delivery is required, remains:

```text
UNASSIGNED
```

Show a clear empty/blocked state:

> No delivery boys are registered for this shelter yet.

Do not create fake delivery personnel.

---

# PHASE 44 — DELIVERY BOY REGISTRATION AND AVAILABILITY

After an eligible Shelter registers a new delivery boy:

```text
Register Delivery Boy
→ backend saves record
→ database saves record
→ default operational status = AVAILABLE
→ Delivery Boys Details shows the new person
```

Do not require the Shelter to manually select its own shelter.

The backend must derive the current Shelter from authentication/context.

Do not allow the browser to assign another Shelter.

---

# PHASE 45 — DELIVERY ASSIGNMENT VALIDATION

Before assigning, the backend must verify:

### Adoption

- Exists.
- Approved/ready for handover.
- Belongs to the current Shelter.

### Delivery Order

- Exists.
- Belongs to the current Shelter.
- Requires delivery.
- Is currently UNASSIGNED.
- Has no active delivery boy.

### Delivery Boy

- Exists.
- Belongs to the current Shelter.
- Is active.
- Is AVAILABLE.
- Has no active delivery.

If any validation fails:

```text
No database changes.
Return an error.
Refresh relevant UI data.
```

---

# PHASE 46 — COMPLETING A DELIVERY

When a delivery boy marks the delivery as completed, or the authorized workflow completes it:

1. Set delivery order to `DELIVERED`.
2. Save completion timestamp.
3. Close the active assignment.
4. Check whether the delivery boy has any other active delivery.
5. If none, set delivery boy to `AVAILABLE`.
6. Update adoption/handover status according to the existing workflow.
7. Update Shelter dashboard data.
8. Update customer/adopter data.
9. Persist all changes.

Use a transaction where related records are changed together.

---

# PHASE 47 — CANCELLATION / FAILURE

If an active delivery is cancelled or fails:

```text
Delivery Order
→ CANCELLED / FAILED
```

Then:

```text
Check active assignments for delivery boy
→ if none: AVAILABLE
```

Do not leave the delivery boy permanently BUSY.

Use the existing business rules for whether the adoption returns to a previous state, requires rescheduling, or requires shelter action.

---

# PHASE 48 — CUSTOMER, SHELTER AND DELIVERY VIEWS

The same database state must appear consistently.

### Customer

Should see:

```text
Adoption Approved
Delivery Assigned
Delivery In Progress
Delivered
```

only when those real states exist.

### Shelter

Should see:

```text
Delivery Order
Assigned Delivery Boy
Delivery Status
```

only when those records exist.

### Delivery Boy

Should see only deliveries actually assigned to them.

Do not display fake progress in any role.

---

# PHASE 49 — DELIVERY BOY ACTIVE DELIVERY LIMIT

Enforce:

```text
1 delivery boy
=
maximum 1 active delivery
```

at the backend level.

Do not depend on:

- disabled buttons
- hidden dropdown options
- frontend state
- manual staff discipline

The database-backed business logic must enforce it.

---

# PHASE 50 — REFRESH / PERSISTENCE TEST

After every important operation:

```text
Assign delivery boy
→ refresh
```

Expected:

```text
Order = ASSIGNED
Delivery Boy = BUSY
```

Then:

```text
Complete delivery
→ refresh
```

Expected:

```text
Order = DELIVERED
Delivery Boy = AVAILABLE
```

No status should revert because the page refreshed.

---

# PHASE 51 — FINAL DELIVERY TEST MATRIX

### Test 1 — Normal assignment

```text
Adoption = APPROVED
Delivery Order = UNASSIGNED
Rahul = AVAILABLE

Assign Rahul

Expected:
Delivery Order = ASSIGNED
Rahul = BUSY
```

### Test 2 — Busy boy

```text
Rahul = BUSY

Try assigning Rahul to another order

Expected:
Rejected
Original order unchanged
Rahul remains BUSY
```

### Test 3 — Completion

```text
Rahul = BUSY
Order = OUT_FOR_DELIVERY

Complete order

Expected:
Order = DELIVERED
Rahul = AVAILABLE
```

### Test 4 — All busy

```text
Rahul = BUSY
Suresh = BUSY
New delivery order created

Expected:
Order = UNASSIGNED
"No delivery boys are currently available."
```

### Test 5 — Cross-shelter assignment

```text
Shelter A
+
Delivery Boy belongs to Shelter B

Expected:
Backend rejects the assignment
```

### Test 6 — Concurrent assignment

```text
Two assignment requests target Rahul simultaneously

Expected:
Only one succeeds
Other fails safely
No duplicate active assignments
```

### Test 7 — Refresh

```text
Assign Rahul
Refresh browser

Expected:
Order remains ASSIGNED
Rahul remains BUSY
```

---

# PHASE 52 — REQUIRED SEARCH BEFORE IMPLEMENTATION

Before adding new logic, search the project for existing:

- Delivery models
- Delivery orders
- Delivery assignments
- Delivery status fields
- Delivery boy models
- Driver/courier models
- `busy`
- `available`
- `assigned_to`
- `delivery_status`
- Shipment models
- Adoption models
- Handover models
- Existing assignment APIs/views
- Existing frontend assignment components

Repair and extend existing implementations whenever possible.

Do NOT create a second parallel delivery-order system.

Do NOT create a second parallel delivery-boy status system.

Do NOT duplicate existing APIs.

---

# FINAL DELIVERY BUSINESS RULE

The business relationship must be:

```text
REAL CUSTOMER ADOPTION
        ↓
ADOPTION APPROVED
        ↓
DELIVERY REQUIRED?
        ↓
YES
        ↓
REAL DELIVERY ORDER
        ↓
UNASSIGNED
        ↓
SHELTER ASSIGNS
        ↓
AVAILABLE DELIVERY BOY
        ↓
DELIVERY BOY = BUSY
        ↓
DELIVERY IN PROGRESS
        ↓
DELIVERED
        ↓
DELIVERY BOY = AVAILABLE
        ↓
ADOPTION / HANDOVER COMPLETED
```

The **database is the source of truth**.

The frontend displays the state.

The backend enforces the rules.

The system must prevent:

- assigning a BUSY delivery boy
- assigning across shelters
- assigning one delivery boy to multiple active deliveries
- fake delivery orders
- fake availability
- frontend-only Busy/Available states
- delivery progress without a real delivery record
