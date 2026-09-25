# KindHeart Shelter Module — Complete Cleanup, Redesign & Backend/Data Audit

## Purpose

Update the existing **KindHeart Shelter Module** without replacing the working application architecture.

This is a combined:

- Shelter dashboard cleanup
- Shelter UI redesign
- Adoption journey improvement
- Delivery fleet restructuring
- Delivery partner CRUD improvement
- Account/data persistence fix
- Database/model consistency audit
- Admin/Shelter delivery visibility improvement
- Regression test

The implementation must use the **existing Django backend, existing database, existing authentication, existing models where appropriate, and existing Shelter module structure**.

Do not build a parallel Shelter module.

---

# 1. Scope

Review and update:

1. Shelter Dashboard
2. Shelter sidebar/navigation
3. Your Adoption Journey
4. Delivery Fleet
5. Delivery Details
6. Delivery Boys / Delivery Personnel
7. Add Delivery Partner
8. Delivery partner profile/details
9. Delivery/adoption status workflow
10. Shelter → Delivery Personnel data ownership
11. Admin visibility of registered delivery personnel
12. Data persistence after refresh/re-login
13. Django models/forms/views/URLs/API/database
14. Django Administrator verification
15. Shelter regression testing

---

# 2. First Step — Audit the Existing Shelter Module

Before changing the UI, inspect the existing implementation.

Trace:

**Shelter UI → JavaScript → Django URL → Django View/API → Form/Serializer → Model → Database**

Identify:

- Existing Shelter dashboard template/component
- Existing sidebar
- Existing KPI cards
- Existing adoption journey
- Existing delivery fleet
- Existing delivery partner form
- Existing delivery data models
- Existing shelter/delivery relationships
- Existing status fields
- Existing database records
- Existing mock/seed/bulk data
- Existing APIs
- Existing Django Admin registrations
- Existing permissions

Do not guess field names.

Use the actual models and database schema as the source of truth.

---

# 3. Remove Bulk/Dummy Dog Data from Shelter Module

The Shelter module currently contains bulk dog records that make the UI look populated with fake/demo data.

Clean the Shelter module.

## Remove

Remove **bulk/demo/seeded dog records** that are clearly being used only as placeholder content.

Also remove duplicated/bulk test records that make the Shelter dashboard or pet management screens look artificially populated.

## Preserve

Do NOT delete legitimate pet records that were actually registered through the application.

Before deletion:

1. Determine whether the records are seed/demo/test data.
2. Verify whether they are referenced by adoption requests, medical records, deliveries, payments, or other real business records.
3. Remove only records that are safely identified as dummy/bulk data.
4. Preserve real records and relational integrity.

## UI result

The Shelter module should look clean and realistic when there are no pets or only a few real pets.

Use proper empty states instead of filling the interface with fake dogs.

Example empty state:

> No pets registered yet.  
> Add your first pet to start the adoption process.

Do not use fabricated counts.

---

# 4. Remove Bulk/Dummy Delivery Partner Data

Apply the same cleanup to Delivery Personnel / Delivery Boys.

Remove only:

- Demo delivery partners
- Seeded bulk personnel
- Placeholder delivery accounts
- Duplicate test records

Preserve legitimate registered delivery personnel.

Use an empty state when no delivery personnel exist.

Example:

> No delivery personnel registered yet.  
> Add a delivery partner to manage pet handovers and deliveries.

---

# 5. Shelter Dashboard — Keep Original Values

Do not replace existing dashboard values with invented values.

Any existing dashboard KPI/value should remain based on its existing database source.

Examples may include:

- Total Pets
- Pending Adoptions
- Approved Adoptions
- Completed Adoptions
- Delivery Orders
- Registered Delivery Personnel

The exact values must come from the current application/database.

### Important

Do not hardcode replacement values.

If the existing database has zero records after cleanup, display the real value:

**0**

not a fake number.

If a card already represents a meaningful metric, preserve its underlying business meaning while improving the layout.

---

# 6. Improve "Your Adoption Journey"

Improve the existing **Your Adoption Journey** section in the Shelter Dashboard.

Do not remove it.

Do not replace the underlying values with fake ones.

The goal is to make the journey:

- Easier to understand
- More visual
- More actionable
- Connected to real adoption records
- Status-driven
- Consistent with delivery/handover progress

## Recommended journey states

### 1. Under Review

The adoption request has been submitted and is waiting for shelter review.

### 2. Approved

The shelter has approved the adoption request.

### 3. Handover / Delivery Scheduled

A delivery partner has been assigned and the handover/delivery is scheduled.

### 4. Out for Delivery

The pet has left the shelter and is currently in the delivery process.

### 5. Adoption Completed

The pet has been successfully handed over to the customer.

## Optional exception states

Support existing business requirements such as:

- Rejected
- Cancelled
- Suspended
- Delivery Failed
- Returned

Do not add statuses to the UI unless the backend can actually store and use them.

---

# 7. Adoption Status Must Be Backend Driven

The status displayed in:

- Adoption requests
- Your Adoption Journey
- Delivery records
- Pet/adoption details

must come from the actual backend state.

Do NOT determine status only through frontend JavaScript.

Use a single consistent status source.

For example:

```text
UNDER_REVIEW
APPROVED
HANDOVER_SCHEDULED
OUT_FOR_DELIVERY
ADOPTION_COMPLETED
REJECTED
CANCELLED
```

Use the project's existing status field if one already exists.

If the existing status field is inadequate, modify the model carefully and create a migration.

---

# 8. Adoption Status Transition Rules

Use controlled state transitions.

Recommended flow:

```text
UNDER_REVIEW
      ↓
APPROVED
      ↓
HANDOVER_SCHEDULED
      ↓
OUT_FOR_DELIVERY
      ↓
ADOPTION_COMPLETED
```

Alternative terminal states:

```text
UNDER_REVIEW → REJECTED
APPROVED → CANCELLED
HANDOVER_SCHEDULED → CANCELLED
OUT_FOR_DELIVERY → DELIVERY_FAILED
```

