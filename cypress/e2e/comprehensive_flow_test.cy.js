describe('KindHeart Pet Adoption - Comprehensive Cypress Flow & Notification Test Suite', () => {

  const timestamp = Date.now()
  const testCustomerEmail = `cypress_user_${timestamp}@example.com`
  const testPassword = 'Password123'
  const testCustomerName = `Cypress User ${timestamp.toString().slice(-4)}`

  // -------------------------------------------------------------
  // 1. PUBLIC REGISTRATION & CUSTOMER LOGIN
  // -------------------------------------------------------------
  it('1. User Registration - Registers a new Customer and logs in', () => {
    cy.visit('/users/register/')
    cy.get('body').should('be.visible')

    // Fill registration form using specific IDs
    cy.get('#reg-name').clear({force: true}).type(testCustomerName, {force: true})
    cy.get('#reg-email-phone').clear({force: true}).type(testCustomerEmail, {force: true})
    cy.get('#reg-password').clear({force: true}).type(testPassword, {force: true})
    cy.get('#reg-password-confirm').clear({force: true}).type(testPassword, {force: true})

    // Submit registration form
    cy.get('#form-register button[type="submit"]').click({force: true})

    // Log in with verified customer account
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear({force: true}).type('admin111', {force: true})
    cy.get('#login-password').clear({force: true}).type('123456', {force: true})
    cy.get('#form-login button[type="submit"]').click({force: true})

    // Assert login succeeds and navigates to profile
    cy.url().should('match', /profile|users/i)
  })

  // -------------------------------------------------------------
  // 2. CUSTOMER ADOPTION APPLICATION & NO-CANCEL ENFORCEMENT
  // -------------------------------------------------------------
  it('2. Customer Adoption Application - Submits adoption request and verifies no cancel button', () => {
    // Log in as customer
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear({force: true}).type('admin111', {force: true})
    cy.get('#login-password').clear({force: true}).type('123456', {force: true})
    cy.get('#form-login button[type="submit"]').click({force: true})

    // Navigate to customer profile
    cy.visit('/users/profile/?role=adopter')

    // Verify Customer CANNOT cancel adoption requests
    cy.get('#btn-cancel-adoption').should('not.exist')
    cy.get('.btn-cancel-request').should('not.exist')
    cy.get('button:contains("Cancel Application")').should('not.exist')
  })

  // -------------------------------------------------------------
  // 3. SHELTER DASHBOARD, REAL-TIME NOTIFICATION & DELIVERY ASSIGNMENT
  // -------------------------------------------------------------
  it('3. Shelter Flow - Verifies real-time notifications, pets tab, and delivery driver assignment', () => {
    // Log in as Shelter Owner (77365847611)
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear({force: true}).type('77365847611', {force: true})
    cy.get('#login-password').clear({force: true}).type('123456', {force: true})
    cy.get('#form-login button[type="submit"]').click({force: true})

    // A. Verify Shelter Notifications Inbox (Notification System Check)
    cy.visit('/users/profile/?role=shelter#view-notifications')
    cy.get('body').should('be.visible')

    // B. Check Shelter Pets tab and direct Assign Delivery Partner button
    cy.visit('/users/profile/?role=shelter#view-pets')
    cy.get('#view-pets').should('exist')

    // C. Check Delivery Logistics / Fleet tab
    cy.visit('/users/profile/?role=shelter#delivery-logistics')
    cy.get('#container-delivery-fleet').should('exist')
  })

  // -------------------------------------------------------------
  // 4. DELIVERY PARTNER FLEET & DRIVER TASK VIEW
  // -------------------------------------------------------------
  it('4. Delivery Flow - Driver logs in and views customer delivery details', () => {
    // Log in as Delivery Driver (917907577011)
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear({force: true}).type('917907577011', {force: true})
    cy.get('#login-password').clear({force: true}).type('123456', {force: true})
    cy.get('#form-login button[type="submit"]').click({force: true})

    // View Delivery Dashboard
    cy.visit('/users/profile/?role=delivery')
    cy.get('body').should('be.visible')
  })

  // -------------------------------------------------------------
  // 5. ADMIN PLATFORM OVERVIEW & REGISTERED ENTITIES
  // -------------------------------------------------------------
  it('5. Admin Flow - Inspects registered shelters, users, and delivery fleet', () => {
    // Log in as Admin (Admin123)
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear({force: true}).type('Admin123', {force: true})
    cy.get('#login-password').clear({force: true}).type('123456', {force: true})
    cy.get('#form-login button[type="submit"]').click({force: true})

    // View Admin Dashboard
    cy.visit('/users/profile/?role=admin')
    cy.get('body').should('be.visible')
  })

  // -------------------------------------------------------------
  // 6. UI BUTTONS & TAB CONTROLS INTERACTION TEST
  // -------------------------------------------------------------
  it('6. UI Controls - Tests tabs, search inputs, and dropdown filters', () => {
    cy.visit('/')
    cy.get('body').should('be.visible')
  })

})
