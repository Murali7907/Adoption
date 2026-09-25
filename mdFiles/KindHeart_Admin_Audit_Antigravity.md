# KindHeart Admin Module — Full Audit, Fix & Redesign Specification

## Objective

Update and audit the existing **KindHeart pet-adoption platform** from the **Admin module**.

This task is not only a UI update. Antigravity must verify the complete Admin flow across:

- Admin frontend/UI
- Django views/forms/URLs
- Models
- Database records
- APIs/AJAX/fetch requests
- Authentication and role permissions
- Django Admin (`/admin/`)
- Persistent storage after page refresh/re-login

The goal is to make the Admin module reliable, persistent, consistent with the database, and visually redesigned without breaking the existing Shelter, Customer, Delivery, or public pet-adoption functionality.

---

# 1. Remove "All Pets" from Admin

## Required change

Remove the **All Pets** directory/page from the **Admin module**.

Remove it from:

- Admin sidebar
- Admin navigation
- Admin dashboard cards/shortcuts if they specifically represent All Pets
- Admin breadcrumbs
- Admin route/URL
- Admin page/template/component
- Admin action links
- Admin search/navigation references
- Any Admin-only API endpoint that exists solely for this page

## Important

Do **not** delete the underlying Pet model or pet records.

Do **not** remove:

- Shelter pet management
- Shelter pet listings
- Customer Find a Pet
- Public pet browsing
- Adoption workflows
- Pet-related APIs required by other modules

Only remove the **Admin All Pets directory/interface**.

---

# 2. Critical Bug — Data Disappears After Refresh

## Problem to investigate

Currently, Admin data appears to exist immediately after an action, but after refreshing the page, the data is missing.

This must be treated as a **persistence/backend problem**, not merely a frontend rendering problem.

## Audit the complete data flow

For every Admin CRUD operation:

1. Identify the frontend form/button.
2. Identify the JavaScript/fetch/AJAX request if used.
3. Identify the Django URL.
4. Identify the Django view.
5. Identify the form/serializer used.
6. Identify the Django model.
7. Verify the database write operation.
8. Verify transaction completion.
9. Verify the response sent to the frontend.
10. Refresh the page and confirm the data is loaded again from the database.

## Explicitly check for these problems

- Data stored only in JavaScript state
- Data stored only in `localStorage`
- Data stored only in `sessionStorage`
- Temporary/mock/static arrays
- Frontend-only CRUD
- Missing `.save()`
- Missing `commit`
- Incorrect model instance creation
- Incorrect `update()` / `delete()` logic
- Wrong database connection
- Wrong database/table
- Transactions being rolled back
- Errors being swallowed in JavaScript
- API returning success while database write fails
- Page reload using a different data source
- Hardcoded dashboard values
- Cache showing stale records
- Incorrect queryset/filter
- Incorrect user/role filtering
- Soft-deleted records being unintentionally hidden
- Admin page reading from a different model than the write operation

## Acceptance test

For each CRUD action:

### Create
- Create record.
- Close/reload browser.
- Log out and log in again.
- Record must still exist.

### Update
- Modify record.
- Refresh.
- Modified value must remain.

### Delete
- Delete record.
- Refresh.
- Deleted record must remain deleted according to the selected deletion policy.

### Deactivate
- Deactivate account.
- Refresh.
- Account must remain inactive.
- User must no longer be able to perform actions that require an active account.

---

# 3. Registered Shelters Must Appear in Admin

## Problem

Registered shelters cannot currently be found reliably in the Admin shelter list.

Fix the Admin shelter listing so that all valid registered shelters are loaded from the database.

## Verify

Check:

- Shelter model
- User/account relationship
- Shelter profile relationship
- Registration status
- Approval status
- Active/inactive status
- Queryset filtering
- Pagination
- Search
- Sorting
- Role filtering
- Soft-delete filtering
- Foreign-key relationships
- Records created before and after the latest UI changes

## Required Admin Shelter List

The Admin Shelter section should show useful information such as:

| Field | Requirement |
|---|---|
| Shelter Name | Database value |
| Contact Person | Database value |
| Email | Database value |
| Phone | Database value |
| Location | Database value |
| Registration Date | Database value |
| Verification/Approval Status | Database value |
| Account Status | Active / Deactivated |
| Total Pets | Related pet count if available |
| Actions | View / Edit / Approve / Deactivate / Delete |

Do not fabricate values.

Every displayed field must have a real source in the backend/database.

---

# 4. Add "Deactivate Account" Option

Add a proper account deactivation mechanism for Admin.

## UI

Add:

**Deactivate Account**

to the relevant Admin account-management actions.

For a currently active account:

- Show `Deactivate`
- Ask for confirmation
- Update account status in the database

For a deactivated account:

- Show `Activate`
- Do not show `Deactivate` as the primary state action

