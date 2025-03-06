python3 -m build
twine upload --repository testpypi dist/*
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ thorr