# Sky Sentinel Testing & Coverage Report

## Testing Methodology
The testing suite utilizes `pytest` to execute both isolated unit tests and comprehensive end-to-end integration tests across all modules. 
To avoid side effects and external API costs during automated testing, the following strategies are employed:
- In-memory SQLite databases (`:memory:`) for indexer and query engine tests.
- Mocked API responses (`unittest.mock.patch`) for the Gemini Vision Language Model.
- Isolated temporary workspaces for file I/O testing (frame extraction).

## Coverage Summary
Target Overall Coverage: >= 70%

### Generating the Report
To execute the test suite and generate the HTML coverage report, run the following command from the project root:

```bash
pytest --cov=src --cov-report=html:tests/coverage_report