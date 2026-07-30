# Update Translations

Run the full Babel translation pipeline: extract strings, update .po files, and compile to .mo.

```bash
# 1. Extract translatable strings from source code
.venv/bin/pybabel extract --no-location -F babel.cfg -o src/locales/messages.pot src/

# 2. Update existing .po files with new strings
.venv/bin/pybabel update -i src/locales/messages.pot -d src/locales

# 3. Compile .po → .mo (required after editing translations)
.venv/bin/pybabel compile -d src/locales
```
Fix fuzzy if needed.

After running these commands, edit the `.po` files in `src/locales/<lang>/LC_MESSAGES/` to add the missing translations, then re-run step 3 to compile.
