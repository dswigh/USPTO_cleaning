current_dir = $(shell pwd)
uid = $(shell id -u)
gid = $(shell id -g)
download_path=ord/

mypy:
	poetry run python -m mypy . --ignore-missing-imports

strict_mypy:
	poetry run python -m mypy . --ignore-missing-imports --strict

black:
	poetry run python -m black .

pytest:
	poetry run python -m pytest -vv tests/test_extract.py

gen_all_no_trust:
	poetry run python -m orderly.extract --name_contains_substring="" --trust_labelling=False --output_path="data/orderly/all_no_trust"
	poetry run python -m orderly.clean --clean_data_path="data/orderly/all_no_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/all_no_trust/extracted_ords" --molecules_to_remove_path="data/orderly/all_no_trust/all_molecule_names.csv"

gen_all_trust:
	poetry run python -m orderly.extract --name_contains_substring="" --trust_labelling=True --output_path="data/orderly/all_trust"
	poetry run python -m orderly.clean --clean_data_path="data/orderly/all_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/all_trust/extracted_ords" --molecules_to_remove_path="data/orderly/all_trust/all_molecule_names.csv"

gen_uspto_no_trust:
	poetry run python -m orderly.extract --name_contains_substring="uspto" --trust_labelling=False --output_path="data/orderly/uspto_no_trust"
	poetry run python -m orderly.clean --clean_data_path="data/orderly/uspto_no_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/uspto_no_trust/extracted_ords" --molecules_to_remove_path="data/orderly/uspto_no_trust/all_molecule_names.csv"

gen_uspto_trust:
	poetry run python -m orderly.extract --name_contains_substring="uspto" --trust_labelling=True --output_path="data/orderly/uspto_trust"
	poetry run python -m orderly.clean --clean_data_path="data/orderly/uspto_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/uspto_trust/extracted_ords" --molecules_to_remove_path="data/orderly/uspto_trust/all_molecule_names.csv"

gen_datasets: gen_all_no_trust gen_all_trust gen_uspto_no_trust gen_uspto_trust

gen_test_data:
	poetry run python -m orderly.extract --data_path=orderly/data/test_data/ord_test_data --output_path=orderly/data/test_data/extracted_ord_test_data_trust_labelling  --trust_labelling=True --name_contains_substring="" --overwrite=False --use_multiprocessing=True
	poetry run python -m orderly.extract --data_path=orderly/data/test_data/ord_test_data --output_path=orderly/data/test_data/extracted_ord_test_data_dont_trust_labelling  --trust_labelling=False --name_contains_substring="" --overwrite=False --use_multiprocessing=True

build_orderly:
	docker image build --target orderly_base --tag orderly_base .
	docker image build --target orderly_base_sudo --tag orderly_base_sudo .

run_orderly:
	docker run -v $(current_dir)/data:/home/worker/repo/data/ -u $(uid):$(gid) -it orderly_base

run_orderly_sudo:
	docker run -v $(current_dir)/data:/home/worker/repo/data/ -it orderly_base_sudo

build_orderly_from_pip:
	docker image build --target orderly_pip --tag orderly_pip .

run_orderly_from_pip:
	docker run -v $(current_dir)/data:/home/worker/repo/data/ -u $(uid):$(gid) -it orderly_pip

run_orderly_black:
	docker image build --target orderly_black --tag orderly_black .
	docker run -v $(current_dir):/home/worker/repo/ -u $(uid):$(gid) orderly_black

run_orderly_pytest:
	docker image build --target orderly_test --tag orderly_test .
	docker run orderly_test

run_orderly_mypy:
	docker image build --target orderly_mypy --tag orderly_mypy .
	docker run orderly_mypy

run_orderly_mypy_strict:
	docker image build --target orderly_mypy_strict --tag orderly_mypy_strict .
	docker run orderly_mypy_strict

run_orderly_gen_test_data:
	docker image build --target orderly_gen_test_data --tag orderly_gen_test_data .
	docker run -v $(current_dir)/orderly/data/:/home/worker/repo/orderly/data/ -u $(uid):$(gid) orderly_gen_test_data

linux_download_ord:
	docker image build --target orderly_download_linux --tag orderly_download_linux .
	docker run -v $(current_dir)/data:/tmp_data -u $(uid):$(gid) orderly_download_linux

_linux_get_ord:
	mkdir -p /tmp_data/${download_path}
	touch /tmp_data/${download_path}/tst_permissions_file.txt
	rm /tmp_data/${download_path}/tst_permissions_file.txt
	curl -L -o /app/repo.zip https://github.com/open-reaction-database/ord-data/archive/refs/heads/main.zip
	unzip -o /app/repo.zip -d /app
	cp -a /app/ord-data-main/data/. /tmp_data/${download_path}

root_download_ord:
	docker image build --target orderly_download_root --tag orderly_download_root .
	docker run -v $(current_dir)/data:/tmp_data orderly_download_root
	
_root_get_ord:
	mkdir -p /tmp_data/${download_path}
	touch /tmp_data/${download_path}/tst_permissions_file.txt
	rm /tmp_data/${download_path}/tst_permissions_file.txt
	curl -L -o /app/repo.zip https://github.com/open-reaction-database/ord-data/archive/refs/heads/main.zip
	unzip -o /app/repo.zip -d /app
	cp -a /app/ord-data-main/data/. /tmp_data/${download_path}

sudo_chown:
	sudo chown -R $(uid):$(gid) $(current_dir)

build_rxnmapper:
	docker image build --target rxnmapper_base --tag rxnmapper_base .

run_rxnmapper:
	docker run -v $(current_dir)/data:/tmp_data -it rxnmapper_base

run_python_310:
	docker run -it python:3.10-slim-buster /bin/bash
