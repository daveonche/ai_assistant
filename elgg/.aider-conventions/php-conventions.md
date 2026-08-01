# SKILL: php-conventions (Elgg Core PHP Language Guardrails)

## 1. SOURCE CODE LAYOUT & DEFAULTS

- Enforce strict adherence to PSR-12 coding standard guidelines across all custom implementations.
- Soft tabs ONLY: Enforce exactly 4-space indentation (no hard tabs, no 2-space padding).
- Explicitly declare strict typing at the absolute head of every file: `declare(strict_types=1);`.
- DO NOT use the closing PHP tag `?>` at the end of pure PHP files to avoid accidental whitespace output.
- BANNED: The shorthand echo tag `<?=` is forbidden inside system controllers or processing hooks; use standard block tags.
- Limit maximum line length strictly to 120 characters per line. End every file with a single blank trailing newline.
- DO NOT use multi-statement lines separated by semicolons; implement exactly one expression per line.

## 2. SYNTAX, TYPES, & STRUCTURAL CONTROLS

- Enforce explicit type-hinting globally for all method arguments and return types. Use nullable indicators (`?string`) or union types (`int|float`) where applicable.
- DO NOT use legacy loose arrays `array()`. Use modern shorthand syntax exclusively: `['key' => 'value']`.
- BANNED: The keywords `and`, `or`, and `xor` are completely forbidden for boolean operations. Use `&&` and `||`.
- Enforce strict identity comparisons: ALWAYS use `===` and `!==` instead of the loose variants `==` and `!=`.
- Avoid complex nested ternary statements. Limit ternary usage strictly to simple one-liner assignments.
- Use `is_null()`, `empty()`, or explicit type verification functions over comparisons against literal types (`$var === null`).
- Prefix unused variables or ignored parameters inside execution closures with an underscore: `$_key`.

## 3. CLASS & OBJECT ARCHITECTURE

- Class structures MUST declare member visibility flags explicitly for every property and method (`public`, `protected`, `private`).
- Layout order within classes: Constants -> Public Properties -> Protected Properties -> Private Properties -> Constructor -> Magic Methods -> Public Methods -> Protected Methods -> Private Methods.
- DO NOT instantiate object classes using literal dynamic strings. Use class resolution syntax: `new UserService(User::class)`.
- Apply SOLID design paradigms and strictly adhere to the Liskov Substitution Principle (subclasses must be transparently exchangeable with parent classes).
- Use `final` wrappers on utility, configuration, or value-object classes to block unwanted deep inheritance structures.

## 4. EXCEPTIONS & ERROR CONTROL

- BANNED: Do not suppress execution errors using the `@` error-control operator under any circumstances.
- ALWAYS pass explicit message strings and type states when instantiating system failures: `throw new InvalidArgumentException('Message');`.
- NEVER intercept or rescue the root generic `Throwable` block unless re-throwing it or logging a final critical systems failure. Anchor specifically on explicit exceptions.
- Implement isolated `try-catch` structures clean within execution blocks, avoiding unnecessary structural logic encapsulation inside the error sweep.
