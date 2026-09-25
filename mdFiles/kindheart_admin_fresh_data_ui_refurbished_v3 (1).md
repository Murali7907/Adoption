# KindHeart — Admin Fresh Data + Shelter/Delivery Workflow + Dashboard/UI Refurbishment

## Goal

Update the existing KindHeart Django project using the current architecture. Make the Admin area consistent with the real business workflow and remove the old/sample dashboard content.

Main Admin page:

`http://localhost:8000/users/profile/?role=admin`

Do not rebuild unrelated parts of the project.

---

# 1. RESET THE EXISTING ADMIN DATA

Clear the old/demo data currently shown in these Admin sections so fresh data can be entered:

- `#dashboard`
- `#adoption-orders`
- `#pets`
- `#shelters`
- `#customers`
- `#delivery-logistics`
- `#payments`
- `#users-permissions`
- `#system-settings`

Also clear stale records that directly feed those sections, including old role profiles, pet records, adoption orders, delivery assignments, payment records, and demo relationships.

Preserve:

- application code
- migrations
- static files
- templates
- configuration
- the existing Admin account needed for access

Do not blindly destroy migration history or lock the Admin out.

After reset, the sections must show genuine empty/zero states from the database, not hard-coded fake zeros.

---

# 2. PUBLIC REGISTRATION — CUSTOMER ONLY

Remove these roles from the public registration page:

- Shelter
- Delivery

Customer remains the public self-registration role.

Also enforce this in the backend so direct requests cannot create `shelter` or `delivery` accounts through the public registration endpoint.

---

# 3. SHELTER ACCOUNT CREATION — ADMIN ONLY

Shelters are created from the existing Admin Shelter section:

`http://localhost:8000/users/profile/?role=admin#shelters`

Admin creates a Shelter with practical details such as:

- Shelter name
- Contact person
- Email
- Phone
- Address/location
- Organization information where applicable
- Login email
- Initial password

Create/link the existing User, UserProfile, and Shelter records and assign `role = shelter`.

The new Shelter must immediately appear in Admin → Shelters.

Do not use a Shelter self-registration request queue.

---

# 4. SHELTER LOGIN + SHELTER OWNERSHIP

The Admin-created Shelter logs in through the existing login page and goes to the Shelter Dashboard.

The Shelter controls its own operational data only.

The Shelter should manage:

- its profile
- its own documents
- its pets
- its adoption/handover records
- its Delivery staff
- its Delivery staff documents

---

# 5. PET REGISTRATION BELONGS TO SHELTERS

Pet registration/listing is a Shelter responsibility.

A Shelter should be able to:

- Add Pet
- Edit its own Pet
- Update availability/details
- Manage pet photos/details/health information already supported by the project

Admin should not be the normal operator for adding pets for shelters.

Keep the Admin Pets section primarily for platform-wide viewing/management, oversight, removal/suspension where appropriate, and reporting.

Do not create duplicate pet-registration workflows.

---

# 6. SHELTER DOCUMENTS — SHELTER UPLOADS, ADMIN VIEWS

The Shelter uploads its own supporting documents after login.

Examples:

- organization/registration proof
- address proof
- authorized-person proof
- applicable license/reference
- additional supporting documents

Keep useful document metadata such as type, file, uploader, upload time, reference number, and expiry when relevant.

Admin can view/open/download appropriate documents from the Shelter profile.

Admin does not need to upload the Shelter's documents.

---

# 7. REMOVE VERIFICATION CENTER COMPLETELY

Remove the entire Admin section:

`http://localhost:8000/users/profile/?role=admin#verification-center`

Remove:

- navigation entry
- page/content
- cards/tables
- verification queue
- verification-only buttons
- dead links/reference code

Do not replace it with another Verification Center.

Shelter documents are records/proofs only. No separate shelter verification workflow is required.

---

# 8. REMOVE AUDIT FROM THE SHELTER SECTION

From:

`http://localhost:8000/users/profile/?role=admin#shelters`

Remove the visible Audit column/action/widget from the Shelter management UI.

Keep a backend audit/history system only if it is already useful elsewhere for meaningful accountability. Do not show it as a primary Shelter Board field.

