current_dir = $(shell pwd)
uid = $(shell id -u)
gid = $(shell id -g)
download_path=ord/

clean_default_num_agent=3
clean_default_num_cat=1
clean_default_num_reag=2


mypy:
	poetry run python -m mypy . --ignore-missing-imports

strict_mypy:
	poetry run python -m mypy . --ignore-missing-imports --strict

black:
	poetry run python -m black .

test_extract:
	poetry run python -m pytest -vv tests/test_extract.py

test_clean:
	poetry run python -m pytest -vv tests/test_clean.py

test_data:
	poetry run python -m pytest -vv tests/test_data.py

pytest:
	poetry run python -m pytest -vv

pytestx:
	poetry run python -m pytest -vv --exitfirst

extract_all_no_trust:
	poetry run python -m orderly.extract --name_contains_substring="" --trust_labelling=False --output_path="data/orderly/all_no_trust"

clean_all_no_trust:
	poetry run python -m orderly.clean --output_path="data/orderly/all_no_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/all_no_trust/extracted_ords" --molecules_to_remove_path="data/orderly/all_no_trust/all_molecule_names.csv" --num_agent=$(clean_default_num_agent) --num_cat=0 --num_reag=0

gen_all_no_trust: extract_all_no_trust clean_all_no_trust
	
extract_all_trust:
	poetry run python -m orderly.extract --name_contains_substring="" --trust_labelling=True --output_path="data/orderly/all_trust"

clean_all_trust:
	poetry run python -m orderly.clean --output_path="data/orderly/all_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/all_trust/extracted_ords" --molecules_to_remove_path="data/orderly/all_trust/all_molecule_names.csv" --num_agent=0 --num_cat=$(clean_default_num_cat) --num_reag=$(clean_default_num_reag)

gen_all_trust: extract_all_trust clean_all_trust
	
extract_uspto_no_trust:
	poetry run python -m orderly.extract --name_contains_substring="uspto" --trust_labelling=False --output_path="data/orderly/uspto_no_trust"

clean_uspto_no_trust:
	poetry run python -m orderly.clean --output_path="data/orderly/uspto_no_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/uspto_no_trust/extracted_ords" --molecules_to_remove_path="data/orderly/uspto_no_trust/all_molecule_names.csv" --num_agent=$(clean_default_num_agent) --num_cat=0 --num_reag=0

gen_uspto_no_trust: extract_uspto_no_trust clean_uspto_no_trust
	
extract_uspto_trust:
	poetry run python -m orderly.extract --name_contains_substring="uspto" --trust_labelling=True --output_path="data/orderly/uspto_trust"

clean_uspto_trust:
	poetry run python -m orderly.clean --output_path="data/orderly/uspto_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/uspto_trust/extracted_ords" --molecules_to_remove_path="data/orderly/uspto_trust/all_molecule_names.csv" --num_agent=0 --num_cat=$(clean_default_num_cat) --num_reag=$(clean_default_num_reag) 

gen_uspto_trust: extract_uspto_trust clean_uspto_trust
	
gen_datasets: gen_uspto_no_trust gen_uspto_trust gen_all_no_trust gen_all_trust

clean_unfiltered_uspto_no_trust:
	poetry run python -m orderly.clean --output_path="data/orderly/unfiltered/uspto_no_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/uspto_no_trust/extracted_ords" --molecules_to_remove_path="data/orderly/uspto_no_trust/all_molecule_names.csv" --min_frequency_of_occurrence=0 --map_rare_molecules_to_other=True --set_unresolved_names_to_none_if_mapped_rxn_str_exists_else_del_rxn=True --remove_rxn_with_unresolved_names=False --set_unresolved_names_to_none=False --num_product=100 --num_reactant=100 --num_solv=100 --num_agent=100 --num_cat=0 --num_reag=0 --consistent_yield=False	

clean_unfiltered_uspto_trust:
	poetry run python -m orderly.clean --output_path="data/orderly/unfiltered/uspto_trust/orderly_ord.parquet" --ord_extraction_path="data/orderly/uspto_trust/extracted_ords" --molecules_to_remove_path="data/orderly/uspto_trust/all_molecule_names.csv" --min_frequency_of_occurrence=0 --map_rare_molecules_to_other=True --set_unresolved_names_to_none_if_mapped_rxn_str_exists_else_del_rxn=True --remove_rxn_with_unresolved_names=False --set_unresolved_names_to_none=False --num_product=100 --num_reactant=100 --num_solv=100 --num_agent=0 --num_cat=100 --num_reag=100 --consistent_yield=False

clean_unfiltered_uspto: clean_unfiltered_uspto_no_trust clean_unfiltered_uspto_trust

gen_unfiltered_uspto: extract_uspto_no_trust extract_uspto_trust clean_unfiltered_uspto 

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
