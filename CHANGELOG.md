# Changelog

## [1.2.0] - 2024-03-04
- Set default value of `operation` parameter to `None` in `Ottu.get_payment_methods(...)` method (Earlier it was `"purchase"`).
- Removed following Django settings in favor of [`OTTU_AUTH`](/README.md#authentication-settings)
  - `OTTU_AUTH_USERNAME`
  - `OTTU_AUTH_PASSWORD`
  - `OTTU_AUTH_API_KEY`

## [1.1.1] - 2024-02-28
- Updated `Django` dependency to `<4.3` to fix compatibility issues.

## [1.1.0] - 2024-02-09

### Added
- New authentication classes (`KeycloakPasswordAuth` and `KeycloakClientAuth`).
- New method `Ottu.get_payment_methods(...)` to get available payment methods.

## [1.0.0] - 2023-12-11

### Added
- Initial release of `ottu-py` wth core APIs.
- Django integration with `ottu-py`.
- GitHub Actions workflow for automated testing and PyPI deployment.
- Pre-commit hooks configuration for code formatting and linting.
