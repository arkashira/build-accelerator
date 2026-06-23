# Compiler
A compiler with a free tier and paid tier.

## Features
* Free tier with a reasonable limit on compilation time or codebase size
* Easy signup and upgrade process
* Scales to teams with a paid tier that offers additional features and support

## Usage
1. Create an instance of the `Compiler` class.
2. Call the `compile` method with the codebase size as an argument.
3. Check the `success` attribute of the `CompilationResult` object to see if the compilation was successful.
4. Call the `signup` method with an email address as an argument to sign up for the free tier.
5. Call the `upgrade` method with an email address as an argument to upgrade to the paid tier.
