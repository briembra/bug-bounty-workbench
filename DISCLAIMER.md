# Disclaimer

This repository is a methodology and toolkit for **authorized** security
testing. It is intended for use in one of exactly two situations:

1. You are testing a system under a bug bounty or vulnerability disclosure
   program's published policy, within that program's stated scope.
2. You own the system, or have written permission from the owner to test it.

Everything in this repository assumes that authorization exists. Nothing in it
grants authorization.

## What this repository deliberately does not contain

- Denial-of-service, load-generation, or stress tooling.
- Credential, token, OTP, or order-number brute forcers.
- Mass internet scanners or indiscriminate crawlers.
- Tooling that targets third-party platforms outside a customer's tenant.
- Anything designed to harm people rather than test systems.

## Responsibility

Running any technique here against a system you are not authorized to test may
be a criminal offence in your jurisdiction (for example under the U.S. Computer
Fraud and Abuse Act, the UK Computer Misuse Act, or the Dutch Wetboek van
Strafrecht art. 138ab). You are responsible for the systems you touch and the
data you handle.

## Data handling

Bug bounty work regularly exposes personal data. If you encounter real user
data:

- capture the minimum needed to prove impact (one record),
- redact identifying fields in the report,
- do not store the dataset, do not share it, do not enumerate further,
- tell the program.

## No warranty

The authors accept no liability for misuse, damage, legal consequences, or
bounty outcomes. The software and documentation are provided as-is under the MIT
license.
