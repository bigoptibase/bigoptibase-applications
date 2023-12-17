VERS := $(shell grep 'version=' setup.py | sed -E 's/\s+version="//' | sed 's/",\s*//')

clean:
		rm -r build
		rm -r dist
		rm -r dcss.egg-info

dist-clean:
		rm ansible/*.whl

build:
		env/bin/python setup.py bdist_wheel
		cp dist/* ansible/.

deploy-staging:
		ansible-playbook ansible/cicd.yml -i ansible/staging

deploy-prod:
		ansible-playbook ansible/cicd.yml -i ansible/production

deploy-staging-current:
		ansible-playbook ansible/cicd.yml -i ansible/staging -e "bob_pkg_name=dcss-${VERS}-py3-none-any.whl"

deploy-prod-current:
		ansible-playbook ansible/cicd.yml -i ansible/production -e "bob_pkg_name=dcss-${VERS}-py3-none-any.whl"
