

To create this package we run
```bash
python3 -m venv myenv
source myenv/bin/activate
python3 -m pip install --upgrade build
python3 -m pip install twine
python3 -m build
python3 -m twine upload dist/*
```

To install and test the example package
```bash
pip install voronoi_cell
python3 -m pip install voronoi_cell
```


# Things to do
Open webpage to the public
Create requirements.txt