Do not allow arbitrary jumping between statuses from the UI.

For example:

- An Under Review request should not jump directly to Adoption Completed.
- Adoption Completed should not be changed casually from the normal UI.
- Only authorized roles should perform each transition.

---

# 9. Role Responsibilities for Adoption Workflow

Respect the existing business rule that:

**The partner shelter assigns the delivery partner/courier.**

Suggested responsibility:

### Shelter

Can:

- Review adoption request
- Approve/reject
- Schedule handover
- Assign one of its own delivery personnel
- Update delivery/handover status where permitted
- Mark adoption completed after successful handover

### Delivery Personnel

Can:

- View assigned deliveries
- Update permitted delivery progress
- Mark delivery/handover milestones according to the workflow

### Customer

Can:

- View adoption status
- View delivery/handover progress
- Receive status updates

### Admin

Can:

- Monitor records
- View registered delivery personnel across shelters
- Perform permitted administrative controls
- Audit status history where supported

Do not move shelter-specific operational ownership to Admin.

---

# 10. Remove Sidebar Pills and Anomalies

Clean the Shelter left sidebar.

Remove:

- Unnecessary status pills
- Decorative count pills that do not represent real data
- Duplicate navigation items
- Broken links
- Empty badges
- Stale counters
- UI anomalies
- Inconsistent labels
- Visual artifacts
- Placeholder text

A sidebar item should exist only when it maps to a valid Shelter feature.

## Sidebar requirements

Keep the navigation:

- Clean
- Consistent
- Easy to scan
- Free from unnecessary badges/pills
- Consistent with the Admin navigation design language

Do not show a badge simply because the UI can display one.

If a number is shown, it must be backed by actual backend data and have clear meaning.

---

# 11. Delivery Fleet — Simplify the Structure

Redesign the Shelter **Delivery Fleet** area.

The Delivery Fleet section should contain exactly **two separate tabs**:

## Tab 1 — Delivery Details

This tab contains delivery/adoption handover records.

Show information such as:

- Delivery/Adoption ID
- Pet
- Customer
- Delivery Personnel
- Current Status
- Scheduled Date
- Handover Date if completed
- Location/details if already supported
- Actions appropriate to the Shelter

This is about **delivery jobs**, not personnel management.

---

## Tab 2 — Delivery Boys / Delivery Personnel

This tab contains the Shelter's registered delivery personnel.

Show:

- Photo
- Full Name
- Phone
- Email
- Vehicle Type if available
- Vehicle Number if available
- License/ID information if supported
- Account Status
- Availability
- Date Registered
- Assigned Delivery Count
- Actions

This is about **people**, not live shipments.

---

# 12. Remove These Existing Delivery Fleet Sections Completely

Remove the existing sections:

### "Registered Delivery Personnel & Shelter Affiliation"

Remove this entire section and its related UI/data representation.

The Shelter should not need to view a separate affiliation panel because the delivery personnel list should already be scoped to the current Shelter.

### "Live Shipments & GPS Telematics"

Remove this section and its related UI/data.

Also remove any related mock/live GPS/telematics data that exists solely for this section.

Do not create a fake GPS system.

Do not retain dead dashboard cards or navigation links referring to this feature.

---

# 13. Remove Related Dead Data

When removing the above sections, inspect for data that exists only to support:

- Fake GPS coordinates
- Fake live shipment locations
- Dummy telemetry
- Shipment tracking demo records
- Affiliation dashboard mock data
- Static delivery map markers
- Fake driver-location data

Remove such demo data safely.

Do NOT delete actual delivery records that are required by the business workflow.

Do not remove the underlying delivery model simply because the GPS UI is removed.

---

# 14. Delivery Personnel Ownership Model

This is a critical requirement.

A Shelter should see **only its own delivery personnel**.

A Shelter must NOT see:

- Other shelter names
- Other shelter delivery personnel
- Other shelter affiliation options
- A global shelter dropdown during registration
- Other shelter records through the Shelter UI

## Correct relationship

The delivery personnel record should be associated with the **currently authenticated Shelter**.

Conceptually:

```text
Logged-in Shelter
        ↓
Add Delivery Personnel
        ↓
Backend automatically assigns current Shelter
```

The Shelter should not select the shelter manually.

---

# 15. Remove "Affiliated Shelter" Field from Add Delivery Partner

In the Shelter's **Add Delivery Partner** form:

REMOVE:

- Affiliated Shelter dropdown
- Shelter selector
- List of other shelters
- Any field allowing the Shelter to choose another shelter

The current Shelter should be assigned server-side using the authenticated user's Shelter relationship.

Example backend concept:

```python
delivery_person.shelter = request.user.shelter
delivery_person.save()
```

Use the project's actual model relationships rather than copying this literally.

---

# 16. Shelter Data Isolation

Every Shelter query must be scoped to the current Shelter.

Conceptually:

```text
current_shelter = request.user.shelter

DeliveryPersonnel.objects.filter(
    shelter=current_shelter
)
```

Again, use the actual project's model names.

Apply this to:

- Delivery personnel list
- Delivery personnel search
- Delivery personnel edit
- Delivery personnel details
- Delivery personnel delete/deactivate
- Delivery assignments
- Delivery details
- Shelter dashboard counts

A Shelter must not be able to bypass this by modifying a URL ID or API request.

Backend authorization is mandatory.

---

# 17. Improve "Add Delivery Partner"

Expand the registration form to capture useful delivery personnel information.

## Identity

- Profile Photo
- Full Name
- Date of Birth if the project supports it
- Gender if required by the current domain model
- Government/identity document information if legally appropriate and already supported
- Short bio/notes if useful

Do not collect unnecessary sensitive information merely because it can be collected.

---

## Contact

- Phone Number
- Email
- Alternate Phone if supported
- Address

---

## Delivery/Work Information

- Vehicle Type
- Vehicle Number
- License Number if required by the product
- Availability
- Employment/partner status
- Experience/notes

---

## Account Information

- Username/email depending on existing authentication design
- Initial account status
- Active / Deactivated
- Registration date