---

# 9. SHELTER CUSTOMER/USER PROFILE VIEW

When Admin clicks **View** for a user/customer, the profile should show the user's relevant account information such as:

- Name
- Username/email/phone used for login
- Role
- Account status
- Registration/profile details

### Password security rule

Never display the user's actual password or plaintext password in the Admin UI.

Passwords must remain securely hashed.

If Admin needs to help a user who forgot a password, provide a safe **Reset Password / Set Temporary Password** action rather than exposing the existing password.

---

# 10. DELIVERY — CREATED BY SHELTER, NOT ADMIN

Delivery personnel are created by Shelters.

Remove the Admin **Add Delivery Partner** / **Add Delivery** action from:

`#delivery-logistics`

Admin must not create delivery partners from the Admin Delivery section.

The Shelter creates multiple delivery staff from its own Shelter Dashboard.

The Shelter provides:

- Delivery person's name
- Phone/email
- relevant contact/address details
- license number/type/expiry where applicable
- vehicle details where applicable
- login email
- initial password

Each Delivery account must be linked to the Shelter that created it.

---

# 11. ADMIN DELIVERY LOGISTICS — SHOW WHERE EACH DELIVERY PERSON COMES FROM

The Admin Delivery & Logistics section should be a monitoring/management view of Delivery staff created by Shelters.

For each Delivery person, show useful fields such as:

- Delivery person's name
- Login email/phone where appropriate
- Status
- Assigned/current delivery information where available
- **Shelter** — the Shelter they belong to / were created by
- License/vehicle summary where relevant

The Shelter relationship must come from the actual database relationship, not a manually entered label.

Example:

`Ravi Kumar | Active | Happy Paws Shelter | Vehicle: KL-01-XX-1234`

Remove the Admin add/create button.

Admin may retain legitimate view/manage actions appropriate to an oversight role, such as view, deactivate/suspend, or reset credentials, if those already exist and fit the product.

Do not allow Admin UI to create an orphan Delivery record without a Shelter.

---

# 12. DELIVERY DOCUMENTS

Shelters can upload Delivery proofs/documents for their own Delivery staff.

Possible documents:

- driving license
- license details
- vehicle registration
- insurance
- identity proof where needed
- other relevant license/certificate

Admin can view these documents through the relevant Delivery/Shelter management view.

No separate verification center is required.

---

# 13. ADOPTION WORKFLOW — FREE ADOPTION, NO APPROVAL STAGE

KindHeart is an adoption platform, not a pet-selling platform.

The adoption itself is free.

Do not calculate a pet sale price or pet-sale revenue.

Remove approval-stage language from the Admin dashboard and adoption funnel.

Use a simpler lifecycle such as:

`Adoption Request → Handover/Delivery Scheduled → Completed`

with practical terminal states such as:

- Cancelled

Do not make Admin approval a required stage for an adoption order.

Do not show an “Approval Pending” funnel on the Admin dashboard.

---

# 14. PAYMENTS — NO PET SALE PRICE

Keep the existing Admin Payments section:

`http://localhost:8000/users/profile/?role=admin#payments`

but clear old/demo payment data.

Payments should only represent real operational/service transactions, for example:

- delivery/transport charge
- optional service charge if the product actually uses one
- payment gateway transaction
- refund
- legitimate operational expense where already supported

For a free adoption with no service charge:

`Payment = Not Required`

Do not force a payment on every adoption and do not create pet-sale revenue.

---

# 15. ADMIN DASHBOARD — REFURNISH AND MATCH REAL DATA

Refurbish:

`http://localhost:8000/users/profile/?role=admin#dashboard`

The dashboard must reflect the same live database data used by the other Admin sections.

Remove these current/obsolete dashboard blocks completely:

### Remove Transit Exception Flagged

Remove the card/alert containing text such as:

`Transit Exception Flagged • Order #KH10242 (Rocky)`

and:

`Courier Delayed`

Do not replace it with fabricated exception data.

### Remove User Registration Requests

Remove the entire:

`User Registration Requests`

block, including:

`0 Pending`

