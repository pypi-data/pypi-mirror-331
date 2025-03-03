from setuptools import setup

with open('README.md', 'r') as oF:
	long_description=oF.read()

setup(
	name='mouth2-oc',
	version='2.0.4',
	description='Mouth contains a service to run outgoing communications like email and sms messages',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://ouroboroscoding.com/body/mouth2',
	project_urls={
		'Documentation': 'https://ouroboroscoding.com/body/mouth2',
		'Source': 'https://github.com/ouroboroscoding/mouth2',
		'Tracker': 'https://github.com/ouroboroscoding/mouth2/issues'
	},
	keywords=['rest','microservices'],
	author='Chris Nasr - Ouroboros Coding Inc.',
	author_email='chris@ouroboroscoding.com',
	license='Custom',
	packages=['mouth'],
	package_data={'mouth': ['definitions/*.json']},
	python_requires='>=3.10',
	install_requires=[
		'body-oc>=2.0.2,<2.1',
		'brain2-oc>=2.2.1,<2.3',
		'config-oc>=1.1.0,<1.2',
		'define-oc>=1.0.4,<1.1',
		'email-smtp>=1.0.1,<1.1',
		'namedredis>=1.0.2,<1.1',
		'rest_mysql>=1.1.5,<1.2',
		'tools-oc>=1.2.5,<1.3',
		'twilio==9.4.1',
		'undefined-oc>=1.0.0,<1.1'
	],
	entry_points={
		'console_scripts': ['mouth=mouth.__main__:cli']
	},
	zip_safe=True
)