Do not duplicate authentication fields unnecessarily.

---

# 18. Delivery Partner Photo

Add a proper profile-photo field.

Requirements:

- Upload image
- Validate file type
- Validate size
- Generate/use safe file storage
- Display thumbnail/profile image in list
- Display larger image in detail view
- Show placeholder avatar when no image exists

The photo must be stored persistently in the configured Django media storage.

Do not store only a temporary browser preview.

---

# 19. Delivery Partner Detail Drawer/Page

Clicking a Delivery Personnel record should show a complete profile.

Display:

### Profile

- Photo
- Full name
- Contact information
- Account status

### Work

- Current Shelter
- Vehicle details
- Availability
- Registration date
- Delivery count

### Activity

- Recent assigned deliveries
- Current delivery status
- Completed deliveries
- Cancelled/failed deliveries if supported

Do not show another Shelter's information to a Shelter user.

---

# 20. Delivery Personnel Account State

Use a proper state model.

At minimum:

```text
ACTIVE
DEACTIVATED
```

Where the application already supports approval/verification, use:

```text
UNDER_REVIEW
APPROVED
DEACTIVATED
```

Do not mix adoption status with delivery-person account status.

These are two different state machines.

---

# 21. Separate Status Types

Do not use one generic `status` field for unrelated concepts if the model architecture does not support that safely.

Maintain conceptual separation:

## Adoption Status

```text
UNDER_REVIEW
APPROVED
HANDOVER_SCHEDULED
OUT_FOR_DELIVERY
ADOPTION_COMPLETED
REJECTED
CANCELLED
```

## Delivery Personnel Account Status

```text
UNDER_REVIEW
APPROVED
DEACTIVATED
```

## Delivery Job Status

```text
PENDING
ASSIGNED
SCHEDULED
OUT_FOR_DELIVERY
DELIVERED
FAILED
CANCELLED
```

If the project already has equivalent fields, map the UI to those fields instead of creating duplicate fields.

---

# 22. Registered Delivery Personnel Visible to Shelter

The Shelter must be able to view the delivery personnel registered under that Shelter.

The list must be loaded from the database.

After registration:

1. Submit form.
2. Backend creates record.
3. Shelter list refreshes.
4. New delivery personnel appears.
5. Browser refresh does not remove it.
6. Logout/login does not remove it.

---

# 23. Registered Delivery Personnel Visible to Admin

Admin must be able to see registered delivery personnel across the platform.

Admin view should include:

- Delivery Personnel
- Associated Shelter
- Account Status
- Contact
- Vehicle
- Registration Date
- Delivery count
- Actions

This is different from the Shelter view.

### Shelter

Sees only:

**My Shelter's Delivery Personnel**

### Admin

Sees:

**All Registered Delivery Personnel**

---

# 24. Admin Must See the Correct Shelter Affiliation

The Admin view may display:

- Shelter Name
- Shelter ID if the project uses it

The Shelter view should not display a global list of other shelter names.

This distinction must be enforced at both UI and backend/API level.

---

# 25. Critical Bug — Data Disappears After Refresh

Apply the same persistence fix required in the Admin module.

The following Shelter operations must write to the real database:

- Add pet
- Edit pet
- Add delivery personnel
- Edit delivery personnel
- Deactivate delivery personnel
- Activate delivery personnel
- Adoption status changes
- Delivery details
- Any changed Shelter settings that already exist

Do NOT rely on:

- JavaScript arrays
- Frontend state only
- localStorage
- sessionStorage
- temporary JSON
- mock APIs

for persistent business data.

---

# 26. Persistence Debugging Workflow

For each broken operation:

### Step 1
Find the frontend form/button.

### Step 2
Find the actual HTTP request.

### Step 3
Find the Django URL.

### Step 4
Find the Django view/API.

### Step 5
Find the form/serializer.

### Step 6
Find the Django model.

### Step 7
Confirm `.save()` / `create()` / `update()` behavior.

### Step 8
Confirm the request succeeds.

### Step 9
Confirm the database record exists.

### Step 10
Reload the page.

### Step 11
Confirm the page queries the database again.

### Step 12
Logout/login.

### Step 13
Confirm the data remains.

---

# 27. Search for Frontend-Only Data

Search the Shelter module for:

- Hardcoded arrays
- Seed data
- Demo delivery persons
- Mock drivers
- Fake counts
- Placeholder dogs
- Static adoption statuses
- `localStorage`
- `sessionStorage`
- Fake success responses
- Static JSON data

Replace only the items intended to represent real business data.

Do not remove genuinely static UI configuration.

---

# 28. Database / Model Audit

Inspect:

- User model
- Shelter model
- Delivery personnel model
- Delivery model
- Pet model
- Adoption model/request model
- Status fields
- Foreign keys
- Media/photo fields
- Migrations
- Signals
- Django Admin registrations

Check:

- Shelter → Delivery Personnel relationship
- Shelter → Pet relationship
- Shelter → Adoption relationship
- Adoption → Delivery relationship
- Delivery → Delivery Personnel relationship

Verify all ForeignKeys and `on_delete` behavior.

---

# 29. Field Mapping Audit

Create an implementation matrix for every changed section:

| UI Field | Django Field | Model | DB Column | Source | Persisted |
|---|---|---|---|---|---|
| Delivery Photo | actual photo field | Delivery Personnel | actual column | Database | Yes |
| Full Name | actual name field | Delivery Personnel/User | actual column | Database | Yes |
| Phone | actual phone field | User/Profile | actual column | Database | Yes |
| Vehicle Type | actual field | Delivery Personnel | actual column | Database | Yes |
| Vehicle Number | actual field | Delivery Personnel | actual column | Database | Yes |
| Account Status | actual status field | Delivery Personnel/User | actual column | Database | Yes |
| Shelter | current authenticated Shelter relationship | Delivery Personnel | actual FK column | Backend | Yes |

Do not invent field names.

If a requested UI field does not exist in the backend, document it before implementing a schema change.

---

# 30. Django Migrations

If model changes are required:

