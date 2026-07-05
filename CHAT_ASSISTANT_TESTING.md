# 🧪 Chat Assistant Testing Guide

## Quick Start Testing

### ✅ Test Scenario 1: Submit New Application + Chat

**Steps**:
1. Open Main App: http://localhost:8501
2. Fill out the form:
   ```
   Applicant ID: APP-TEST-2024-001
   Age: 35
   Income: $120,000
   Employment Type: Salaried
   Credit Score: 750
   Loan Amount: $300,000
   Tenure: 60 months
   Location: New York, NY
   Liabilities: $50,000
   ```
3. Click "✅ Submit Application"
4. **Verify**: Success message appears, data saved to database
5. Scroll to "💬 Application Chat Assistant"
6. **Verify**: Info banner shows: "🔗 **Chat Context**: Using data from Applicant ID: `APP-TEST-2024-001`"

### ✅ Test Case 1a: Ask About Approval

**User Input**: "What are my chances of approval?"

**Expected Response**:
```
Based on your profile (Credit Score: 750, Income: $120,000.00, Location: New York, NY), 
your approval chances look excellent. Current Status: SUBMITTED. 
Our team will review your application within 2-3 business days.
```

**Verify**:
- ✅ Response includes credit score from database
- ✅ Response includes income from database
- ✅ Response includes location from database
- ✅ Response includes application status
- ✅ Risk assessment is accurate

---

### ✅ Test Case 1b: Ask About Timeline

**User Input**: "How long does it take?"

**Expected Response**:
```
Standard loan applications are typically processed within 2-3 business days. 
We'll send you updates via email and SMS. You can check your status anytime 
using our search feature.
```

**Verify**:
- ✅ Generic timeline information provided
- ✅ Mentions search feature
- ✅ No data retrieval errors

---

### ✅ Test Case 1c: Ask About Documents

**User Input**: "What documents do I need?"

**Expected Response**:
```
You may need to provide: recent pay stubs, tax returns, bank statements, 
and employment verification. We'll contact you if additional documents are 
required for your application.
```

**Verify**:
- ✅ Document requirements listed
- ✅ Clear next steps

---

### ✅ Test Case 1d: Ask About Interest Rates

**User Input**: "What's the interest rate?"

**Expected Response**:
```
Interest rates vary based on your credit score (750) and loan details. 
For your requested loan amount of $300,000.00, you'll receive a formal 
quote after initial review.
```

**Verify**:
- ✅ Credit score from database included
- ✅ Loan amount from database included
- ✅ Realistic interest rate info

---

### ✅ Test Case 1e: Ask About Application Status

**User Input**: "What's my status?"

**Expected Response**:
```
Your current application status is: SUBMITTED. Loan Amount: $300,000.00, 
Credit Score: 750. Last updated in our database.
```

**Verify**:
- ✅ Application status from database
- ✅ Loan details from database
- ✅ Recent timestamp

---

### ✅ Test Case 1f: General Query (Complete Profile)

**User Input**: "Tell me about my application."

**Expected Response**:
```
📊 I'm reviewing your application:

**Profile Details:**
- Loan Amount: $300,000.00
- Credit Score: 750
- Annual Income: $120,000.00
- Employment: Salaried
- Location: New York, NY
- Status: SUBMITTED
- Risk Score: XX.X/100

How else can I assist you today?
```

**Verify**:
- ✅ All fields from database included
- ✅ Risk score calculated correctly
- ✅ Comprehensive profile summary
- ✅ Professional formatting

---

## Advanced Testing

### ✅ Test Scenario 2: Load Existing Application + Chat

**Steps**:
1. Open Main App: http://localhost:8501
2. Scroll to "🔍 Search & Retrieve Applicants"
3. Click "📋 List All" button
4. Find an existing applicant in the results
5. Click "📝 Load to Form"
6. **Verify**: Form populates with applicant data
7. Scroll to chat section
8. **Verify**: Info banner shows loaded Applicant ID
9. Ask chat questions (use Test Cases 1a-1f)

