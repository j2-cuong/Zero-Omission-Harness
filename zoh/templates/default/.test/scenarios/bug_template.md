# Bug #{id}: {title}

## Metadata
- **Bug ID:** BUG_{timestamp}_{component}
- **Created:** {date}
- **Created By:** {ai_id}
- **Status:** new | confirmed | in_fix | fixed | verified | closed
- **Priority:** critical | high | medium | low
- **Severity:** crash | hang | logic | performance | memory | concurrency
- **Component:** {component_name}

## Reproduction

### Prerequisites
```
{environment setup commands}
```

### Steps
1. {step 1}
2. {step 2}
3. {step 3}

### Environment
- **OS:** {os}
- **Runtime:** {runtime version}
- **Branch:** {branch}
- **Commit:** {commit_hash}

## Test Command

```bash
# Standardized test command (override if needed)
# Python projects:
pytest tests/test_bug_{id}.py -v

# Node.js projects:
npm test -- --testNamePattern="bug_{id}"

# Go projects:
go test -run TestBug{id} ./...

# Rust projects:
cargo test bug_{id}

# Generic:
{custom_test_command}
```

## Expected Behavior
```
{description of correct behavior}
```

## Actual Behavior
```
{description of buggy behavior}
```

## Error Output
```
{error logs, stack traces}
```

---

## Fix Verification

### Test Result After Fix
```bash
# Must pass before marking as fixed
{test_command}
```

**Result:** ⬜ PASS / ⬜ FAIL

### Regression Test
```bash
# Run full regression at merge time (optional for now)
{regression_command}
# Examples:
# pytest tests/ -v
# npm test
# go test ./...
```

---

## Timeline
| Date | Event | By |
|------|-------|-----|
| {date} | Bug reported | {reporter} |
| {date} | Test created | {creator} |
| {date} | Bug confirmed (test failed) | {confirmer} |
| {date} | Fix applied | {fixer} |
| {date} | Test passed | {verifier} |
| {date} | Regression passed | {tester} |
| {date} | Closed | {closer} |

## Lifecycle State
```yaml
lifecycle:
  current_state: {state}
  
  states:
    new: 
      - test_created_but_not_run
      - next: run_test_to_confirm
      
    confirmed:
      - test_run_and_failed
      - root_cause_investigation_required
      - next: investigate_and_fix
      
    in_fix:
      - fix_being_implemented
      - next: run_test_to_verify
      
    fixed:
      - test_run_and_passed
      - next: run_regression_test
      
    verified:
      - regression_test_passed
      - next: close_and_document
      
    closed:
      - all_tests_passed
      - documentation_updated
      
  auto_actions:
    on_fix_commit:
      - "run_bug_test_automatically"
      - "notify_if_test_fails"
      
    on_merge:
      - "run_all_bug_tests_for_regression"
      - "run_related_component_tests"
```

## Related
- **Related Issues:** {links}
- **Related PR:** {link}
- **Affects Version:** {version}
- **Fixed In Version:** {version}

---

## Notes
{additional notes}

## Attachments
- [ ] Screenshots
- [ ] Logs
- [ ] Core dump (if crash)
- [ ] Memory trace (if memory issue)
