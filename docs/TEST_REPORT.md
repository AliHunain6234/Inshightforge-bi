# Test report

Executed `python -m unittest discover -s tests -v`.

- 7 tests passed
- 0 failures
- Unit coverage: password security, signed sessions, KPI contracts, risk direction and sorting
- Integration coverage: health, unauthorized denial, login, session cookie, authenticated dashboard, generic authentication errors
- Live browser smoke: login, overview, prediction queue, screenshot capture

Known gaps: production load, accessibility automation, PostgreSQL adapter, DAST, and real-data model calibration.