1. Update `models.py`.
2. Generate migration.
3. Inspect migration.
4. Apply migration.
5. Verify database schema.
6. Verify Django Admin.
7. Verify application.

Do not modify the database manually unless that is required by the project's established workflow.

---

# 31. Django Administrator Verification

Use Django Administrator as an independent verification layer.

Verify:

### Delivery Personnel

- New personnel record appears.
- Correct Shelter relation exists.
- Photo is stored correctly.
- Status is correct.
- Contact details are correct.
- Vehicle details are correct.

### Adoption

- Adoption records have correct statuses.
- Delivery/handover relationship is correct.

### Shelter

- Shelter relationship exists.
- Only the intended Shelter owns the delivery personnel record.

The frontend and Django Admin should represent the same underlying database data.

---

# 32. Security Test — Shelter Cannot See Another Shelter

Explicitly test:

### Shelter A

Can:

- View Shelter A delivery personnel
- Add personnel to Shelter A
- Edit Shelter A personnel
- Deactivate Shelter A personnel
- View Shelter A deliveries

Cannot:

- View Shelter B personnel
- Add personnel to Shelter B
- Edit Shelter B personnel
- Delete Shelter B personnel
- See Shelter B in an affiliation dropdown
- Access Shelter B delivery data by changing a URL ID

### Admin

Can:

- View Shelter A
- View Shelter B
- View personnel from both
- See their shelter affiliations
- Perform authorized administrative actions

---

# 33. Empty-State Design

After cleaning bulk data, the UI must still look complete.

Do not leave broken tables or empty panels.

Use professional empty states:

### Pets

> No pets registered yet.

### Delivery Personnel

> No delivery personnel registered yet.

### Delivery Details

> No delivery records available.

### Adoption Journey

> No active adoption journeys.

Buttons may include:

- Add Pet
- Add Delivery Partner
- View Adoption Requests

Only show actions that the Shelter can actually perform.

---

# 34. Shelter Dashboard Visual Improvements

Improve the dashboard without destroying the existing product structure.

Use:

- Better spacing
- Clear section hierarchy
- Consistent card proportions
- Clean tables
- Useful status indicators
- Better empty states
- Better responsive behavior
- Clear action placement

Avoid:

- Excessive pills
- Unnecessary badges
- Fake metrics
- Redundant cards
- Decorative maps
- Fake live tracking
- Dense tables
- Random icons
- Inconsistent terminology

---

# 35. Preserve Existing Real Values

For every existing Shelter dashboard metric:

**Preserve the original business meaning and database-backed value.**

Do not:

- Reset real counts
- Replace real counts with examples
- Hardcode a different number
- Delete real adoption records just to clean the UI

Only remove records that are confirmed demo/bulk/test data.

---

# 36. API and Query Audit

For every Shelter endpoint affected by this work, check:

- Authentication
- Role check
- Shelter ownership filter
- Queryset
- Form/serializer
- POST/PUT/PATCH behavior
- DELETE behavior
- Error response
- Empty response
- Pagination
- Search
- Sorting

A frontend filter is not a security control.

---

# 37. Error Handling

Every operation must properly handle:

### Success
Show real success feedback.

### Validation error
Show the relevant field error.

### Unauthorized
Return access denied.

### Forbidden
Prevent access to another Shelter's records.

### Not found
Handle missing records gracefully.

### Server error
Show a useful error message.

Never show:

> Successfully saved

when the database operation failed.

---

# 38. Final Verification Matrix

After implementation, test:

| Feature | Create | Edit | Refresh | Logout/Login | Backend Verified | Django Admin Verified |
|---|---:|---:|---:|---:|---:|---:|
| Pet | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Delivery Personnel | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Delivery Status | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Adoption Status | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Photo Upload | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Do not mark a test as PASS unless it was actually performed.

---

# 39. Shelter Regression Checklist

Verify all existing Shelter functionality after changes:

## Dashboard
- [ ] Loads correctly
- [ ] Original values remain correct
- [ ] Your Adoption Journey works
- [ ] Empty states work

## Sidebar
- [ ] Pills removed
- [ ] Anomalies removed
- [ ] No broken links
- [ ] No duplicate links

## Pets
- [ ] Real pets load
- [ ] Bulk/demo dog data removed
- [ ] Add pet works
- [ ] Edit pet works
- [ ] Data persists after refresh

## Adoption
- [ ] Requests load
- [ ] Under Review works
- [ ] Approved works
- [ ] Handover Scheduled works
- [ ] Out for Delivery works
- [ ] Adoption Completed works
- [ ] Rejected/Cancelled works where supported
- [ ] Journey reflects actual status

## Delivery Fleet
- [ ] Delivery Details tab works
- [ ] Delivery Personnel tab works
- [ ] Removed GPS section stays removed
- [ ] Removed affiliation section stays removed
- [ ] Real delivery data loads

## Delivery Personnel
- [ ] Add works
- [ ] Photo upload works
- [ ] Details save
- [ ] Current Shelter automatically assigned
- [ ] Other shelters are not exposed
- [ ] Edit works
- [ ] Deactivate works
- [ ] Activate works
- [ ] Records persist after refresh
- [ ] Records persist after logout/login

## Security
- [ ] Shelter cannot access another Shelter
- [ ] Admin can view all registered personnel
- [ ] Direct URL/API bypass is blocked

## Backend
- [ ] Django views checked
- [ ] URLs checked
- [ ] Models checked
- [ ] Forms/serializers checked
- [ ] Migrations checked
- [ ] Database checked
- [ ] Django Admin checked

---

# 40. Required Final Audit Report

At the end, generate a factual implementation report.

## A. Issues Found

List the real problems discovered.

## B. Root Causes

Classify each problem:

- UI
- JavaScript
- API
- Django View
- Model
- Database
- Migration
- Permission
- Query/filter
- Authentication
- Media/file storage

## C. Files Changed

List actual files modified.

## D. Database Changes

List:

- Models changed
- Migrations created
- Fields added/changed
- Relationships changed
- Data cleanup performed

## E. Data Cleanup

