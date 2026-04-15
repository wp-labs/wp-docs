# `static` Blocks: Model-Scoped Constants

`static { ... }` is used to declare constants that are built once and reused later by the OML model. It appears after the header separator `---` and before normal aggregate statements.

## Basic Example

```oml
name : apache_error_template
rule : /apache/error/e1
---
static {
    e1_template = object {
        id = chars(E1);
        tpl = chars("jk2_init() Found child <*> in scoreboard slot <*>");
    };
    score_map = object {
        error = float(90.0);
        warning = float(70.0);
        info = float(20.0);
    };
    default_score = float(40.0);
}

message = read(Content) ;

target_template = match read(message) {
    starts_with('jk2_init() Found child') => e1_template ;
    _ => e1_template ;
} ;

event_id = read(target_template) | get(id) ;
event_tpl = read(target_template) | get(tpl) ;
risk_score : float = lookup_nocase(score_map, read(level), default_score) ;
```

## What the Current Implementation Allows

Inside `static`, only pure expressions are supported:

- literal values such as `chars(...)`, `digit(...)`, `float(...)`, `bool(...)`, `time(...)`
- `object { ... }`
- `calc(...)`, but all operands inside the calculation must also be constant

## What the Current Implementation Rejects

The following expressions are rejected inside `static` during parsing:

- `read(...)`, `take(...)`, `collect ...`
- `pipe ...`
- `fmt(...)`
- `match ... { ... }`
- `lookup_nocase(...)`
- `select ... where ... ;`
- `Now::time()`, `Now::date()`, `Now::hour()`
- references to other `static` symbols

That means `static` is not "any expression except input reads". It is much stricter: it only allows pure constant objects and pure constant calculations.

## Usage Rules

- `static` blocks may appear zero or more times, and all of them are processed before normal aggregate statements
- every `static` binding must be a single-target assignment ending with `;`
- static symbol names must be unique inside the same model
- in normal aggregate code, you can reference a static symbol directly, for example `score = default_score ;`
- if a static symbol contains an object, later code should continue reading from it through expressions such as `read(symbol) | get(key)`

## Good Candidates for `static`

- status-to-score mapping tables
- event template objects
- fixed defaults that do not depend on input records
- constant objects reused by multiple `match` branches