`Review and approve or reject newly registered users before granting platform login access.`

`Refresh Requests`

and the message:

`All user registrations are verified. No pending approval requests.`

Do not keep a fake request count.

### Remove Live Logistics & Courier Watch

Remove the entire Admin dashboard section:

`Live Logistics & Courier Watch`

Do not replace it with sample courier data.

### Remove Adoption Funnel

Remove the current:

`Adoption Funnel`

section and its order-stage visualization, especially any old approval-stage logic.

The dashboard should not imply that Admin approval is required for adoption.

---

# 16. WHAT THE REFURNISHED ADMIN DASHBOARD SHOULD SHOW

Replace the removed blocks with useful real-time summary information based on actual database queries.

Recommended KPI cards:

- Total Pets
- Available Pets
- Total Shelters
- Total Customers
- Total Delivery Staff
- Active Adoption Requests
- Completed Adoptions
- Delivery Jobs (current/recent, if available)

Recommended supporting sections:

### Recent Adoption Activity
Show recent real adoption records using statuses such as:

- Requested
- Handover Scheduled
- Completed
- Cancelled

### Recent Shelter Activity
Show newly created/updated shelters.

### Recent Pet Listings
Show recently added pets and their shelter.

### Recent Delivery Activity
Show real current/recent delivery records and the linked Shelter/Delivery person.

### Recent Payments
Show only actual recorded operational/service transactions.

All dashboard numbers and lists must come from the same database records shown by the corresponding Admin pages.

Do not hard-code sample numbers.

If there is no data, show clean empty states such as:

`No adoption activity yet.`

---

# 17. USERS & PERMISSIONS — UI REFRESH

Section:

`http://localhost:8000/users/profile/?role=admin#users-permissions`

Keep the existing four roles:

- Admin
- Shelter
- Delivery
- Customer

Refresh the UI into a clean production-style permission manager.

Use:

- clear role navigation/tabs
- grouped permissions
- readable labels
- toggles/checkboxes
- clear Save Changes action
- saved/unsaved state feedback
- sensible categories

Suggested permission groups:

- Users
- Shelters
- Pets
- Adoption
- Delivery
- Payments
- Reports
- Notifications
- Reviews/Complaints
- Settings

Permission changes must persist to the backend and be enforced by backend authorization.

### Permission scope

**Admin:** global management.

**Shelter:** only its own shelter, pets, adoption work, Delivery staff, and related documents/data.

**Delivery:** only assigned delivery operations.

**Customer:** only the customer's own profile, pet discovery, adoption, tracking, reviews/complaints, and related information.

Prevent cross-shelter and cross-customer access.

---

# 18. SYSTEM SETTINGS — UI REFRESH

Section:

`http://localhost:8000/users/profile/?role=admin#system-settings`

Refurbish the current System Settings UI into a clean, professional Admin settings page.

Use logical sections such as:

### General
- Platform name
- Support email
- Support phone
- Timezone
- Currency

### Registration
- Customer registration controls
- Password rules
- Session/security options

### Shelter
- Shelter profile fields
- Pet publishing rules
- Document upload limits/types

### Delivery
- Delivery status/tracking settings
- Delivery document settings

### Adoption
- Adoption fee fixed at zero
- Adoption request settings
- Handover/completion rules

### Notifications
- Email/in-app notifications
- Admin alerts

### Payments
- Delivery/service payment controls
- Refund settings
- Transaction settings

Do not create pet-sale payment settings.

### Security
- Password policy
- Login/security limits
- File upload limits/types

The UI should use the existing KindHeart visual language, good spacing, clear hierarchy, responsive layout, and meaningful empty/default states.

---

# 19. SECTION CONSISTENCY RULE

The Admin dashboard and all linked sections must tell the same story.

Examples:

- If Pets shows 0, Dashboard Total Pets must be 0.
- If Shelters shows 3 active shelters, Dashboard Total Shelters must show 3.
- If Delivery Logistics shows 5 Delivery staff, Dashboard Total Delivery Staff must show 5.
- If Payments has no transactions, Dashboard Recent Payments must show an empty state.
- Adoption counts and statuses must match the Adoption Orders data.
- Delivery data must match the Shelter that created each Delivery user.

