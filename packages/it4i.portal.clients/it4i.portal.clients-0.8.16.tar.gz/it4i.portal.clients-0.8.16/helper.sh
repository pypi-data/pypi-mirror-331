#!/bin/bash
export IT4I_FACTORY_PREBUILD=1
python2 setup.py sdist
pip2 install dist/it4i.portal.clients-0.8.13.tar.gz