Explicitly report:

- Demo/bulk dog records removed
- Demo/bulk delivery personnel removed
- GPS/telematics demo data removed
- Real records preserved

Do not report guessed counts.

## F. Verification

For every major feature:

**PASS / FAIL / NOT VERIFIED**

Only use PASS after actual testing.

## G. Remaining Issues

List anything unresolved.

---

# 41. Definition of Done

The Shelter module is complete only when all of the following are true:

### Dashboard

- Clean dashboard
- Original real values preserved
- Improved Your Adoption Journey
- No fake metrics

### Sidebar

- Pills removed
- Anomalies removed
- No dead links

### Pets

- Demo/bulk dog data cleaned
- Real pets preserved
- Empty state works

### Delivery Fleet

Only two tabs remain:

1. **Delivery Details**
2. **Delivery Boys / Delivery Personnel**

The following are completely removed:

- **Registered Delivery Personnel & Shelter Affiliation**
- **Live Shipments & GPS Telematics**
- Their UI references
- Their dead/mock data
- Their dead navigation links

### Delivery Personnel

- Current Shelter is automatically assigned
- Other Shelter names are not exposed
- Photo supported
- More delivery partner details supported
- Profile/detail view supported
- Account status supported
- CRUD persists

### Adoption Workflow

A real backend-driven workflow exists:

```text
UNDER_REVIEW
    ↓
APPROVED
    ↓
HANDOVER_SCHEDULED
    ↓
OUT_FOR_DELIVERY
    ↓
ADOPTION_COMPLETED
```

with supported exception states as required by the existing project.

### Data Persistence

Data remains after:

- Refresh
- Browser reopen
- Logout/login

### Visibility

- Shelter sees its own delivery personnel
- Admin sees registered delivery personnel across shelters
- No cross-shelter data leakage

### Backend

- Django verified
- Database verified
- Migrations verified
- Django Administrator verified
- Frontend/backend fields match
- Authorization verified

### Final Rule

Do not stop at visual completion.

The complete chain must work:

**Shelter UI → Backend/API → Django Model → Database → Django Admin → Refresh/Re-login → Shelter UI**

# 42. Admin ↔ Shelter Connection / Onboarding Architecture

The Admin must be the authority that connects a Shelter to the KindHeart platform.

The Shelter should **not choose, attach, or switch its own platform affiliation**.

## Recommended relationship

Use this relationship:

```text
ADMIN
  │
  ├── Creates / Reviews Shelter
  │
  ├── Approves Shelter
  │
  └── Activates Shelter Account
          │
          ▼
       SHELTER
          │
          ├── Registers Pets
          ├── Receives Adoption Requests
          ├── Registers Delivery Personnel
          └── Assigns Its Delivery Personnel
```

The important ownership chain is:

```text
Shelter Account
      ↓
Shelter Organization
      ↓
Pets / Adoption Requests / Delivery Personnel / Deliveries
```

---

# 43. Recommended Shelter Registration Workflow

Use a controlled workflow:

```text
Shelter Registration
        ↓
PENDING
        ↓
ADMIN REVIEW
        ↓
APPROVED
        ↓
ACTIVE
```

Possible exception states:

```text
PENDING
  ├── UNDER_REVIEW
  ├── APPROVED
  └── REJECTED

APPROVED
  └── ACTIVE

ACTIVE
  └── SUSPENDED / DEACTIVATED
```

Do not mix Shelter account status with adoption status or delivery-person status.

---

# 44. Who Creates the Shelter?

Support the project's existing registration model, but enforce Admin approval.

## Option A — Recommended

Shelter registers publicly:

```text
Shelter Registration
        ↓
User/Shelter account created
        ↓
Status = PENDING
        ↓
Admin sees "Pending Shelter"
        ↓
Admin reviews
        ↓
Admin approves
        ↓
Shelter becomes ACTIVE
```

This avoids an Admin manually entering every Shelter account while still giving Admin control.

## Option B

Admin creates a Shelter directly from:

**Admin → Shelters → Add Shelter**

Use this for manually onboarded/verified partner shelters.

The system should support the existing registration flow rather than creating duplicate account systems.

---

# 45. Admin Shelter Approval Screen

The Admin Shelter Management section should contain an approval workflow.

Recommended tabs/filters:

- All
- Pending
- Under Review
- Approved / Active
- Rejected
- Suspended / Deactivated

Each Shelter row should show:

- Shelter name
- Contact person
- Email
- Phone
- Location
- Registration date
- Status
- Number of pets
- Number of delivery personnel
- Actions

Actions may include:

- View
- Review
- Approve
- Reject
- Edit
- Deactivate
- Reactivate
- Delete

---

# 46. Shelter Verification

When Admin selects a pending Shelter, show a detailed review page/drawer.

Possible sections:

### Organization

- Shelter name
- Registration/organization identifier if supported
- Description
- Address
- Contact information
- Website/social links if supported

### Primary Contact

- Full name
- Email
- Phone

### Verification

- Submitted date
- Current status
- Reviewed by
- Reviewed date
- Admin notes
- Rejection reason where applicable

### Operations

- Registered pets
- Adoption activity
- Delivery personnel
- Completed adoptions

Do not create fake verification documents or fields that the database does not support.

---

# 47. Shelter Account Connection Must Be Backend-Driven

When Admin approves a Shelter, the backend should establish the correct relationship:

```text
User Account
      ↓
Shelter Profile
      ↓
Shelter Organization
```

Use the project's actual model architecture.

Do not rely on:

- Frontend-selected IDs
- localStorage
- hidden form fields
- manually typed Shelter IDs
- URL parameters alone

The authenticated user must resolve to its associated Shelter on the backend.

Conceptually:

```python
request.user.shelter
```

or the equivalent relationship already used by the project.

---

# 48. Admin Must Not Need to Manually Reassign Every Child Record

Once a Shelter is approved and connected:

### Pet registration

```text
Logged-in Shelter
      ↓
Add Pet
      ↓
Backend automatically sets Pet.shelter
```

### Delivery Personnel registration