Do not maintain separate hard-coded dashboard values.

---

# 20. FILES TO INSPECT FIRST

Inspect the existing implementation before editing, especially:

`users/models.py`
`users/views.py`
`users/urls.py`
`users/templates/users/register.html`
`users/templates/users/login.html`
`users/templates/users/profile.html`

`pets/models.py`
`pets/views.py`
`pets/urls.py`

and the existing Admin/Shelter templates for:

- dashboard
- adoption orders
- pets
- shelters
- customers/users
- delivery/logistics
- payments
- users & permissions
- system settings
- verification center

Also inspect existing migrations and model relationships.

Reuse the existing architecture. Do not create duplicate User, Shelter, Delivery, Permission, Payment, Adoption, or Settings systems.

---

# 21. DO NOT REWRITE THE WHOLE PROJECT

Make only the requested changes.

Do not:

- rebuild the entire backend
- replace the frontend framework
- create a second authentication system
- create duplicate models
- redesign unrelated customer/shelter pages unnecessarily
- break existing pet adoption functionality

---

# 22. ACCEPTANCE CHECK

The work is complete when:

1. Old/sample data in the listed Admin sections is cleared from the underlying database.
2. Customer remains the public registration role.
3. Shelter is removed from public registration.
4. Delivery is removed from public registration.
5. Admin can create Shelters.
6. Shelter can register/add/manage its own Pets.
7. Shelter can upload its own documents.
8. Admin can view Shelter documents.
9. Verification Center is completely removed.
10. Audit is removed from the Shelter Board UI.
11. Admin user/customer View shows username/email and account details but never plaintext passwords.
12. Delivery accounts are created only by Shelters.
13. Admin no longer has an Add Delivery Partner button.
14. Admin Delivery Logistics shows which Shelter each Delivery person belongs to.
15. Shelter can upload Delivery proofs/documents.
16. Adoption is free.
17. No Admin adoption approval stage is shown.
18. Payment data is real and service/transport based, not pet-sale based.
19. Transit Exception/Courier Delayed dashboard block is removed.
20. User Registration Requests dashboard block is removed.
21. Live Logistics & Courier Watch is removed from the dashboard.
22. Adoption Funnel is removed from the dashboard.
23. Dashboard KPIs and lists match the actual section data.
24. Users & Permissions has a fresh, usable UI with persistence.
25. System Settings has a fresh, usable UI with persistence.
26. Existing Customer/Pet/Adoption core functionality remains working.

## Final instruction

Inspect the current codebase first, then implement this specification using the existing architecture.

Keep the work focused on the requested Admin/data/workflow changes. Avoid unnecessary refactoring and avoid generating sample/fake records just to populate the new UI.

Run `python manage.py check` and the relevant tests/migration checks after the changes.

---

# 19. SHARED BASE TEMPLATE — USE `base.html`

Use the existing Django `base.html` as the shared layout foundation wherever the project already supports it.

Apply the shared base structure consistently across:

- Admin
- Shelter
- Customer
- Delivery
- Homepage/public pages

Keep common elements centralized in `base.html` where appropriate, such as:

- global HTML structure
- shared navigation/header
- footer
- common CSS/JS includes
- theme support
- common notifications/messages
- shared responsive layout behavior

Do not duplicate the same global layout markup independently across every role template when it can be inherited from `base.html`.

Do not break role-specific navigation or dashboard content.

---

# 20. ADMIN PETS SECTION — REMOVE “REGISTER NEW PET”

In the Admin Pets section:

`http://localhost:8000/users/profile/?role=admin#pets`

remove the **Register New Pet / Add New Pet** action from the Admin UI.

Pet registration belongs to the Shelter.

Admin Pets should be an oversight/management view of pets already registered by Shelters.

Admin may retain appropriate management actions such as viewing, editing permitted platform-level fields, suspending/removing an invalid listing, or reviewing pet information where the existing product requires it.

Do not provide a duplicate Admin pet-registration workflow.

---

# 21. REMOVE THE OLD SHELTER COURIER ASSIGNMENT RULE TEXT/CONCEPT