## Backend

Use a real persistent account-status field.

Prefer an existing appropriate field such as:

- `is_active`

or the existing project-specific account status model/field.

Do not create duplicate account-state fields if a correct field already exists.

## Required behavior

When deactivated:

- Account status changes in the database.
- Status survives refresh.
- Status survives logout/login.
- User should not be able to access protected authenticated functionality that requires an active account.
- Existing records/history should not be accidentally deleted.

---

# 5. Add "Delete Account" Option

Add a separate **Delete Account** action.

This must be clearly different from deactivation.

## Delete confirmation

Use a strong confirmation dialog.

Example:

> Delete this account permanently?
>
> This action may remove or detach account-related data. Review dependencies before continuing.

Do not perform accidental deletion from a single click.

## Backend requirements

Before implementing hard deletion:

1. Inspect foreign-key relationships.
2. Check `on_delete` behavior.
3. Check related shelter/customer/pet/adoption/payment/review/message records.
4. Determine whether the existing project architecture supports:
   - Hard delete
   - Soft delete
   - Archive/deactivation

Use the safest design compatible with the current application.

Do not break referential integrity.

## Important

Do not delete unrelated business records only because a user account is removed.

For example, historical adoption/payment/audit information should not disappear unexpectedly unless the existing data-retention design explicitly requires it.

---

# 6. Redesign the "User & Permission" Section

Do not make a small cosmetic adjustment.

Redesign the existing **User & Permission** section into a professional Admin control interface while preserving the existing functionality.

## Existing roles

The application has:

- Admin
- Shelter
- Delivery
- Customer

There is only **one Admin role** in this application.

Do not introduce a "Super Administrator" role unless the existing architecture already requires one.

## New layout

Use a clean management layout such as:

### Header
- User & Permission
- Short description
- Search
- Filter
- Refresh
- Add/Create action only where appropriate

### User list
Display:

- User
- Role
- Email
- Account Status
- Last Login if available
- Created Date
- Actions

### Actions

Depending on role and permissions:

- View
- Edit
- Deactivate
- Activate
- Delete
- Manage Permissions

## Permission management

Replace static/non-editable permission pills with an actual editable permission UI.

Organize permissions by feature:

### Dashboard
- View Dashboard

### Users
- View Users
- Create User
- Edit User
- Deactivate User
- Delete User

### Shelters
- View Shelters
- Approve Shelters
- Edit Shelters
- Suspend/Deactivate Shelters
- Delete Shelters

### Pets
- View relevant pet information
- Do not recreate the removed Admin All Pets directory

### Adoption
- View Requests
- Manage Requests

### Delivery
- View Delivery
- Manage Delivery

### Payments
- View Payments
- Manage/verify applicable payment operations

### Reports
- View Reports
- Export Reports

### System Settings
- View Settings
- Modify Settings

## UI behavior

Use:

- Permission groups
- Clear toggles/checkboxes
- Readable hierarchy
- Save Changes button
- Cancel/Reset
- Unsaved-change indicator
- Success/error feedback
- Disabled/loading states
- Confirmation when needed

Permissions must actually persist in the backend.

Do not create UI-only permission toggles.

---

# 7. Redesign "System Settings"

The **System Settings** section is an Admin section, not a separate user role/module.

Redesign it into a professional settings center.

## Recommended structure

### General
- Application name
- Application description
- Support email
- Support phone if already supported
- Default timezone
- Default currency if supported
- Date/time format

### Account & Security
- Password/security policy
- Session settings
- Account activation/deactivation behavior
- Login-related settings that already exist in the project

### Notifications
- Email notification settings if implemented
- In-app notification settings
- Adoption request notifications
- Shelter registration notifications
- Delivery-related notifications

### Adoption Settings
Only expose settings that are actually supported by the backend.

Examples:

- Adoption request workflow
- Approval requirements
- Status configuration
- Required profile information

### Platform Settings
- Maintenance mode if supported
- Registration settings
- File/image upload limits if supported
- Pagination settings if supported

### Audit & Logs
- Admin actions
- Login/security events if already implemented
- Important system changes

Do not display fake settings that do nothing.

## Persistence rule

Every editable setting must:

1. Have a backend/database source.
2. Load its current value from the backend.
3. Save to the backend.
4. Persist after refresh.
5. Persist after logout/login.
6. Be reflected in the application behavior where applicable.

---

# 8. Backend ↔ Frontend ↔ Database Consistency Audit

Perform a field-by-field audit for every Admin section changed in this task.

Create a mapping for:

**UI Field → Django Form/Serializer → View/API → Model Field → Database Column**

Example:

| UI Field | Backend Field | Model | DB Column | Status |
|---|---|---|---|---|
| Shelter Name | `name` | Shelter | `name` | Verify |
| Email | `email` | User/Profile | corresponding DB column | Verify |
| Account Status | `is_active` or existing field | User | corresponding DB column | Verify |
| Approval Status | existing project field | Shelter | corresponding DB column | Verify |