```text
Logged-in Shelter
      ↓
Add Delivery Personnel
      ↓
Backend automatically sets DeliveryPersonnel.shelter
```

### Adoption request

The adoption request should identify the pet and therefore resolve the responsible Shelter through the backend relationship.

### Delivery assignment

```text
Shelter
   ↓
Select one of its own Delivery Personnel
   ↓
Create/update Delivery assignment
```

The Shelter does not select another Shelter.

---

# 49. Admin Visibility vs Shelter Visibility

The two roles must have different data scopes.

## Admin

Admin is platform-level.

Can see:

```text
All Shelters
All registered Delivery Personnel
All Pets
All Adoption Requests
All relevant platform records
```

Subject to the application's Admin permissions.

## Shelter

Shelter is tenant/organization-level.

Can see:

```text
Own Shelter
Own Pets
Own Adoption Requests
Own Delivery Personnel
Own Delivery Details
Own Shelter-related operational data
```

Must not see:

```text
Other Shelters
Other Shelter's Pets
Other Shelter's Delivery Personnel
Other Shelter's Deliveries
Other Shelter's operational data
```

This distinction must be enforced in the **Django backend**, not only in the UI.

---

# 50. Do Not Use a Global Shelter Dropdown in Shelter Module

Remove any Shelter selector from Shelter-side forms where the current Shelter is already known.

Examples:

### Add Pet

Do not show:

```text
Select Shelter
```

The backend should determine the Shelter from the authenticated user.

### Add Delivery Personnel

Do not show:

```text
Affiliated Shelter
```

The backend should determine the Shelter.

### Delivery Assignment

Do not show delivery personnel belonging to other Shelters.

Only show:

```text
Current Shelter → Available Delivery Personnel
```

---

# 51. Admin Shelter Deactivation

Admin should be able to deactivate a Shelter account without immediately destroying historical business data.

Recommended:

```text
ACTIVE
   ↓
DEACTIVATED
```

When deactivated:

- Shelter cannot perform normal authenticated operations.
- Existing pets/adoptions/delivery history remains available to authorized Admin.
- Historical records are preserved.
- Existing active workflows should be handled according to the project's business rules.
- The Shelter cannot create new operational records unless reactivated.

Use the existing `is_active` or appropriate account-status architecture where possible.

Do not create duplicate status fields unnecessarily.

---

# 52. Admin Shelter Deletion

Deletion should be separate from deactivation.

Before hard deletion, inspect:

- Pets
- Adoption requests
- Deliveries
- Delivery personnel
- Payments
- Messages
- Reviews
- Notifications
- Audit logs
- Foreign-key relationships

Prefer safe archival/soft-deletion where the application's existing architecture requires historical preservation.

Do not delete a Shelter simply to remove it from the active list if that would destroy historical adoption or delivery records.

---

# 53. Shelter Connection to Delivery Personnel

The relationship should be:

```text
Shelter A
 ├── Delivery Person A1
 ├── Delivery Person A2
 └── Delivery Person A3

Shelter B
 ├── Delivery Person B1
 └── Delivery Person B2
```

A Shelter can manage only its own personnel.

Admin can view the complete platform relationship:

```text
Shelter A → A1, A2, A3
Shelter B → B1, B2
```

This makes the existing **Shelter Affiliation** panel unnecessary in the Shelter UI because affiliation is already established by the authenticated Shelter relationship.

---

# 54. Shelter Approval and Delivery Personnel Approval Are Separate

Do not confuse:

### Shelter status

```text
PENDING
UNDER_REVIEW
APPROVED
ACTIVE
REJECTED
DEACTIVATED
```

with:

### Delivery personnel status

```text
UNDER_REVIEW
APPROVED
ACTIVE
DEACTIVATED
```

and:

### Adoption status

```text
UNDER_REVIEW
APPROVED
HANDOVER_SCHEDULED
OUT_FOR_DELIVERY
ADOPTION_COMPLETED
REJECTED
CANCELLED
```

and:

### Delivery job status

```text
PENDING
ASSIGNED
SCHEDULED
OUT_FOR_DELIVERY
DELIVERED
FAILED
CANCELLED
```

These states represent different business objects and should not be collapsed into a single generic status.

---

# 55. Recommended Admin → Shelter Lifecycle

Implement/document the complete lifecycle:

```text
1. Shelter registers
        ↓
2. Shelter account = PENDING
        ↓
3. Admin reviews registration
        ↓
4. Admin verifies information
        ↓
5. Admin APPROVES
        ↓
6. Shelter account = ACTIVE
        ↓
7. Shelter logs in
        ↓
8. Shelter manages own pets
        ↓
9. Shelter manages own delivery personnel
        ↓
10. Shelter processes adoption requests
        ↓
11. Shelter assigns own delivery personnel
        ↓
12. Adoption completed
```

### Rejection path

```text
PENDING / UNDER_REVIEW
        ↓
REJECTED
        ↓
Shelter cannot operate as an active Shelter
```

### Suspension path

```text
ACTIVE
   ↓
DEACTIVATED / SUSPENDED
   ↓
Operations blocked
   ↓
History preserved
```

---

# 56. Required Admin ↔ Shelter Tests

Test the relationship explicitly.

## Test 1 — New Shelter

- Register Shelter A
- Confirm database record
- Confirm status is Pending
- Confirm Admin can see Shelter A
- Confirm Shelter A cannot perform restricted operations before approval if the product requires approval
- Approve Shelter A
- Confirm Shelter A can log in/operate
- Confirm relationship persists after refresh/re-login

## Test 2 — Shelter Data Ownership

- Create Pet A under Shelter A
- Create Delivery Person A under Shelter A
- Log in as Shelter A
- Confirm both appear

Create Shelter B.

- Log in as Shelter B
- Confirm Shelter A data is not visible

## Test 3 — Delivery Personnel

- Add Delivery Person A from Shelter A
- Do not select a Shelter manually
- Verify backend automatically assigns Shelter A
- Confirm Admin sees:
  `Delivery Person A → Shelter A`