Remove the old Admin-facing rule/content block that says:

“Shelter Courier Assignment Rule: In KindHeart's pet logistics model, the partner shelter assigns the delivery partner and verifies climate crate preparation. Platform Administrators supervise transit SLAs, telematics, and intervene strictly when exceptions occur (Delays, Failed Pickups, Driver Cancellations, Handover Disputes).”

Do not keep this as a visible instruction, dashboard card, help text, or business-rule panel.

The actual ownership model remains simple:

- Shelter creates/controls its own Delivery staff.
- Delivery staff belongs to a Shelter.
- Admin can view/manage platform records according to permissions.

Do not create a separate Admin courier-assignment workflow from this text.

---

# 22. DELIVERY SECTION — REMOVE “ADD DELIVERY PARTNER”

In the Admin Delivery & Logistics section, remove:

- Add Delivery Partner
- Add Delivery
- Create Delivery Partner

The Admin is not the creator of Delivery staff.

Delivery staff are created by the Shelter from the Shelter Dashboard.

The Admin Delivery section should show existing Delivery records and their owning Shelter, without providing an Admin-side creation form.

---

# 23. REPORT ANALYTICS — REMOVE THE SEPARATE ADMIN REPORT/ANALYTICS PAGE

The current report/analytics concept is not required as a separate Admin module/page.

Remove the unnecessary standalone Report Analytics presentation from the Admin module.

Do not leave an empty Report/Analytics navigation item.

Instead, surface the useful summary information directly on the Admin Dashboard.

The Admin Dashboard should show concise, readable analytics derived from live database data, such as:

- total pets
- available pets
- total shelters
- total customers
- total delivery staff
- active adoption requests
- completed adoptions
- current/recent delivery count where real data exists
- legitimate payment totals where real transactions exist

Where useful, add small dashboard charts/tables for:

- adoption activity
- pet availability
- shelter activity
- delivery activity
- legitimate service/payment activity

Do not invent statistics when the database has no data.

If there is no data, show a clean empty state.

---

# 24. ADMIN DASHBOARD — FINAL CONTENT RULE

The Admin Dashboard should be the main place for platform-level summaries.

It should NOT contain:

- Transit Exception Flagged demo alerts
- Courier Delayed demo alerts
- User Registration Requests
- Pending registration approval widgets
- Live Logistics & Courier Watch
- Old Adoption Funnel
- Separate Report Analytics navigation
- Fake/sample counts
- Pet registration controls
- Delivery creation controls
- Verification Center controls
- Shelter Courier Assignment Rule text

It SHOULD contain:

- real KPI summaries
- recent adoption activity
- recent shelter activity
- recent pet listings
- recent delivery activity
- relevant payment/service activity
- concise analytics derived from the same database records used by the individual Admin sections

All dashboard data must stay synchronized with:

- Pets
- Shelters
- Customers
- Delivery Logistics
- Adoption Orders
- Payments

Do not hard-code dashboard values separately from the underlying records.

---

# 25. ADMIN SECTION CONSISTENCY

The Admin dashboard and Admin subsections must represent the same underlying data model.

For example:

- Dashboard Total Pets = actual records visible in Admin → Pets.
- Dashboard Total Shelters = actual records visible in Admin → Shelters.
- Dashboard Total Customers = actual customer records.
- Dashboard Delivery Staff = actual Delivery records linked to Shelters.
- Dashboard adoption metrics = actual adoption records.
- Dashboard payment metrics = actual legitimate payment/service records.

Do not maintain separate hard-coded dashboard counters.

When a new Shelter, Pet, Customer, Delivery user, Adoption, or legitimate Payment is created, the relevant Admin dashboard numbers/lists should update from the database.

---

# 26. FINAL UI CLEANUP

Apply the following UI cleanup across the affected Admin sections:

- Remove obsolete cards and duplicate actions.
- Remove empty navigation items after deleting a feature.
- Keep labels consistent with the actual business workflow.
- Avoid decorative/sample data.
- Use clean empty states when there are no records.
- Keep tables readable and focused on useful information.
- Do not expose credentials or sensitive information.
- Keep shared layout behavior consistent through `base.html`.
- Keep the existing KindHeart visual language while making the affected Admin screens cleaner and more professional.

