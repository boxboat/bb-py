all: build dist

rst:
	pandoc --from=markdown --to=rst --output=README.rst README.md

build:
	python setup.py build

install:
	python setup.py install

dist:
	python setup.py bdist_wheel # --universal (when support for python 3)
	tar -zcf bb-py.tgz dist

clean:
	python setup.py clean
	rm -rf build dist bb_py.egg-info bb-py.tgz
