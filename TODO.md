# Fix Password Validation on Registration Page

## Tasks
- [x] Modify validateAll function in core/static/js/cadastro.js to enable submit button when password is valid and terms are checked, without requiring password match
- [x] Add client-side password match check in handleSubmit function to prevent form submission if passwords don't match, displaying an error message
- [x] Test the changes to ensure password dots update correctly and button enables when appropriate
- [x] Verify server-side validation still handles password mismatches
- [x] Add dark mode CSS rules for password validation dots to change colors properly in dark mode