- Confirm Shelter B cannot see Delivery Person A

## Test 4 — URL/API Tampering

Attempt to access a Shelter A record while authenticated as Shelter B.

Expected:

```text
403 Forbidden
```

or an appropriate not-found response according to the project's security design.

The record must not be exposed.

## Test 5 — Deactivation

- Admin deactivates Shelter A
- Refresh
- Shelter A remains deactivated
- Shelter A cannot perform protected operations
- Historical records remain available to authorized Admin

## Test 6 — Reactivation

- Admin reactivates Shelter A
- Shelter can resume normal operations
- Existing relationships remain intact

---

# 57. Admin/Shelter Data Model Target

Use the closest existing architecture to this conceptual relationship:

```text
User
 │
 ├── role = ADMIN
 │
 └── role = SHELTER
          │
          ▼
       Shelter
          │
          ├── Pets
          │
          ├── Adoption Requests
          │
          ├── Delivery Personnel
          │       │
          │       └── Deliveries
          │
          └── Shelter-specific records
```

If the project uses profile models instead of direct foreign keys, retain that architecture.

Do not duplicate Shelter information in every model unless necessary.

Prefer relationships that allow the backend to determine ownership reliably.

---

# 58. Required Final Admin/Shelter Ownership Audit

Antigravity must verify:

- [ ] Every Shelter user resolves to exactly the intended Shelter
- [ ] Admin can see all valid Shelters
- [ ] Shelter cannot choose another Shelter
- [ ] Shelter cannot change its ownership through a frontend field
- [ ] Shelter cannot change ownership through a direct API request
- [ ] Pet records inherit the correct Shelter
- [ ] Delivery personnel inherit the correct Shelter
- [ ] Delivery records resolve to the correct Shelter
- [ ] Adoption records resolve to the correct Shelter through the pet/adoption relationship
- [ ] Admin can view cross-Shelter delivery personnel
- [ ] Shelter sees only its own delivery personnel
- [ ] Deactivation persists
- [ ] Approval status persists
- [ ] Relationships survive refresh/re-login
- [ ] Django Admin shows the same relationships as the application

# 59. Final Architecture Rule

The source of truth for organizational ownership must be the Django backend/database.

The frontend should never decide which Shelter owns a record.

The correct pattern is:

```text
Authenticated User
      ↓
Authenticated Role
      ↓
Authenticated Shelter
      ↓
Owned Business Records
```

For Admin:

```text
Authenticated Admin
      ↓
Platform-level access
      ↓
All authorized Shelters / records
```

For Shelter:

```text
Authenticated Shelter User
      ↓
Resolve current Shelter on server
      ↓
Filter every query by that Shelter
      ↓
Create child records using that Shelter
```

This architecture should be applied consistently to pets, adoptions, delivery personnel, deliveries, and all future Shelter-owned records.

# 55. Mandatory Backend + Database Integration

This implementation must be **fully connected to the real Django backend and configured database**.

Do not treat a successful UI action as completion. Every Shelter operation must be traced and verified through:

```text
Shelter UI
   ↓
Frontend form / fetch / AJAX
   ↓
Django URL
   ↓
Django View / API
   ↓
Form / Serializer / Validation
   ↓
Django Model
   ↓
Configured Database
   ↓
Django Query
   ↓
Shelter UI
```

## 55.1 Single Source of Truth

For persistent business data, the source of truth must be the Django database.

Do not use these as the primary source of truth:

- hardcoded arrays
- mock JSON
- frontend-only state
- `localStorage`
- `sessionStorage`
- static demo objects
- fake API responses
- generated values in JavaScript

Frontend state may be used for temporary UI state, but saved business data must come from the backend.

---

## 55.2 Database Connection Verification

Before implementation is considered complete, inspect the actual Django database configuration and confirm that the running application and Django Administrator use the same database/environment.

Verify:

- `DATABASES` configuration
- database engine
- database name/path/host where applicable
- credentials/environment variables where applicable
- migration state
- database connection from Django
- tables for Shelter, User, Pet, Adoption, Delivery Personnel, Delivery and related records

Do not assume that the development server and Django Administrator are connected to the same database.

Explicitly verify this.

---

## 55.3 Admin → Shelter Connection Must Persist in Database

When Admin approves a Shelter, the relationship must be stored in the real database.

Verify:

```text
Admin approves Shelter A
        ↓
Django backend updates Shelter/account state
        ↓
Database stores the approved/active state
        ↓
Refresh
        ↓
Shelter A remains approved/active
        ↓
Logout/Login
        ↓
Shelter A remains connected
```

The approval state must not exist only in the frontend.

---

## 55.4 Shelter Ownership Must Persist in Database

When a Shelter creates a pet or Delivery Personnel record, the backend must automatically associate the new record with the authenticated Shelter.

Conceptually:

```text
Authenticated User
       ↓
Current Shelter
       ↓
Create Pet / Delivery Personnel / related record
       ↓
Database stores Shelter ForeignKey/relationship
```

Do not accept an arbitrary Shelter ID from the Shelter-side browser as the authoritative owner.

The server must determine the current Shelter from authenticated user context.

---

## 55.5 Delivery Personnel Database Flow

The complete flow must work as follows:

```text
Shelter logs in
      ↓
Open Delivery Personnel
      ↓
Add Delivery Partner
      ↓
Submit form
      ↓
Django validates data
      ↓
Django automatically identifies current Shelter
      ↓
Delivery Personnel record is created
      ↓
Shelter relationship is saved
      ↓
Photo/file is persisted in configured media storage
      ↓
Database record exists
      ↓
Frontend reloads from backend
```

Do not mark the operation successful until the database save succeeds.

---

## 55.6 Shelter Queries Must Be Backend-Scoped

All Shelter-side querysets must be restricted to the authenticated Shelter.

Conceptually:

```python
DeliveryPersonnel.objects.filter(shelter=current_shelter)
```

and similarly for relevant:

- Pets
- Adoption Requests
- Deliveries
- Delivery Personnel
- Shelter-specific records

Use the project's real model relationships and field names.