Do not guess field names.

Read the actual Django models and migrations before changing the frontend.

---

# 9. Django Models & Migrations Audit

Inspect:

- `models.py`
- migrations
- forms
- serializers if present
- views
- URL routes
- templates
- JavaScript
- API endpoints
- authentication/permissions
- signals if present
- Django Admin registrations

Check for:

- Duplicate fields
- Missing migrations
- Unapplied migrations
- Fields used by UI but missing from model
- Model fields no longer used by UI
- Incorrect nullability
- Incorrect default values
- Foreign-key issues
- Unique constraints
- Status fields with inconsistent values
- Role values inconsistent between frontend/backend
- Orphaned records
- Broken relationships

If a schema change is actually required:

1. Update the model.
2. Create migrations.
3. Apply migrations.
4. Verify the database.
5. Verify Django Admin.
6. Verify the application.

---

# 10. Verify Through Django Administrator

Use Django Admin as a backend verification source.

Check that the relevant models are properly registered and usable.

Verify:

- Users
- Shelters
- Customer accounts
- Delivery accounts
- Pets where applicable
- Adoption requests
- Payments if present
- Permissions/roles
- System settings if represented by models
- Relevant status fields

For the shelter issue specifically:

1. Open Django Admin.
2. Find shelter/user records.
3. Confirm the records actually exist in the database.
4. Compare them with the Admin frontend.
5. Identify why frontend shelter records are missing if Django Admin contains them.

The final Admin UI must use the correct source of truth.

---

# 11. Database Verification

Inspect the actual configured Django database.

Verify:

- Database engine
- Database name
- Active environment
- Connection configuration
- Applied migrations
- Table names
- Relevant columns
- Existing records
- Foreign keys
- Unique constraints
- Account status values
- Shelter registration/approval values

Important:

Do not accidentally inspect one database while the running application writes to another.

Check that the development application and Django Admin point to the same database/environment.

---

# 12. Refresh / Persistence Test Matrix

After implementation, test every relevant Admin feature using this pattern:

| Test | Action | Refresh | Logout/Login | Expected |
|---|---|---|---|---|
| Shelter Create | Create shelter | Yes | Yes | Record remains |
| Shelter Edit | Edit shelter | Yes | Yes | Changes remain |
| Deactivate | Deactivate account | Yes | Yes | Account stays inactive |
| Activate | Reactivate account | Yes | Yes | Account becomes active |
| Delete | Delete account | Yes | Yes | Deletion remains |
| Permission Change | Change permission | Yes | Yes | Permission remains |
| System Setting | Change setting | Yes | Yes | Setting remains |
| Search | Search shelter/user | Yes | Yes | Correct records available |
| Filter | Apply status filter | Yes | Yes | Correct results |
| Pagination | Change page | Yes | Yes | Data remains accessible |

---

# 13. Admin UX / UI Quality Requirements

The redesigned Admin interface should be:

- Professional
- Consistent
- Responsive
- Accessible
- Clean
- Data-oriented
- Easy to scan
- Consistent across User & Permission and System Settings

Use a consistent:

- Sidebar
- Header
- Page title
- Breadcrumb
- Card style
- Table style
- Form style
- Button hierarchy
- Modal/dialog pattern
- Toast/alert pattern
- Empty state
- Loading state
- Error state

Avoid unnecessary visual effects that reduce usability.

Do not introduce a completely different design language from the existing KindHeart Admin module unless necessary.

---

# 14. Do Not Break Other Roles

After Admin changes, explicitly verify:

## Shelter

- Login
- Dashboard
- Pet management
- Registered/approved shelter state
- Adoption requests
- Delivery assignment
- Profile

## Customer

- Login
- Profile
- Find a Pet
- Pet details
- Adoption request
- Messages/notifications where supported

## Delivery

- Login
- Assigned deliveries
- Delivery status
- Related shelter handover workflow

## Public

- Homepage
- Find a Pet
- Pet details
- Authentication pages

Do not remove or alter these workflows while fixing Admin.

---

# 15. Specific Shelter Courier Rule

Preserve the existing business rule:

**The partner shelter assigns the delivery partner/courier for the pet handover.**

Do not move this responsibility to Admin unless the existing product requirements explicitly require it.

---

# 16. Security & Permission Validation

Verify that Admin-only actions are actually protected by backend authorization.

Do not rely only on hidden buttons.

Test:

- Admin can access Admin-only routes.
- Shelter cannot access Admin-only routes.
- Customer cannot access Admin-only routes.
- Delivery cannot access Admin-only routes.
- Deactivated users cannot access protected functions requiring active accounts.
- Direct URL access is protected.
- API endpoints enforce permissions.
- Delete/deactivate endpoints enforce Admin authorization.

