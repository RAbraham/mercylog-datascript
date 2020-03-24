* Generate Brython Library
```python
cd ./mercylog_datascript
python -m brython --make_package mercylog_datascript
```

* Update Version in `pyproject.toml`
* Commit/Push and then create a release. Add the `mercylog_datascript.brython.js` as a binary in the release

* Update mercylog-datascript-client/index.html with the latest release path