---

# 27. FINAL ROLE/OWNERSHIP RULES

Use these ownership rules throughout the project:

**Admin**

- Creates/manages Shelters.
- Oversees platform-wide records.
- Views Delivery staff and their owning Shelter.
- Does not create Delivery staff.
- Does not register/add Pets for Shelters.
- Does not run a Verification Center.

**Shelter**

- Manages its own Shelter profile/documents.
- Registers/adds its own Pets.
- Manages its own adoption operations.
- Creates and manages its own Delivery staff.
- Provides Delivery login credentials.
- Uploads Delivery documents/proofs.

**Delivery**

- Uses the account created by its Shelter.
- Handles assigned delivery operations only.

**Customer**

- Self-registers.
- Browses Pets.
- Requests adoption.
- Tracks relevant adoption/handover information.

---

# 28. FINAL IMPLEMENTATION CHECK

Before declaring the update complete, verify all of the following:

- `base.html` is used for shared site structure across Admin, Shelter, Customer, Delivery, and Homepage where appropriate.
- Admin cannot register/add a new Pet.
- Shelter can register/add its own Pets.
- Admin cannot add a Delivery Partner.
- Shelter can add multiple Delivery staff.
- Every Delivery record identifies its owning Shelter.
- Admin Shelter section has no Audit column/action.
- Shelter documents can be uploaded by Shelter and viewed by Admin.
- Delivery documents can be uploaded by Shelter and viewed by Admin where authorized.
- Verification Center is completely removed.
- The old Shelter Courier Assignment Rule text/feature is completely removed.
- Users & Permissions has no unnecessary “Active” pill if it is only decorative/redundant; use meaningful permission controls instead.
- Admin user view shows username/email/phone/role/status as appropriate but never a plaintext password.
- Admin Dashboard contains no Transit Exception Flagged/Courier Delayed demo content.
- Admin Dashboard contains no User Registration Requests widget.
- Admin Dashboard contains no Live Logistics & Courier Watch block.
- Admin Dashboard contains no old Adoption Funnel approval workflow.
- Admin Dashboard contains useful report/analytics summaries directly.
- There is no unnecessary separate Report Analytics module/page.
- Dashboard statistics match the live data in the related Admin sections.
- No fake/sample records are introduced to make the dashboard look populated.
- System Settings and User Permissions use the refreshed UI from the previous requirements.
- Adoption remains free and payments represent only legitimate service/operational transactions.

---

# 30. MANDATORY ADMIN-ONLY REMOVALS — DO NOT LEAVE THE OLD BUTTONS/SECTIONS

The previous UI still contains some old Admin actions. These must be removed from the actual rendered Admin interface, not merely hidden from the specification.

## A. Admin Pets — REMOVE "Register New Pet"

Admin page:

`http://localhost:8000/users/profile/?role=admin#pets`

Completely remove the Admin-side:

- `Register New Pet`
- `Add New Pet`
- Any equivalent Admin button/link/action that creates a Pet
- Any Admin modal/form specifically used to register a new Pet
- Any Admin JavaScript handler/API call whose only purpose is Admin pet creation

The Admin must NOT have a Pet registration button.

### IMPORTANT

Do NOT remove the Shelter-side Pet creation capability.

The correct ownership is:

`Shelter Dashboard → Add Pet`

Admin can view/manage existing Pets according to the existing Admin permissions, but Shelter is the normal creator/registrar of Pets.

Search the existing Admin templates, JavaScript, buttons, modals, and route links for text/labels similar to:

- Register New Pet
- Register Pet
- Add New Pet
- Add Pet
- Create Pet

Remove only the Admin creation path. Preserve the Shelter creation path.

---

## B. Admin Delivery — REMOVE "Add Delivery Partner"

Admin page:

`http://localhost:8000/users/profile/?role=admin#delivery-logistics`

Completely remove the Admin-side:

