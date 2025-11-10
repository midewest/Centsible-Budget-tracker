"# CENTSIBLE BUDGET TRACKER RULES

## TECHNICAL RULES

1. **Code Style:**
   - Follow PEP 8 guidelines for Python code
   - Use 4 spaces for indentation
   - Limit lines to 79 characters
   - Use descriptive variable and function names

2. **Database:**
   - Use SQLAlchemy ORM for all database operations
   - Implement proper indexing for frequently queried fields
   - Use transactions for all write operations

3. **Security:**
   - Always hash passwords using Werkzeug's PBKDF2
   - Implement CSRF protection on all forms
   - Validate and sanitize all user inputs
   - Use prepared statements for all SQL queries

4. **Performance:**
   - Implement caching for frequently accessed data
   - Use database connection pooling
   - Optimize queries to avoid N+1 problems

5. **Testing:**
   - Write unit tests for all new functionality
   - Maintain 90%+ test coverage
   - Include integration tests for critical paths

## BUSINESS RULES

1. **Expense Tracking:**
   - Allow manual entry of expenses
   - Support recurring expense tracking
   - Implement category management

2. **Budgeting:**
   - Allow monthly budget setting by category
   - Implement overspending alerts
   - Provide budget recommendations

3. **Reporting:**
   - Generate monthly/weekly reports
   - Support export to CSV/PDF
   - Include spending insights and trends

4. **User Experience:**
   - Implement dark mode toggle
   - Ensure mobile responsiveness
   - Provide clear visual feedback for all actions

5. **Data Privacy:**
   - Never store raw passwords
   - Implement proper data retention policies
   - Provide user data export functionality
"