---

# 17. Error Handling

Every Admin CRUD action must handle:

### Success
Show a clear success message.

### Validation error
Show the relevant field/message.

### Server error
Show a useful error message.

### Unauthorized
Return/display appropriate access-denied behavior.

### Not found
Handle missing/deleted records safely.

Never silently fail.

Never show "Success" when the database operation failed.

---

# 18. Remove Dead/Mock Data

During the audit, search for:

- Hardcoded shelter arrays
- Hardcoded user arrays
- Dummy permission objects
- Fake dashboard counts
- Static status values
- Temporary JSON data
- Mock API responses
- Frontend-generated IDs
- Fake settings values

Replace them with real backend/database data where the feature is intended to be functional.

Do not replace a genuinely static configuration value unnecessarily.

---

# 19. Final Admin Verification Checklist

Before considering the task complete, verify all of the following:

### Navigation
- [ ] Admin All Pets directory removed
- [ ] No broken All Pets links
- [ ] No orphaned route
- [ ] No unused imports/components related to All Pets

### Shelters
- [ ] Registered shelters appear
- [ ] Shelter search works
- [ ] Shelter filters work
- [ ] Shelter view works
- [ ] Shelter edit works
- [ ] Approve works where supported
- [ ] Deactivate works
- [ ] Activate works
- [ ] Delete works safely

### Users & Permissions
- [ ] Redesigned UI
- [ ] All required roles visible
- [ ] Permissions are editable
- [ ] Permissions save to backend
- [ ] Permissions remain after refresh
- [ ] Permissions remain after logout/login
- [ ] Admin authorization is enforced server-side

### System Settings
- [ ] Redesigned UI
- [ ] Settings load from backend
- [ ] Settings save to backend
- [ ] Settings remain after refresh
- [ ] Settings remain after logout/login
- [ ] No fake/non-functional settings

### Persistence
- [ ] Create persists
- [ ] Edit persists
- [ ] Deactivate persists
- [ ] Activate persists
- [ ] Delete persists
- [ ] Permission changes persist
- [ ] Settings changes persist

### Backend
- [ ] Django models verified
- [ ] Migrations verified
- [ ] Views verified
- [ ] URLs verified
- [ ] Forms/serializers verified
- [ ] APIs verified
- [ ] Permissions verified
- [ ] Database verified
- [ ] Django Admin verified

### Cross-module regression
- [ ] Shelter module works
- [ ] Customer module works
- [ ] Delivery module works
- [ ] Public pet pages work
- [ ] Adoption workflow works

---

# 20. Required Final Audit Report

After completing the implementation, do not just say "done".

Produce an internal audit summary containing:

## A. Problems Found

List every actual problem discovered.

## B. Root Cause

For each important problem, identify whether it was caused by:

- Frontend state
- API
- Django view
- Model
- Migration
- Database
- Permissions
- Query/filter
- Authentication
- UI routing
- Other

## C. Changes Made

List the files/modules changed and what was changed.

## D. Database Verification

Report:

- Database used
- Relevant tables/models checked
- Migration state
- Important fields checked
- Shelter records verified
- Account status field verified
- Permission storage verified
- Settings storage verified

## E. Django Admin Verification

Report which relevant models were checked through Django Administrator and whether the frontend data matches.

## F. Test Results

For each Admin feature, report:

**PASS / FAIL**

Do not mark a test PASS unless it was actually verified.

## G. Remaining Issues

List anything that could not be verified or remains unresolved.

---

# 21. Implementation Rules for Antigravity

1. Work from the existing KindHeart codebase.
2. Do not recreate the entire Admin module from scratch unless the existing implementation is irreparably broken.
3. Preserve existing working functionality.
4. Inspect the backend before changing database-dependent UI.
5. Use the database as the source of truth.
6. Do not use localStorage/sessionStorage as a substitute for backend persistence.
7. Do not fabricate backend fields.
8. Do not create fake success responses.
9. Do not delete unrelated data.
10. Keep Admin-only changes scoped to the Admin module.
11. Preserve the Shelter → Delivery Partner assignment rule.
12. Verify changes using the Django Administrator.
13. Verify the actual database.
14. Test refresh and re-login persistence.
15. Check browser console and Django server logs for errors.
16. Fix root causes instead of hiding symptoms.
17. Do not finish until the final verification checklist has been executed.

---

# Definition of Done

This task is complete only when:

**Admin UI → Django backend → database → Django Administrator → refresh/re-login**

all show consistent, persistent data and the Admin module works without regressions.

The Admin **All Pets** directory is removed, registered shelters are visible, account deactivation and deletion work correctly, User & Permission and System Settings have been redesigned, and all changed functionality has been verified against the real Django backend and database.