- `Add Delivery Partner`
- `Add Delivery`
- `Create Delivery Partner`
- Any equivalent Admin button/link/action for creating Delivery personnel
- Any Admin modal/form specifically used to create a Delivery account
- Any Admin JavaScript/API path whose only purpose is Admin delivery-person creation

The Admin Delivery section must be a management/oversight view only.

### IMPORTANT

Do NOT remove the Shelter-side Delivery creation capability.

The correct ownership is:

`Shelter Dashboard → Delivery Management → Add Delivery Person`

A Shelter can create multiple Delivery accounts and provide their login credentials.

The Delivery record must always show its owning Shelter when viewed by Admin.

---

## C. REMOVE THE OLD ADMIN "REPORT ANALYTICS" MODULE

Do not keep a separate Admin module/page called:

- Report Analytics
- Analytics
- Reports & Analytics

when it only duplicates information already required by the Admin Dashboard.

Instead, surface useful summary information directly on:

`http://localhost:8000/users/profile/?role=admin#dashboard`

The Admin Dashboard should show real database-driven summaries such as:

- Total Pets
- Available Pets
- Total Shelters
- Total Customers
- Total Delivery Staff
- Active Adoption Requests
- Completed Adoptions
- Current/Recent Deliveries where available
- Real operational/service payment totals where available

Use simple cards, tables, and recent activity sections that are understandable without a separate analytics module.

Do not create a complicated BI/charting system just to replace the old module.

---

## D. VERIFY THE REMOVALS AFTER IMPLEMENTATION

After making the changes, inspect the actual rendered Admin page and confirm that these strings/buttons no longer appear anywhere in the Admin UI:

- `Register New Pet`
- `Add New Pet`
- `Register Pet` (when it refers to Admin pet creation)
- `Add Delivery Partner`
- `Add Delivery` (when it refers to Admin delivery creation)
- `Create Delivery Partner`
- `Report Analytics`
- `Analytics` (as the old separate Admin module)

Also verify there are no dead links that still open the removed Admin forms.

The following must still exist where appropriate:

- Shelter → Add Pet
- Shelter → Delivery Management → Add Delivery Person
- Admin → View existing Pets
- Admin → View existing Delivery staff
- Admin → Dashboard summaries

---

# 31. ADMIN UI CONSISTENCY CHECK

Use the existing shared `base.html` for common Admin/Shelter/Customer/Delivery/Homepage structure wherever the project already supports it.

Do not duplicate:

- navbar
- sidebar
- footer
- theme controls
- common scripts/styles

Keep the role-specific content inside the role pages/sections.

After the UI changes, verify the Admin dashboard, Pets, Shelters, Delivery, Users & Permissions, and System Settings all use the same visual language and shared layout.

---

# 32. FINAL BUSINESS OWNERSHIP RULES

Use these ownership rules consistently across the codebase:

`Admin`
→ creates and manages Shelters
→ supervises the platform
→ views existing Pets and Delivery staff
→ manages global permissions/settings

`Shelter`
→ manages its own Shelter profile
→ registers/adds its own Pets
→ manages its own adoption requests
→ creates its own Delivery staff
→ uploads Shelter and Delivery documents

`Delivery`
→ performs assigned delivery/handover operations

`Customer`
→ discovers Pets and submits adoption requests

Do not reverse these responsibilities in the UI or backend.

---

# 33. FINAL ACCEPTANCE CHECK — SPECIFIC OLD UI MUST BE GONE

The task is NOT complete if any of the following remains in the Admin module:

- Admin `Register New Pet` button
- Admin `Add Pet` creation workflow
- Admin `Add Delivery Partner` button
- Admin `Add Delivery` creation workflow
- Separate `Report Analytics` module
- Verification Center
- User Registration Requests dashboard card
- Live Logistics & Courier Watch
- Transit Exception / Courier Delayed demo alert
- Old Adoption Funnel approval-stage visualization

At the same time, do NOT accidentally remove:

- Shelter Add Pet
- Shelter Delivery Management / Add Delivery Person
- Shelter document upload
- Admin document viewing
- Customer registration
- Customer adoption functionality

Make the changes in the existing codebase and verify the rendered UI after implementation.
