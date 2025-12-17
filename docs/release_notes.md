# Release Notes

## 0.3.6

### Maintenance

- Updated dependencies to address known vulnerabilities

## 0.3.5

### Bug Fixes

- Fixed string concatenation error in FileError class for required property
  validation that was causing incorrect error location paths

### Enhancements

- Added comprehensive file metadata support including created, modified, name,
  classification, modality, size, version, and zip_member_count fields to
  Flywheel object validation
- Enhanced Flywheel metadata validation with support for 'flywheel' file type
  in validator initialization

### Maintenance

- Improved error handling for Flywheel hierarchy location parsing to properly
  extract container locations from key paths
- Updated project configuration and build files

## 0.3.4

### Maintenance

- Updated build system to use multi-stage Docker builds with flywheel/python
  base image for improved performance and consistency
- Upgraded Python version to 3.13 with enhanced environment configuration
- Modernized CI/CD pipeline with updated pre-commit hooks and validation steps
- Updated documentation formatting and structure for better maintainability

## 0.3.2

### Bug Fixes

- Fixed crash when CSV headers are not present in schema by improving error
  handling in column type casting
- Corrected row number reporting in CSV validation error messages

### Changes

- Moved empty column filtering logic from validator to CSV loader for better
  separation of concerns
- Changed CSV validation to remove empty columns during loading phase rather
  than validation phase

### Maintenance

- Updated pre-commit configuration and CI/CD pipeline references
- Improved code organization and error handling patterns

## 0.3.1

### Bug Fixes

- Fixed comma counting validation for CSV files to properly handle quoted
  fields containing commas using proper CSV parsing
- Corrected row number reporting in CSV validation errors (off-by-one error)

### Maintenance

- Enhanced CSV file format validation with better error messaging
- Updated .gitignore to include .github directory

## 0.3.0

### Enhancements

- Added comprehensive CSV file format validation including comma consistency
  and header duplicate detection
- Implemented malformed file error handling for CSV files with inconsistent
  field counts
- Enhanced CSV header validation to detect and report duplicate column names

### Bug Fixes

- Fixed CSV file parsing to handle files with mismatched comma counts between
  rows
- Improved error reporting for CSV files that cannot be properly parsed

### Maintenance

- Refactored error handling system with new error types for malformed files
- Added comprehensive test coverage for CSV validation scenarios
- Updated validation workflow to catch file format errors before schema
  validation

## 0.2.9

### Enhancements

- Added support for JSONSchema `allOf` validation constructs
- Enhanced schema validation capabilities for more complex validation
  scenarios

### Maintenance

- Updated jsonschema dependency version for improved compatibility
- Improved test asset organization and naming conventions
- Updated CI/CD configuration

## 0.2.8

### Maintenance

- Updated CI/CD pipeline configuration and linting rules
- Applied comprehensive ruff linting fixes across all Python modules
- Improved code formatting and style consistency throughout the codebase
- Enhanced build and deployment processes