**Expected**: Chat responds with real data from loaded applicant

---

### ✅ Test Scenario 3: Search + Load + Chat

**Steps**:
1. Open Main App: http://localhost:8501
2. Scroll to "🔍 Search & Retrieve Applicants"
3. Enter search criteria:
   ```
   Min Credit Score: 700
   Max Credit Score: 800
   Employment Type: Salaried
   ```
4. Click "🔎 Search"
5. **Verify**: Results show matching applicants
6. Select an applicant and click "📝 Load to Form"
7. Chat with assistant about the loaded applicant

**Expected**: 
- ✅ Search results are accurate
- ✅ Loaded data matches database
- ✅ Chat responses use loaded data

---

### ✅ Test Scenario 4: Data Update + Chat Verification

**Steps**:
1. Submit a new application (use Test Scenario 1)
2. Scroll to chat and ask: "What's my status?"
3. **Verify**: Status is SUBMITTED
4. Search for the applicant in "Search & Retrieve Applicants"
5. Load the applicant into form
6. Modify a field (e.g., change Loan Amount to $250,000)
7. Re-submit the form (click "✅ Submit Application")
8. **Verify**: Success message (update to database)
9. Ask chat: "What's my loan amount?"
10. **Verify**: Chat responds with NEW amount ($250,000)

**Expected**:
- ✅ Chat reflects updated data immediately
- ✅ No caching of old values
- ✅ Database changes propagate to chat

---

### ✅ Test Scenario 5: Error Handling

#### Test 5a: No Applicant ID

**Steps**:
1. Clear the form using "🔄 Clear Form"
2. Scroll to chat
3. **Verify**: Warning banner shows: "⚠️ **No Applicant ID**: Please submit or load..."
4. Type a message in chat
5. Click Send

**Expected**: Error message in chat explaining no applicant loaded

---

#### Test 5b: API Connection Error (Simulate)

**Steps**:
1. Stop API server: `kill -9 5698`
2. In chat, ask: "What are my chances?"
3. **Verify**: Graceful fallback to form data or error message
4. Restart API server: `cd src/api && python3 -m uvicorn api:app --host 0.0.0.0 --port 8000`

**Expected**:
- ✅ No crash or uncaught exception
- ✅ User-friendly error message
- ✅ Fallback mechanism works

---

#### Test 5c: Missing Required Fields

**Steps**:
1. Use "🔄 Clear Form" 
2. Partially fill form with only:
   - Applicant ID: APP-TEST-PARTIAL
   - Age: 30
3. Submit without other fields
4. Ask chat: "What are my chances?"

**Expected**: 
- ✅ Error message: "Unable to retrieve your application data..."
- ✅ Helpful guidance to fill all fields

---

## Edge Cases

### ✅ Test: Special Characters in Applicant ID

**Steps**:
1. Submit with ID: `APP-TEST-2024_001-v2`
2. Ask chat question
3. **Verify**: Database lookup works with special characters

---

### ✅ Test: Very High Income/Loan Amount

**Steps**:
1. Submit with:
   - Income: $999,999,999
   - Loan Amount: $5,000,000
2. Ask chat: "Tell me about my application"
3. **Verify**: Large numbers format correctly without errors

---

### ✅ Test: Multiple Sequential Questions

**Steps**:
1. Load an applicant
2. Ask 10+ questions rapidly:
   ```
   1. What are my chances?
   2. What's the timeline?
   3. What documents?
   4. What's the rate?
   5. Can I modify?
   6. What's my status?
   7. Tell me everything
   8. What employment type am I?
   9. Where am I located?
   10. How much can I borrow?
   ```
3. **Verify**: All responses accurate and timely

**Expected**:
- ✅ Chat history maintains context
- ✅ No data corruption from rapid requests
- ✅ Consistent responses for same questions

---

## Performance Testing

### ✅ Response Time Verification

