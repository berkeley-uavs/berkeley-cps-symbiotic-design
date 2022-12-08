# 'ISC-License' \
Copyright (c) 2019, Timothée Mazzucotelli \
Permission to use, copy, modify, and/or distribute this software for any \
purpose with or without fee is hereby granted, provided that the above \
copyright notice and this permission notice appear in all copies. \
THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES \
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF \
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR \
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES \
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN \
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF \
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE. \

.DEFAULT_GOAL := help
SHELL := bash

DUTY = $(shell [ -n "${VIRTUAL_ENV}" ] || echo pdm run) duty

args = $(foreach a,$($(subst -,_,$1)_args),$(if $(value $a),$a="$($a)"))
check_quality_args = files
docs_serve_args = host port
release_args = version
test_args = match

BASIC_DUTIES = \
	changelog \
	check-dependencies \
	clean \
	coverage \
	docs \
	docs-deploy \
	docs-regen \
	docs-serve \
	format \
	release

QUALITY_DUTIES = \
	check-quality \
	check-docs \
	check-types \
	test

.PHONY: help
help:
	@$(DUTY) --list

.PHONY: lock
lock:
	@pdm lock

.PHONY: check
check:
	pdm run duty check-quality check-types check-docs
	@$(DUTY) check-dependencies


.PHONY: openvpn-connect
openvpn-connect:
	echo "Connecting to VPN..."
	openvpn --config ../challenge_data/aws-cvpn-config.ovpn --daemon


.PHONY: docker-broker-conf
docker-broker-conf:
	echo "Configuring broker..."
	#pdm run suam-config install --no-symlink --input=../challenge_data/data/broker.conf.yaml
	mkdir /etc/xdg/SimpleUAM
	mkdir /etc/xdg/SimpleUAM/config
	cp ../challenge_data/data/broker.conf.yaml /etc/xdg/SimpleUAM/config


.PHONY: mount-drive
mount-drive:
	echo "Mounting shared drive...(it can take some time...)"
	mkdir -p ../challenge_data/aws
	mount -t nfs 10.0.137.113:/fsx/ ../challenge_data/aws


.PHONY: results
results:
	echo "Generating results script"
	i=0
	while true; \
	do \
		echo "Iteration:"; \
		echo $$i;
		pdm run generate_random "--n=1", "--n_wings_max=0"; \
		cd ../challenge_data; \
		git add --a; \
		git commit -m "new result generated"; \
		git push; \
		echo "new result pushed to github"; \
		cd ../host; \
		(( i++ )); \
	done


.PHONY: start-ssh
start-ssh:
	echo "Starting ssh server..."
	service ssh restart


.PHONY: check
check:
	pdm run duty check-quality check-types check-docs
	@$(DUTY) check-dependencies

.PHONY: uninstall
uninstall:
	rm -rf .coverage*
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf tests/.pytest_cache
	rm -rf build
	rm -rf dist
	rm -rf htmlcov
	rm -rf pip-wheel-metadata
	rm -rf site
	find . -type d -name __pycache__ | xargs rm -rf
	find . -type d -name __pypackages__ | xargs rm -rf
	find . -name '*.rej' -delete
	find . -name pdm.lock -delete
	find . -name .pdm.toml -delete

.PHONY: $(BASIC_DUTIES)
$(BASIC_DUTIES):
	@$(DUTY) $@ $(call args,$@)

.PHONY: $(QUALITY_DUTIES)
$(QUALITY_DUTIES):
	pdm run duty $@ $(call args,$@)
