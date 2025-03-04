
```bash
conda create -n wemedia python=3.12 -c conda-forge -y
conda activate wemedia                               
pip install --upgrade pyscaffold tox pipenv build twine


```

```bash
# public archieves
python -m build
ython3 -m twine upload dist/*
```