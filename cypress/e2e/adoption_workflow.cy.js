describe('KindHeart Pet Adoption Suite', () => {
  beforeEach(() => {
    // Visit base URL (http://127.0.0.1:8000 configured in cypress.config.js)
    cy.visit('/')
  })

  it('loads the homepage successfully', () => {
    cy.title().should('match', /KindHeart|Pet/i)
  })

  it('navigates to login page and verifies form fields', () => {
    cy.visit('/users/login/')
    cy.get('#login-email-phone').should('be.visible')
    cy.get('button[type="submit"]').should('be.visible')
  })
})