All rights reserved, Open Interpreter Inc.

# Linux

```
sudo apt-get install poppler-utils wkhtmltopdf
```

# MacOS

```
brew install poppler wkhtmltopdf
```

I had to change permissions on the project dir (`sudo chown -R killianlucas:staff /Users/killianlucas/Documents/GitHub/languagetools/`) and my poetry cache (`sudo chown -R killianlucas:staff ~/Library/Caches/pypoetry/`) for poppler to work.