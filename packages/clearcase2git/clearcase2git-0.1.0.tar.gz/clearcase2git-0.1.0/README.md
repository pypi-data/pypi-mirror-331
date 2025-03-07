# Coloured diff

This software makes a diff between 2 files or 2 git revision of a same file, displays it as a Clearcase diff in a RTF file.

To run the software from the root folder, run the command
```bash
python -m app.main
```

To modify the inputs, modify the file `app/main.py` and put the files to make a diff on.
The git revision diff is not yet available but is coming soon.

To activate the file rendering, uncomment the line `# rtf_writer.display(filename)` in the file `app/main.py`
