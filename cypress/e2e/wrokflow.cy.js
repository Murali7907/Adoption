describe('KindHeart App Direct Route Tests', () => {
  it('opens the homepage', () => {
    cy.visit('/')
    cy.url().should('include', '127.0.0.1:8000')
  })

  it('opens login page', () => {
    cy.visit('/users/login/')
    cy.get('#login-email-phone').should('be.visible')
    cy.get('#login-email-phone').type('admin111', {force: true})
    cy.get('#login-password').type('123456', {force: true})
    cy.get('#form-login button.btn-submit').click({force: true})
  })
})