A frontend filter is not sufficient.

---

## 55.7 Admin Queries Must Be Platform-Scoped

Admin is allowed to inspect platform-wide records according to the application's Admin permissions.

Admin queries may therefore load:

- all approved/pending Shelters
- all registered Delivery Personnel
- all relevant deliveries
- all adoption records
- all pets where Admin functionality requires them

The Admin list must use the same database as the Shelter module.

---

## 55.8 Field-to-Database Verification

For every changed Shelter feature, document the real mapping:

```text
UI field
   ↓
Request field
   ↓
Django form/serializer field
   ↓
Django model field
   ↓
Database column
```

At minimum verify these areas:

### Shelter

- Shelter name
- Contact person
- Email
- Phone
- Address/location
- Approval status
- Account status
- Registration date

### Delivery Personnel

- Full name
- Photo
- Phone
- Email
- Vehicle information
- Availability
- Account status
- Shelter relationship
- Registration date

### Adoption

- Adoption request
- Pet relationship
- Shelter relationship through the correct model relationship
- Adoption status
- Customer relationship
- Delivery/handover relationship where supported

### Delivery

- Delivery/adoption ID
- Pet
- Customer
- Delivery Personnel
- Delivery status
- Scheduled date
- Completion/handover date where supported

Never invent database field names. Read the existing Django models first.

---

## 55.9 CRUD Persistence Tests

Every changed CRUD operation must pass all four layers:

### Create

1. Submit UI form.
2. Confirm Django request succeeds.
3. Confirm database row exists.
4. Refresh page.
5. Confirm record still appears.
6. Log out/in.
7. Confirm record still appears.

### Update

1. Edit in UI.
2. Confirm backend update succeeds.
3. Confirm database value changed.
4. Refresh.
5. Confirm changed value remains.
6. Log out/in.
7. Confirm changed value remains.

### Deactivate

1. Deactivate through UI.
2. Confirm backend updates status.
3. Confirm database status changed.
4. Refresh.
5. Confirm status remains inactive.
6. Confirm protected functionality is blocked as designed.

### Delete

1. Confirm deletion action.
2. Confirm backend handles deletion/archival.
3. Confirm expected database state.
4. Refresh.
5. Confirm record is no longer shown according to the deletion policy.
6. Confirm related historical records are not unintentionally destroyed.

---

## 55.10 Django Administrator Cross-Check

For each major database-backed operation, independently verify the result in Django Administrator.

Example:

```text
Shelter UI creates Delivery Personnel
          ↓
Database row created
          ↓
Open Django Administrator
          ↓
Delivery Personnel record is visible
          ↓
Correct Shelter relationship is visible
          ↓
Correct status/photo/contact fields are visible
```

Likewise:

- Admin approves Shelter → verify in Django Admin
- Admin deactivates Shelter → verify in Django Admin
- Shelter adds Delivery Personnel → verify in Django Admin
- Shelter updates Delivery Personnel → verify in Django Admin
- Adoption status changes → verify in Django Admin
- Delivery assignment changes → verify in Django Admin

---

## 55.11 Migration Verification

If this task introduces or changes database fields/relationships:

1. Modify Django model.
2. Generate migration.
3. Inspect migration content.
4. Apply migration.
5. Confirm migration is recorded as applied.
6. Confirm database columns/constraints exist.
7. Confirm Django Admin can read/write the fields.
8. Confirm application can read/write the fields.

Do not mark the task complete if the model expects a field that is missing from the actual database.

---

## 55.12 API Security Verification

Test the backend directly, not only through the visible UI.

Attempt to:

- create Delivery Personnel for another Shelter
- edit another Shelter's Delivery Personnel
- read another Shelter's Delivery Personnel
- delete another Shelter's Delivery Personnel
- change another Shelter's Pet
- change another Shelter's Adoption
- change Shelter ownership using a manipulated ID

Expected result:

```text
Denied / Forbidden / Not Found
```

according to the project's established security design.

The backend must reject unauthorized ownership changes even if the browser request is manually modified.

---

## 55.13 Media/File Persistence

For Delivery Personnel photos:

- Use Django's configured media/file storage.
- Save the actual file reference in the database.
- Verify the stored file survives refresh.
- Verify the image remains after logout/login.
- Verify the image is still available from the detail page/list.
- Do not rely on a temporary browser preview.

If the project uses local media storage, ensure the configured media path is correct. If it uses another storage backend, use the existing project configuration.

---

## 55.14 No Fake Success State

Every frontend success message must correspond to a confirmed backend success response.

Bad pattern:

```text
User clicks Save
↓
Frontend immediately displays "Saved"
↓
Backend fails
```

Required pattern:

```text
User clicks Save
↓
Request sent to Django
↓
Django validates and writes database
↓
Successful response
↓
Frontend displays "Saved"
↓
Frontend reloads/updates from backend data
```

Handle validation errors, permission errors and server errors explicitly.

---

## 55.15 Final End-to-End Acceptance Test

The final test must demonstrate the complete connection:

```text
ADMIN
  ↓
approves Shelter A
  ↓
DATABASE stores Shelter A as approved/active
  ↓
SHELTER A logs in
  ↓
SHELTER A adds Delivery Personnel A1
  ↓
DATABASE stores A1 → Shelter A
  ↓
SHELTER A refreshes
  ↓
A1 remains visible
  ↓
ADMIN opens Delivery Personnel
  ↓
A1 is visible with Shelter A affiliation
  ↓
SHELTER B logs in
  ↓
A1 is NOT visible
  ↓
SHELTER A assigns A1 to an allowed delivery workflow
  ↓
DATABASE stores the relationship
  ↓
Adoption/delivery status changes
  ↓
Database stores the new state
  ↓
Refresh / logout / login
  ↓
State remains correct
  ↓
DJANGO ADMIN
  ↓
All corresponding records and relationships match
```

This end-to-end flow is a mandatory **definition of done**.

If any step is frontend-only, points to a different database, loses data after refresh, or exposes another Shelter's records, the implementation is **not complete**.