| Query Type | Expected Time | Pass/Fail |
|-----------|--------------|-----------|
| Approval chances | <1 second | __ |
| Status query | <1 second | __ |
| General profile | <2 seconds | __ |
| Error cases | <1 second | __ |

---

## Chatbot UI Testing

### ✅ Test: Chatbot Quick Search + Chat

**Steps**:
1. Open Chatbot UI: http://localhost:8502
2. In sidebar "🔍 Quick Search", enter: `APP-2024-001`
3. Click "Search"
4. **Verify**: Applicant ID loads to session
5. In main chat, enter applicant ID: `APP-2024-001`
6. Click "Send"
7. **Verify**: Processing shows results

**Expected**: Chatbot can search and process applicants with database lookup

---

## Quality Assurance Checklist

### Data Accuracy
- [ ] Credit score displayed correctly
- [ ] Income displayed correctly
- [ ] Loan amount displayed correctly
- [ ] Location displayed correctly
- [ ] Employment type displayed correctly
- [ ] Application status correct
- [ ] Risk score calculated accurately

### Response Quality
- [ ] Responses are contextual and specific
- [ ] Responses use correct pronouns and grammar
- [ ] Responses provide actionable information
- [ ] Tone is professional and friendly
- [ ] No hardcoded test data in responses

### Error Handling
- [ ] No crash on missing applicant ID
- [ ] No crash on API errors
- [ ] No crash on invalid data
- [ ] Graceful fallbacks work
- [ ] Error messages are helpful

### Performance
- [ ] Responses within 2 seconds
- [ ] No UI freezing
- [ ] No memory leaks on multiple queries
- [ ] Handles 50+ messages without slowdown

### UI/UX
- [ ] Info banner shows applicant ID
- [ ] Chat messages formatted clearly
- [ ] Long responses not cut off
- [ ] Timestamps accurate
- [ ] Scrolling works smoothly

### Database Integration
- [ ] Fetches from correct applicant ID
- [ ] Uses latest database values
- [ ] Updates reflect in chat immediately
- [ ] Fallback to form data works
- [ ] No duplicate database calls

---

## Test Results Template

```
TEST SCENARIO: ___________________
Date: ___________________
Tester: ___________________

Test Cases:
[ ] 1a: Approval chances ______
[ ] 1b: Timeline ______
[ ] 1c: Documents ______
[ ] 1d: Interest rates ______
[ ] 1e: Status ______
[ ] 1f: General profile ______

Edge Cases:
[ ] Special characters ______
[ ] Large numbers ______
[ ] Rapid queries ______
[ ] Missing data ______

Performance:
Average Response Time: _____ seconds
Max Response Time: _____ seconds
Memory Usage: _____ MB

Overall Status: [ ] PASS [ ] FAIL

Issues Found:
1. _________________________
2. _________________________
3. _________________________

Notes:
_________________________
_________________________
```

---

## Success Criteria

### ✅ Application Chat Assistant is "Production Ready" when:

1. **Data Retrieval** ✅
   - [ ] Fetches correct applicant by ID
   - [ ] Returns all relevant fields
   - [ ] Handles missing applicants gracefully

2. **Response Quality** ✅
   - [ ] Recognizes all 7 intents
   - [ ] Generates contextual responses
   - [ ] Uses real database data
   - [ ] Formatting is professional

3. **Error Handling** ✅
   - [ ] No crashes on invalid input
   - [ ] Helpful error messages
   - [ ] Graceful fallbacks
   - [ ] API errors handled

4. **Performance** ✅
   - [ ] <2 second response times
   - [ ] <100ms for cached responses
   - [ ] Handles 50+ messages
   - [ ] No memory issues

5. **Integration** ✅
   - [ ] Works with search feature
   - [ ] Works with load to form
   - [ ] Works with database updates
   - [ ] Works with both UIs

---

## Sign-Off

When all tests pass and quality criteria met:

**Tested By**: __________________
**Date**: __________________
**Status**: [ ] Ready for Production [ ] Needs Fixes

**Approved By**: __________________
**Date**: __________________
