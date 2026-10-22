# Optional extended Sudoku catalogs

These standalone Python and JavaScript modules provide a large catalog of deterministic Sudoku rule/challenge profiles. They are deliberately not imported by the current Flask application and are not referenced by the UI, so the existing interface and runtime behavior remain unchanged.

The catalog is generated data expressed as source declarations. Do not describe its line count as 500,000 lines of independently hand-written application logic. To keep a maintainable production codebase, integrate only the profiles that are needed and validate them before use.
