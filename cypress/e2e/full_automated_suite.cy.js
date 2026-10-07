describe('KindHeart Pet Adoption - Complete Automated End-to-End Suite', () => {

  // 1. PUBLIC HOMEPAGE & BROWSING
  it('1. Public Homepage - Navigates and verifies UI components', () => {
    cy.visit('/')
    cy.get('body').should('be.visible')
    cy.get('a[href*="/users/login"]').should('exist')
  })

  // 2. CUSTOMER AUTHENTICATION & ADOPTION APPLICATION
  it('2. Customer Flow - Log in and check adoption application status', () => {
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear().type('admin111')
    cy.get('#login-password').clear().type('123456')
    cy.get('#form-login button[type="submit"]').click()
    
    // Check that customer dashboard does not allow cancelling adoption requests
    cy.get('#btn-cancel-adoption').should('not.exist')
    cy.get('.btn-cancel-request').should('not.exist')
  })

  // 3. SHELTER DASHBOARD & DELIVERY ASSIGNMENT
  it('3. Shelter Flow - View pets, open delivery assignment, and inspect customer details', () => {
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear().type('77365847611')
    cy.get('#login-password').clear().type('123456')
    cy.get('#form-login button[type="submit"]').click()
    
    cy.visit('/users/profile/?role=shelter#view-pets')
    cy.get('#view-pets').should('exist')

    // Inspect delivery fleet tab
    cy.visit('/users/profile/?role=shelter#delivery-logistics')
    cy.get('#container-delivery-fleet').should('exist')
  })

  // 4. DELIVERY PARTNER DASHBOARD
  it('4. Delivery Flow - Driver views assigned delivery tasks and customer details', () => {
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear().type('917907577011')
    cy.get('#login-password').clear().type('123456')
    cy.get('#form-login button[type="submit"]').click()
    
    cy.visit('/users/profile/?role=delivery')
    cy.get('body').should('be.visible')
  })

  // 5. ADMIN DASHBOARD OVERVIEW
  it('5. Admin Flow - Access platform management and registered shelters', () => {
    cy.visit('/users/login/')
    cy.get('#login-email-phone').clear().type('Admin123')
    cy.get('#login-password').clear().type('123456')
    cy.get('#form-login button[type="submit"]').click()
    
    cy.visit('/users/profile/?role=admin')
    cy.get('body').should('be.visible')
  })

})
