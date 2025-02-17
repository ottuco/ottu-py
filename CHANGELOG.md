# Changelog

## [Dev]
- Fixed `PaymentMethod.__init__() got an unexpected keyword argument 'icons'` error.

## [1.5.0] - 2024-08-16
- Added option to set `timeout` on all requests made by the SDK.

## [1.4.0] - 2024-04-02
- Added option to send dynamic parameters to session update (`Session.update(...)`)

## [1.4.0] - 2024-04-02
- Added option to send dynamic parameters to the Checkout API. The affected methods are:
  - `Ottu.checkout(...)`
  - `Ottu.checkout_autoflow(...)` (via `checkout_extra_args` parameter)
  - `Ottu.auto_debit_autoflow(...)` (via `checkout_extra_args` parameter)
- A new parameter `include_sdk_setup_preload` added new parameter to the Checkout API
- Removed positional arguments from following methods:
  - `Ottu.checkout(...)`
  - `Ottu.Session.update(...)`
  - `Ottu.checkout_autoflow(...)`
  - `Ottu.auto_debit_autoflow(...)`

## [1.3.0] - 2024-03-14
- Remove irrelevant `customer_id` check from checkout API
- Loosen `httpx` dependency (now supports `httpx>=0.25.0`)

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
